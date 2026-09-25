"""Supersession must close the prior row's lifecycle, not only link it.

Regression for the defect reported by the 2026-09-18 external runtime evaluation:
superseding a record set ``superseded_by`` but left the old row
``lifecycle_status='active'``, breaking the invariant that a superseded row is
never active.
"""

import sqlite3
from pathlib import Path

import pytest

from tools import memory_tool


@pytest.fixture()
def profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "profile"
    home.mkdir()
    monkeypatch.setattr(memory_tool, "_profile_dir", lambda: home)
    return home


def _write(content: str, supersedes: str | None = None) -> dict:
    return memory_tool._write_durable_memory(
        content=content, target="memory", memory_type="decision", scope="profile",
        project="site", task=None, authority="user", source="owner",
        provenance="test", lifecycle_status=None, verification_status="verified",
        supersedes=supersedes, agent="cem",
    )


def _row(home: Path, record_id: str) -> tuple:
    conn = sqlite3.connect(home / "state" / "memory_provenance.db")
    row = conn.execute(
        "SELECT lifecycle_status, superseded_by FROM typed_memories WHERE id=?", (record_id,)
    ).fetchone()
    conn.close()
    return row


def test_superseded_row_is_no_longer_active(profile: Path) -> None:
    old = _write("deploy path is /old/path")
    assert old["success"]
    new = _write("deploy path is /new/path", supersedes=old["memory_id"])
    assert new["success"]

    assert _row(profile, old["memory_id"]) == ("superseded", new["memory_id"])
    assert _row(profile, new["memory_id"]) == ("active", None)


def test_no_row_is_both_active_and_superseded(profile: Path) -> None:
    a = _write("fact version 1")
    b = _write("fact version 2", supersedes=a["memory_id"])
    _write("fact version 3", supersedes=b["memory_id"])

    conn = sqlite3.connect(profile / "state" / "memory_provenance.db")
    bad = conn.execute(
        "SELECT COUNT(*) FROM typed_memories WHERE lifecycle_status='active' AND superseded_by IS NOT NULL"
    ).fetchone()[0]
    active = conn.execute(
        "SELECT content FROM typed_memories WHERE lifecycle_status='active'"
    ).fetchall()
    conn.close()
    assert bad == 0
    assert active == [("fact version 3",)]


def test_existing_stores_are_repaired_on_open(profile: Path) -> None:
    old = _write("legacy fact")
    new = _write("replacement fact")
    db = profile / "state" / "memory_provenance.db"
    conn = sqlite3.connect(db)
    # Simulate a row written by the defective code path.
    conn.execute(
        "UPDATE typed_memories SET superseded_by=?, lifecycle_status='active' WHERE id=?",
        (new["memory_id"], old["memory_id"]),
    )
    conn.commit()
    conn.close()

    memory_tool._init_durable_db().close()

    assert _row(profile, old["memory_id"]) == ("superseded", new["memory_id"])
