# Changelog

All notable changes to the public CEM888 source are recorded here. Each `## vX.Y.Z` section becomes the notes of the matching GitHub release.

Status labels follow [docs/STATUS.md](./docs/STATUS.md): a mechanism listed here is **implemented in this source tree**; it is not customer-certified until it passes on the exact installed customer artifact.

## v1.0.3 — first public beta

First public source release of the CEM888 runtime under AGPL-3.0 (community lane) with a separate negotiated commercial license.

**Source**
- Identity-neutral runtime source: CPython 3.14, package `cem888-agent` 1.0.3. Provenance and digests in [PROVENANCE.md](./PROVENANCE.md).
- Tier-0 authority manifest (`src/agent/authority.py`): path and shell-mutation authority, immutable manifest.
- Bounded context compiler (`src/agent/context_compiler.py`): per-turn context packet with a selection receipt; superseded state excluded from current context.
- Typed durable memory with lifecycle and supersession (`src/tools/memory_tool.py`).

**Evidence**
- Public conformance suite (`tests/`, 9 checks) with CI on every push.
- Published technical status, including a non-conformant earlier customer artifact (2 PASS / 9 FAIL): [docs/STATUS.md](./docs/STATUS.md).
- Integration contract, enforcement matrix, native host adapter contract and architecture note under [docs/](./docs).

**Known limits**
- Public beta, one maintainer; APIs and on-disk formats may change.
- Supported install path is the account flow at https://cem888.ai, not this repository.
- The DeepSeek Flash customer artifact is still in its certification lane. Native Claude Code / Codex adapters are planned, not shipped.
- The shell authority check is an in-process semantic boundary, not an OS security boundary.
