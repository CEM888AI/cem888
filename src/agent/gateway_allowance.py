"""Gateway allowance check — pre-call gate for free message / credit enforcement.

Called before each LLM turn to verify the user still has free messages
or credits remaining. When both are exhausted, returns a hard-stop message.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
from pathlib import Path
from typing import Optional

from cem888_constants import get_cem888_home

logger = logging.getLogger(__name__)

GATEWAY_ALLOWANCE_URL = "https://cem888.ai/api/allowance"
FREE_MESSAGES_DEFAULT = 1000
REQUEST_TIMEOUT = 10  # seconds — must be fast, blocking the turn otherwise


def _resolve_cem_api_token() -> Optional[str]:
    """Resolve the CEM888.AI API token from the active profile's .env."""
    token = os.getenv("CEM_API_TOKEN", "").strip()
    if token:
        return token

    # Fallback: read from the profile's .env file directly
    cem888_home = get_cem888_home()
    if cem888_home:
        env_path = Path(cem888_home) / ".env"
        if env_path.exists():
            try:
                for line in env_path.read_text().splitlines():
                    if line.startswith("CEM_API_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if token:
                            return token
            except Exception:
                pass
    return None


def check_allowance() -> dict:
    """Query the CEM888 gateway for the current user's allowance.

    Returns:
        {
            "can_proceed": bool,
            "free_messages_remaining": int,
            "credit_balance": float,
            "action": str | None,       # "top_up" when blocked
            "top_up_url": str | None,
            "error": str | None,        # set when the check itself fails
        }
    """
    token = _resolve_cem_api_token()
    if not token:
        # No CEM888 API token — not using the CEM888 gateway proxy.
        # Allow through; this agent is using its own API keys directly.
        return {
            "can_proceed": True,
            "free_messages_remaining": None,
            "credit_balance": None,
            "action": None,
            "top_up_url": None,
            "error": None,
        }

    try:
        req = urllib.request.Request(
            GATEWAY_ALLOWANCE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())

        return {
            "can_proceed": data.get("can_proceed", True),
            "free_messages_remaining": data.get("free_messages_remaining"),
            "credit_balance": data.get("credit_balance"),
            "action": data.get("action"),
            "top_up_url": data.get("top_up_url"),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        if e.code == 402:
            body = {}
            try:
                body = json.loads(e.read().decode())
            except Exception:
                pass
            return {
                "can_proceed": False,
                "free_messages_remaining": 0,
                "credit_balance": 0,
                "action": "top_up",
                "top_up_url": body.get("top_up_url", "https://cem888.ai/profile.html?topup=true"),
                "error": body.get("error", "Credits exhausted"),
            }
        logger.warning("Gateway allowance HTTP %d: %s", e.code, e.reason)
        return {
            "can_proceed": True,  # Fail open — don't block on gateway error
            "free_messages_remaining": None,
            "credit_balance": None,
            "action": None,
            "top_up_url": None,
            "error": f"Gateway returned HTTP {e.code}",
        }
    except Exception as exc:
        logger.warning("Gateway allowance check failed: %s", exc)
        return {
            "can_proceed": True,  # Fail open — don't block on network error
            "free_messages_remaining": None,
            "credit_balance": None,
            "action": None,
            "top_up_url": None,
            "error": str(exc),
        }


def format_block_message(allowance: dict) -> str:
    """Return a user-facing message when the allowance gate blocks."""
    free = allowance.get("free_messages_remaining", 0)
    credits = allowance.get("credit_balance", 0)
    top_up_url = allowance.get("top_up_url", "https://cem888.ai/profile.html")

    return (
        f"🚫 **Message limit reached.**\n\n"
        f"You've used all {FREE_MESSAGES_DEFAULT} free messages and have "
        f"${credits:.2f} in credits remaining.\n\n"
        f"To continue using CEM888, add API compute credits:\n"
        f"{top_up_url}"
    )
