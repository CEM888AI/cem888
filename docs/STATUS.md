# CEM888 Technical Status

**Updated: 2026-10-01**

This page is the public status boundary for CEM888. It distinguishes the **CEM engineering runtime / ancestor**, the **customer product artifact**, and **planned host integrations** so an evaluator does not have to infer readiness from version labels, source files or architecture diagrams.

## Executive status

CEM888 is a working engineering system in public beta. The current release objective is not to invent the architecture from scratch; it is to **promote the product-relevant capability set into one customer artifact, freeze that artifact, and prove the same claims on the installed build**.

The CEM engineering runtime is the ancestor. It is **not** the website customer wheel/product artifact. Customer certification must therefore name the exact artifact, digest or release revision being tested.

## Capability status

| Capability | Current public status | Customer-release requirement |
| --- | --- | --- |
| Authoritative current state + supersession | **Customer first-boot path exercised; explicit supersession worked, but duplicate-current defect remains** | Fix uniqueness defect and re-run on new frozen artifact |
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
| Native Claude Code / Codex adapters | **Planned** | Implement only after current DeepSeek install gate |
| Regulated-sector certification | **Not claimed** | Deployment-specific future work |

## Current customer-release lane

The immediate release sequence is:

```text
finish CEM engineering capability set
  -> promote customer-relevant changes together
  -> build one DeepSeek-first candidate artifact
  -> freeze artifact + digests
  -> run install conformance
  -> run clean-install / upgrade / retry tests
  -> re-baseline the exact installed artifact
  -> external beta / partner handoff
```

Only after this lane passes does the roadmap expand to alternate standalone providers and native existing-host adapters.


## Fresh-install acceptance — 2026-10-01

A newly installed customer agent was exercised through first boot, durable typed-state writes, automatic exhale, two genuine fresh-process restarts, explicit supersession, BM25/vector/FTS/vault retrieval, one evidence-verified file action, duplicate/retry replay, and second-restart lifecycle recovery.

**Result: core first-boot / continuity path passed with defects.** The run is **not** represented as full customer certification.

Observed defects included duplicate current decision state, one path-sensitive hybrid-retrieval empty result, shared-root residue, MCP stdio noise, an empty duplicate Chroma lane, memory-typing/open-work hygiene issues, and a doctor false negative.

Full artifact details, evidence boundary, and non-claims: **[Fresh-install acceptance — 2026-10-01](./FRESH_INSTALL_ACCEPTANCE_2026-10-01.md)**.

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

> **Fix the defects found in the October 1 fresh-install run, freeze a new DeepSeek-first customer artifact, and rerun the same acceptance test unchanged before promoting it to customer-certified.**
