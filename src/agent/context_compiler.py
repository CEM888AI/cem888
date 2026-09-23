"""Deterministic minimal-sufficient context compilation.

Raw session history remains untouched.  This module builds an API-time-only
view containing a bounded recent exchange window and a typed packet of ranked
authoritative state.  Receipts contain metadata and hashes, never raw context.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


DEFAULT_TOKEN_BUDGET = 1024
DEFAULT_RECENT_EXCHANGES = 3


@dataclass(frozen=True)
class Candidate:
    source_id: str
    source_type: str
    content: str
    authority: int
    active: bool = True
    verified: bool = True
    unresolved: bool = False


@dataclass
class CompiledContext:
    messages: list[dict]
    current_user_index: int
    packet: str
    receipt: dict


def _profile_home() -> Path:
    configured = os.environ.get("CEM888_HOME", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    # An unset profile is a new standalone agent.  Live agents supply
    # CEM888_HOME/CEM888_PROFILE explicitly.
    profile = os.environ.get("CEM888_PROFILE", "default").strip() or "default"
    return (Path.home() / ".cem888" / "profiles" / profile).resolve()


def _tokens(text: str) -> int:
    return max(0, (len(text) + 3) // 4)


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9_./:-]+", text.lower()) if len(term) > 2}


def _bounded_read(path: Path, limit: int = 24000) -> str:
    try:
        if not path.is_file():
            return ""
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def _active_pathways(home: Path) -> list[Candidate]:
    db = home / "state" / "memory_provenance.db"
    if not db.is_file():
        return []
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True, timeout=2)
        rows = conn.execute(
            "SELECT id, kind, canonical_payload, scope, last_success_evidence "
            "FROM pathways WHERE status='active' ORDER BY updated_at DESC LIMIT 50"
        ).fetchall()
        conn.close()
    except (sqlite3.Error, OSError):
        return []
    return [
        Candidate(
            source_id=str(row[0]), source_type=f"canonical_pathway:{row[1]}",
            content=f"scope={row[3]} value={row[2]} evidence={row[4]}", authority=100,
        )
        for row in rows
    ]


def _typed_memory_candidates(home: Path, user_query: str) -> list[Candidate]:
    """Read the CEM-82 durable store, never the bounded manifest.

    Current, verified, same-project/task records are scored by the normal MSCC
    selector.  Superseded/archived rows are intentionally excluded here and
    remain available through the explicit memory(recall, include_history=true)
    tool path.
    """
    database = home / "state" / "memory_provenance.db"
    if not database.is_file():
        return []
    try:
        conn = sqlite3.connect(f"file:{database}?mode=ro&immutable=1", uri=True, timeout=2)
        rows = conn.execute(
            "SELECT id, content, memory_type, scope, project, task, authority, source, provenance, verification_status "
            "FROM typed_memories WHERE lifecycle_status='active' AND superseded_by IS NULL "
            "ORDER BY updated_at DESC LIMIT 200"
        ).fetchall()
        conn.close()
    except (sqlite3.Error, OSError):
        return []
    terms = _terms(user_query)
    candidates: list[Candidate] = []
    for row in rows:
        content = str(row[1] or "")
        metadata = " ".join(str(item or "") for item in row[2:8]).lower()
        overlap = len(terms & _terms(content + " " + metadata))
        if terms and overlap == 0:
            continue
        authority = 94 if str(row[9]).lower() == "verified" else 82
        candidates.append(Candidate(
            source_id=str(row[0]), source_type=f"typed_memory:{row[2]}",
            content=(f"scope={row[3]} project={row[4] or '-'} task={row[5] or '-'} "
                     f"authority={row[6]} source={row[7]} provenance={row[8] or '-'}\n{content}"),
            authority=authority,
        ))
    return candidates


def _paragraph_candidates(source_id: str, source_type: str, text: str, authority: int) -> list[Candidate]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n|(?=^##? )", text, flags=re.MULTILINE) if chunk.strip()]
    return [
        Candidate(f"{source_id}:{index}", source_type, chunk[:6000], authority)
        for index, chunk in enumerate(chunks[:80])
    ]


def collect_candidates(
    *,
    user_query: str,
    plugin_context: str = "",
    memory_context: str = "",
    home: Optional[Path] = None,
) -> list[Candidate]:
    home = home or _profile_home()
    candidates: list[Candidate] = []
    identity = "\n".join(
        part for part in (
            _bounded_read(home / "SOUL.md", 8000),
            _bounded_read(home / "USER.md", 5000),
        ) if part
    )
    if identity:
        candidates.extend(_paragraph_candidates("profile_identity", "identity_relationship", identity, 95))
    files = [
        (home / "state" / "continuity_packet.json", "current_checkpoint", 92),
        (home / "plugins" / "engineering-logger" / "STATE_POINTERS.md", "open_work", 90),
        (home / "plugins" / "observer" / "CURRENT_WORLD_STATE.md", "verified_world_state", 88),
        (home / "plugins" / "work-mode" / "state.json", "current_objective", 91),
        (home / "state" / "gatekeeper_state.json", "tool_state", 84),
    ]
    for path, kind, authority in files:
        text = _bounded_read(path)
        if text:
            candidates.extend(_paragraph_candidates(str(path.relative_to(home)), kind, text, authority))
    candidates.extend(_active_pathways(home))
    candidates.extend(_typed_memory_candidates(home, user_query))
    # CEM-170 FIX: pre_llm_call output is NOT a candidate.
    #
    # It used to be compiled in here as source_type "continuity_retrieval" with
    # authority 78.  _score() then applied the normal relevance gate: when the
    # user's message shared no terms with the injected text the candidate scored
    # -1000 and was dropped before selection.  Context that a plugin had
    # explicitly returned for injection -- scratch-pad prohibitions, unresolved
    # file-mutation warnings, work-mode anchors -- was therefore silently
    # discarded on any turn that did not already happen to be discussing it.
    # Authority 95 (identity tier) was the only thing exempt from that gate,
    # which is why SOUL.md survived and everything else did not.
    #
    # The parameter is retained for call-site compatibility and is intentionally
    # unused: agent/conversation_loop.py now appends plugin context to the turn's
    # user message unconditionally, honouring the documented pre_llm_call
    # contract ("context is ALWAYS injected into the user message").
    del plugin_context
    if memory_context:
        candidates.extend(_paragraph_candidates("memory_prefetch", "retrieved_memory", memory_context, 70))
    return candidates


def _score(candidate: Candidate, query_terms: set[str]) -> tuple[int, str]:
    if not candidate.active:
        return (-100000, "inactive_or_superseded")
    terms = _terms(candidate.content)
    overlap = len(query_terms & terms)
    if query_terms and overlap == 0 and candidate.authority < 95 and not candidate.unresolved:
        return (-1000, "no_query_relevance")
    score = candidate.authority * 10 + overlap * 35
    if candidate.verified:
        score += 30
    if candidate.unresolved:
        score += 25
    reason = f"authority={candidate.authority};overlap={overlap};verified={int(candidate.verified)}"
    return score, reason


def select_candidates(candidates: Iterable[Candidate], user_query: str, token_budget: int) -> tuple[list[Candidate], list[dict]]:
    query_terms = _terms(user_query)
    ranked = []
    for candidate in candidates:
        score, reason = _score(candidate, query_terms)
        ranked.append((score, candidate.source_id, candidate, reason))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected: list[Candidate] = []
    decisions: list[dict] = []
    used = 0
    seen_hashes: set[str] = set()
    for score, _, candidate, reason in ranked:
        digest = hashlib.sha256(candidate.content.encode("utf-8", errors="replace")).hexdigest()
        cost = _tokens(f"[{candidate.source_type} id={candidate.source_id}]\n{candidate.content}\n\n")
        include = score >= 0 and digest not in seen_hashes and used + cost <= token_budget
        decisions.append({
            "source_id": candidate.source_id,
            "source_type": candidate.source_type,
            "included": include,
            "score": score,
            "reason": "duplicate" if digest in seen_hashes else ("budget" if score >= 0 and used + cost > token_budget else reason),
            "tokens": cost,
        })
        if include:
            selected.append(candidate)
            seen_hashes.add(digest)
            used += cost
    return selected, decisions


def _recent_messages(messages: list[dict], exchanges: int) -> tuple[list[dict], int]:
    if not messages:
        return [], -1
    user_indices = [i for i, msg in enumerate(messages) if isinstance(msg, dict) and msg.get("role") == "user"]
    start = user_indices[-min(len(user_indices), max(1, exchanges))] if user_indices else max(0, len(messages) - 8)
    chosen = []
    current_original = user_indices[-1] if user_indices else len(messages) - 1
    current_new = -1
    for original_index, msg in enumerate(messages[start:], start=start):
        if not isinstance(msg, dict):
            continue
        copied = msg.copy()
        chosen.append(copied)
        if original_index == current_original:
            current_new = len(chosen) - 1
    return chosen, current_new


def compile_context(
    messages: list[dict],
    *,
    user_query: str,
    plugin_context: str = "",
    memory_context: str = "",
    token_budget: Optional[int] = None,
    recent_exchanges: Optional[int] = None,
    provider: str = "",
    model: str = "",
) -> CompiledContext:
    budget = token_budget or int(os.environ.get("CEM888_CONTEXT_PACKET_TOKENS", DEFAULT_TOKEN_BUDGET))
    recent = recent_exchanges or int(os.environ.get("CEM888_CONTEXT_RECENT_EXCHANGES", DEFAULT_RECENT_EXCHANGES))
    budget = max(512, min(budget, 32768))
    recent = max(1, min(recent, 8))
    candidates = collect_candidates(user_query=user_query, plugin_context=plugin_context, memory_context=memory_context)
    # Reserve enough space for the packet's outer XML-style envelope. Section
    # headers are charged by select_candidates, so the configured ceiling is a
    # ceiling on the complete packet rather than only its payload.
    selected, decisions = select_candidates(candidates, user_query, max(128, budget - 32))
    sections = []
    section_tokens: dict[str, int] = {}
    for candidate in selected:
        text = f"[{candidate.source_type} id={candidate.source_id}]\n{candidate.content}"
        sections.append(text)
        section_tokens[candidate.source_type] = section_tokens.get(candidate.source_type, 0) + _tokens(text)
    packet_id = "ctx_" + hashlib.sha256(
        (user_query + "\0" + "\0".join(item.source_id for item in selected)).encode("utf-8", errors="replace")
    ).hexdigest()[:24]
    packet = "<minimal_sufficient_context packet_id=\"%s\">\n%s\n</minimal_sufficient_context>" % (
        packet_id, "\n\n".join(sections)
    ) if sections else ""
    recent_messages, current_user_index = _recent_messages(messages, recent)
    receipt = {
        "schema_version": 1,
        "context_packet_id": packet_id,
        "created_at_unix_ms": int(time.time() * 1000),
        "state_version": 1,
        "selected": [item.source_id for item in selected],
        "selected_types": [item.source_type for item in selected],
        "excluded": [item["source_id"] for item in decisions if not item["included"]][:100],
        "selection": decisions,
        "section_tokens": section_tokens,
        "packet_tokens": _tokens(packet),
        "recent_message_count": len(recent_messages),
        "recent_exchange_limit": recent,
        "raw_message_count": len(messages),
        "query_sha256": hashlib.sha256(user_query.encode("utf-8", errors="replace")).hexdigest(),
        "provider": str(provider or "")[:80],
        "model": str(model or "")[:120],
    }
    _atomic_json(_profile_home() / "state" / "context_receipts" / "latest.json", receipt)
    return CompiledContext(recent_messages, current_user_index, packet, receipt)


def enabled() -> bool:
    """Return whether this profile selected the canonical MSCC lifecycle.

    The environment override remains useful for an explicitly controlled
    canary.  Ordinary gateway and customer installs select the same runtime
    implementation through the existing ``plugins.enabled`` configuration,
    so profile-local wrappers do not become a second implementation.
    """
    override = os.environ.get("CEM888_MINIMAL_CONTEXT", "").strip().lower()
    if override:
        return override in {"1", "true", "yes", "on"}
    config_path = _profile_home() / "config.yaml"
    try:
        import yaml
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        enabled_plugins = ((config.get("plugins") or {}).get("enabled") or [])
        return "minimal-context-compiler" in enabled_plugins
    except (ImportError, OSError, ValueError, TypeError):
        # The runtime remains fail-open when an old/minimal install lacks
        # PyYAML.  A deployment that needs MSCC can still opt in explicitly
        # with CEM888_MINIMAL_CONTEXT.
        return False
