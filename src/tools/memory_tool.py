#!/usr/bin/env python3
"""
Memory Tool Module - Persistent Curated Memory

Provides bounded, file-backed memory that persists across sessions. Two stores:
  - memories/MEMORY_MANIFEST.md: agent's operating and project notes (environment
    facts, conventions, tool quirks, things learned)
  - memories/USER_MANIFEST.md: what the agent knows about the user (preferences,
    communication style, expectations, workflow habits)

Neither is the profile: profile-root USER.md is the real identity file -- a
different file that merely shares the name -- and memory_tool never writes it.
The manifests are bounded pointers; durable records live in the typed store.

Both are injected into the system prompt as a frozen snapshot at session start.
Mid-session writes update files on disk immediately (durable) but do NOT change
the system prompt -- this preserves the prefix cache for the entire session.
The snapshot refreshes on the next session start.

Entry delimiter: § (section sign). Entries can be multiline.
Character limits (not tokens) because char counts are model-independent.

Design:
- Single `memory` tool with action parameter: add, replace, remove, read
- replace/remove use short unique substring matching (not full text or IDs)
- Behavioral guidance lives in the tool schema description
- Frozen snapshot pattern: system prompt is stable, tool responses show live state
"""

import json
import logging
import os
import re
import tempfile
import time
import sqlite3
import hashlib
from uuid import uuid4
from contextlib import contextmanager
from pathlib import Path
from cem888_constants import get_cem888_home
from typing import Dict, Any, List, Optional

from utils import atomic_replace

# fcntl is Unix-only; on Windows use msvcrt for file locking
msvcrt = None
try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        pass

logger = logging.getLogger(__name__)

# Where memory files live — resolved dynamically so profile overrides
# (CEM888_HOME env var changes) are always respected.  The old module-level
# constant was cached at import time and could go stale if a profile switch
# happened after the first import.
def get_memory_dir() -> Path:
    """Return the profile-scoped memories directory."""
    return get_cem888_home() / "memories"

ENTRY_DELIMITER = "\n§\n"
MANIFEST_VERSION = "CEM888 memory manifest v1"

# The two markdown files below are deliberately a *manifest*, not the durable
# store.  CEM-82 keeps compatibility with existing profiles by leaving old
# entries readable, but every new semantic write is committed here first.
#
# CEM-170: the manifests are USER_MANIFEST.md / MEMORY_MANIFEST.md.  They used
# to be USER.md / MEMORY.md, which collided with the REAL profile file
# (profile-root USER.md, injected into the identity slot by
# agent/context_compiler.py) and made the architecture unreadable to the agent
# itself.  The legacy names are migrated on first read, then removed.
MANIFEST_FILENAME = {"user": "USER_MANIFEST.md", "memory": "MEMORY_MANIFEST.md"}
LEGACY_MANIFEST_FILENAME = {"user": "USER.md", "memory": "MEMORY.md"}
_MEMORY_TYPES = {
    "identity", "preference", "operating_rule", "project_state", "task_state",
    "decision", "procedure", "relationship", "episodic", "tool_evidence",
}


def _profile_dir() -> Path:
    return get_cem888_home()


def _durable_db_path() -> Path:
    return _profile_dir() / "state" / "memory_provenance.db"


def _init_durable_db() -> sqlite3.Connection:
    path = _durable_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS typed_memories (
          id TEXT PRIMARY KEY, content TEXT NOT NULL, content_sha256 TEXT NOT NULL,
          memory_type TEXT NOT NULL, scope TEXT NOT NULL, agent TEXT NOT NULL,
          project TEXT, task TEXT, authority TEXT NOT NULL, source TEXT NOT NULL,
          provenance TEXT, lifecycle_status TEXT NOT NULL, verification_status TEXT NOT NULL,
          supersedes TEXT, superseded_by TEXT, created_at REAL NOT NULL, updated_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_typed_memory_active ON typed_memories(lifecycle_status, superseded_by, memory_type, project, task)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_typed_memory_dedupe ON typed_memories(content_sha256, memory_type, scope, agent)")
    conn.commit()
    return conn


def _default_memory_type(target: str) -> str:
    # Backwards-compatible deterministic classification for older callers.
    return "preference" if target == "user" else "operating_rule"


def _manifest_entry(target: str) -> str:
    pointer = "durable preference/identity records" if target == "user" else "durable operating/project records"
    return (
        f"{MANIFEST_VERSION}; {pointer} live in state/memory_provenance.db. "
        "Use typed memory recall; do not store content in this manifest."
    )


def _write_durable_memory(
    *, content: str, target: str, memory_type: Optional[str], scope: Optional[str],
    project: Optional[str], task: Optional[str], authority: Optional[str], source: Optional[str],
    provenance: Optional[str], lifecycle_status: Optional[str], verification_status: Optional[str],
    supersedes: Optional[str], agent: Optional[str],
) -> Dict[str, Any]:
    """Commit a typed record before any manifest operation.

    This is intentionally local/profile-scoped and reuses the existing
    provenance DB used by the context compiler.  A failed manifest update can
    therefore never discard durable content or invite retry loops.
    """
    kind = (memory_type or _default_memory_type(target)).strip().lower()
    if kind not in _MEMORY_TYPES:
        return {"success": False, "error": f"Invalid memory_type '{kind}'."}
    now = time.time()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    record_id = "mem_" + uuid4().hex
    resolved_agent = (agent or os.environ.get("CEM888_PROFILE") or _profile_dir().name).strip()
    try:
        conn = _init_durable_db()
        existing = conn.execute(
            "SELECT id FROM typed_memories WHERE content_sha256=? AND memory_type=? AND scope=? AND agent=?",
            (digest, kind, (scope or "profile").strip(), resolved_agent),
        ).fetchone()
        if existing:
            conn.close()
            return {"success": True, "memory_id": existing[0], "duplicate": True}
        if supersedes:
            conn.execute("UPDATE typed_memories SET superseded_by=?, updated_at=? WHERE id=?", (record_id, now, supersedes))
        conn.execute(
            "INSERT INTO typed_memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (record_id, content, digest, kind, (scope or "profile").strip(), resolved_agent,
             (project or "").strip() or None, (task or "").strip() or None,
             (authority or "user").strip(), (source or "model").strip(),
             (provenance or "").strip() or None, (lifecycle_status or "active").strip(),
             (verification_status or "unverified").strip(), (supersedes or "").strip() or None,
             None, now, now),
        )
        conn.commit(); conn.close()
    except (sqlite3.Error, OSError) as exc:
        return {"success": False, "error": f"Durable memory write failed: {exc}"}
    return {"success": True, "memory_id": record_id, "duplicate": False, "content_sha256": digest}


def _recall_durable_memory(query: str, *, limit: int, include_history: bool) -> Dict[str, Any]:
    terms = [term for term in re.findall(r"[a-z0-9_./:-]+", query.lower()) if len(term) > 2]
    try:
        conn = _init_durable_db()
        where = "" if include_history else "WHERE lifecycle_status='active' AND superseded_by IS NULL"
        rows = conn.execute(
            f"SELECT id, content, memory_type, scope, project, task, authority, source, provenance, lifecycle_status, verification_status, supersedes, superseded_by, created_at FROM typed_memories {where} ORDER BY created_at DESC LIMIT 250"
        ).fetchall()
        conn.close()
    except (sqlite3.Error, OSError) as exc:
        return {"success": False, "error": f"Durable memory retrieval failed: {exc}"}
    def score(row: tuple) -> int:
        text = " ".join(str(value or "") for value in row[1:8]).lower()
        return sum(text.count(term) for term in terms)
    selected = sorted(rows, key=lambda row: (-score(row), -float(row[13] or 0)))[:max(1, min(int(limit), 20))]
    return {"success": True, "results": [
        {"id": row[0], "content": row[1], "type": row[2], "scope": row[3], "project": row[4], "task": row[5], "authority": row[6], "source": row[7], "provenance": row[8], "lifecycle_status": row[9], "verification_status": row[10], "supersedes": row[11], "superseded_by": row[12], "created_at": row[13]}
        for row in selected if not terms or score(row) > 0
    ]}


# ---------------------------------------------------------------------------
# Memory content scanning — lightweight check for injection/exfiltration
# in content that gets injected into the system prompt.
#
# Patterns live in ``tools/threat_patterns.py`` — the single source of truth
# shared with the context-file scanner and the tool-result delimiter system.
# Memory uses the "strict" scope (broadest pattern set) because:
#  - memory entries are user-curated; the user can rewrite a flagged entry
#  - memory enters the system prompt as a FROZEN snapshot, so a poisoned
#    entry persists for the entire session and across sessions until
#    explicitly removed.
# ---------------------------------------------------------------------------

from tools.threat_patterns import first_threat_message as _first_threat_message


def _scan_memory_content(content: str) -> Optional[str]:
    """Scan memory content for injection/exfil patterns. Returns error string if blocked."""
    return _first_threat_message(content, scope="strict")


def _drift_error(path: "Path", bak_path: str) -> Dict[str, Any]:
    """Build the error dict returned when external drift is detected.

    The on-disk memory file contains content that wouldn't round-trip
    through the tool's parser/serializer — flushing would discard the
    appended/edited content from a patch tool, shell append, manual edit,
    or sister-session write. We refuse the mutation, point the operator at
    the .bak.<ts> snapshot we took, and tell them what to do next.
    """
    return {
        "success": False,
        "error": (
            f"Refusing to write {path.name}: file on disk has content that "
            f"wouldn't round-trip through the memory tool (likely added by "
            f"the patch tool, a shell append, a manual edit, or a "
            f"concurrent session). A snapshot was saved to {bak_path}. "
            f"Resolve the drift first — either rewrite the file as a clean "
            f"§-delimited list of entries, or move the extra content out — "
            f"then retry. This guard exists to prevent silent data loss "
            f"(issue #26045)."
        ),
        "drift_backup": bak_path,
        "remediation": (
            "Open the .bak file, integrate the missing entries into the "
            "memory tool one at a time via memory(action=add, content=...), "
            "then remove or rewrite the original file to a clean state."
        ),
    }


class MemoryStore:
    """
    Bounded curated memory with file persistence. One instance per AIAgent.

    Maintains two parallel states:
      - _system_prompt_snapshot: frozen at load time, used for system prompt injection.
        Never mutated mid-session. Keeps prefix cache stable.
      - memory_entries / user_entries: live state, mutated by tool calls, persisted to disk.
        Tool responses always reflect this live state.
    """

    def __init__(self, memory_char_limit: int = 2200, user_char_limit: int = 1375):
        self.memory_entries: List[str] = []
        self.user_entries: List[str] = []
        self.memory_char_limit = memory_char_limit
        self.user_char_limit = user_char_limit
        # Frozen snapshot for system prompt -- set once at load_from_disk()
        self._system_prompt_snapshot: Dict[str, str] = {"memory": "", "user": ""}
        self._failed_durable_writes: Dict[str, tuple[float, str]] = {}

    def load_from_disk(self):
        """Load entries from MEMORY.md and USER.md, capture system prompt snapshot.

        The frozen snapshot is what enters the system prompt. We scan each
        entry for injection/promptware patterns at snapshot-build time —
        ANY hit replaces the entry text in the snapshot with a placeholder
        like ``[BLOCKED: …]``, so a poisoned-on-disk memory file (supply
        chain, compromised tool, sister-session write) cannot inject into
        the system prompt.

        The live ``memory_entries`` / ``user_entries`` lists keep the
        original text so the user can still SEE poisoned entries via
        ``memory(action=read)`` and remove them — silently dropping them
        would hide the attack from the user.

        Scanning is deterministic from disk bytes, so the snapshot remains
        stable for the entire session (prefix-cache invariant holds).
        """
        mem_dir = get_memory_dir()
        mem_dir.mkdir(parents=True, exist_ok=True)

        self.memory_entries = self._read_manifest("memory")
        self.user_entries = self._read_manifest("user")

        # CEM-82 migration: the historical bounded files held durable facts.
        # Preserve each entry in the profile's existing provenance DB and then
        # replace the injected surface with deterministic pointers.  A failed
        # migration leaves the files untouched; it never deletes evidence.
        self._migrate_legacy_manifest("memory")
        self._migrate_legacy_manifest("user")

        # Deduplicate entries (preserves order, keeps first occurrence)
        self.memory_entries = list(dict.fromkeys(self.memory_entries))
        self.user_entries = list(dict.fromkeys(self.user_entries))

        # Sanitize entries for the system-prompt snapshot only.  Live state
        # (memory_entries / user_entries) keeps the raw text so the user
        # can see + remove poisoned entries via the memory tool.
        sanitized_memory = self._sanitize_entries_for_snapshot(self.memory_entries, "MEMORY.md")
        sanitized_user = self._sanitize_entries_for_snapshot(self.user_entries, "USER.md")

        # Capture frozen snapshot for system prompt injection
        self._system_prompt_snapshot = {
            "memory": self._render_block("memory", sanitized_memory),
            "user": self._render_block("user", sanitized_user),
        }

    def _migrate_legacy_manifest(self, target: str) -> None:
        entries = self._entries_for(target)
        if entries and all(entry.startswith(MANIFEST_VERSION) for entry in entries):
            return
        migrated = []
        for entry in entries:
            receipt = _write_durable_memory(
                content=entry,
                target=target,
                memory_type=_default_memory_type(target),
                scope="profile",
                project=None,
                task=None,
                authority="legacy_manifest",
                source="legacy_manifest",
                provenance="memories/" + self._path_for(target).name,
                lifecycle_status="active",
                verification_status="unverified",
                supersedes=None,
                agent=None,
            )
            if not receipt.get("success"):
                logger.warning("CEM-82 manifest migration deferred for %s: %s", target, receipt.get("error"))
                return
            migrated.append(receipt["memory_id"])
        # Empty files become a compact manifest as well, so later additions
        # cannot accidentally recreate a content store.
        self._set_entries(target, [_manifest_entry(target)])
        try:
            self.save_to_disk(target)
        except (OSError, RuntimeError) as exc:
            logger.warning("CEM-82 manifest pointer write deferred for %s: %s", target, exc)
            self._set_entries(target, entries)

    def suppress_identical_failure(self, *, action: str, target: str, content: str, error: str) -> Optional[Dict[str, Any]]:
        """Return a terminal receipt for a repeated failed durable write.

        The guard is runtime state, keyed by the exact semantic request and
        failure class.  It never turns a failed write into success, but it
        makes the second identical failure non-retryable so the agent can
        resume the user's original task.
        """
        key = hashlib.sha256(f"{action}\0{target}\0{content}\0{error}".encode("utf-8")).hexdigest()
        now = time.monotonic()
        prior = self._failed_durable_writes.get(key)
        self._failed_durable_writes[key] = (now, error)
        if prior and now - prior[0] <= 300:
            return {
                "success": False,
                "error": "Repeated identical durable memory failure suppressed.",
                "error_code": "memory_write_retry_suppressed",
                "retry_suppressed": True,
                "continue_original_task": True,
            }
        return None

    def clear_durable_failure(self, *, action: str, target: str, content: str) -> None:
        prefix = f"{action}\0{target}\0{content}\0"
        for key in list(self._failed_durable_writes):
            # Keys are opaque; a successful write clears all short-lived guard
            # entries because the operation has demonstrably made progress.
            self._failed_durable_writes.pop(key, None)

    @staticmethod
    def _sanitize_entries_for_snapshot(entries: List[str], filename: str) -> List[str]:
        """Return ``entries`` with any threat-matching entry replaced by a placeholder.

        Each entry is scanned with the shared threat-pattern library at the
        ``"strict"`` scope (same as memory writes).  On match, the entry is
        replaced in the returned list with ``"[BLOCKED: <filename> entry
        contained threat pattern: <ids>. Removed from system prompt.]"`` —
        the placeholder enters the snapshot, the original entry stays in
        live state for the user to inspect and delete.

        Empty or already-block-marker entries pass through unchanged.
        """
        from tools.threat_patterns import scan_for_threats

        sanitized: List[str] = []
        for entry in entries:
            if not entry or entry.startswith("[BLOCKED:"):
                sanitized.append(entry)
                continue
            findings = scan_for_threats(entry, scope="strict")
            if findings:
                logger.warning(
                    "Memory entry from %s blocked at load time: %s",
                    filename, ", ".join(findings),
                )
                sanitized.append(
                    f"[BLOCKED: {filename} entry contained threat pattern(s): "
                    f"{', '.join(findings)}. Removed from system prompt; "
                    f"use memory(action=read) to inspect and memory(action=remove) "
                    f"to delete the original.]"
                )
            else:
                sanitized.append(entry)
        return sanitized

    @staticmethod
    @contextmanager
    def _file_lock(path: Path):
        """Acquire an exclusive file lock for read-modify-write safety.

        Uses a separate .lock file so the memory file itself can still be
        atomically replaced via os.replace().
        """
        lock_path = path.with_suffix(path.suffix + ".lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)

        if fcntl is None and msvcrt is None:
            yield
            return

        fd = open(lock_path, "a+", encoding="utf-8")
        try:
            if fcntl:
                fcntl.flock(fd, fcntl.LOCK_EX)
            else:
                fd.seek(0)
                msvcrt.locking(fd.fileno(), msvcrt.LK_LOCK, 1)
            yield
        finally:
            if fcntl:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except (OSError, IOError):
                    pass
            elif msvcrt:
                try:
                    fd.seek(0)
                    msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
                except (OSError, IOError):
                    pass
            fd.close()

    @staticmethod
    def _path_for(target: str) -> Path:
        """Path of the manifest pointer file for ``target``.

        Named ``*_MANIFEST.md`` so it can never be mistaken for the real
        profile file of the same target (CEM-170).
        """
        return get_memory_dir() / MANIFEST_FILENAME[target]

    @staticmethod
    def _legacy_path_for(target: str) -> Path:
        """Pre-CEM-170 manifest path, read once then removed."""
        return get_memory_dir() / LEGACY_MANIFEST_FILENAME[target]

    def _read_manifest(self, target: str) -> List[str]:
        """Read the manifest for ``target``, migrating the legacy name once.

        A pre-existing USER.md / MEMORY.md manifest is read, re-written
        under the new name, and deleted so the colliding filename cannot
        return and be confused with the profile file again.
        """
        entries = self._read_file(self._path_for(target))
        if entries:
            self._remove_legacy_manifest(target)
            return entries

        legacy = self._legacy_path_for(target)
        if not legacy.exists():
            return entries
        legacy_entries = self._read_file(legacy)
        if not legacy_entries:
            self._remove_legacy_manifest(target)
            return entries

        self._set_entries(target, legacy_entries)
        try:
            self.save_to_disk(target)
            self._remove_legacy_manifest(target)
        except (OSError, RuntimeError) as exc:
            logger.warning("CEM-170 legacy manifest migration deferred for %s: %s", target, exc)
        return legacy_entries

    @staticmethod
    def _remove_legacy_manifest(target: str) -> None:
        """Delete the pre-CEM-170 manifest file and its lock, if present."""
        legacy = MemoryStore._legacy_path_for(target)
        for path in (legacy, legacy.with_name(legacy.name + ".lock")):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    def _reload_target(self, target: str) -> Optional[str]:
        """Re-read entries from disk into in-memory state.

        Called under file lock to get the latest state before mutating.
        Returns the backup path if external drift was detected (the on-disk
        file contains content that wouldn't round-trip through our
        parser/serializer, OR an entry larger than the store's char limit).
        When drift is detected the caller must abort the mutation —
        flushing would discard the un-roundtrippable content.
        Returns None on clean reload.
        """
        path = self._path_for(target)
        bak = self._detect_external_drift(target)
        fresh = self._read_manifest(target)
        fresh = list(dict.fromkeys(fresh))  # deduplicate
        self._set_entries(target, fresh)
        return bak

    def save_to_disk(self, target: str):
        """Persist entries to the appropriate file. Called after every mutation."""
        get_memory_dir().mkdir(parents=True, exist_ok=True)
        self._write_file(self._path_for(target), self._entries_for(target))
        self._remove_legacy_manifest(target)

    def _entries_for(self, target: str) -> List[str]:
        if target == "user":
            return self.user_entries
        return self.memory_entries

    def _set_entries(self, target: str, entries: List[str]):
        if target == "user":
            self.user_entries = entries
        else:
            self.memory_entries = entries

    def _char_count(self, target: str) -> int:
        entries = self._entries_for(target)
        if not entries:
            return 0
        return len(ENTRY_DELIMITER.join(entries))

    def _char_limit(self, target: str) -> int:
        if target == "user":
            return self.user_char_limit
        return self.memory_char_limit

    def add(self, target: str, content: str) -> Dict[str, Any]:
        """Append a new entry. Returns error if it would exceed the char limit."""
        content = content.strip()
        if not content:
            return {"success": False, "error": "Content cannot be empty."}

        # Scan for injection/exfiltration before accepting
        scan_error = _scan_memory_content(content)
        if scan_error:
            return {"success": False, "error": scan_error}

        with self._file_lock(self._path_for(target)):
            # Re-read from disk under lock to pick up writes from other sessions.
            # If external drift was detected, the file was backed up to .bak.<ts>
            # — refuse the mutation so we don't clobber the un-roundtrippable
            # content the patch tool / shell append / sister session wrote.
            bak = self._reload_target(target)
            if bak:
                return _drift_error(self._path_for(target), bak)

            entries = self._entries_for(target)
            limit = self._char_limit(target)

            # Reject exact duplicates
            if content in entries:
                return self._success_response(target, "Entry already exists (no duplicate added).")

            # Calculate what the new total would be
            new_entries = entries + [content]
            new_total = len(ENTRY_DELIMITER.join(new_entries))

            if new_total > limit:
                current = self._char_count(target)
                return {
                    "success": False,
                    "error": (
                        f"Memory at {current:,}/{limit:,} chars. "
                        f"Adding this entry ({len(content)} chars) would exceed the limit. "
                        f"Replace or remove existing entries first."
                    ),
                    "current_entries": entries,
                    "usage": f"{current:,}/{limit:,}",
                }

            entries.append(content)
            self._set_entries(target, entries)
            self.save_to_disk(target)

        return self._success_response(target, "Entry added.")

    def replace(self, target: str, old_text: str, new_content: str) -> Dict[str, Any]:
        """Find entry containing old_text substring, replace it with new_content."""
        old_text = old_text.strip()
        new_content = new_content.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}
        if not new_content:
            return {"success": False, "error": "new_content cannot be empty. Use 'remove' to delete entries."}

        # Scan replacement content for injection/exfiltration
        scan_error = _scan_memory_content(new_content)
        if scan_error:
            return {"success": False, "error": scan_error}

        with self._file_lock(self._path_for(target)):
            bak = self._reload_target(target)
            if bak:
                return _drift_error(self._path_for(target), bak)

            entries = self._entries_for(target)
            matches = [(i, e) for i, e in enumerate(entries) if old_text in e]

            if not matches:
                return {"success": False, "error": f"No entry matched '{old_text}'."}

            if len(matches) > 1:
                # If all matches are identical (exact duplicates), operate on the first one
                unique_texts = {e for _, e in matches}
                if len(unique_texts) > 1:
                    previews = [e[:80] + ("..." if len(e) > 80 else "") for _, e in matches]
                    return {
                        "success": False,
                        "error": f"Multiple entries matched '{old_text}'. Be more specific.",
                        "matches": previews,
                    }
                # All identical -- safe to replace just the first

            idx = matches[0][0]
            limit = self._char_limit(target)

            # Check that replacement doesn't blow the budget
            test_entries = entries.copy()
            test_entries[idx] = new_content
            new_total = len(ENTRY_DELIMITER.join(test_entries))

            if new_total > limit:
                return {
                    "success": False,
                    "error": (
                        f"Replacement would put memory at {new_total:,}/{limit:,} chars. "
                        f"Shorten the new content or remove other entries first."
                    ),
                }

            entries[idx] = new_content
            self._set_entries(target, entries)
            self.save_to_disk(target)

        return self._success_response(target, "Entry replaced.")

    def remove(self, target: str, old_text: str) -> Dict[str, Any]:
        """Remove the entry containing old_text substring."""
        old_text = old_text.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}

        with self._file_lock(self._path_for(target)):
            bak = self._reload_target(target)
            if bak:
                return _drift_error(self._path_for(target), bak)

            entries = self._entries_for(target)
            matches = [(i, e) for i, e in enumerate(entries) if old_text in e]

            if not matches:
                return {"success": False, "error": f"No entry matched '{old_text}'."}

            if len(matches) > 1:
                # If all matches are identical (exact duplicates), remove the first one
                unique_texts = {e for _, e in matches}
                if len(unique_texts) > 1:
                    previews = [e[:80] + ("..." if len(e) > 80 else "") for _, e in matches]
                    return {
                        "success": False,
                        "error": f"Multiple entries matched '{old_text}'. Be more specific.",
                        "matches": previews,
                    }
                # All identical -- safe to remove just the first

            idx = matches[0][0]
            entries.pop(idx)
            self._set_entries(target, entries)
            self.save_to_disk(target)

        return self._success_response(target, "Entry removed.")

    def format_for_system_prompt(self, target: str) -> Optional[str]:
        """
        Return the frozen snapshot for system prompt injection.

        This returns the state captured at load_from_disk() time, NOT the live
        state. Mid-session writes do not affect this. This keeps the system
        prompt stable across all turns, preserving the prefix cache.

        Returns None if the snapshot is empty (no entries at load time).
        """
        block = self._system_prompt_snapshot.get(target, "")
        return block if block else None

    # -- Internal helpers --

    def _success_response(self, target: str, message: str = None) -> Dict[str, Any]:
        entries = self._entries_for(target)
        current = self._char_count(target)
        limit = self._char_limit(target)
        pct = min(100, int((current / limit) * 100)) if limit > 0 else 0

        resp = {
            "success": True,
            "target": target,
            "entries": entries,
            "usage": f"{pct}% — {current:,}/{limit:,} chars",
            "entry_count": len(entries),
        }
        if message:
            resp["message"] = message
        return resp

    def _render_block(self, target: str, entries: List[str]) -> str:
        """Render a system prompt block with header and usage indicator."""
        if not entries:
            return ""

        limit = self._char_limit(target)
        content = ENTRY_DELIMITER.join(entries)
        current = len(content)
        pct = min(100, int((current / limit) * 100)) if limit > 0 else 0

        if target == "user":
            header = f"USER MANIFEST (pointer — NOT the profile; the profile is profile-root USER.md) [{pct}% — {current:,}/{limit:,} chars]"
        else:
            header = f"MEMORY MANIFEST (pointer — durable notes live in the typed store) [{pct}% — {current:,}/{limit:,} chars]"

        separator = "═" * 46
        return f"{separator}\n{header}\n{separator}\n{content}"

    @staticmethod
    def _read_file(path: Path) -> List[str]:
        """Read a memory file and split into entries.

        No file locking needed: _write_file uses atomic rename, so readers
        always see either the previous complete file or the new complete file.
        """
        if not path.exists():
            return []
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return []

        if not raw.strip():
            return []

        # Use ENTRY_DELIMITER for consistency with _write_file. Splitting by "§"
        # alone would incorrectly split entries that contain "§" in their content.
        entries = [e.strip() for e in raw.split(ENTRY_DELIMITER)]
        return [e for e in entries if e]

    def _detect_external_drift(self, target: str) -> Optional[str]:
        """Return a backup-path string if on-disk content shows external drift.

        The memory file is supposed to be a list of small entries the tool
        wrote, joined by §. Detect drift via two signals:

        1. Round-trip mismatch — re-parsing and re-serializing the file
           doesn't produce identical bytes (rare; would catch oddly-encoded
           delimiters).
        2. Entry-size overflow — any single parsed entry exceeds the
           store's whole-file char limit. The tool budgets the ENTIRE store
           against that limit; no single tool-written entry can exceed it.
           When we see one entry larger than the limit, an external writer
           (patch tool, shell append, manual edit, sister session) appended
           free-form content into what the tool will treat as one entry.
           Flushing would then truncate that entry to the model's new
           content, discarding the appended bytes — issue #26045.

        Returns the absolute path of the .bak file when drift was found and
        backed up; returns None when the file looks tool-shaped.

        Note: this is an INSTANCE method (not static) because we need the
        per-target char_limit for signal #2.
        """
        path = self._path_for(target)
        if not path.exists():
            return None
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, IOError):
            return None
        if not raw.strip():
            return None

        parsed = [e.strip() for e in raw.split(ENTRY_DELIMITER) if e.strip()]
        roundtrip = ENTRY_DELIMITER.join(parsed)

        char_limit = self._char_limit(target)
        max_entry_len = max((len(e) for e in parsed), default=0)

        drift_detected = (raw.strip() != roundtrip) or (max_entry_len > char_limit)
        if not drift_detected:
            return None

        # Drift confirmed — snapshot the file so the operator can recover
        # whatever the external writer added, then return the .bak path so
        # the caller can refuse the mutation.
        ts = int(time.time())
        bak_path = path.with_suffix(path.suffix + f".bak.{ts}")
        try:
            bak_path.write_text(raw, encoding="utf-8")
        except (OSError, IOError):
            return str(bak_path) + " (BACKUP FAILED — file unchanged on disk)"
        return str(bak_path)

    @staticmethod
    def _write_file(path: Path, entries: List[str]):
        """Write entries to a memory file using atomic temp-file + rename.

        Previous implementation used open("w") + flock, but "w" truncates the
        file *before* the lock is acquired, creating a race window where
        concurrent readers see an empty file. Atomic rename avoids this:
        readers always see either the old complete file or the new one.
        """
        content = ENTRY_DELIMITER.join(entries) if entries else ""
        try:
            # Write to temp file in same directory (same filesystem for atomic rename)
            fd, tmp_path = tempfile.mkstemp(
                dir=str(path.parent), suffix=".tmp", prefix=".mem_"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
                atomic_replace(tmp_path, path)
            except BaseException:
                # Clean up temp file on any failure
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
        except (OSError, IOError) as e:
            raise RuntimeError(f"Failed to write memory file {path}: {e}")


def memory_tool(
    action: str,
    target: str = "memory",
    content: str = None,
    old_text: str = None,
    memory_type: str = None,
    scope: str = None,
    project: str = None,
    task: str = None,
    authority: str = None,
    source: str = None,
    provenance: str = None,
    lifecycle_status: str = None,
    verification_status: str = None,
    supersedes: str = None,
    agent: str = None,
    query: str = None,
    include_history: bool = False,
    limit: int = 5,
    store: Optional[MemoryStore] = None,
) -> str:
    """
    Single entry point for the memory tool. Dispatches to MemoryStore methods.

    Returns JSON string with results.
    """
    if store is None:
        return tool_error("Memory is not available. It may be disabled in config or this environment.", success=False)

    if target not in {"memory", "user"}:
        return tool_error(f"Invalid target '{target}'. Use 'memory' or 'user'.", success=False)

    if action in {"add", "store"}:
        if not content:
            return tool_error("Content is required for 'add' action.", success=False)
        scan_error = _scan_memory_content(content.strip())
        if scan_error:
            # Scan/validation rejections are non-overflow write failures too.
            # Suppress an identical retry so a model cannot burn the turn
            # repeatedly attempting a write that the deterministic guard will
            # continue to reject.
            rejected = {"success": False, "error": scan_error}
            suppressed = store.suppress_identical_failure(
                action=action, target=target, content=content.strip(), error=scan_error
            )
            result = suppressed or rejected
        else:
            durable = _write_durable_memory(
                content=content.strip(), target=target, memory_type=memory_type, scope=scope,
                project=project, task=task, authority=authority, source=source,
                provenance=provenance, lifecycle_status=lifecycle_status,
                verification_status=verification_status, supersedes=supersedes, agent=agent,
            )
            if not durable.get("success"):
                suppressed = store.suppress_identical_failure(
                    action=action, target=target, content=content.strip(), error=str(durable.get("error", "unknown"))
                )
                result = suppressed or durable
            else:
                store.clear_durable_failure(action=action, target=target, content=content.strip())
                # Deliberately do not append the durable payload to MEMORY.md or
                # USER.md.  They remain the bounded, compatibility manifest.
                result = {
                    "success": True,
                    "message": "Durable memory routed; manifest unchanged.",
                    "receipt": {**durable, "memory_type": memory_type or _default_memory_type(target),
                                "scope": scope or "profile", "target": target,
                                "manifest_updated": False},
                    "continue_original_task": True,
                }

    elif action == "recall":
        result = _recall_durable_memory(query or content or "", limit=limit, include_history=include_history)

    elif action == "replace":
        if not old_text:
            return tool_error("old_text is required for 'replace' action.", success=False)
        if not content:
            return tool_error("content is required for 'replace' action.", success=False)
        result = store.replace(target, old_text, content)

    elif action == "remove":
        if not old_text:
            return tool_error("old_text is required for 'remove' action.", success=False)
        result = store.remove(target, old_text)

    else:
        return tool_error(f"Unknown action '{action}'. Use: add, store, recall, replace, remove", success=False)

    return json.dumps(result, ensure_ascii=False)


def check_memory_requirements() -> bool:
    """Memory tool has no external requirements -- always available."""
    return True


# =============================================================================
# OpenAI Function-Calling Schema
# =============================================================================

MEMORY_SCHEMA = {
    "name": "memory",
    "description": (
        "Save or recall durable information that survives across sessions. New writes are "
        "typed records routed by runtime to the profile's durable provenance store; the "
        "small injected MEMORY.md/USER.md surface is only a bounded manifest.\n\n"
        "WHEN TO SAVE (do this proactively, don't wait to be asked):\n"
        "- User corrects you or says 'remember this' / 'don't do that again'\n"
        "- User shares a preference, habit, or personal detail (name, role, timezone, coding style)\n"
        "- You discover something about the environment (OS, installed tools, project structure)\n"
        "- You learn a convention, API quirk, or workflow specific to this user's setup\n"
        "- You identify a stable fact that will be useful again in future sessions\n\n"
        "PRIORITY: User preferences and corrections > environment facts > procedural knowledge. "
        "The most valuable memory prevents the user from having to repeat themselves.\n\n"
        "Do NOT save task progress, session outcomes, completed-work logs, or temporary TODO "
        "state to memory; use session_search to recall those from past transcripts.\n"
        "If you've discovered a new way to do something, solved a problem that could be "
        "necessary later, save it as a skill with the skill tool.\n\n"
        "TWO MANIFEST TARGETS (compatibility pointers only):\n"
        "- 'user': who the user is -- name, role, preferences, communication style, pet peeves\n"
        "- 'memory': your notes -- environment facts, project conventions, tool quirks, lessons learned\n\n"
        "ACTIONS: store/add (typed durable record), recall (search typed records), "
        "replace/remove (legacy manifest maintenance only). Use memory_type and scope; "
        "do not select paths or attempt a retry after a receipt.\n\n"
        "SKIP: trivial/obvious info, things easily re-discovered, raw data dumps, and temporary task state."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "store", "recall", "replace", "remove"],
                "description": "The action to perform."
            },
            "target": {
                "type": "string",
                "enum": ["memory", "user"],
                "description": "Which memory store: 'memory' for personal notes, 'user' for user profile."
            },
            "content": {
                "type": "string",
                "description": "The entry content. Required for 'add' and 'replace'."
            },
            "old_text": {
                "type": "string",
                "description": "Short unique substring identifying the entry to replace or remove."
            },
            "memory_type": {"type": "string", "enum": sorted(_MEMORY_TYPES), "description": "Semantic type for store/add."},
            "scope": {"type": "string", "description": "Owner scope, such as profile, project, or task."},
            "project": {"type": "string", "description": "Project identifier when relevant."},
            "task": {"type": "string", "description": "Task identifier when relevant."},
            "authority": {"type": "string", "description": "Authority level, e.g. user or verified_system."},
            "source": {"type": "string", "description": "Origin, e.g. user_stated, tool_fetched, system_observed."},
            "provenance": {"type": "string", "description": "Source/evidence reference, not raw evidence."},
            "lifecycle_status": {"type": "string", "description": "Normally active; use archived/failed only when true."},
            "verification_status": {"type": "string", "description": "verified, unverified, or failed."},
            "supersedes": {"type": "string", "description": "Prior durable memory id replaced by this record."},
            "query": {"type": "string", "description": "Search query for recall."},
            "include_history": {"type": "boolean", "description": "Include superseded/archived records for explicit audit requests."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Recall result limit."},
        },
        "required": ["action", "target"],
    },
}


# --- Registry ---
from tools.registry import registry, tool_error

registry.register(
    name="memory",
    toolset="memory",
    schema=MEMORY_SCHEMA,
    handler=lambda args, **kw: memory_tool(
        action=args.get("action", ""),
        target=args.get("target", "memory"),
        content=args.get("content"),
        old_text=args.get("old_text"),
        memory_type=args.get("memory_type"), scope=args.get("scope"), project=args.get("project"),
        task=args.get("task"), authority=args.get("authority"), source=args.get("source"),
        provenance=args.get("provenance"), lifecycle_status=args.get("lifecycle_status"),
        verification_status=args.get("verification_status"), supersedes=args.get("supersedes"),
        agent=args.get("agent"), query=args.get("query"), include_history=args.get("include_history", False),
        limit=args.get("limit", 5),
        store=kw.get("store")),
    check_fn=check_memory_requirements,
    emoji="🧠",
)
