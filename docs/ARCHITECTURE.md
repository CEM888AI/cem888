# CEM888 Architecture Note

**Audience:** an engineer deciding in ten minutes whether this runtime does what the README says.
**Scope:** the three mechanisms that carry the core claim, with the file where each one lives. Everything here is implemented in this source tree; status per capability is in [STATUS.md](./STATUS.md). Customer certification is a separate gate.

```text
turn start ──► resolve authority ──► compile bounded context ──► model proposes
                                                                     │
turn finish ◄── write typed state ◄── record receipt ◄── authorize / block action
```

---

## 1. State lifecycle — what counts as "true now"

**Store:** SQLite, `state/memory_provenance.db` under the agent's profile home. Table `typed_memories`, written by `src/tools/memory_tool.py`.

Each record carries:

| Field | Purpose |
| --- | --- |
| `id`, `content`, `content_sha256` | Identity and content hash |
| `memory_type`, `scope`, `agent`, `project`, `task` | What kind of fact, and whose |
| `authority`, `source`, `provenance` | Who asserted it and where it came from |
| `lifecycle_status` | `active`, or a terminal state such as `archived` / `failed` |
| `verification_status` | `verified`, `unverified` or `failed` |
| `supersedes`, `superseded_by` | Explicit replacement chain |
| `created_at`, `updated_at` | Timestamps (ordering only, never identity) |

**Write rules**

- **Idempotent.** A write whose `(content_sha256, memory_type, scope, agent)` already exists returns the existing id with `duplicate: true` instead of inserting a second row. A retried write does not create a second fact.
- **Supersession is explicit.** A new record that names `supersedes=<id>` sets `superseded_by` on the old row in the same transaction. The old row stays for history; it stops being current.
- Defaults are conservative: new rows are `active` and `unverified` unless the caller states otherwise.

**Read rule (current truth).** The context compiler reads the store read-only and considers only:

```sql
WHERE lifecycle_status = 'active' AND superseded_by IS NULL
```

Superseded or archived rows never enter the current working packet, however relevant they look. They remain reachable through an explicit history recall (`include_history=true`), labeled as non-current. This is the "relevance does not increase authority" rule, and it is covered by `tests/test_context_compiler_public.py`.

## 2. Bounded context — what the model sees

**Code:** `src/agent/context_compiler.py` (`compile_context`).

Each turn the compiler gathers candidates, each with a fixed authority weight:

| Candidate source | Authority |
| --- | --- |
| Active canonical pathways (`pathways` table, `status='active'`) | 100 |
| Agent identity / relationship files | 95 |
| Verified typed memory | 94 |
| Current checkpoint (`state/continuity_packet.json`) | 92 |
| Unverified typed memory | 82 |
| Retrieved memory prefetch | 70 |

Selection is deterministic:

1. Inactive or superseded candidates score −100000 (excluded).
2. Candidates below authority 95 with **zero** term overlap with the current query are excluded as `no_query_relevance`, unless they are marked unresolved.
3. Everything else scores `authority × 10 + overlap × 35`, with +30 if verified and +25 if unresolved.
4. Candidates are taken in score order until the token budget is spent (default 1,024 tokens, clamped to 512–32,768). Exact-duplicate content is dropped by SHA-256.

The model receives the selected candidates as one `<minimal_sufficient_context>` packet plus the last few exchanges (default 3, max 8), not the full transcript.

## 3. Action authority — where "no" is enforced

**Code:** `src/agent/authority.py`. The Tier-0 manifest (`authority.json`) is the only runtime source allowed to decide an agent's identity, profile binding and protected write roots. Prompts, memory and plugins may describe those facts; they cannot override them.

**File writes** (`AgentAuthority.write_denial`, called from `src/agent/file_safety.py`), evaluated in order:

1. Target is the manifest itself → `AUTHORITY_MANIFEST_IMMUTABLE`.
2. Target is under a forbidden root → `TARGET_AUTHORITY_MISMATCH`.
3. Target is under a protected root and not under an allowed root → `TARGET_AUTHORITY_MISMATCH`.
4. Otherwise allowed.

**Shell commands** (`AgentAuthority.command_denial`, called from `src/tools/terminal_tool.py` **before** the ordinary dangerous-command approval step, and not bypassable with `force=True`):

- Non-mutating commands pass.
- A mutating command (`rm`, `mv`, `cp`, redirects, `git commit/push/...`, `pip`, `python -c`, etc.) is denied if its working directory, any literal path argument (resolved, so `/var` → `/private/var` aliases do not evade it), or any protected root string would fail `write_denial`.
- If authority cannot be loaded, the terminal call is refused with `AUTHORITY_UNAVAILABLE`. Unresolved authority is not permission.

**Stated limit:** the shell check is an in-process semantic boundary, not an OS sandbox. Hostile shell expansion and symlink tricks need OS-level controls (service user, filesystem permissions, containers) as defense in depth. Which integrations can hard-block which actions is classified in the [Enforcement Matrix](./ENFORCEMENT_MATRIX.md).

## 4. What a receipt contains

Every compiled context writes a receipt atomically to `state/context_receipts/latest.json`:

| Field | Meaning |
| --- | --- |
| `schema_version`, `state_version` | Format versions |
| `context_packet_id` | `ctx_` + SHA-256 of the query and selected source ids (24 hex chars) |
| `created_at_unix_ms` | When the packet was compiled |
| `selected`, `selected_types` | Which sources went into the packet |
| `excluded` | Up to 100 source ids left out |
| `selection` | Per candidate: `included`, `score`, `reason` (`duplicate`, `budget`, `no_query_relevance`, `inactive_or_superseded`, or the score breakdown), `tokens` |
| `section_tokens`, `packet_tokens` | Token cost by source type and in total |
| `recent_message_count`, `recent_exchange_limit`, `raw_message_count` | How much transcript was carried vs. available |
| `query_sha256` | Hash of the user query; the raw query text is **not** stored |
| `provider`, `model` | Which model the packet was compiled for |

A receipt answers "why did the model see this and not that" for a given turn. It is provenance, not certification. Verification receipts for executed actions follow the same principle (record what was checked and what evidence was observed); their coverage is still partial, see [STATUS.md](./STATUS.md).

## How to check this yourself

```bash
python3.14 -m pip install pytest
PYTHONPATH=src python3.14 -m pytest -v tests
```

The suite exercises manifest immutability, forbidden/allowed roots, shell-mutation denial, superseded-row exclusion and receipt query hashing. Scope and limits: [PUBLIC_CONFORMANCE.md](./PUBLIC_CONFORMANCE.md).
