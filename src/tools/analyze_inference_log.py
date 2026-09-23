#!/usr/bin/env python3
"""Analyze CEM888_TELEMETRY log events into per-turn ship-readiness metrics.

Consumes privacy-preserving telemetry events emitted by agent/inference_telemetry.py
(prefix ``CEM888_TELEMETRY``). Produces, per opaque turn_id:

  * API (inference) calls per turn
  * Tool calls per turn
  * Repeated-tool re-open detection (same tool hit repeatedly on one turn)
  * Cache-read vs fresh-token margin
  * Token / latency / cost aggregates

No prompts, responses, tool args, URLs, or raw session ids are read or emitted
— only the privacy-preserving scalar allowlist fields already in the events.

Usage:
    python3 tools/analyze_inference_log.py PATH_TO_LOG [--min-events N] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List


EVENT_PREFIX = "CEM888_TELEMETRY "
ALLOWED_ANALYSIS_FIELDS = {
    "event", "call_id", "turn_id", "session_id", "purpose", "tool_name",
    "provider", "model", "provider_class", "outcome", "error_class", "attempt",
    "api_calls", "provider_count", "provider_hits", "provider_errors",
    "context_chars", "input_tokens", "output_tokens", "total_tokens",
    "cache_read_tokens", "cache_write_tokens", "reasoning_tokens",
    "estimated_cost_usd", "cost_status", "duration_ms", "completed", "failed",
    "interrupted", "partial", "blocked", "exit_reason",
}


def parse_events(text: str) -> List[Dict]:
    """Extract telemetry event dicts from a log blob."""
    events: List[Dict] = []
    for match in re.finditer(re.escape(EVENT_PREFIX) + r"(\{.*?\})\n", text):
        try:
            rec = json.loads(match.group(1))
        except Exception:
            continue
        # only keep allowlisted fields
        events.append({k: v for k, v in rec.items() if k in ALLOWED_ANALYSIS_FIELDS})
    return events


def timefield(rec: Dict) -> int:
    return int(rec.get("timestamp_unix_ms", 0))


def analyze(events: List[Dict]) -> Dict:
    # Group by turn
    turns: Dict[str, List[Dict]] = defaultdict(list)
    for rec in events:
        turns[rec.get("turn_id", "")].append(rec)

    per_turn: Dict[str, Dict] = {}
    for turn_id, recs in turns.items():
        if not turn_id:
            continue
        infer_started = [r for r in recs if r.get("event") == "inference_started"]
        infer_completed = [r for r in recs if r.get("event") == "inference_completed"]
        tool_events = [r for r in recs if r.get("event", "").startswith("tool_")]
        tool_success = [r for r in tool_events if r.get("event") == "tool_completed" and r.get("outcome") == "success"]

        # re-open detection: same tool repeatedly, with a short gap (likely re-reading a file)
        tool_names = [r.get("tool_name", "?") for r in tool_success]
        repeats = {name: n for name, n in Counter(tool_names).items() if n > 1}

        cache_read = sum(r.get("cache_read_tokens", 0) for r in infer_completed)
        fresh = sum(r.get("input_tokens", 0) for r in infer_completed)
        total = sum(r.get("total_tokens", 0) for r in infer_completed)

        per_turn[turn_id] = {
            "inference_calls": len(set(r.get("call_id") for r in infer_started + infer_completed if r.get("call_id"))),
            "inference_completed": len(infer_completed),
            "tool_events": len(tool_events),
            "tool_success": len(tool_success),
            "repeated_tools": repeats,
            "cache_read_tokens": cache_read,
            "fresh_input_tokens": fresh,
            "total_tokens": total,
            "cache_hit_pct": round(100.0 * cache_read / total, 1) if total else 0.0,
            "duration_ms": max((r.get("duration_ms", 0) for r in infer_completed), default=0),
        }

    # Aggregate across turns
    agg = {
        "turns": len(per_turn),
        "total_inference_calls": sum(v["inference_calls"] for v in per_turn.values()),
        "total_tool_success": sum(v["tool_success"] for v in per_turn.values()),
        "total_tokens": sum(v["total_tokens"] for v in per_turn.values()),
        "avg_inference_calls_per_turn": round(sum(v["inference_calls"] for v in per_turn.values()) / len(per_turn), 2) if per_turn else 0,
        "avg_tool_success_per_turn": round(sum(v["tool_success"] for v in per_turn.values()) / len(per_turn), 2) if per_turn else 0,
        "avg_cache_hit_pct": round(sum(v["cache_hit_pct"] for v in per_turn.values()) / len(per_turn), 1) if per_turn else 0.0,
        "turns_with_reruns": sum(1 for v in per_turn.values() if v["repeated_tools"]),
    }
    return {"aggregate": agg, "per_turn": per_turn}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logfile", help="path to agent log containing CEM888_TELEMETRY events")
    ap.add_argument("--min-events", type=int, default=10, help="ignore logfiles with fewer telemetry events")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    try:
        text = open(args.logfile, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    events = parse_events(text)
    if len(events) < args.min_events:
        print(f"only {len(events)} telemetry events (< {args.min_events}); not enough to analyze", file=sys.stderr)
        return 2

    result = analyze(events)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    agg = result["aggregate"]
    print("=== CEM888 TELEMETRY — per-turn ship-readiness aggregate ===")
    print(f"turns analyzed            : {agg['turns']}")
    print(f"total inference calls     : {agg['total_inference_calls']}")
    print(f"total tool successes      : {agg['total_tool_success']}")
    print(f"avg API calls / turn      : {agg['avg_inference_calls_per_turn']}")
    print(f"avg tool successes / turn : {agg['avg_tool_success_per_turn']}")
    print(f"avg cache-hit %           : {agg['avg_cache_hit_pct']}%")
    print(f"turns with repeated tools : {agg['turns_with_reruns']}")
    print()
    print("=== per-turn detail (inference calls + re-opens) ===")
    for tid, v in sorted(result["per_turn"].items(), key=lambda kv: -kv[1]["inference_calls"])[:15]:
        print(f"  turn {tid[:12]}…  infer={v['inference_calls']}  tools={v['tool_success']}  "
              f"cache={v['cache_hit_pct']}%  reruns={v['repeated_tools'] or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
