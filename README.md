<div align="center">

# CEM888

### Local-first state & control runtime underneath AI agents

**STATE decides what is true. MODELS decide what to do about it.**

[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](#license)
[![Stage: Public beta](https://img.shields.io/badge/stage-public_beta-orange?style=flat-square)](#current-stage)

**[cem888.ai](https://cem888.ai)** · **[Technical status](./docs/STATUS.md)** · **[Engineering evidence](https://github.com/CEM888AI/runtime-case-studies)** · **[Benchmarks](https://github.com/CEM888AI/benchmarks)**

</div>

---

## The 60-second version

AI models are becoming better reasoners, but an agent still needs a system outside the model to answer four operational questions reliably:

1. **What is true now?**
2. **What does this model need to know now?**
3. **What is this agent allowed to do?**
4. **What actually happened after it acted?**

CEM888 is the runtime for that layer.

It maintains authoritative working state outside the LLM, carries relevant state across sessions and model changes, compiles bounded context for the current task, applies action authority at enforceable boundaries, and evaluates observable outcomes instead of treating model prose as proof.

```text
EXISTING AGENT / HOST
        |
        v
CEM888 STATE + CONTROL RUNTIME
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

> **Keep the agent. Add the reliability layer.**

## Current stage

CEM888 is in public beta. The current release lane is deliberately narrow: **finish and certify the DeepSeek Flash customer install first, then expand provider and native-host support from measured evidence.**

| Surface | Current status |
| --- | --- |
| **CEM engineering runtime / ancestor** | Operating and used to prove product-relevant mechanisms. It is not the website customer artifact. |
| **Customer product artifact** | DeepSeek Flash-first install, parity, upgrade and conformance certification in progress. |
| **Claude Code / Codex native adapters** | Planned after the DeepSeek customer path passes its release gate; not shipped or certified today. |
| **High-consequence / regulated deployments** | Long-term product direction. No sector-specific certification claim is being made. |

The customer artifact is a **promotion and certification target**, not assumed correct because a mechanism exists elsewhere. Every release claim should name the exact artifact or evidence behind it.

See **[Technical Status](./docs/STATUS.md)** for the current capability table and published limitations.

## Reproducible public checks

This repository now includes a small public falsifier suite for claims that are already implemented in the public engineering source tree.

```bash
python3.14 -m pip install pytest
PYTHONPATH=src python3.14 -m pytest -q tests
```

The current public checks cover:

- Tier-0 protected-path authority and manifest immutability;
- rejection of literal shell mutations against denied protected roots;
- exclusion of superseded typed-memory rows from current context candidates;
- bounded-context receipt behavior, including hashed query provenance without copying raw query text into the receipt.

See **[Public conformance checks](./docs/PUBLIC_CONFORMANCE.md)** for the exact scope and limitations.

These are source-level falsifiers, **not a substitute for exact customer-artifact certification**. Customer release claims still require the frozen installed artifact to pass its own conformance gate.

## Why CEM888 exists

LLMs are excellent at inference and synthesis. They are poor places to keep durable operational truth.

Without an external state/control layer, long-running agents can:

- rebuild project state from stale conversation;
- carry superseded decisions forward because they are semantically similar;
- repeat expensive or consequential work after retries/restarts;
- widen action scope from model reasoning;
- report completion without an observable postcondition;
- lose useful working state when the model, host or session changes.

CEM888 separates those responsibilities.

### Authoritative state

Current operational truth lives outside model context. The model can reason over state; it does not get to redefine authority through wording.

### Supersession

Newer authoritative state can replace older state while preserving history.

> **Relevance can help retrieve a candidate. Relevance does not increase its authority.**

### Bounded working context

The runtime compiles the minimum useful current packet instead of treating an ever-growing transcript as working memory.

### Continuity

Structured state can survive fresh sessions, restarts and model changes without requiring the user to reconstruct the project from scratch.

### Action authority

Models propose actions. Runtime state and scope determine what may cross a CEM-controlled execution boundary.

### Verification + receipts

A model saying "done" is not the same as proof. Where the postcondition is mechanically observable, CEM888 evaluates runtime-visible evidence and records structured result state / receipts.

### Provider neutrality

The model is replaceable intelligence. The state/control contract is intended to remain stable as providers change.

## Claim discipline

CEM888 separates **implemented**, **customer-certified**, **specified**, and **planned** behavior.

That distinction is intentional.

For example, the dual owner-prohibition model — preventing prohibited material from being promoted as current truth while also blocking matching protected actions at an enforceable boundary — is part of the public control contract, but it is **not represented as customer-certified end to end until both falsifiers pass on the exact installed artifact**.

See:

- **[Technical status](./docs/STATUS.md)**
- **[Integration contract](./docs/INTEGRATION.md)**
- **[Enforcement matrix](./docs/ENFORCEMENT_MATRIX.md)**
- **[Native host adapters](./docs/HOST_ADAPTERS.md)**

## Evidence

CEM888 publishes engineering evidence separately from product certification.

That evidence includes benchmark runs, failure case studies, context-bounding measurements, continuity tests, verification failures/fixes, tenant-isolation defects, install conformance results and other falsifiers.

**[Engineering case studies →](https://github.com/CEM888AI/runtime-case-studies)**  
**[Benchmark archive →](https://github.com/CEM888AI/benchmarks)**  
**[Partner technical brief →](https://github.com/CEM888AI/runtime-case-studies/blob/main/partner-technical-brief.md)**

Historical experiments remain useful engineering evidence, but a customer/partner build receives its own re-baseline after the exact artifact is frozen and install-certified.

## For investors, partners and technical evaluators

A fast diligence path:

1. **[Technical status](./docs/STATUS.md)** — what is implemented, in progress, specified and not yet certified.
2. **[Partner technical brief](https://github.com/CEM888AI/runtime-case-studies/blob/main/partner-technical-brief.md)** — the product boundary and integration model.
3. **[Engineering case studies](https://github.com/CEM888AI/runtime-case-studies)** — real failures, diagnoses and measured repairs.
4. **[Benchmarks](https://github.com/CEM888AI/benchmarks)** — public benchmark archive and methodology.
5. **[Provenance](./PROVENANCE.md)** — what this source tree is and what is deliberately not included.

The product thesis is simple: **model intelligence will keep changing; companies still need durable state, action authority, continuity and evidence outside the model.**

## Integration model

CEM888 is designed to attach at lifecycle seams rather than force a partner to replace its agent architecture:

```text
TURN START
  -> resolve identity / task
  -> load authoritative current state
  -> compile bounded working context

BEFORE CONSEQUENTIAL ACTION
  -> resolve target / scope
  -> authorize or block where an enforceable boundary exists

AFTER EXECUTION
  -> capture observable evidence
  -> evaluate the postcondition

TURN FINISH
  -> commit resulting state
  -> record checkpoint / receipt
```

A partner can continue to own its UI, planner, model choice, tools, domain workflow and observability stack.

## Native-host direction

The longer-term host-adapter path is designed so a customer can keep using an existing AI product while CEM888 supplies the state/control layer underneath it.

MCP connectivity alone is not enough to claim full control. Each host must be classified from the lifecycle boundaries it actually exposes.

The first planned deep adapters after the current DeepSeek-first release lane are **Claude Code** and **Codex**.

See **[Native Host Adapters](./docs/HOST_ADAPTERS.md)**.

## Local-first and customer control

CEM888 is designed around customer-controlled runtime state.

The website is the account/onboarding/download surface. Customer agents run on the customer's machine or customer-controlled infrastructure rather than on a shared CEM888 execution service.

Clean customer installs must start with clean identity, state, authority, configuration and credentials.

## Repository scope

This repository is the public/community CEM888 source lane and customer execution/package surface.

It is **not** the canonical production-development authority. Public GitHub exists for community access, evidence, documentation, evaluation and distribution.

Private implementation details that are not necessary to integrate with or evaluate the product — including private prompts, proprietary scoring/routing policy, customer data, credentials and operational secrets — are not part of the public contract.

See **[PROVENANCE.md](./PROVENANCE.md)** and the preserved **[third-party license notices](./licenses/third-party/MIT-NOTICE.txt)**.

## Installation

The supported end-user onboarding flow begins at **[cem888.ai](https://cem888.ai)**.

1. Create a free account.
2. Create/configure the agent.
3. Generate the installer for the target machine.
4. Install locally.

The current customer release work is optimized and tested most heavily around **DeepSeek Flash**. Provider neutrality is an architectural goal; equivalent cost/performance optimization for every provider should not be assumed until measured.

## Enterprise direction

CEM888 is intended to mature into a reliability, continuity and control layer for AI in data-sensitive and high-consequence environments, including legal, financial, public-sector and regulated enterprise systems.

That direction requires customer-controlled deployment, identity isolation, provenance, explicit authority, evidence-backed verification, restart/recovery continuity and clear trust boundaries.

This is a product direction, **not a claim of certification or regulatory compliance today**.

## License

**Community lane — AGPL-3.0.** CEM888-authored community work in this repository is distributed under AGPL-3.0, subject to preserved third-party notices and licenses.

**Commercial lane — negotiated terms.** Separate commercial agreements can cover proprietary embedding, white-labeling, redistribution, custom integration, support and private deployment of CEM888-authored work.

For commercial licensing, technical partnerships, design-partner discussions or investment conversations:

**creator@cem888.ai**

---

Maintained by **Chandler Morone / CEM Unlimited LLC**.

**[cem888.ai](https://cem888.ai)** · **[Engineering evidence](https://github.com/CEM888AI/runtime-case-studies)** · **[Benchmarks](https://github.com/CEM888AI/benchmarks)**
