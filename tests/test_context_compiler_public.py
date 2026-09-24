import hashlib
import json
import sqlite3
from pathlib import Path

from agent import context_compiler


def _create_typed_store(home: Path) -> Path:
    db = home / "state" / "memory_provenance.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE typed_memories (
          id TEXT PRIMARY KEY,
          content TEXT NOT NULL,
          memory_type TEXT NOT NULL,
          scope TEXT NOT NULL,
          project TEXT,
          task TEXT,
          authority TEXT NOT NULL,
          source TEXT NOT NULL,
          provenance TEXT,
          verification_status TEXT NOT NULL,
          lifecycle_status TEXT NOT NULL,
          superseded_by TEXT,
          updated_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    return db


def test_superseded_memory_is_not_a_current_candidate(tmp_path: Path) -> None:
    home = tmp_path / "profile"
    db = _create_typed_store(home)
    conn = sqlite3.connect(db)
    conn.executemany(
        """
        INSERT INTO typed_memories
        (id, content, memory_type, scope, project, task, authority, source,
         provenance, verification_status, lifecycle_status, superseded_by, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "old",
                "deploy path is /old/path",
                "decision",
                "profile",
                "site",
                None,
                "user",
                "owner",
                "turn-old",
                "verified",
                "superseded",
                "new",
                1.0,
            ),
            (
                "new",
                "deploy path is /current/path",
                "decision",
                "profile",
                "site",
                None,
                "user",
                "owner",
                "turn-new",
                "verified",
                "active",
                None,
                2.0,
            ),
        ],
    )
    conn.commit()
    conn.close()

    candidates = context_compiler._typed_memory_candidates(home, "deploy path")
    ids = [candidate.source_id for candidate in candidates]

    assert "new" in ids
    assert "old" not in ids


def test_selection_receipt_contains_hashes_and_metadata_not_raw_query(
    tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "profile"
    home.mkdir(parents=True)
    (home / "SOUL.md").write_text("Permanent identity invariant.", encoding="utf-8")
    monkeypatch.setenv("CEM888_HOME", str(home))

    secret_query = "private sentinel query that must not appear in receipt"
    result = context_compiler.compile_context(
        [{"role": "user", "content": secret_query}],
        user_query=secret_query,
        token_budget=512,
    )

    receipt_path = home / "state" / "context_receipts" / "latest.json"
    receipt_text = receipt_path.read_text(encoding="utf-8")
    receipt = json.loads(receipt_text)

    assert secret_query not in receipt_text
    assert receipt["query_sha256"] == hashlib.sha256(secret_query.encode()).hexdigest()
    assert "selection" in receipt
    assert "packet_tokens" in receipt
    assert result.receipt["context_packet_id"] == receipt["context_packet_id"]


def test_irrelevant_non_identity_candidate_is_excluded() -> None:
    candidate = context_compiler.Candidate(
        source_id="old-note",
        source_type="retrieved_memory",
        content="completely unrelated material",
        authority=70,
    )
    selected, decisions = context_compiler.select_candidates(
        [candidate], "deploy current website", 512
    )

    assert selected == []
    assert decisions[0]["included"] is False
    assert decisions[0]["reason"] == "no_query_relevance"
