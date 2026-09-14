"""Generic managed-tool gateway helpers for CEM888.AI-hosted vendor passthroughs."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)

from cem888_constants import get_cem888_home
from tools.tool_backend_helpers import managed_cem888_tools_enabled

_DEFAULT_TOOL_GATEWAY_DOMAIN = "cem888.ai"
_DEFAULT_TOOL_GATEWAY_SCHEME = "https"
_CEM888_ACCESS_TOKEN_REFRESH_SKEW_SECONDS = 120


@dataclass(frozen=True)
class ManagedToolGatewayConfig:
    vendor: str
    gateway_origin: str
    cem888_user_token: str
    managed_mode: bool


def auth_json_path():
    """Return the CEM888 auth store path, respecting CEM888_HOME overrides."""
    return get_cem888_home() / "auth.json"


def _read_cem888_provider_state() -> Optional[dict]:
    try:
        path = auth_json_path()
        if not path.is_file():
            return None
        data = json.loads(path.read_text())
        providers = data.get("providers", {})
        if not isinstance(providers, dict):
            return None
        cem888_provider = providers.get("cem888", {})
        if isinstance(cem888_provider, dict):
            return cem888_provider
    except Exception:
        pass
    return None


def _parse_timestamp(value: object) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _access_token_is_expiring(expires_at: object, skew_seconds: int) -> bool:
    expires = _parse_timestamp(expires_at)
    if expires is None:
        return True
    remaining = (expires - datetime.now(timezone.utc)).total_seconds()
    return remaining <= max(0, int(skew_seconds))


def read_cem888_access_token() -> Optional[str]:
    """Read a CEM888.AI Subscriber OAuth access token from auth store or env override."""
    explicit = os.getenv("TOOL_GATEWAY_USER_TOKEN")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    cem888_provider = _read_cem888_provider_state() or {}
    access_token = cem888_provider.get("access_token")
    cached_token = access_token.strip() if isinstance(access_token, str) and access_token.strip() else None

    if cached_token and not _access_token_is_expiring(
        cem888_provider.get("expires_at"),
        _CEM888_ACCESS_TOKEN_REFRESH_SKEW_SECONDS,
    ):
        return cached_token

    try:
        from cem888_cli.auth import resolve_cem888_access_token

        refreshed_token = resolve_cem888_access_token(
            refresh_skew_seconds=_CEM888_ACCESS_TOKEN_REFRESH_SKEW_SECONDS,
        )
        if isinstance(refreshed_token, str) and refreshed_token.strip():
            return refreshed_token.strip()
    except Exception as exc:
        logger.debug("CEM888.AI access token refresh failed: %s", exc)

    return cached_token


def get_tool_gateway_scheme() -> str:
    """Return configured shared gateway URL scheme."""
    scheme = os.getenv("TOOL_GATEWAY_SCHEME", "").strip().lower()
    if not scheme:
        return _DEFAULT_TOOL_GATEWAY_SCHEME

    if scheme in {"http", "https"}:
        return scheme

    raise ValueError("TOOL_GATEWAY_SCHEME must be 'http' or 'https'")


def build_vendor_gateway_url(vendor: str) -> str:
    """Return the gateway origin for a specific vendor."""
    vendor_key = f"{vendor.upper().replace('-', '_')}_GATEWAY_URL"
    explicit_vendor_url = os.getenv(vendor_key, "").strip().rstrip("/")
    if explicit_vendor_url:
        return explicit_vendor_url

    shared_scheme = get_tool_gateway_scheme()
    shared_domain = os.getenv("TOOL_GATEWAY_DOMAIN", "").strip().strip("/")
    if shared_domain:
        return f"{shared_scheme}://{vendor}-gateway.{shared_domain}"

    return f"{shared_scheme}://{vendor}-gateway.{_DEFAULT_TOOL_GATEWAY_DOMAIN}"


def resolve_managed_tool_gateway(
    vendor: str,
    gateway_builder: Optional[Callable[[str], str]] = None,
    token_reader: Optional[Callable[[], Optional[str]]] = None,
) -> Optional[ManagedToolGatewayConfig]:
    """Resolve shared managed-tool gateway config for a vendor."""
    if not managed_cem888_tools_enabled():
        return None

    resolved_gateway_builder = gateway_builder or build_vendor_gateway_url
    resolved_token_reader = token_reader or read_cem888_access_token

    gateway_origin = resolved_gateway_builder(vendor)
    cem888_user_token = resolved_token_reader()
    if not gateway_origin or not cem888_user_token:
        return None

    return ManagedToolGatewayConfig(
        vendor=vendor,
        gateway_origin=gateway_origin,
        cem888_user_token=cem888_user_token,
        managed_mode=True,
    )


def is_managed_tool_gateway_ready(
    vendor: str,
    gateway_builder: Optional[Callable[[str], str]] = None,
    token_reader: Optional[Callable[[], Optional[str]]] = None,
) -> bool:
    """Return True when gateway URL and CEM888.AI access token are available."""
    return resolve_managed_tool_gateway(
        vendor,
        gateway_builder=gateway_builder,
        token_reader=token_reader,
    ) is not None
