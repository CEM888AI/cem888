# Changelog

All notable changes to the public CEM888 source are recorded here. Each `## vX.Y.Z` section becomes the notes of the matching GitHub release.

Status labels follow [docs/STATUS.md](./docs/STATUS.md): a mechanism listed here is **implemented in this source tree**; it is not customer-certified until it passes on the exact installed customer artifact.

## Unreleased

Nothing pending. The most recent change set is `## v1.0.46` below.

## v1.0.46 — 2026-10-15

**Source move.** This tree was republished from the current customer runtime: **83 files advanced, none added, none removed** — the public surface did not grow. It had been frozen at 2026-10-05 while the working source moved on, and that drift produced a published claim that was false (see "Public conformance suite" below).

**Fixed**
- **Public conformance suite: the suite was asserting a contract this engine does not have, and the published result was wrong.** It asserted that a forbidden root is *denied*; the path/shell denial surface was struck by an owner ruling on 2026-09-28, and the engine records the reasoning internally. The suite went red on 2026-10-05 and stayed red for ten days while the README claimed 12/12 — a billboard stating a control the runtime does not enforce. It now asserts the fail-closed manifest loader (with a positive control), the layer taxonomy, and the ruling itself: **15 / 15 pass**. Two falsifier runs — re-denying a layer, and serving a superseded row as current — are confirmed to turn it red. See [docs/PUBLIC_CONFORMANCE.md](./docs/PUBLIC_CONFORMANCE.md).
- Supersession closes the prior record's lifecycle (`lifecycle_status='superseded'`) in the same transaction that sets `superseded_by`, so a row that names its successor is never `active`. Regression-tested.
  **Corrected 2026-10-15:** an earlier revision of this entry also claimed that *existing stores are repaired when opened*. This source tree performs **no** repair-on-open (there is no `UPDATE … WHERE superseded_by IS NOT NULL` anywhere in the runtime), so the claim was removed. What protects current truth is the read gate — `lifecycle_status='active' AND superseded_by IS NULL` — and the test now asserts exactly that, including that the excluded row stays reachable through history.
- Context-file cap in the shipped doctrine: the seeding and tips text now state what the engine actually enforces — **32,000 characters** for project context (`CONTEXT_FILE_MAX_CHARS`, cut head 70% + tail 20%, middle dropped) and **8,000** for lazily-discovered directory hints. An earlier revision of this tree told customers 20,000.
- Documentation that over-claimed a denial control was corrected; the matrix now states only what the runtime actually enforces.
- A wedged desktop driver no longer blocks every later call: the failure is now reported instead of reading as an empty screen.

**Changed**
- Public conformance suite: **15 checks** (was 12 reported / 9 at first release). Test dependencies: `pytest`, `pyyaml`.
- Licensing (2026-10-05): the **Elastic License 2.0 is superseded by the CEM888 Source-Available Commercial License** (owner decision, Plane CEM-297). Source-available, commercial, **never converts to open source**, and **free for personal, non-commercial use only** — nothing that makes money, or builds a business, is free. Commercial Use (business production use, earning from its output, proprietary redistribution, private modifications, resale, embedding, white-labeling, OEM distribution, or providing it to third parties as a hosted or managed service) requires a **paid** licence from CEM Unlimited LLC. Non-retroactive: v1.0.3 remains AGPL-3.0; versions first released under BSL 1.1 or ELv2 remain under those terms. Full text: [licensing/LICENSE.md](./licensing/LICENSE.md).
- Licensing: the unreleased change to Business Source License 1.1 is superseded by the **Elastic License 2.0 (ELv2)** — source-available, and it never converts to an open-source license (owner decision, Plane CEM-297). ELv2 grants broad use, including commercial internal use, with two limitations: you may not offer CEM888 to third parties as a hosted or managed service, and you may not move, change, disable or circumvent the license-key functionality. Business production use, paid client work, embedding, resale, white-labeling and OEM distribution require a valid CEM888 license key for the applicable tier or a separate commercial license from CEM Unlimited LLC. v1.0.3 remains AGPL-3.0; any version first released under BSL 1.1 remains under those BSL terms.

**Known limits** (unchanged from v1.0.3)
- Public beta, one maintainer; APIs and on-disk formats may change.
- Supported install path is the account flow at https://cem888.ai, not this repository.
- The DeepSeek Flash customer artifact is still in its certification lane. Native Claude Code / Codex adapters are planned, not shipped.
- The shell authority check is an in-process semantic boundary, not an OS security boundary.

## v1.0.3 — first public beta

First public source release of the CEM888 runtime under AGPL-3.0 (community lane) with a separate negotiated commercial license.

**Source**
- Identity-neutral runtime source: CPython 3.14, package `cem888-agent` 1.0.3.
- Tier-0 authority manifest: path and shell-mutation authority, immutable manifest.
- Bounded context compiler: per-turn context packet with a selection receipt; superseded state excluded from current context.
- Typed durable memory with lifecycle and supersession.

**Evidence**
- Public conformance suite (9 checks at release), with falsifier runs that turn it red.
- Published technical status, including a non-conformant earlier customer artifact (2 PASS / 9 FAIL): [docs/STATUS.md](./docs/STATUS.md).
- Integration contract, enforcement matrix, native host adapter contract and architecture note under [docs/](./docs).

**Known limits**
- Public beta, one maintainer; APIs and on-disk formats may change.
- Supported install path is the account flow at https://cem888.ai, not this repository.
- The DeepSeek Flash customer artifact is still in its certification lane. Native Claude Code / Codex adapters are planned, not shipped.
- The shell authority check is an in-process semantic boundary, not an OS security boundary.
