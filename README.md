<div align="center">

# CEM888

### Reliability, continuity, and control for AI agents

**STATE decides what is true. MODELS decide what to do about it.**

[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](#license)
[![Public beta](https://img.shields.io/badge/public_beta-v1.0.3-orange?style=flat-square)](#status)

**[cem888.ai](https://cem888.ai)** · **[Technical status](./docs/STATUS.md)** · **[Integration](./docs/INTEGRATION.md)** · **[Engineering evidence](https://github.com/CEM888AI/runtime-case-studies)**

</div>

---

## What CEM888 is

CEM888 is a **reliability and control runtime that sits underneath AI agents**.

It keeps operating truth outside the LLM so the model can reason and act without also being responsible for remembering what is current, what it is allowed to do, or whether a claimed result actually happened.

```text
EXISTING AGENT / HOST
        |
        v
CEM888 CONTROL LAYER
  - identity + scope
  - authoritative current state
  - continuity / recovery
  - bounded working context
  - action authority
  - verification + receipts
        |
        v
EXISTING MODELS / TOOLS / DATA
```

CEM888 is designed to be additive:

> **Keep the agent. Add the reliability layer.**

It does not require a company to replace its UI, planner, domain logic, model provider, or tool stack simply to gain continuity and control.

## Use the AI you already pay for

The planned host-adapter path is designed so a customer can keep using an existing AI product — for example Claude Code, Codex, GitHub Copilot / VS Code, Cursor, JetBrains-hosted agents, or another supported host — while CEM888 supplies the state, continuity, control, and verification layer underneath it.

Where the host exposes enough lifecycle control, the target flow is:

```text
existing paid AI host
        |
        v
CEM888 host adapter
  - current-state inhale
  - bounded context injection
  - standing authority
  - action verification
  - exactly-once exhale
        |
        v
customer project / tools / data
```

The commercial hypothesis is straightforward:

> **If CEM888 can keep the host focused on the current objective and authoritative working state, the same AI subscription may spend less work re-reading, reconstructing context, repeating failed paths, or carrying stale conversation history.**

That is a testable claim, not a published savings promise.

For each supported host, the planned proof is **host alone vs. the same host + CEM888** on the same task and repository. Measurements include observable token/usage, prompt/context size, repeated reads/searches, tool calls, retries, wall-clock time, fresh-session recovery, drift from current state, stale-state mistakes, and verified completion.

The first planned deep host adapters after the DeepSeek-first customer release are **Claude Code** and **Codex**. Broader targets include GitHub Copilot / VS Code, Cursor, JetBrains, OpenCode, and other hosts where lifecycle access is strong enough to support meaningful CEM behavior.

See **[Native host adapters](./docs/HOST_ADAPTERS.md)** for the integration roadmap, lifecycle contract, certification levels, and benchmark plan.

## Status

**The CEM888 runtime is built and operating.**

The current release work is focused on the **customer-install surface**: making the downloadable artifact faithfully carry the same runtime behavior, identify exactly what it is running, and pass clean-install / upgrade / conformance checks as one frozen release candidate.

That distinction matters:

```text
CEM888 runtime
  -> freeze the proven capability set
  -> promote customer-safe changes together
  -> build one customer artifact
  -> freeze artifact + digests
  -> certify the install
  -> re-baseline that exact artifact
  -> partner handoff
```

This avoids rebuilding the customer wheel after every runtime improvement and keeps the artifact a deterministic promotion target.

See **[docs/STATUS.md](./docs/STATUS.md)** for the current release track.

## Core architecture

### Authoritative state

Current operational truth lives outside the model context. The model can reason over state; it does not get to redefine authority by wording something more confidently.

### Supersession

Newer authoritative state can replace older state without deleting history.

> **Relevance can help retrieve a candidate. Relevance does not increase its authority.**

### Bounded working context

The runtime compiles the smallest useful current working packet rather than replaying an ever-growing transcript.

### Continuity

Durable state lets work survive fresh sessions, restarts, model changes, and host changes where the host exposes the required integration boundary.

### Action authority

Models propose actions. Runtime state and scope determine whether consequential execution is allowed.

Explicit owner prohibitions constrain **both** sides of the loop: prohibited/superseded material must not be surfaced as current authoritative working state, and attempts to operationalize it through a CEM-controlled action boundary are blocked before execution. A connected model cannot restore permission merely through semantic similarity, stale memory, alternate wording, or a generic instruction to "finish it." Only explicit owner authorization can narrow or revoke the prohibition.

### Verification + receipts

A model saying “done” is not the same thing as observable proof. CEM888 can evaluate outcomes against runtime-visible evidence and record structured result states / receipts.

### Provider neutrality

The state and control layer is independent of any single model provider. Model intelligence can change without making the model itself the durable ledger.

## For technical partners

If you are evaluating CEM888 for integration, diligence, or partnership, read these in order:

1. **[Technical status](./docs/STATUS.md)** — runtime versus customer-install release track.
2. **[Partner technical brief](https://github.com/CEM888AI/runtime-case-studies/blob/main/partner-technical-brief.md)** — architecture, lifecycle, integration seams, authority, continuity, and verification.
3. **[Integration contract](./docs/INTEGRATION.md)** — the lifecycle boundary an existing agent connects to.
4. **[Capability promotion matrix](./docs/CAPABILITY_MATRIX.md)** — runtime capability → customer source → frozen artifact → install certification.
5. **[Architecture](https://github.com/CEM888AI/runtime-case-studies/blob/main/architecture.md)** — conceptual turn flow.
6. **[Engineering case studies](https://github.com/CEM888AI/runtime-case-studies)** — real failures, root causes, fixes, and measured evidence.
7. **[Benchmarks](https://github.com/CEM888AI/benchmarks)** — benchmark archive and raw results.

The point of these documents is to let a CTO understand the system without requiring a founder walkthrough first.

## Integration model

CEM888 attaches at lifecycle seams rather than asking a partner to rewrite its agent:

```text
TURN START
  -> resolve identity / task
  -> load authoritative state
  -> compile bounded working context

BEFORE CONSEQUENTIAL ACTION
  -> resolve target / scope
  -> authorize or block

AFTER EXECUTION
  -> capture observable evidence
  -> verify outcome

TURN FINISH
  -> commit resulting state
  -> record receipt / checkpoint
```

The partner can continue to own:

- UI
- planner
- agent logic
- model selection
- tool implementations
- observability stack
- domain workflows

CEM888 owns the reliability/control boundary around them.

## Evidence

CEM888 keeps **engineering evidence** separate from **customer-artifact certification**.

Engineering evidence includes:

- benchmark runs
- context-bounding measurements
- tool-surface reduction
- continuity tests
- verification case studies
- exactly-once/idempotency tests
- tenant-isolation failures and fixes
- install/conformance failures that were used to improve the release path

The benchmark repository preserves older runs because they remain useful evidence of engineering behavior over time. The frozen customer artifact receives its own current re-baseline after install certification.

**[Engineering case studies →](https://github.com/CEM888AI/runtime-case-studies)**  
**[Benchmark archive →](https://github.com/CEM888AI/benchmarks)**

## Local-first and customer control

CEM888 is designed so authoritative runtime state remains on customer-controlled infrastructure.

Account, update, provider, or connector services may participate in onboarding, transport, or model access; they are not the authority for the customer's runtime state.

Customer installations must begin with clean identity, state, authority, configuration, and credentials rather than inheriting maintainer data.

## Enterprise direction

The long-term direction is to make CEM888 a **reliability, continuity, and control layer for AI in high-consequence and data-sensitive environments** — including legal, financial, public-sector, and regulated enterprise systems.

That direction requires more than model quality:

- customer-controlled/private deployment
- tenant and identity isolation
- provenance and auditability
- explicit action authority
- evidence-backed verification
- restart/recovery continuity
- duplicate-effect protection
- clear data and trust boundaries
- provider/model replaceability without losing authoritative state

This is a product direction, not a claim of certification under any specific legal, banking, government, or regulatory regime. Sector-specific compliance and certification are handled per deployment.

## Repository and third-party notices

This repository contains the public/community CEM888 source lane, customer execution/package code, public integration documentation, and release provenance.

CEM888 uses open-source components. Required third-party license notices are preserved in **[third-party license notices](./licenses/third-party/MIT-NOTICE.txt)**.

Private implementation details that are not required to integrate with or evaluate the product — such as internal scoring/weighting, private routing policy, private prompts, customer data, credentials, and operational secrets — are not part of the public contract.

## Installation

The supported end-user onboarding flow begins at **[cem888.ai](https://cem888.ai)** rather than by cloning this repository.

1. Create a free account.
2. Create/configure the agent.
3. Generate the installer for the target machine.
4. Install locally.

Source builds remain available for inspection and development. The supported customer-install path is the account-generated installer.

## License

**Community lane — AGPL-3.0.** CEM888-authored community work in this repository is distributed under AGPL-3.0, subject to preserved third-party notices and licenses.

**Commercial lane — negotiated terms.** Commercial agreements can cover CEM888-authored rights, proprietary embedding, white-labeling, redistribution, custom integration, support, or private deployment. Third-party components retain their own license obligations.

See **[third-party license notices](./licenses/third-party/MIT-NOTICE.txt)**.

For commercial licensing, private/on-prem integration, or technical partnership:

**creator@cem888.ai**

---

Maintained by **Chandler Morone / CEM Unlimited LLC**.

**[cem888.ai](https://cem888.ai)** · [Engineering evidence](https://github.com/CEM888AI/runtime-case-studies) · [Benchmarks](https://github.com/CEM888AI/benchmarks)
