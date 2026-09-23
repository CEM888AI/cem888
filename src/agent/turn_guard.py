"""
Turn Guard — prevents agent infinite loops in group chats.

Each agent gets N turns after a human speaks. When turns hit 0,
the agent stops responding until a human speaks again, which resets
the counter.

State is persisted per-profile so it survives gateway restarts.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────
# The guard is profile-owned.  A customer wheel must never inherit another
# agent's Matrix room or human identity.  Leave it inactive until the
# installing customer explicitly configures all three participants.
GROUP_CHAT_ROOM_ID = os.environ.get("TURN_GUARD_ROOM_ID", "").strip()
HUMAN_USER_ID = os.environ.get("TURN_GUARD_HUMAN_USER", "").strip()
OTHER_AGENT_ID = os.environ.get("TURN_GUARD_OTHER_AGENT", "").strip()
MAX_TURNS = 5

# ── State persistence ──────────────────────────────────────────

def _state_path() -> Path:
    """Resolve the turn-guard state file for this agent's profile."""
    home = os.environ.get("CEM888_HOME", os.path.expanduser("~/.cem888"))
    return Path(home) / "turn_guards.json"


def _load() -> dict:
    path = _state_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            logger.warning("Turn guard state corrupt, resetting.")
    return {}


def _save(state: dict) -> None:
    _state_path().write_text(json.dumps(state, indent=2))


# ── Public API ─────────────────────────────────────────────────

def reset_turns(room_id: str | None = None) -> None:
    """Reset turn counter — called when human speaks."""
    room_id = room_id or GROUP_CHAT_ROOM_ID
    if not room_id:
        return
    state = _load()
    state[room_id] = {"remaining": MAX_TURNS, "last_human_ts": time.time()}
    _save(state)
    logger.info("Turn guard: reset %s to %d turns", room_id, MAX_TURNS)


def check_and_decrement(room_id: str | None = None) -> bool:
    """
    Check if we have turns remaining and decrement.
    Returns True if we should respond, False if we're out of turns.
    """
    room_id = room_id or GROUP_CHAT_ROOM_ID
    if not room_id:
        return True
    state = _load()
    entry = state.get(room_id, {"remaining": MAX_TURNS})
    remaining = entry.get("remaining", MAX_TURNS)

    if remaining <= 0:
        logger.debug("Turn guard: %s — out of turns, blocking response", room_id)
        return False

    remaining -= 1
    entry["remaining"] = remaining
    state[room_id] = entry
    _save(state)
    logger.info("Turn guard: %s — %d turns remaining", room_id, remaining)
    return True


def should_process_message(sender: str, room_id: str) -> bool:
    """
    The single entry point for turn-guard gating.
    Call this in _on_room_message to decide whether to process.

    Returns True if the message should be processed.
    """
    # Customer installs are unrestricted until their own group participants
    # are configured.  Never let a missing guard configuration block chat.
    if not GROUP_CHAT_ROOM_ID or not HUMAN_USER_ID or not OTHER_AGENT_ID:
        return True
    # Only gate the configured group chat
    if room_id != GROUP_CHAT_ROOM_ID:
        return True

    sender_clean = (sender or "").strip()

    # Human always resets and passes through
    if sender_clean == HUMAN_USER_ID:
        reset_turns(room_id)
        return True

    # Other agent? Check our turns
    if sender_clean == OTHER_AGENT_ID:
        return check_and_decrement(room_id)

    # Unknown sender in group chat — allow through
    return True
