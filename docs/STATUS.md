# CEM888 Technical Status

**Updated: 2026-10-17**

> **Source freshness — public repository, source-available licence.** This repository is the source and
> audit record, and it is **public** under the [CEM888 Source-Available Commercial License](../LICENSE)
> (not open source: free for personal non-commercial use, no hosting, no rebranding). It was **republished on 2026-10-15** from the current customer runtime (83 files
> advanced; no file was added to or removed from this tree). Its conformance suite is **15 / 15
> passing**, and the suite itself was corrected the same day: it had been asserting a path/shell
> denial contract that an owner ruling struck on 2026-09-28, so CI was **red from 2026-10-05** while
> an earlier README claimed 12/12. See [PUBLIC_CONFORMANCE.md](./PUBLIC_CONFORMANCE.md). Nothing below
> is upgraded by that republication — the capability rows still describe the **customer artifact**,
> which is a separate certification target.

This page is the runtime status boundary for CEM888. It distinguishes the **CEM engineering runtime / ancestor**, the **customer product artifact**, and **planned host integrations** so an evaluator does not have to infer readiness from version labels, source files or architecture diagrams.

## Executive status

CEM888 is a working engineering system in public beta. The current release objective is not to invent the architecture from scratch; it is to **promote the product-relevant capability set into one customer artifact, freeze that artifact, and prove the same claims on the installed build**.

The CEM engineering runtime is the ancestor. It is **not** the website customer wheel/product artifact. Customer certification must therefore name the exact artifact, digest or release revision being tested.

## Capability status

| Capability | Current public status | Customer-release requirement |
| --- | --- | --- |
| Authoritative current state + supersession | **Explicit supersession works; the duplicate-current defect is fixed (v1.0.46) and regression-tested.** Two related gaps stay open: a state write can still be retired across hosts on a shared phrasing key, and legacy superseded rows are excluded on read rather than repaired on open | Re-run on the current frozen release |
| Bounded working-state compilation | **Implemented on the CEM engineering path** | Re-prove on frozen customer artifact |
| Typed active-work lifecycle | **Customer first-boot path exercised** | Greeting/open-work hygiene defect must be fixed and re-run |
| Multi-session write safety | **Restart continuity + duplicate/retry dedup observed on customer install** | Concurrent-writer contention still needs hostile proof |
| Deterministic action authority | **In progress / hardening** | Bypass audit + measurable deny/effect proof |
| Verification evidence integrity | **In progress / hardening** | Runtime-captured evidence; no trust in caller/model prose |
| Verification coverage | **Partial** | Publish exact covered/unsupported action classes |
| Gate liveness | **Not complete** | Prove gates produce a real deny/withhold/effect |
| Mutation provenance | **Not complete** | Mechanically reconstruct why current state changed |
| Authority-aware deep memory search | **Partially exercised on customer install** | Fix path-sensitive silent-zero retrieval and re-run stale-state falsifier |
| Dual owner-prohibition contract | **Specified; not customer-certified end to end** | Pass retrieval + action falsifiers on exact artifact |
| Native Claude Code / Codex adapters | **Running in the paid app and under active repair — several defects closed 2026-10-08 to 2026-10-18. Neither adapter is certified** | Certification of each adapter against the same acceptance standard |
| Regulated-sector certification | **Not claimed** | Deployment-specific future work |

## Current customer-release lane

Two lanes, two states. The **free** lane publishes frozen, digest-named releases. The **paid** lane does not yet.

| | |
|---|---|
| Current free release | **free-v1.0.48** — 2026-10-18 — four platform bundles (darwin-arm64, darwin-x86_64, linux-x86_64, windows-amd64) plus `SHA256SUMS`, every file digest-published as a release-asset SHA-256 |
| `SHA256SUMS` SHA-256 | `aee07bdfc77d1c65306336abe7b68200c0d7be0a3a563a8a5d8af361b43f9792` |
| Previous free release | **free-v1.0.47** — 2026-10-17, same shape |
| Retired | the **v1.0.46** wheel — it was built with the builder `PROVENANCE.md` forbids, and while it was the shipped wheel the free release refused to publish at all. Re-cut, not patched |
| Last artifact with a **full** acceptance run | `cem888_agent-1.0.41-py3-none-any.whl` — 3,963,252 bytes — SHA-256 `0d090610d74ebaa56edaf5ebb7a0efc568f26b859f2cd23e26b30f43350f9d5a` — release commit `5342bac3` — deployed 2026-10-01, health-checked at that revision |
| Paid lane | **not frozen.** The paid carrier currently ships a wheel set its own lock cannot satisfy, so a paid install falls back to an index — open, and paid delivery is therefore unproven end to end |

```text
promote customer-relevant changes together         [done — 1.0.40 -> 1.0.48]
  -> rebuild wheel + platform bundles              [done — free lane publishing since v1.0.47]
  -> freeze artifact + digests                     [done — free-v1.0.48, digest-named]
  -> publish + verify shipped bundle               [done — four platforms + SHA256SUMS]
  -> run install conformance on the frozen release [OPEN]
  -> run clean-install / upgrade / retry tests     [PARTIAL — upgrade path proven once, retry not]
  -> external beta / partner handoff               [gated on the above]
```

Only after this lane passes does the roadmap expand to alternate standalone providers and native existing-host adapters.


## Fresh-install acceptance — 2026-10-01

A newly installed customer agent was exercised through first boot, durable typed-state writes, automatic exhale, two genuine fresh-process restarts, explicit supersession, BM25/vector/FTS/vault retrieval, one evidence-verified file action, duplicate/retry replay, and second-restart lifecycle recovery.

**Result: core first-boot / continuity path passed with defects.** The run is **not** represented as full customer certification.

Observed defects included duplicate current decision state, one path-sensitive hybrid-retrieval empty result, shared-root residue, MCP stdio noise, an empty duplicate Chroma lane, memory-typing/open-work hygiene issues, and a doctor false negative.

Full artifact details, evidence boundary, and non-claims: **[Fresh-install acceptance — 2026-10-01](./FRESH_INSTALL_ACCEPTANCE_2026-10-01.md)**.

### What has been closed since that run

The list above is the record of 2026-10-01, not the state of the build today. Between 2026-10-14 and 2026-10-19 the following were fixed and closed: the release refused to publish and shipped a wheel built by a forbidden builder; the free installer gave every agent on a machine one directory, so a second agent overwrote the first and `cem888 chat --profile <key>` could never resolve (**accepted on real Windows hardware by the owner, 2026-10-19**); the paid install could land a mute agent behind an unpinned package-source failure, with no shell and zero skills; the Workspace app was fetched, verified, then silently skipped, and the installer judged success on an exit code instead of the artifact; the paid payload shipped no tool-receipt or memory-disposition code at all; a provider key with no funding installed a mute agent instead of saying so; the subscription lane was dead at both ends and a picked subscription was never wired; entitlement minting did not exist on the host; fresh installs defaulted to an unlisted model alias; the transcript was rewritten non-atomically and erased mid-turn; every agent reply was stored twice; context injection was deduplicated for one host only; and the shipped identity text documented context caps the runtime did not enforce.

**What that does not establish:** those are fixes with their own evidence, not a pass of the acceptance standard. No acceptance run has been recorded against any frozen release since **1.0.41**, and the paid lane has not been proven end to end (install → agent → Workspace → entitlement).

## Published non-conformant baseline

An earlier installed customer artifact was intentionally tested rather than assumed correct.

**Published result: 2 PASS / 9 FAIL — NON-CONFORMANT.**

The measured failures included:

- no proven durable exactly-once/idempotency key;
- no cheap turn-start inhale gate;
- incomplete authority metadata;
- schema-fragile memory writer;
- Chroma/BM25 present but not wired into the automatic inhale compiler;
- no timeline/FTS retrieval leg;
- no automatic typed-state exhale writer;
- provider-neutral operations absent from the installed artifact;
- broken local MCP serve import.

That artifact is **not** the partner/customer candidate and is not represented as certified.

Publishing the failure is deliberate: a useful conformance harness should be capable of proving the product wrong.

For the detailed engineering record, see **[Current Engineering Status](https://github.com/CEM888AI/runtime-case-studies/blob/main/current-engineering-status.md)**.

## What the release gate proves

The customer artifact is not considered proven because:

- a source file exists;
- a plugin is installed;
- a mechanism works on the CEM engineering ancestor;
- an installer reports that a feature is enabled.

The claim becomes customer-proven only when the **same falsifier passes on the exact installed artifact**.

The release gate covers, as applicable:

- authoritative current state and supersession;
- bounded working-state compilation;
- continuity across fresh session / restart;
- action scope and authority behavior;
- evidence-backed verification / receipts;
- duplicate/retry protection;
- identity and tenant isolation;
- clean install / update / retry behavior;
- exact artifact identity and digests.

## Claim policy

Public language should distinguish:

- **Implemented** — mechanism exists on the named engineering surface.
- **Customer-certified** — falsifier passed on the exact installed customer artifact.
- **Specified** — contract/design is documented but proof is incomplete.
- **Planned** — roadmap work; not shipped.
- **Not claimed** — intentionally outside the current product claim.

A future integration or architectural intention must not be presented as a shipped capability.

## Benchmarks and evidence

Historical benchmark runs remain part of the engineering record. They are not automatically current release claims.

The frozen customer candidate receives a new baseline so the measurement refers to one exact build.

- **[Engineering case studies](https://github.com/CEM888AI/runtime-case-studies)**
- **[Benchmarks](https://github.com/CEM888AI/benchmarks)**
- **[Partner technical brief](https://github.com/CEM888AI/runtime-case-studies/blob/main/partner-technical-brief.md)**
- **[Enforcement matrix](./ENFORCEMENT_MATRIX.md)**

## Current bottom line

CEM888 has a coherent operating architecture and meaningful engineering proof, but the current customer artifact is being held to a stricter standard than "the code exists."

The next milestone is simple to state:

> **Run the same acceptance test unchanged against the current frozen release (free-v1.0.48), close the items it still fails, then run it against the paid carrier. Only then is either lane customer-certified.**

The free lane is cut, frozen and digest-named (above); the earlier locale-codec class is repaired with a release guard that fails loudly if its own detector stops detecting. What remains open is not the October 1 defect list — most of that list is closed — but the standard itself: no unchanged acceptance run exists on the current release, the paid lane's delivery is unproven, and the two supersession gaps above are open. Neither lane is represented as conformant until the unchanged test passes on the exact artifact.
