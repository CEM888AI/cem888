"""Telegram network helpers — slimmed for CEM888."""
from __future__ import annotations
from typing import List


class TelegramFallbackTransport:
    """Stub — fallback transport not needed for local CEM888 agent."""
    def __init__(self, *args, **kwargs):
        pass


async def discover_fallback_ips() -> List[str]:
    """Return empty list — no fallback IPs needed for CEM888."""
    return []


def parse_fallback_ip_env(env_val: str | None) -> List[str]:
    """Return empty list — stub (called synchronously from _fallback_ips)."""
    return []
