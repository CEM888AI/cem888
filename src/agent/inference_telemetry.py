"""Privacy-preserving structured telemetry for turns and model inference.

Only an explicit scalar allowlist is serialized. Prompts, responses, tool
arguments, URLs, credentials, and raw session/task identifiers are never
accepted by :func:`emit`.
"""

from __future__ import annotations

import contextvars
import hashlib
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional


logger = logging.getLogger("cem888.inference_telemetry")
EVENT_PREFIX = "CEM888_TELEMETRY "
SCHEMA_VERSION = 1

_TURN_ID = contextvars.ContextVar("cem888_telemetry_turn_id", default="")
_SESSION_ID = contextvars.ContextVar("cem888_telemetry_session_id", default="")
_INFERENCE_CALL_ID = contextvars.ContextVar("cem888_telemetry_inference_call_id", default="")
_INFERENCE_ATTEMPT = contextvars.ContextVar("cem888_telemetry_inference_attempt", default=0)

_ALLOWED_FIELDS = {
    "event",
    "call_id",
    "turn_id",
    "session_id",
    "purpose",
    "tool_name",
    "provider",
    "model",
    "provider_class",
    "outcome",
    "error_class",
    "attempt",
    "api_calls",
    "provider_count",
    "provider_hits",
    "provider_errors",
    "context_chars",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "reasoning_tokens",
    "estimated_cost_usd",
    "cost_status",
    "cost_source",
    "duration_ms",
    "completed",
    "failed",
    "interrupted",
    "partial",
    "blocked",
    "exit_reason",
}


def opaque_id(value: Any) -> str:
    """Return a stable non-reversible identifier suitable for correlation."""
    if not isinstance(value, str) or not value:
        return ""
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]


def provider_class(provider: Any, base_url: Any = "") -> str:
    provider_name = str(provider or "").strip().lower()
    base = str(base_url or "").strip().lower()
    if provider_name in {"ollama", "lmstudio", "local", "vllm"}:
        return "local"
    if any(marker in base for marker in ("localhost", "127.0.0.1", "0.0.0.0")):
        return "local"
    return "cloud" if provider_name or base else "unknown"


def set_turn_context(turn_id: Any, session_id: Any = ""):
    """Bind pseudonymous correlation IDs and return reset tokens."""
    return (
        _TURN_ID.set(opaque_id(turn_id)),
        _SESSION_ID.set(opaque_id(session_id)),
    )


def reset_turn_context(tokens) -> None:
    turn_token, session_token = tokens
    _TURN_ID.reset(turn_token)
    _SESSION_ID.reset(session_token)


def current_turn_id() -> str:
    return _TURN_ID.get()


def current_session_id() -> str:
    return _SESSION_ID.get()


def new_call_id() -> str:
    return uuid.uuid4().hex[:24]


def set_inference_context(call_id: str):
    return (
        _INFERENCE_CALL_ID.set(str(call_id or "")[:160]),
        _INFERENCE_ATTEMPT.set(0),
    )


def reset_inference_context(tokens) -> None:
    call_token, attempt_token = tokens
    _INFERENCE_CALL_ID.reset(call_token)
    _INFERENCE_ATTEMPT.reset(attempt_token)


def current_inference_call_id() -> str:
    return _INFERENCE_CALL_ID.get()


def next_inference_attempt() -> int:
    attempt = _INFERENCE_ATTEMPT.get() + 1
    _INFERENCE_ATTEMPT.set(attempt)
    return attempt


def _safe_scalar(value: Any) -> Optional[Any]:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:160]
    return None


def emit(event: str, **fields: Any) -> Dict[str, Any]:
    """Log and return one canonical telemetry event.

    Unknown keys are discarded. This is a deliberate data-loss boundary that
    prevents future callers from accidentally logging content-bearing objects.
    """
    record: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "event": str(event or "unknown")[:80],
        "timestamp_unix_ms": int(time.time() * 1000),
    }
    defaults = {
        "turn_id": current_turn_id(),
        "session_id": current_session_id(),
    }
    defaults.update(fields)
    for key, value in defaults.items():
        if key not in _ALLOWED_FIELDS or key == "event":
            continue
        scalar = _safe_scalar(value)
        if scalar not in (None, ""):
            record[key] = scalar
    try:
        logger.info(
            "%s%s",
            EVENT_PREFIX,
            json.dumps(record, sort_keys=True, separators=(",", ":")),
        )
    except Exception:
        # Observability must never change inference, tool, memory, or turn
        # behavior. Logging failures are deliberately non-fatal.
        pass
    return record


def response_usage(response: Any) -> Dict[str, int]:
    """Extract normalized token counters without retaining response content."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}

    def get(*names: str) -> int:
        for name in names:
            if isinstance(usage, dict):
                value = usage.get(name)
            else:
                value = getattr(usage, name, None)
            if isinstance(value, (int, float)) and value >= 0:
                return int(value)
        return 0

    input_tokens = get("input_tokens", "prompt_tokens")
    output_tokens = get("output_tokens", "completion_tokens")
    total_tokens = get("total_tokens") or input_tokens + output_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cache_read_tokens": get("cache_read_input_tokens", "cache_read_tokens"),
        "cache_write_tokens": get("cache_creation_input_tokens", "cache_write_tokens"),
        "reasoning_tokens": get("reasoning_tokens"),
    }
