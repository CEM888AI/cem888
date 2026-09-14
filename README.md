<div align="center">

# CEM888

### Tell your agents once.

*First public beta — September 2026*

**STATE decides what is true. MODELS decide what to do about it.**

[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue?style=flat-square)](#license)
[![MemoryAgentBench AR](https://img.shields.io/badge/MemoryAgentBench_AR-99.9%25-1f6feb?style=flat-square)](https://github.com/CEM888AI/benchmarks)
[![Local-first](https://img.shields.io/badge/local--first-your_machine-238636?style=flat-square)](https://cem888.ai)
[![Public beta](https://img.shields.io/badge/public_beta-v1.0.3-orange?style=flat-square)](#get-cem888)
[![Python](https://img.shields.io/badge/python-3.14-3776ab?style=flat-square)](#get-cem888)

**⭐ Star this repo** · **[⬇️ Install](#get-cem888)** · **[🚀 Hosted account](https://cem888.ai/register.html)** · **[💗 Sponsor](https://ko-fi.com/cem888ai)**

</div>

---

## Get CEM888

Two ways in. Both give you the same runtime.

### 1. Self-host — free, open source

Requires **CPython 3.14**.

```bash
git clone https://github.com/CEM888AI/cem888.git
cd cem888
pip install -e .
```

Point it at any provider — Claude, GPT, DeepSeek, Gemini, or a fully local model — using your own keys. Nothing phones home; no central server holds your state. No account required, ever.

### 2. Hosted account — managed, nothing to run

**→ [Create your account](https://cem888.ai/register.html)**

Same runtime, hosted and managed, if you'd rather not operate it yourself. Agents, memory and verification without standing up infrastructure.

---

Source provenance, including the rebuild digests, is in [PROVENANCE.md](./PROVENANCE.md).

**This is the first public release — a beta.** `v1.0.3`, AGPL-3.0, September 14 2026.

Expect rough edges: packaging is minimal, the API surface may change between
releases, and there is one maintainer. It runs, and the evidence below is real,
but don't put it under anything load-bearing yet without reading the code.

Bug reports are the most useful thing you can give me right now — [open an issue](https://github.com/CEM888AI/cem888/issues).

## The problem

Your agent forgets. Every new session starts blind. Switch models and the work resets. And when it reports "done," the only evidence you have is that it said so.

That happens because almost every agent framework lets the **model** hold the state — what happened, what's true now, whether the task finished. Models are stochastic and their context windows are finite. Putting the ledger inside them is the architectural mistake.

CEM888 takes it out. Identity, state, continuity, authority, retrieval, execution control, and verification live **outside** the model in a deterministic runtime. The model is called in to reason and act, and its output is checked against runtime state rather than trusted at face value. Swap Claude for GPT for DeepSeek for a fully local model mid-project — the agent keeps its state, its permissions, and its work.

It runs on your machine, against your own model keys. No central server holds your state.

## Where this sits

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

## Evidence

| Measurement | Result |
|---|---|
| MemoryAgentBench AR — live agent, no answer-key access | **99.9%** (1,998/2,000) · next-best published: **71.8%** · [raw data →](https://github.com/CEM888AI/benchmarks) |
| Runaway context from a backward-search anchoring bug | **207 messages → 1,010-token** bounded packet · [case study →](https://github.com/CEM888AI/runtime-case-studies/blob/main/case-study-context-window-bounding.md) |
| Workflow with tool-schema surface scoped per turn | **4 calls / 25.6s → 1 call / 15.7s**, from 84 tools (~29.3K schema tokens) · [case study →](https://github.com/CEM888AI/runtime-case-studies/blob/main/case-study-tool-schema-scoping.md) |

| | |
|---|---|
| **Benchmarks** — raw, reproducible, sourced | [CEM888AI/benchmarks](https://github.com/CEM888AI/benchmarks) |
| **Engineering case studies** — problem → root cause → fix → measurement | [CEM888AI/runtime-case-studies](https://github.com/CEM888AI/runtime-case-studies) |
| **Production reliability evidence** | [CEM888AI/agent-systems-lab](https://github.com/CEM888AI/agent-systems-lab) |
| **Architecture** | [architecture.md](https://github.com/CEM888AI/runtime-case-studies/blob/main/architecture.md) |
| **Terms, Privacy, EULA, IP** | [CEM888AI/legal](https://github.com/CEM888AI/legal) |

The case studies include the failures and root causes, not just the wins. Read those before trusting any of the numbers.

## License

**Community lane — AGPL-3.0.** Individuals, builders, startups, and companies may use and build on CEM888, including commercially, provided they comply with AGPL-3.0.

**Commercial lane — negotiated paid license.** Required to keep a CEM888-based implementation proprietary: embedding, white-labeling, reselling, redistributing, or offering it as part of a closed product or hosted service without AGPL obligations. The trigger is proprietary use or distribution that doesn't comply with AGPL — not company size.

→ **[creator@cem888.ai](mailto:creator@cem888.ai)**

## Enterprise

1. **Commercial licensing** — embed CEM888 in a proprietary product
2. **Private / on-prem integration** — CEM888 inside your environment, your models, your compliance boundary
3. **Custom builds** — agent runtimes for workloads where losing state, or trusting an unverified completion, is expensive

→ **[creator@cem888.ai](mailto:creator@cem888.ai)**

## Support this work

I'm Chandler Morone. I build CEM888 alone, and I paid for it myself.

My background isn't a CS degree — it's dressage, TIG welding, CNC programming, and reading blueprints against what metal actually does under heat. Work where a bad weld doesn't throw an exception; it fails in someone's hands. That's the mindset underneath this runtime: verify the claim, don't trust the report.

I sold my dressage horse to keep building. That funded the runtime. It doesn't fund what comes next.

Agent infrastructure is consolidating into a handful of clouds that own your state and your lock-in. Local-first is the alternative, and it needs to exist before that window closes.

→ **[Ko-fi](https://ko-fi.com/cem888ai)** · [One-time](https://donate.stripe.com/cNi28q5WA3l4bVQaqnfbq02) · [Monthly](https://donate.stripe.com/6oU14m3Os3l47FA41Zfbq03)

| Tier | Monthly | |
|---|---|---|
| **Supporter** | $5 | Name in SPONSORS.md — you keep the benchmarks running |
| **Backer** | $25 | Build log: what shipped, what broke, what it cost |
| **Believer** | $100 | Early access to releases |
| **Company** | $500 | Logo here and on cem888.ai |

Sponsorship pays for model API and compute on the benchmark suite, packaging and security review, and hours on the runtime instead of contract work.

**Sponsorship is not a commercial license.** It purchases no license, no support agreement, and no equity. Commercial licensing is a separate conversation — [creator@cem888.ai](mailto:creator@cem888.ai).

---

<div align="center">

**[cem888.ai](https://cem888.ai)** · [creator@cem888.ai](mailto:creator@cem888.ai) · [LinkedIn](https://linkedin.com/in/chandler-morone-a8010174)

**⭐ Star this repo** — that's what gets CEM888 in front of the next person.

</div>
