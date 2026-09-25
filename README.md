<div align="center">

# CEM888

### Local-first state & control runtime underneath AI agents

**STATE decides what is true. MODELS decide what to do about it.**

[![Tests](https://github.com/CEM888AI/cem888/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/CEM888AI/cem888/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/CEM888AI/cem888?include_prereleases&style=flat-square&label=release)](https://github.com/CEM888AI/cem888/releases)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](#license)
[![Stage: Public beta](https://img.shields.io/badge/stage-public_beta-orange?style=flat-square)](./docs/STATUS.md)

</div>

**What it is.** CEM888 is a runtime that keeps an AI agent's current state, action permissions and completion evidence outside the model, so the agent stays correct across sessions, restarts and model changes.

**How it works.** Every turn runs one loop: it tests, validates and investigates against the current objective, grounds every action towards truth, and keeps going until it has answers or better questions.

**Who it is for.** Teams running long-lived or multi-session agents that need to know what is true now, what the agent is allowed to do, and whether "done" actually happened.

**What this repository is.** The public source and audit record for the CEM888 runtime. It is not the installer. The supported install path is the account flow at **[cem888.ai](https://cem888.ai/register.html)**: create a free account, configure the agent, download the installer for your machine.

**Run the public checks (from source):**

```bash
python3.14 -m pip install pytest pyyaml
PYTHONPATH=src python3.14 -m pytest -q tests
```

**Evidence:** **[Technical status + published test results](./docs/STATUS.md)** · **[Public conformance suite](./docs/PUBLIC_CONFORMANCE.md)** · **[Runtime evaluation](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation)** · **[Architecture note](./docs/ARCHITECTURE.md)** · **[Engineering case studies](https://github.com/CEM888AI/runtime-case-studies)** · **[Benchmarks](https://github.com/CEM888AI/benchmarks)**

---

## Evidence scorecard

Every result below links to its source.

| Check | Result | Scope | Source |
| --- | --- | --- | --- |
| Public conformance suite (this repo, CI on every push) | **12 / 12 pass** | Tier-0 authority, superseded-state exclusion, supersession lifecycle, context-receipt provenance | [PUBLIC_CONFORMANCE.md](./docs/PUBLIC_CONFORMANCE.md) · [CI](https://github.com/CEM888AI/cem888/actions/workflows/tests.yml) |
| Independent runtime evaluation (2026-09-18) | **9 / 9 pass** | Durable state, kill-and-recover, model swap, verified execution, authority boundary, unknown state, provenance, contradiction/freshness, failure recovery | [Hugging Face dataset](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation) |
| Engineering runtime falsifiers | 8 authority · 53 verification · 17 hook-sync · 4 fabricated-evidence · 4 store-locking — all pass | CEM engineering runtime, not yet the customer artifact | [current-engineering-status.md](https://github.com/CEM888AI/runtime-case-studies/blob/main/current-engineering-status.md) |

The runtime evaluation was run by an AI engineering assistant on Hugging Face Jobs infrastructure on September 18, 2026 (Debian 13, DeepSeek, CEM888 v1.0.x). Its full method and terms are on the dataset page.

**Benchmark of record:** BEAM-10M **77.2%** (154.4 / 200), live agent, no answer-key access. Per-question data, scoring script and methodology: **[CEM888AI/benchmarks](https://github.com/CEM888AI/benchmarks)**. Other runs in that repository are labeled experimental or measure a different benchmark and are not substitutes for this number.

## Current stage

CEM888 is in public beta. The current release lane is deliberately narrow: **finish and certify the DeepSeek Flash customer install first, then expand provider and native-host support from measured evidence.**

| Surface | Current status |
| --- | --- |
| **CEM engineering runtime** | Operating and used to prove product-relevant mechanisms. It is not the website customer artifact. |
| **Customer product artifact** | DeepSeek Flash-first install, parity, upgrade and conformance certification in progress. |
| **Claude Code / Codex native adapters** | Next, after the DeepSeek customer path passes its release gate. |
| **High-consequence / regulated deployments** | Product direction; compliance scoped per deployment. |

The customer artifact is a **promotion and certification target**, not assumed correct because a mechanism exists elsewhere. Every release claim names the exact artifact or evidence behind it. Full table: **[Technical Status](./docs/STATUS.md)**.

## What the runtime does

An agent needs a system outside the model to answer four operational questions reliably:

1. **What is true now?** Authoritative current state lives outside model context. Newer state supersedes older state while history is preserved. Relevance can retrieve a candidate; it does not increase its authority.
2. **What does this model need to know now?** The runtime compiles a bounded context packet per turn instead of replaying a growing transcript.
3. **What is this agent allowed to do?** Models propose actions. Runtime state and scope decide what may cross a CEM-controlled execution boundary.
4. **What actually happened?** Where a postcondition is observable, the runtime checks evidence and records a receipt instead of trusting model prose.

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

How each of those works in the source, including what a receipt contains: **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)**.

## Integration model

CEM888 attaches at lifecycle seams rather than replacing a partner's agent architecture:

```text
TURN START                 resolve identity / task -> load current state -> compile bounded context
BEFORE CONSEQUENTIAL ACTION resolve target / scope -> authorize or block where an enforceable boundary exists
AFTER EXECUTION            capture observable evidence -> evaluate the postcondition
TURN FINISH                commit resulting state -> record checkpoint / receipt
```

A partner keeps its UI, planner, model choice, tools, domain workflow and observability stack. MCP connectivity alone is not a claim of full control; each host is classified by the lifecycle boundaries it actually exposes. See **[Integration contract](./docs/INTEGRATION.md)**, **[Enforcement matrix](./docs/ENFORCEMENT_MATRIX.md)** and **[Native host adapters](./docs/HOST_ADAPTERS.md)**.

## Claim discipline

CEM888 separates **implemented**, **customer-certified**, **specified** and **planned** behavior. For example, the dual owner-prohibition model (prohibited material is never promoted as current truth, and matching protected actions are blocked at an enforceable boundary) is part of the public contract, but it is **not represented as customer-certified until both falsifiers pass on the exact installed artifact**.

## Local-first and customer control

The website is the account, onboarding and download surface. Customer agents run on the customer's machine or customer-controlled infrastructure, not on a shared CEM888 execution service. Clean installs start with clean identity, state, authority, configuration and credentials. Model access is bring-your-own-key.

## Repository scope

This repository is the public source and audit record for the CEM888 runtime. It is not the production-development authority and it is not the installer. Private prompts, proprietary scoring/routing policy, customer data, credentials and operational secrets are not part of the public contract. See **[PROVENANCE.md](./PROVENANCE.md)** and the preserved **[third-party license notices](./licenses/third-party/MIT-NOTICE.txt)**.

## Using CEM888 at work: what AGPL-3.0 means

This is a plain-language summary, not legal advice. The **[LICENSE](./LICENSE)** file governs.

| You want to… | Community license (AGPL-3.0) | Need a commercial license? |
| --- | --- | --- |
| Run it internally on your own machines or infrastructure | Yes | No |
| Modify it for internal use | Yes | No |
| Offer a modified version to users over a network | Yes, if you publish your modified source to those users under AGPL-3.0 | No, if you comply |
| Embed it in a closed-source product you sell or distribute | Not without releasing your combined source under AGPL-3.0 | **Yes** |
| White-label, resell, or run it as a closed hosted service | Not without meeting AGPL-3.0 obligations | **Yes** |

The trigger for a commercial license is **proprietary use or distribution that does not comply with AGPL-3.0**, not company size. Commercial terms (proprietary embedding, white-labeling, redistribution, custom integration, support, private deployment) are negotiated per deal: **creator@cem888.ai**.

## Contributing

Outside contributions require agreement to the **[Contributor License Agreement](./CLA.md)** before they can be merged. This keeps the community (AGPL-3.0) and commercial lanes both possible. See **[CONTRIBUTING.md](./CONTRIBUTING.md)**.

## Security

Report vulnerabilities privately to **creator@cem888.ai**. Scope, process and response targets: **[SECURITY.md](./SECURITY.md)**.

## Releases

Tagged releases with notes: **[Releases](https://github.com/CEM888AI/cem888/releases)** · **[CHANGELOG.md](./CHANGELOG.md)**.

## Enterprise direction

CEM888 is intended to mature into a reliability, continuity and control layer for AI in data-sensitive and high-consequence environments, including legal, financial, public-sector and regulated enterprise systems. That requires customer-controlled deployment, identity isolation, provenance, explicit authority, evidence-backed verification, restart/recovery continuity and clear trust boundaries. Sector-specific compliance is scoped with each customer, per deployment.

## License

**Community lane — AGPL-3.0.** CEM888-authored work in this repository is distributed under AGPL-3.0, subject to preserved third-party notices and licenses.

**Commercial lane — negotiated terms.** For commercial licensing, technical partnerships, design-partner discussions or investment conversations: **creator@cem888.ai**.

---

Maintained by **Chandler Morone / CEM Unlimited LLC** · **[cem888.ai](https://cem888.ai)**
