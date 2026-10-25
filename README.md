> **Licence: [CEM888 Source-Available Commercial License](./LICENSE) — commercial, source-available, NOT open source.** Free for personal, non-commercial use only; business production use, paid client work, embedding, resale, white-labeling, OEM distribution and hosted/managed service all require a paid licence from CEM Unlimited LLC — creator@cem888.ai. This applies to **every** release in this repository: no CEM888 release has ever been published under an open-source licence.

<div align="center">

<img src="./assets/readme-banner.png?v=2" alt="CEM888 — STATE decides what is true" width="100%" />

<br/>

<a href="https://cem888.ai">
  <img src="./assets/readme-btn-paid.svg" alt="Download CEM888 — paid product: desktop app, engine, subscription" width="380" height="60" />
</a>
&nbsp;
<a href="https://cem888.ai">
  <img src="./assets/readme-btn-website.svg" alt="cem888.ai" width="176" height="60" />
</a>
&nbsp;
<a href="#documentation-map">
  <img src="./assets/readme-btn-docs.svg" alt="Documentation" width="144" height="60" />
</a>

<br/>

[![Release](https://img.shields.io/github/v/release/CEM888AI/cem888?include_prereleases&style=flat-square&labelColor=050A0F&label=release)](https://github.com/CEM888AI/cem888/releases)
[![Free agent](https://img.shields.io/github/v/release/CEM888AI/cem888?filter=free-v*&style=flat-square&labelColor=050A0F&color=3ADBE8&label=free%20agent)](https://github.com/CEM888AI/cem888/releases/latest)
[![Update](https://img.shields.io/badge/update-cem888_update-FF8A6B?style=flat-square&labelColor=050A0F)](./install/README.md#update)
[![License](https://img.shields.io/badge/license-source--available_commercial-3ADBE8?style=flat-square&labelColor=050A0F)](./LICENSE)
[![Stage](https://img.shields.io/badge/stage-public_beta-B8943A?style=flat-square&labelColor=050A0F)](./docs/STATUS.md)
[![Conformance](https://img.shields.io/badge/public_conformance-15%2F15_pass-3ADBE8?style=flat-square&labelColor=050A0F)](./docs/PUBLIC_CONFORMANCE.md)
[![Benchmark](https://img.shields.io/badge/BEAM--10M-77.2%25-93A3B4?style=flat-square&labelColor=050A0F)](https://github.com/CEM888AI/benchmarks)

<br/>

<img src="./assets/readme-divider.svg" width="100%" alt="" />

</div>

---

## Get CEM888

The desktop app is the product: the agent, persistent state, action authority and verification
receipts, with a subscription attached. It is sold and downloaded only at
[cem888.ai](https://cem888.ai/) — the paid product is not published on GitHub.

The agent on its own is free, and there are two places to get it: [cem888.ai](https://cem888.ai/)
with a free account — no payment — or this repository's
[releases](https://github.com/CEM888AI/cem888/releases). Same agent either way: no desktop app, no
subscription. Commands are in
[install/README.md](https://github.com/CEM888AI/cem888/blob/main/install/README.md).

**Maintained, with regular updates.** Fixes and new releases of the free agent are published here
regularly. Already installed? Run `cem888 update`. Your config, keys, memories and skills are kept,
the download is checksum-verified, and the update rolls back if an agent stops booting. Details,
and the one-time command for installs made before 2026-10-25:
[install/README.md#update](./install/README.md#update).

---

<table>
<tr>
<td align="center" width="33%"><b>The whole product</b><br/><sub>Desktop app, engine and subscription — one account, one download.</sub></td>
<td align="center" width="33%"><b>Your machine, your keys</b><br/><sub>State stays on your disk. Model access is bring-your-own-key.</sub></td>
<td align="center" width="33%"><b>Product, not a script</b><br/><sub>The paid desktop app is downloaded and activated through cem888.ai.</sub></td>
</tr>
</table>

<div align="center">
  <img src="./assets/readme-divider.svg" width="100%" alt="" />
</div>

## The failure this exists for

Every agent framework optimizes **what the agent does next**. Almost nothing decides **what is actually true**. Those are different problems, and the second one is where agents fail in production:

- **State drifts.** The session ends, the transcript gets summarized, and last week's decision comes back as if it were current.
- **Stale truth wins.** An old fact is still retrievable, so relevance resurrects it and the agent acts on a superseded decision.
- **Retries duplicate.** A step runs twice because nothing outside the model recorded that it already ran.
- **"Done" is prose.** The model says it finished. No postcondition was checked, no evidence was captured, no receipt exists.

CEM888 puts the four things an agent needs outside the model:

| Question | Where the answer lives |
| --- | --- |
| **What is true now?** | Authoritative current state. Newer state supersedes older; history is kept. Relevance retrieves a candidate — it never raises its authority. |
| **What does this model need now?** | A context packet compiled per turn, instead of replaying a growing transcript. |
| **What is this agent allowed to do?** | Models propose. Runtime state and scope decide what crosses an execution boundary. |
| **What actually happened?** | Where a postcondition is observable, the runtime checks evidence and writes a receipt instead of trusting prose. |

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

## See the artifacts, not the marketing

The point of a runtime is what it emits. These are **sanitized samples of real structures** — field names and shapes are what the runtime actually produces, values are redacted:

- **[`examples/context-packet.json`](./examples/context-packet.json)** — what one turn is actually given: identity without scoring, owner rulings, current checkpoints, agreement state.
- **[`examples/receipt.json`](./examples/receipt.json)** — a verified action: what was proposed, what was checked, what evidence satisfied the postcondition.
- **[`examples/blocked-action.json`](./examples/blocked-action.json)** — an action denied at the boundary, and the rule that denied it.

No implementation detail is exposed by any of them. That is deliberate — see [Repository scope](#repository-scope).

## Evidence scorecard

Every result links to its source. **Failures are published next to passes**, because a scorecard that can't fail proves nothing:

| Check | Result | Scope | Source |
| --- | --- | --- | --- |
| Public conformance suite | **15 / 15 pass** | Tier-0 authority manifest loading (fail-closed) + layer classification, superseded-state exclusion, supersession lifecycle, context-receipt provenance | [PUBLIC_CONFORMANCE.md](./docs/PUBLIC_CONFORMANCE.md) |
| Independent runtime evaluation (2026-09-18) | **9 / 9 pass, one defect recorded** | Durable state, kill-and-recover, model swap, verified execution, unknown state, provenance, contradiction/freshness, failure recovery. **Two findings are published, not softened:** (1) **authority boundary — PASS on outcome, PARTIAL on mechanism attribution** (the refusal observed was prompt-obeyed, not a hard runtime gate blocking a call mid-execution); (2) the same run found a **storage-hygiene defect — supersession set `superseded_by` without flipping the old row's `lifecycle_status` off `active`,** so a reader trusting `lifecycle_status` alone sees two current records. **That defect is fixed in v1.0.46 — supersession now closes the prior row's lifecycle in the same transaction that names its successor — and regression-tested.** | [Hugging Face dataset](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation) |
| Fresh-install acceptance (2026-10-01) | **Core first-boot / continuity path passed — with documented defects** | Durable state, automatic exhale, two fresh-process restarts, explicit supersession, live retrieval/index surfaces, evidence-verified file action, retry deduplication | [FRESH_INSTALL_ACCEPTANCE_2026-10-01.md](./docs/FRESH_INSTALL_ACCEPTANCE_2026-10-01.md) |
| Claude Code host observation (2026-10-03) | **Turn-level continuity changed live engineering behavior** | Project state + repo/deploy/install constraints arrived automatically; owner prohibition blocked a protected edit; Claude used injected context while diagnosing a Codex connector profile conflict | [case study](https://github.com/CEM888AI/runtime-case-studies/blob/main/case-study-claude-code-turn-level-continuity.md) |
| Earlier installed customer artifact | **2 PASS / 9 FAIL — NON-CONFORMANT** | Historical install-conformance baseline, retained deliberately to show the harness can reject a build | [STATUS.md](./docs/STATUS.md#published-non-conformant-baseline) |
| Engineering runtime falsifiers | 8 authority · 53 verification · 17 hook-sync · 4 fabricated-evidence · 4 store-locking — all pass | CEM engineering runtime, not yet the customer artifact | [current-engineering-status.md](https://github.com/CEM888AI/runtime-case-studies/blob/main/current-engineering-status.md) |

The runtime evaluation was run by an AI engineering assistant on Hugging Face Jobs infrastructure on September 18, 2026 (Debian 13, DeepSeek, CEM888 v1.0.x). Method and terms are on the dataset page.

**Benchmark of record:** BEAM-10M **77.2%** (154.4 / 200), live agent, no answer-key access. Per-question data, scoring script and methodology: **[CEM888AI/benchmarks](https://github.com/CEM888AI/benchmarks)**. Other runs in that repository are labeled experimental or measure a different benchmark, and are not substitutes for this number.

## Closed since this page was last published — 2026-10-19 → 2026-10-23

Eleven defects were closed on the engineering board in the four days this page went stale. Each one
carries its own evidence on the board; none of them is a certification pass, and the two are not the
same sentence.

| Closed | What was broken | What is true now |
| --- | --- | --- |
| 2026-10-23 | **Every publish to `main` was refused.** The updater carrier had drifted from the engine, so no release could be cut from this repository. | The carrier is regenerated from the engine in the same commit, and releases publish again. |
| 2026-10-23 | **Minting a paid token invalidated every sibling token** — `Download not found`, plus a status lamp that latched on forever. | Mints no longer evict siblings, and an apply that ends on a conflict no longer latches the indicator. |
| 2026-10-23 | **Receipts and checkpoints shipped without their teaching or their harness** on the customer carrier. | Teaching and harness now travel with the carrier on all four platform tracks. |
| 2026-10-23 | **A connected Gemini CLI host got no chat room** — the room list was hardcoded to three hosts. | The room list follows the hosts actually connected. |
| 2026-10-23 | **A redundant edit was reported to the owner as a failed write** ("the file was not modified"). | A no-op edit reports as a no-op. A failure and a no-change are different outcomes. |
| 2026-10-23 | **A 600 s approval expiry was recorded as "User denied this command"** — the agent blamed the owner for its own timeout. | Expiry is recorded as expiry, attributed to the runtime, not the operator. |
| 2026-10-19 | **The paid offer page had nowhere to type a password** — a paying member could not sign in. | The sign-in field exists on the offer page. |
| 2026-10-19 | **The Windows paid carrier shipped a wheel set its own lock file could not satisfy** — every install failed on dependency resolution. | Lock and wheel agree; the offline install completes from the carrier alone. |
| 2026-10-19 | **Mac Intel shipped a `cp314` lock against a `cp311` runtime** — the offline install could not resolve on Intel hardware. | The Intel track resolves against the runtime it actually ships. |
| 2026-10-19 | **Four machines, four platform tracks** — download, app, agent, updater and button, run by the owner on real hardware. Passed; the per-machine wheel pin is still a follow-up. | Recorded as an owner-executed install pass, not as conformance to the acceptance standard. |

**What this does not establish.** No unchanged acceptance run has been recorded against a frozen
release since 2026-10-01, and the paid lane is still unproven end to end — install, agent, Workspace,
entitlement. Read [Status](./docs/STATUS.md) before treating any row above as a product guarantee.

## How it fits

CEM888 attaches at lifecycle seams. It does not replace a partner's agent architecture:

```text
TURN START                 resolve identity / task -> load current state -> compile bounded context
BEFORE CONSEQUENTIAL ACTION resolve target / scope -> authorize or block where an enforceable boundary exists
AFTER EXECUTION            capture observable evidence -> evaluate the postcondition
TURN FINISH                commit resulting state -> record checkpoint / receipt
```

A partner keeps its UI, planner, model choice, tools, domain workflow and observability stack. MCP connectivity alone is not a claim of full control — each host is classified by the lifecycle boundaries it actually exposes. See **[Integration contract](./docs/INTEGRATION.md)**, **[Enforcement matrix](./docs/ENFORCEMENT_MATRIX.md)** and **[Native host adapters](./docs/HOST_ADAPTERS.md)**.

### What this is not

| What you already run | What it decides | What CEM888 adds |
| --- | --- | --- |
| Agent frameworks — LangGraph, CrewAI, AutoGen, OpenAI Agents SDK | Which step runs next, and how work is orchestrated | Those stay. CEM888 decides what state the steps are allowed to believe. |
| Memory layers — mem0, Letta, Zep | What to remember and retrieve | Retrieval finds a candidate. CEM888 decides whether it is still *current* and how much authority it carries. |
| Observability and evals — LangSmith, Braintrust, W&B | What happened, after the fact, in traces | CEM888 checks postconditions *before* the agent may claim completion, and writes a receipt at the boundary. |
| Guardrail / policy proxies | Whether a call is textually allowed | Scope and authority are resolved per turn against current state, and denials are recorded, not just logged. |

These compose with CEM888. Nothing here requires replacing the stack you already have.

## FAQ

**Is this an agent framework?** No. It is a runtime underneath one. You keep your planner, model and tools.

**Do I have to rewrite my agent?** No. You integrate at up to four seams (turn start, before a consequential action, after execution, turn finish). Partial integration is supported and classified honestly — the [enforcement matrix](./docs/ENFORCEMENT_MATRIX.md) states what each host can and cannot block.

**Does my data leave my machine?** No. Customer agents run on the customer's machine or customer-controlled infrastructure, not on a shared CEM888 execution service. Model access is bring-your-own-key.

**Can I install from this repository?** Yes — the **free agent**, which is supported here and at [cem888.ai](https://cem888.ai). The **paid product** is not on GitHub; it comes only from cem888.ai. This repository is also the public engineering record: the **engine source** is not published here.

**Why isn't the source here?** Publishing the engine hands over the business without handing over a customer. The published record — architecture, enforcement limits, acceptance runs including the failures, and reproducible benchmark data — is the proof. It is not a substitute for reading the code, and this README does not pretend it is.

**What is actually certified today?** Nothing is certified under this repository's own standard, and the standard is the point. The last full acceptance run was 2026-10-01 on the 1.0.41 artifact, and it passed the core first-boot/continuity path **with documented defects**. Most of those defects have since been closed (2026-10-14 → 2026-10-19); the free lane now publishes frozen, digest-named releases (currently free-v1.0.48); and a Windows install was accepted on real hardware on 2026-10-19. But no unchanged acceptance run has been recorded against a frozen release since, and the paid lane has not been proven end to end — install, agent, Workspace, entitlement. [Status](./docs/STATUS.md) is the single source of truth, and it is updated when things fail, not only when they pass.

**Is the benchmark self-reported?** It is a live agent run with per-question data and the scoring script published in [benchmarks](https://github.com/CEM888AI/benchmarks), plus an independent runtime evaluation published as a dataset. Judge it on the artifacts, not the number.

## Current stage

Public beta. The release lane is deliberately narrow: **finish and certify the customer first-boot path, then expand provider and native-host support from measured evidence.**

| Surface | Current status |
| --- | --- |
| **CEM engineering runtime** | Operating and used to prove product-relevant mechanisms. It is not the website customer artifact. |
| **Customer product artifact** | Last full acceptance run: **2026-10-01**, on the **1.0.41** artifact, core first-boot/continuity passed **with documented defects**. Most of that defect list is now closed (2026-10-14 → 2026-10-19). No acceptance run has been recorded against a frozen release since, and the paid lane is unproven end to end — so it is not certified. |
| **Free agent downloads** (`install/free.sh`, `install/free.ps1`, plus this repository's releases) | Two download locations for the free agent: the free account at **[cem888.ai](https://cem888.ai)** and this repository. The paid desktop app is cem888.ai only — not on GitHub. Frozen, digest-named releases publish here: current is **free-v1.0.55** (2026-10-25), four platforms plus `SHA256SUMS`. Existing installs update in place with `cem888 update` (macOS / Linux; the Windows updater is not published yet). The Windows installer was **accepted on real hardware by the owner on 2026-10-19** — a second agent on the same machine, `cem888 chat --profile <key>` resolves. |
| **Claude Code / Codex native adapters** | Both run in the paid app and are under active repair — defects closed across 2026-10-08 → 2026-10-18. Neither adapter is certified. |
| **High-consequence / regulated deployments** | Product direction; compliance scoped per deployment. |

The customer artifact is a **promotion and certification target**, not assumed correct because a mechanism exists elsewhere. Full table: **[Technical Status](./docs/STATUS.md)**.

## Claim discipline

CEM888 separates **implemented**, **customer-certified**, **specified** and **planned** behavior. For example, the dual owner-prohibition model — prohibited material is never promoted as current truth, and matching protected actions are blocked at an enforceable boundary — is part of the public contract, but it is **not represented as customer-certified until both falsifiers pass on the exact installed artifact.**

## Local-first and customer control

The website is the account, onboarding and download surface. Customer agents run on the customer's machine or customer-controlled infrastructure, not on a shared CEM888 execution service. Clean installs start with clean identity, state, authority, configuration and credentials. Model access is bring-your-own-key.

## Repository scope

This repository is the **public engineering record** for the CEM888 runtime — architecture, honest status, and the evidence behind every claim. It is not the production-development authority, and the paid product is not distributed here.

**What is deliberately not here:** the runtime source, the agent system prompt and prompt stack, the action-authority implementation, the memory and indexing implementation, provider routing, the context/breathing cycle, credentials and auth internals, customer data and state, and per-file provenance. Those are proprietary; publishing them would hand over the engine without handing over the business. Third-party notices are preserved in **[licenses/third-party/MIT-NOTICE.txt](./licenses/third-party/MIT-NOTICE.txt)**.

### Documentation map

| Document | What it answers |
| --- | --- |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | How state, context compilation, authority and receipts work |
| [CAPABILITY_MATRIX.md](./docs/CAPABILITY_MATRIX.md) | What is implemented, certified, specified or planned |
| [ENFORCEMENT_MATRIX.md](./docs/ENFORCEMENT_MATRIX.md) | What can actually be blocked, per host, and what cannot |
| [HOST_ADAPTERS.md](./docs/HOST_ADAPTERS.md) | Claude Code, Codex, Cursor, Copilot — what each exposes |
| [INTEGRATION.md](./docs/INTEGRATION.md) · [INTEGRATION_RECIPES.md](./docs/INTEGRATION_RECIPES.md) | The contract, and worked recipes |
| [PUBLIC_CONFORMANCE.md](./docs/PUBLIC_CONFORMANCE.md) | The 15-check suite and how to read it |
| [STATUS.md](./docs/STATUS.md) | What is certified right now, including known defects |
| [FRESH_INSTALL_ACCEPTANCE_2026-10-01.md](./docs/FRESH_INSTALL_ACCEPTANCE_2026-10-01.md) | A full acceptance run, written up as it happened |

## License

**The published record in this repository** — documentation, matrices, case-study text — is licensed under the **[CEM888 Source-Available Commercial License](https://github.com/CEM888AI/cem888/blob/main/LICENSE)**: read it, audit it, cite it, quote it, fork it for personal non-commercial use. It **never converts** to an open-source licence.

**The runtime itself** is proprietary software distributed under that same licence: broad rights to use what you install, **free for personal, non-commercial use**, with commercial deployment, paid client work, embedding, resale, white-labeling, OEM distribution and hosted service requiring a valid CEM888 licence key for the applicable tier or a separate commercial licence from **CEM Unlimited LLC**.

| You want to… | Without a paid licence |
| --- | --- |
| Read, evaluate, test, or develop against the published record | Yes — no licence needed |
| Run CEM888 in production for yourself, personally | Yes — Free tier, personal and non-commercial |
| Use it in business production, or in paid client/consulting work | **No** — requires a licence key or commercial licence |
| Embed, resell, white-label, or OEM-distribute it | **No** — separate commercial licence |
| Provide it to third parties as a hosted or managed service | **No** — prohibited |
| Move, change, disable, or circumvent the licence-key functionality | **No** — prohibited |

Commercial licensing and tiers: [CEM888 Pro tiers — cem888.ai/workspace](https://cem888.ai/workspace) · [commercial licence, by enquiry — cem888.ai/enterprise.html](https://cem888.ai/enterprise.html)

**Release history — one licence, no exceptions.** Every version distributed on or after **2026-10-05** is licensed under the **[CEM888 Source-Available Commercial License](./LICENSE)**, and that is the only licence the Software has ever been distributed under. **What v1.0.3 actually was: the audit record.** Every release in this repository is the engineering record — documentation, installers, evidence and licence text — and no runtime engine source has ever been published here (all 52 commits since the repository's first commit contain documentation, install tooling and examples only). Earlier versions of this section named an open-source release of v1.0.3; that was wrong, is withdrawn, and grants nothing.

## Contributing · Security · Releases

Outside contributions require the **[Contributor License Agreement](./CLA.md)** before merge — see **[CONTRIBUTING.md](./CONTRIBUTING.md)**. Report vulnerabilities privately to **creator@cem888.ai**; scope and response targets in **[SECURITY.md](./SECURITY.md)**. Tagged releases with notes: **[Releases](https://github.com/CEM888AI/cem888/releases)** · **[CHANGELOG.md](./CHANGELOG.md)**.

## Enterprise direction

CEM888 is intended to mature into a reliability, continuity and control layer for AI in data-sensitive and high-consequence environments, including legal, financial, public-sector and regulated enterprise systems. That requires customer-controlled deployment, identity isolation, provenance, explicit authority, evidence-backed verification, restart/recovery continuity and clear trust boundaries. Sector-specific compliance is scoped with each customer, per deployment.

---

<div align="center">

**If this is the layer you've been missing, a star is how the next engineer finds it.**

Built and maintained by **Chandler Morone / CEM Unlimited LLC** · **[cem888.ai](https://cem888.ai)** · creator@cem888.ai

</div>
