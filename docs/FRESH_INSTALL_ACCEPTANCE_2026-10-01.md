# Fresh-install acceptance — 2026-10-01

**Status:** CORE FIRST-BOOT / CONTINUITY PATH PASSED WITH DEFECTS

This document records an operator-observed acceptance run against a newly installed CEM888 customer agent. It is intentionally narrower than full customer certification: the run exercised first-boot identity, durable state, automatic exhale, restart continuity, explicit supersession, retrieval/index surfaces, one evidence-verified file action, duplicate/retry deduplication, and second-restart continuity. It did **not** certify the full authority-bypass matrix, concurrent-writer behavior, all verification action classes, long-horizon boundedness, or the complete hostile Stage-2 fault suite.

## Artifact tested

- Agent: `customer-2` / Nove
- Runtime-reported version: **v1.0.0 (2026.09.12)**
- Manifest revision: **customer-1.0.38**
- Certified source digest: `8047698c9636a8d352f78578c3f482744f415162835b4667d9f7c5b1c523befd`
- Install path: `~/.cem888/profiles/nove/venv`
- Python: **3.14.7**
- OS: **macOS 26.5.2 (Darwin)**
- Model path: **deepseek-flash (BYOK)**

## What passed as installed

| Check | Observed result |
| --- | --- |
| Profile identity isolation | Customer profile contained the expected agent/owner identity and no founder/other-customer identity, path, credential, or durable-state contamination inside the profile |
| Durable typed-state write | Canary, active task, and decision were written through the normal typed-memory path and read back from SQLite |
| Automatic exhale | Runtime automatically wrote continuity/state surfaces and indexed the turn without a manual DB writer |
| Fresh-process continuity | Two genuine fresh processes recovered current work/state without transcript replay |
| Explicit supersession path | Historical ORANGE decision became superseded and PURPLE was retrieved as current |
| Retrieval/index surfaces | Typed state, BM25, Chroma/vector, FTS, Obsidian vault mirror, and the MSCC path were active and read/write exercised |
| Bounded-context compiler path | One observed compile reduced 25 candidates to 11 selected candidates in ~19 ms; this is evidence the compiler path is active, **not** a long-horizon boundedness certification |
| Evidence-verified file action | File content was independently re-read and SHA-256 matched before completion was treated as verified |
| Duplicate/retry deduplication | Replaying the same completion returned `duplicate: true` and the same memory identity; no duplicate logical task/completion was observed |
| Second-restart lifecycle | Current PURPLE state, completed file task, canary, and completion evidence survived another fresh process; completed work was not presented as active |

## Defects found

These findings are deliberately retained; this run is evidence only because it was allowed to fail individual checks.

1. **Duplicate current decision:** two active PURPLE decision records remained after the supersession flow. Explicit `supersedes=` linkage worked, but current-truth uniqueness was not fully enforced.
2. **Path-sensitive hybrid retrieval:** one `hybrid_ranking` entry path returned an empty result while the populated BM25/vector/FTS path returned the expected candidates.
3. **Shared-root residue:** the profile itself was identity-clean, but the shared `~/.cem888` root contained founder/operator-era backups/plugins and sibling profiles. This prevents a claim that the whole customer root was pristine.
4. **MCP stdio noise:** a dotenv banner reached stdout and was parsed as a JSON-RPC frame before the MCP channel recovered.
5. **Duplicate/dead Chroma lane:** an empty in-profile Chroma database existed while live vector traffic used the vault store.
6. **Memory typing hygiene:** some inbound probe prompts were stored as `memory_type=decision`.
7. **Open-work hygiene:** a greeting remained as an active open-work item.
8. **Doctor false negative:** `cem888 doctor` reported a missing venv entry point even though `venv/bin/cem888` existed.
9. **Optional dependency ambiguity:** croniter, discord.py, Docker, and agent-browser were absent; the product needs to declare which are required versus capability-specific/optional.

## Claims this run does NOT establish

This run does **not** certify:

- full deterministic action-authority bypass resistance;
- the dual owner-prohibition contract;
- all verification action classes;
- concurrent-writer safety under injected contention;
- mutation-provenance reconstruction for arbitrary state;
- long-horizon context boundedness across 100+ turns;
- hostile crash injection around every side-effect/commit boundary;
- native Claude Code or Codex adapters;
- regulated-sector compliance.

Those claims remain gated on their own falsifiers and, where applicable, a newly frozen customer artifact after the defects above are repaired.

## Current conclusion

The tested artifact demonstrated a working first-boot continuity path: durable state, automatic exhale, restart recovery, explicit supersession, live retrieval/index surfaces, evidence-backed completion for a file action, retry deduplication, and second-restart continuity all operated without manual repair.

The artifact is **not represented as fully customer-certified** because the run also exposed a current-truth uniqueness defect, a silent-zero retrieval path, shared-root residue, and several install/runtime hygiene issues.

The next step is to fix those defects, freeze a new artifact, and rerun this exact test unchanged before promoting the result.
