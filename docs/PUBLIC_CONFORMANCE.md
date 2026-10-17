# Public conformance tests

These tests are a **small public falsifier suite for claims already implemented in this repository**.
They are not a claim that the customer artifact is fully certified.

The suite currently covers **four public invariants in 15 checks**:

1. **Tier-0 authority manifest + layer classification**
   - the loader **fails closed**: a manifest with no `allowed_write_roots` (or no
     `protected_write_roots`) is refused, never downgraded to "no authority";
   - a manifest that declares a different `profile_root` **or** a different `profile_name`
     than the profile directory it sits in is refused;
   - a valid manifest loads and carries its write roots — the positive control, without
     which the refusals above prove nothing;
   - layer classification: `authority.json` and `AGENT_SYSTEM_MAP.json` are classified as
     their own layers, and profile paths (`SOUL.md`, `AGENTS.md`, `state/…`, `skills/…`,
     `plugins/…`, `cron/…`, `memories/…`, `config.yaml`) are classified into the taxonomy;
   - **no layer carries `gate="denied"`**, and `write_denial` / `command_denial` /
     `layer_write_denial` return `None`.
     ⚠️ **This asserts an ABSENCE on purpose.** The path/shell denial surface was struck by
     an owner ruling on 2026-09-28, and the authority module records the reasoning in
     three docstrings. The test fails if blanket denial is reintroduced — it is a ruling
     guard, not a control. The authority surface here is a **classification and
     fail-closed loading** contract; it is not an OS security boundary.

2. **Authority-aware current-state retrieval**
   - a superseded typed-memory row is not eligible for the current working-context packet.

3. **Bounded-context receipts**
   - the receipt records selection metadata and a SHA-256 of the query;
   - raw query text is not copied into the receipt;
   - irrelevant non-identity candidates can be excluded for lack of task relevance.

4. **Supersession lifecycle**
   - superseding a record moves the old row to `lifecycle_status='superseded'`, not only `superseded_by`;
   - across a chain of supersessions, exactly one row is active and none is both active and superseded;
   - a row left by the defective path (linked, but still `active`) is **never served as
     current state** — the current-state read requires `lifecycle_status='active' AND
     superseded_by IS NULL` — while remaining reachable through history.
     ⚠️ An earlier version of this suite asserted that such stores are *repaired when
     opened*. **This source tree performs no such repair** (there is no
     `UPDATE … WHERE superseded_by IS NOT NULL` anywhere in the runtime), so that claim was
     removed rather than left asserting behaviour the code cannot support.

Run locally:

```bash
python3.14 -m pip install pytest pyyaml
PYTHONPATH=src python3.14 -m pytest -q tests
```

## This suite is falsified before it is trusted

A passing suite is only evidence if it is **able to fail**. Two mutations were run against
this suite and confirmed to turn it red:

| Mutation | Result |
| --- | --- |
| re-deny a layer (`LAYER_STATE.gate = "denied"`) | `1 failed` — `test_no_layer_carries_a_denied_gate` |
| serve a superseded row as current (`where = ""`) | `1 failed` — `test_a_row_written_by_the_defective_path_is_never_current` |

Before 2026-10-15 this file asserted the **deleted** denial contract, so CI went red on
2026-10-05 and stayed red for ten days while the README claimed 12/12. A test that asserts a
control the engine does not have is not a stricter test — it is a wrong one.

## Scope boundary

These tests exercise the **public engineering source tree**. They do not replace the
customer-artifact certification gate described in `docs/STATUS.md`. A mechanism passing here is
not automatically a customer-certified claim; the exact frozen install artifact still has to pass
its own conformance run.

The authority checks here cover the in-process semantic authority boundary that is implemented
in the authority module. That module explicitly states that it is **not an OS security
boundary** for hostile shell expansion/symlink cases. Strong deployments may add service-user,
filesystem, container, or other OS controls as defense in depth.
