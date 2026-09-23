"""Shared constants for CEM888 Agent.

Import-safe module with no dependencies — can be imported from anywhere
without risk of circular imports.
"""

import os
import sysconfig
from contextvars import ContextVar, Token
from pathlib import Path


_profile_fallback_warned: bool = False
_UNSET = object()
_CEM888_HOME_OVERRIDE: ContextVar[str | object] = ContextVar(
    "_CEM888_HOME_OVERRIDE", default=_UNSET
)


def set_cem888_home_override(path: str | Path | None) -> Token:
    """Set a context-local CEM888 home override and return its reset token.

    This is for in-process, per-task scoping.  It deliberately does not mutate
    ``os.environ`` because that is shared by every thread in the process.
    """
    value: str | object = _UNSET if path is None else str(path)
    return _CEM888_HOME_OVERRIDE.set(value)


def reset_cem888_home_override(token: Token) -> None:
    """Restore the previous context-local CEM888 home override."""
    _CEM888_HOME_OVERRIDE.reset(token)


def get_cem888_home_override() -> str | None:
    """Return the active context-local CEM888 home override, if any."""
    override = _CEM888_HOME_OVERRIDE.get()
    if override is _UNSET or not override:
        return None
    return str(override)


class CEM888HomeUnresolved(RuntimeError):
    """Agent-scoped path resolution could not establish a profile home.

    Raised instead of silently resolving an agent-scoped path to the global
    ``~/.cem888`` root.  Machine-readable code: ``CEM888_HOME_UNRESOLVED``.
    """

    code = "CEM888_HOME_UNRESOLVED"


def _active_profile_name() -> str:
    """Best-effort read of the sticky active-profile marker. Import-safe."""
    try:
        p = Path.home() / ".cem888" / "active_profile"
        return p.read_text().strip() if p.exists() else ""
    except (UnicodeDecodeError, OSError):
        return ""


def get_cem888_home(*, allow_global: bool = False) -> Path:
    """Return the CEM888 home directory.

    Resolution order — every step is deterministic and explicit:

      1. context-local override (``set_cem888_home_override``)
      2. the ``CEM888_HOME`` environment variable
      3. ``~/.cem888`` — accepted ONLY when that is the correct answer, i.e.
         no other profile is sticky-active.  Callers that deliberately want
         installation-level/root behavior pass ``allow_global=True``.

    When ``CEM888_HOME`` is unset *and* a non-default profile is sticky-active
    this process cannot know which profile it belongs to.  Resolving to the
    global root there would silently read and write ANOTHER profile's data, so
    it now fails closed with ``CEM888_HOME_UNRESOLVED`` plus remediation
    instead of warning and continuing.  Subprocess spawners MUST propagate
    ``CEM888_HOME`` explicitly (see the systemd template in
    ``cem888_cli/gateway.py`` and the kanban dispatcher in
    ``cem888_cli/kanban_db.py``).
    """
    override = get_cem888_home_override()
    if override:
        return Path(override)

    val = os.environ.get("CEM888_HOME", "").strip()
    if val:
        return Path(val)

    active = _active_profile_name()
    if active and active != "default" and not allow_global:
        raise CEM888HomeUnresolved(
            "CEM888_HOME_UNRESOLVED: CEM888_HOME is unset but active_profile "
            "is %r, so this process cannot determine which profile it belongs "
            "to. Refusing to resolve an agent-scoped path to the global root "
            "(~/.cem888) because that would read and write the wrong "
            "profile's data. Remediation: export CEM888_HOME=%s (and have the "
            "spawner propagate it), or pass allow_global=True if this call is "
            "deliberately installation-level."
            % (active, Path.home() / ".cem888" / "profiles" / active)
        )

    return Path.home() / ".cem888"



def get_default_cem888_root() -> Path:
    """Return the root CEM888 directory for profile-level operations.

    In standard deployments this is ``~/.cem888``.

    In Docker or custom deployments where ``CEM888_HOME`` points outside
    ``~/.cem888`` (e.g. ``/opt/data``), returns ``CEM888_HOME`` directly
    — that IS the root.

    In profile mode where ``CEM888_HOME`` is ``<root>/profiles/<name>``,
    returns ``<root>`` so that ``profile list`` can see all profiles.
    Works both for standard (``~/.cem888/profiles/coder``) and Docker
    (``/opt/data/profiles/coder``) layouts.

    Import-safe — no dependencies beyond stdlib.
    """
    native_home = Path.home() / ".cem888"
    env_home = os.environ.get("CEM888_HOME", "")
    if not env_home:
        return native_home
    env_path = Path(env_home)
    try:
        env_path.resolve().relative_to(native_home.resolve())
        # CEM888_HOME is under ~/.cem888 (normal or profile mode)
        return native_home
    except ValueError:
        pass

    # Docker / custom deployment.
    # Check if this is a profile path: <root>/profiles/<name>
    # If the immediate parent dir is named "profiles", the root is
    # the grandparent — this covers Docker profiles correctly.
    if env_path.parent.name == "profiles":
        return env_path.parent.parent

    # Not a profile path — CEM888_HOME itself is the root
    return env_path


def _get_packaged_data_dir(name: str) -> Path | None:
    """Return an installed data-files directory if one exists.

    Used to discover bundled skills/optional-skills when CEM888 is installed
    from a wheel that emitted them via setuptools data_files.
    """
    candidates = []
    for scheme in ("data", "purelib", "platlib"):
        raw = sysconfig.get_path(scheme)
        if raw:
            candidates.append(Path(raw) / name)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def get_optional_skills_dir(default: Path | None = None) -> Path:
    """Return the optional-skills directory, honoring package-manager wrappers.

    Packaged installs may ship ``optional-skills`` outside the Python package
    tree and expose it via ``CEM888_OPTIONAL_SKILLS``.
    """
    override = os.getenv("CEM888_OPTIONAL_SKILLS", "").strip()
    if override:
        return Path(override)
    packaged = _get_packaged_data_dir("optional-skills")
    if packaged is not None:
        return packaged
    if default is not None:
        return default
    return get_cem888_home() / "optional-skills"


def get_optional_mcps_dir(default: Path | None = None) -> Path:
    """Return the optional-mcps directory, honoring package-manager wrappers.

    Mirrors :func:`get_optional_skills_dir` for the MCP catalog (CEM888.AI-approved
    Model Context Protocol servers shipped with the repo but disabled by
    default). Packaged installs may ship ``optional-mcps`` outside the Python
    package tree and expose it via ``CEM888_OPTIONAL_MCPS``.
    """
    override = os.getenv("CEM888_OPTIONAL_MCPS", "").strip()
    if override:
        return Path(override)
    packaged = _get_packaged_data_dir("optional-mcps")
    if packaged is not None:
        return packaged
    if default is not None:
        return default
    return get_cem888_home() / "optional-mcps"


def get_bundled_skills_dir(default: Path | None = None) -> Path:
    """Return the bundled skills directory for source and packaged installs.

    Resolution order:
        1. ``CEM888_BUNDLED_SKILLS`` env var (Nix wrapper / explicit override)
        2. Wheel-installed ``<sysconfig data>/skills`` (pip install path)
        3. Caller-supplied ``default`` (typically the source-checkout path)
        4. ``<CEM888_HOME>/skills`` last-resort
    """
    override = os.getenv("CEM888_BUNDLED_SKILLS", "").strip()
    if override:
        return Path(override)
    packaged = _get_packaged_data_dir("skills")
    if packaged is not None:
        return packaged
    if default is not None:
        return default
    return get_cem888_home() / "skills"


def get_cem888_dir(new_subpath: str, old_name: str) -> Path:
    """Resolve a CEM888 subdirectory with backward compatibility.

    New installs get the consolidated layout (e.g. ``cache/images``).
    Existing installs that already have the old path (e.g. ``image_cache``)
    keep using it — no migration required.

    Args:
        new_subpath: Preferred path relative to CEM888_HOME (e.g. ``"cache/images"``).
        old_name: Legacy path relative to CEM888_HOME (e.g. ``"image_cache"``).

    Returns:
        Absolute ``Path`` — old location if it exists on disk, otherwise the new one.
    """
    home = get_cem888_home()
    old_path = home / old_name
    if old_path.exists():
        return old_path
    return home / new_subpath


def display_cem888_home() -> str:
    """Return a user-friendly display string for the current CEM888_HOME.

    Uses ``~/`` shorthand for readability::

        default:  ``~/.cem888``
        profile:  ``~/.cem888/profiles/coder``
        custom:   ``/opt/cem888-custom``

    Use this in **user-facing** print/log messages instead of hardcoding
    ``~/.cem888``.  For code that needs a real ``Path``, use
    :func:`get_cem888_home` instead.
    """
    home = get_cem888_home()
    try:
        return "~/" + str(home.relative_to(Path.home()))
    except ValueError:
        return str(home)


def secure_parent_dir(path: Path) -> None:
    """Chmod ``0o700`` on the parent directory of *path*, but only if safe.

    Refuses to chmod ``/`` or any top-level directory (resolved parent with
    fewer than 3 parts, i.e. ``/`` or any direct child like ``/usr``) to
    prevent catastrophic host bricking when ``CEM888_HOME`` or other path
    env vars resolve to an unexpected location.

    See https://github.com/CEM888AI/CEM888/issues/25821.
    """
    parent = path.parent.resolve()
    # Refuse root and its direct children (/usr, /home, /var, /tmp, …).
    if parent == Path("/") or len(parent.parts) < 3:
        return
    try:
        os.chmod(parent, 0o700)
    except OSError:
        pass


def get_subprocess_home() -> str | None:
    """Return a per-profile HOME directory for subprocesses, or None.

    When ``{CEM888_HOME}/home/`` exists on disk, subprocesses should use it
    as ``HOME`` so system tools (git, ssh, gh, npm …) write their configs
    inside the CEM888 data directory instead of the OS-level ``/root`` or
    ``~/``.  This provides:

    * **Docker persistence** — tool configs land inside the persistent volume.
    * **Profile isolation** — each profile gets its own git identity, SSH
      keys, gh tokens, etc.

    The Python process's own ``os.environ["HOME"]`` and ``Path.home()`` are
    **never** modified — only subprocess environments should inject this value.
    Activation is directory-based: if the ``home/`` subdirectory doesn't
    exist, returns ``None`` and behavior is unchanged.
    """
    cem888_home = get_cem888_home_override() or os.getenv("CEM888_HOME")
    if not cem888_home:
        return None
    profile_home = os.path.join(cem888_home, "home")
    if os.path.isdir(profile_home):
        return profile_home
    return None


VALID_REASONING_EFFORTS = ("minimal", "low", "medium", "high", "xhigh")


def parse_reasoning_effort(effort: str) -> dict | None:
    """Parse a reasoning effort level into a config dict.

    Valid levels: "none", "minimal", "low", "medium", "high", "xhigh".
    Returns None when the input is empty or unrecognized (caller uses default).
    Returns {"enabled": False} for "none".
    Returns {"enabled": True, "effort": <level>} for valid effort levels.
    """
    if not effort or not effort.strip():
        return None
    effort = effort.strip().lower()
    if effort == "none":
        return {"enabled": False}
    if effort in VALID_REASONING_EFFORTS:
        return {"enabled": True, "effort": effort}
    return None


def is_termux() -> bool:
    """Return True when running inside a Termux (Android) environment.

    Checks ``TERMUX_VERSION`` (set by Termux) or the Termux-specific
    ``PREFIX`` path.  Import-safe — no heavy deps.
    """
    prefix = os.getenv("PREFIX", "")
    return bool(os.getenv("TERMUX_VERSION") or "com.termux/files/usr" in prefix)


_wsl_detected: bool | None = None


def is_wsl() -> bool:
    """Return True when running inside WSL (Windows Subsystem for Linux).

    Checks ``/proc/version`` for the ``microsoft`` marker that both WSL1
    and WSL2 inject.  Result is cached for the process lifetime.
    Import-safe — no heavy deps.
    """
    global _wsl_detected
    if _wsl_detected is not None:
        return _wsl_detected
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            _wsl_detected = "microsoft" in f.read().lower()
    except Exception:
        _wsl_detected = False
    return _wsl_detected


_container_detected: bool | None = None


def is_container() -> bool:
    """Return True when running inside a Docker/Podman container.

    Checks ``/.dockerenv`` (Docker), ``/run/.containerenv`` (Podman),
    and ``/proc/1/cgroup`` for container runtime markers.  Result is
    cached for the process lifetime.  Import-safe — no heavy deps.
    """
    global _container_detected
    if _container_detected is not None:
        return _container_detected
    if os.path.exists("/.dockerenv"):
        _container_detected = True
        return True
    if os.path.exists("/run/.containerenv"):
        _container_detected = True
        return True
    try:
        with open("/proc/1/cgroup", "r", encoding="utf-8") as f:
            cgroup = f.read()
            if "docker" in cgroup or "podman" in cgroup or "/lxc/" in cgroup:
                _container_detected = True
                return True
    except OSError:
        pass
    _container_detected = False
    return False


# ─── Well-Known Paths ─────────────────────────────────────────────────────────


def get_config_path() -> Path:
    """Return the path to ``config.yaml`` under CEM888_HOME.

    Replaces the ``get_cem888_home() / "config.yaml"`` pattern repeated
    in 7+ files (skill_utils.py, cem888_logging.py, cem888_time.py, etc.).
    """
    return get_cem888_home() / "config.yaml"


def get_skills_dir() -> Path:
    """Return the path to the skills directory under CEM888_HOME."""
    return get_cem888_home() / "skills"



def get_env_path() -> Path:
    """Return the path to the ``.env`` file under CEM888_HOME."""
    return get_cem888_home() / ".env"


# ─── Network Preferences ─────────────────────────────────────────────────────


def apply_ipv4_preference(force: bool = False) -> None:
    """Monkey-patch ``socket.getaddrinfo`` to prefer IPv4 connections.

    On servers with broken or unreachable IPv6, Python tries AAAA records
    first and hangs for the full TCP timeout before falling back to IPv4.
    This affects httpx, requests, urllib, the OpenAI SDK — everything that
    uses ``socket.getaddrinfo``.

    When *force* is True, patches ``getaddrinfo`` so that calls with
    ``family=AF_UNSPEC`` (the default) resolve as ``AF_INET`` instead,
    skipping IPv6 entirely.  If no A record exists, falls back to the
    original unfiltered resolution so pure-IPv6 hosts still work.

    Safe to call multiple times — only patches once.
    Set ``network.force_ipv4: true`` in ``config.yaml`` to enable.
    """
    if not force:
        return

    import socket

    # Guard against double-patching
    if getattr(socket.getaddrinfo, "_cem888_ipv4_patched", False):
        return

    _original_getaddrinfo = socket.getaddrinfo

    def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if family == 0:  # AF_UNSPEC — caller didn't request a specific family
            try:
                return _original_getaddrinfo(
                    host, port, socket.AF_INET, type, proto, flags
                )
            except socket.gaierror:
                # No A record — fall back to full resolution (pure-IPv6 hosts)
                return _original_getaddrinfo(host, port, family, type, proto, flags)
        return _original_getaddrinfo(host, port, family, type, proto, flags)

    _ipv4_getaddrinfo._cem888_ipv4_patched = True  # type: ignore[attr-defined]
    socket.getaddrinfo = _ipv4_getaddrinfo  # type: ignore[assignment]


# ─── Streaming Response Constants ────────────────────────────────────────────

# Response ID for partial stream stubs used during error recovery
PARTIAL_STREAM_STUB_ID = "partial-stream-stub"

FINISH_REASON_LENGTH = "length"


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS_URL = f"{OPENROUTER_BASE_URL}/models"
