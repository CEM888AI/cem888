<!--
FLAGSHIP README — DRAFT. Rename to README.md when this repo goes public.
Every <!-- CONFIRM --> marker is a fact I could not verify. Fill before publishing.
Nothing in this file claims traction, users, customers, or adoption that does not exist.
-->

<div align="center">

# CEM888

### Tell your agents once.

**STATE decides what is true. MODELS decide what to do about it.**

[![Stars](https://img.shields.io/github/stars/CEM888AI/cem888?style=social)](https://github.com/CEM888AI/cem888)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](./LICENSE)
[![MemoryAgentBench AR](https://img.shields.io/badge/MemoryAgentBench_AR-99.9%25-1f6feb?style=flat-square)](https://github.com/CEM888AI/benchmarks)
[![Local-first](https://img.shields.io/badge/local--first-your_machine-238636?style=flat-square)](https://cem888.ai)

<!-- HERO GIF GOES HERE — 10-15s: agent resumes work across a session boundary AND a model swap.
     This is the single highest-converting asset on the page. Do not publish without it. -->
![CEM888 in action](docs/media/hero.gif)

**[Quick start](#quick-start) · [Why](#the-problem) · [Proof](#proof) · [Compare](#where-this-sits) · [Sponsor](#support-this-work) · [Enterprise](#commercial-and-enterprise)**

</div>

---

## The problem

Your agent forgets. Every new session starts blind. Switch models and the work resets. And when it reports "done," the only evidence you have is that it said so.

That happens because almost every agent framework lets the **model** hold the state — what happened, what's true now, whether the task finished. Models are stochastic and their context windows are finite. Putting the ledger inside them is the architectural mistake.

CEM888 takes it out.

Identity, state, continuity, authority, retrieval, execution control, and verification live **outside** the model in a deterministic runtime. The model is called in to reason and act. Its output is checked against runtime state, not trusted at face value. Swap Claude for GPT for DeepSeek for a fully local model mid-project — the agent keeps its state, its permissions, and its work.

It runs on your machine, against your own model keys. No central server holds your state.

## Quick start

<!-- CONFIRM: exact install + run commands on a clean machine before publishing.
     If this takes more than 3 steps, the funnel leaks here. -->

```bash
# 1. Install
<!-- CONFIRM -->

# 2. Point it at a model (any provider, or fully local)
<!-- CONFIRM -->

# 3. Run
<!-- CONFIRM -->
```

Then close the terminal, reopen it tomorrow, and pick up where you left off. That's the whole demo.

## Where this sits

Agent memory is a crowded space, and most of it solves a different problem.

| | What it does | Who holds authority | Runs where |
|---|---|---|---|
| **Memory layers** (Mem0, Zep, Graphiti) | Store and retrieve facts for the model | The model | Cloud-managed, self-host option |
| **Stateful runtimes** (Letta / MemGPT) | Model self-edits tiered memory blocks | The model | Cloud-managed, self-host option |
| **CEM888** | Runtime owns state, governs tool access, verifies completion against evidence | **The runtime** | **Local-first, your keys** |

Memory is necessary and not sufficient. An agent that remembers perfectly can still call the wrong tool, exceed its scope, or report a task complete that never ran. CEM888 treats state, authority, and verification as one control layer.

## How it works

- **Deterministic state authority** — a runtime-owned record of what's true, independent of any model's context window
- **Minimal Sufficient Context compilation** — a small bounded packet compiled per turn, instead of replaying growing history into the model
- **Tool governance** — the model *proposes* actions; a separate authority layer decides whether they run, and at what scope
- **Verification receipts** — "done" is checked against evidence: file diffs, executed commands, recorded state changes
- **Provider-neutral execution** — same runtime behind Claude, GPT, DeepSeek, Gemini, or local. Swapping the model doesn't reset the agent
- **Failure containment** — retries, duplicate completions, and exactly-once semantics handled as a lifecycle problem, not left to model discretion

<!-- 5-7 FUNCTIONAL GIFs, one per capability. Highest priority three:
     1. Verification receipt catching a false completion claim
     2. Model swap mid-task, state intact
     3. Tool governance blocking an out-of-scope call -->

Full architecture → [runtime-case-studies/architecture.md](https://github.com/CEM888AI/runtime-case-studies/blob/main/architecture.md)

## Proof

| Measurement | Result |
|---|---|
| MemoryAgentBench AR — live agent, no answer-key access | **99.9%** (1,998/2,000) · next-best published: **71.8%** · [raw data →](https://github.com/CEM888AI/benchmarks) |
| Runaway context from a backward-search anchoring bug | **207 messages → 1,010-token** bounded packet · [case study →](https://github.com/CEM888AI/runtime-case-studies/blob/main/case-study-context-window-bounding.md) |
| Workflow with tool-schema surface scoped per turn | **4 calls / 25.6s → 1 call / 15.7s**, from 84 tools (~29.3K schema tokens) · [case study →](https://github.com/CEM888AI/runtime-case-studies/blob/main/case-study-tool-schema-scoping.md) |

Every number links to raw, reproducible data. The case studies include the failures and root causes, not just the wins — [read them](https://github.com/CEM888AI/runtime-case-studies) before you trust any of it.

## License

**Community runtime: AGPL-3.0.** Free, and staying free. Use it, fork it, run it, build on it.

**Commercial license:** required to embed CEM888 in a proprietary product without AGPL obligations. → [creator@cem888.ai](mailto:creator@cem888.ai)

<!-- CONFIRM: LICENSE file in this repo matches AGPL-3.0 and the legal repo no longer says ALL RIGHTS RESERVED. -->

## Commercial and enterprise

Three things I do commercially:

1. **Commercial licensing** — embed CEM888 in a proprietary product
2. **Private/on-prem integration** — CEM888 inside your environment, your models, your compliance boundary
3. **Custom builds** — agent runtimes for workloads where losing state or trusting an unverified completion is expensive

→ **[creator@cem888.ai](mailto:creator@cem888.ai)**

## Support this work

I'm Chandler Morone. I build CEM888 alone, and I paid for it myself.

My background isn't a CS degree — it's dressage, TIG welding, CNC programming, and reading blueprints against what metal actually does under heat. Work where a bad weld doesn't throw an exception; it fails in someone's hands. That's the mindset underneath this runtime: verify the claim, don't trust the report.

I sold my dressage horse to keep building. That funded the runtime. It doesn't fund what comes next.

Agent infrastructure is consolidating into a handful of clouds that own your state and your lock-in. Local-first is the alternative, and it needs to exist before that window closes. **Sponsoring keeps this independent and keeps the community runtime free.**

→ **[Ko-fi](https://ko-fi.com/cem888ai)** · [One-time](https://donate.stripe.com/cNi28q5WA3l4bVQaqnfbq02) · [Monthly](https://donate.stripe.com/6oU14m3Os3l47FA41Zfbq03)

| Tier | Monthly | |
|---|---|---|
| **Supporter** | $5 | Name in SPONSORS.md — you keep the benchmarks running |
| **Backer** | $25 | Build log: what shipped, what broke, what it cost |
| **Believer** | $100 | Early access to releases |
| **Company** | $500 | Logo here and on cem888.ai |

Sponsorship pays for model API and compute on the benchmark suite, packaging and security review for releases, and hours on the runtime instead of contract work.

## Contributing

<!-- CONFIRM: CLA Assistant configured before accepting the first external PR.
     CLA (not DCO) preserves the ability to dual-license. -->

Issues and PRs welcome. Start with [good first issue](https://github.com/CEM888AI/cem888/labels/good%20first%20issue).

## More

| | |
|---|---|
| Benchmarks — raw, reproducible, sourced | [CEM888AI/benchmarks](https://github.com/CEM888AI/benchmarks) |
| Engineering case studies | [CEM888AI/runtime-case-studies](https://github.com/CEM888AI/runtime-case-studies) |
| Reliability evidence from production runs | [CEM888AI/agent-systems-lab](https://github.com/CEM888AI/agent-systems-lab) |
| Terms, Privacy, EULA, IP | [CEM888AI/legal](https://github.com/CEM888AI/legal) |

---

<div align="center">

**[cem888.ai](https://cem888.ai)** · [creator@cem888.ai](mailto:creator@cem888.ai) · [LinkedIn](https://linkedin.com/in/chandler-morone-a8010174)

If CEM888 is useful to you, **star it** — that's what gets it in front of the next person.

</div>
