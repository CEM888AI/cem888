# CEM888 Architecture

> **STATE decides what is true. MODELS decide what to do about it.**

CEM888 is a local-first **state and control runtime underneath AI agents**. It exists because a model can reason well and still fail at the system responsibilities that long-running agents need most: maintaining current truth, preserving owner authority, carrying only the right working state, surviving retries and restarts, and proving what actually happened after an action.

CEM888 moves those responsibilities out of prompt prose and into runtime machinery.

The result is not a larger prompt and not a memory wrapper. It is a control layer that keeps the agent oriented while the model remains replaceable intelligence.

---

## Evidence boundary

This document separates three surfaces deliberately:

- **Public source** — the inspectable implementation and public falsifiers in this repository.
- **CEM engineering runtime** — the live ancestor/runtime on which product mechanisms are exercised, falsified and hardened.
- **Customer artifact** — the exact wheel and platform bundles delivered to a customer; these are promoted and re-proven as release artifacts rather than assumed equivalent to the engineering runtime.

That separation is a release discipline, not an architectural caveat. The architecture is already operating on the engineering runtime. Customer release proof is the final artifact-specific step.

### Current evidence snapshot

| Surface | Current evidence |
| --- | --- |
| Public conformance | **12 tests across 4 invariants — 12 / 12 pass** |
| Independent runtime evaluation | **9 / 9 pass** |
| CEM owner-prohibition / authority path | **8 / 8 pass** |
| CEM structured verification | **53 / 53 pass** |
| Hook/source synchronization falsifiers | **17 / 17 pass** |
| Fabricated-evidence falsifier | **4 / 4 pass** |
| Cross-process store locking | **4 / 4 pass** |
| Current release train | **12 / 12 release gates green** |

The deliberately preserved **2 PASS / 9 FAIL** result belongs to an earlier non-conformant customer artifact. It is retained as a falsification artifact — proof that the harness can reject a build — and is not the status of the current CEM engineering runtime.

Public evidence: [Technical status](./STATUS.md) · [Public conformance](./PUBLIC_CONFORMANCE.md) · [Independent runtime evaluation](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation) · [Current engineering status](https://github.com/CEM888AI/runtime-case-studies/blob/main/current-engineering-status.md)

---

# 1. The runtime loop

A CEM888 turn is a state transition, not a transcript append.

```text
INPUT / OWNER STEERING
        |
        v
RESOLVE IDENTITY + AUTHORITY
        |
        v
LOAD CURRENT AUTHORITATIVE STATE
        |
        v
RETRIEVE CANDIDATES
        |
        v
RECONCILE AUTHORITY + SUPERSESSION
        |
        v
COMPILE BOUNDED WORKING CONTEXT
        |
        v
MODEL REASONS / PROPOSES ACTION
        |
        v
RUNTIME AUTHORIZES OR BLOCKS
        |
        v
TOOL EXECUTES
        |
        v
OBSERVE POSTCONDITION
        |
        v
VERIFY WHAT ACTUALLY HAPPENED
        |
        v
COMMIT STATE + RECEIPT
        |
        +-----------------------> NEXT TURN
```

The model contributes intelligence where intelligence is useful: ambiguity, planning, synthesis, semantic judgment and novel reasoning.

The runtime owns the parts that should not depend on model confidence:

- identity;
- current state;
- supersession;
- authority;
- working-context budgets;
- duplicate protection;
- lifecycle state;
- verification state;
- receipts and provenance.

A shorter formulation is:

> **MODELS PROPOSE. STATE RESOLVES. RUNTIME AUTHORIZES. TOOLS EXECUTE. VERIFIER PROVES.**

---

# 2. Current truth is typed state, not conversation history

**Public implementation:** `src/tools/memory_tool.py`

CEM888 stores durable state in SQLite under the agent profile rather than treating the conversation transcript as the source of truth.

Each typed record carries identity, scope, authority, provenance, lifecycle and verification metadata.

| Field family | What it answers |
| --- | --- |
| identity + hash | What exact object is this? |
| type + scope + agent/project/task | What kind of state is it, and whose? |
| authority + source + provenance | Who asserted it and where did it come from? |
| lifecycle status | Is it current, superseded, archived or failed? |
| verification status | What evidence state does it have? |
| supersedes / superseded_by | What replaced what? |
| timestamps | When was the transition recorded? |

### Supersession is explicit

When Decision B replaces Decision A, A is not deleted and B is not merely appended beside it.

The lifecycle transition records that B supersedes A. A remains available as history but stops being eligible as current truth.

The current-state read rule is explicit:

```sql
WHERE lifecycle_status = 'active'
  AND superseded_by IS NULL
```

That gives CEM888 a property ordinary transcript retrieval does not have:

> **Relevance can retrieve a candidate. Relevance does not increase its authority.**

A stale decision can remain highly similar to the current query without being allowed to become current again.

### Idempotent durable writes

Durable writes use stable content identity so retries do not silently create a second fact. If the same durable object already exists, the runtime returns the existing identity rather than duplicating state.

Fresh-store concurrency has also been exercised specifically because “works after warmup” is not sufficient evidence for a durable state layer. The current engineering path includes bounded retry and duplicate-race handling so an already-written object is recognized as the same durable effect instead of being reported as a mysterious failure.

---

# 3. The working context is compiled, not accumulated

**Public implementation:** `src/agent/context_compiler.py`

The model does not need the entire conversation in order to continue correctly.

Before reasoning, CEM888 builds a bounded packet from the smallest currently useful set of state:

- active objective;
- current decisions;
- active constraints;
- unresolved blockers;
- pending verification;
- recent verified progress;
- relevant durable memory;
- identity / relationship invariants;
- compact evidence references.

Resolved, archived, superseded and irrelevant material is not allowed to consume ordinary working-context budget merely because it appeared earlier.

### Deterministic selection before lossy compression

The ordering is important:

1. determine which objects are still current;
2. exclude lifecycle-ineligible state;
3. score the eligible candidates for the present task;
4. fit the required state inside a bounded packet;
5. only then shorten surviving narrative text if necessary.

The runtime never uses a lossy summary as the authority for exact IDs, paths, decisions, states, verification obligations or owner constraints.

### Long-horizon acceptance

The working-state compiler has been exercised over a **60-turn long-horizon fixture** and a real engineering task.

The acceptance work checks that:

- working state stays inside its configured budget;
- context does not grow monotonically with turn count;
- resolved work leaves active carry;
- superseded decisions stop being current;
- pending verification remains until evidence closes it;
- raw tool output does not ride indefinitely;
- fresh sessions reconstruct objective and current state;
- historical detail remains retrievable;
- mandatory carry fields are not silently lost;
- per-turn receipts explain what was retained or removed.

This is the mechanism behind the intended user experience: long-running work can continue for hours without requiring the agent to drag an ever-growing transcript behind it.

**Conversation history becomes disposable working material. Authoritative state does not.**

---

# 4. Tier-0 authority is outside model control

**Public implementation:** `src/agent/authority.py`

The Tier-0 manifest, `authority.json`, defines the agent's identity, profile binding and protected/allowed/forbidden write roots.

Prompts and memories can describe authority. They do not grant it.

The running model is explicitly prevented from directly rewriting its own Tier-0 manifest.

### File writes

`AgentAuthority.write_denial()` evaluates the target before a protected write:

1. the Tier-0 manifest itself is immutable to the running agent;
2. forbidden roots are denied;
3. protected roots require standing allowed scope;
4. an unresolved authority state is not treated as permission.

### Shell / terminal actions

`AgentAuthority.command_denial()` runs before ordinary dangerous-command approval and is not bypassed by a model simply setting a force flag.

Mutating operations are checked against resolved paths and protected roots before execution.

The architectural boundary is intentional:

- **CEM semantic authority** decides whether the agent has permission for an operation and target.
- **OS controls** such as service users, filesystem permissions or containers can be layered beneath it when a deployment requires stronger process isolation.

Those are complementary layers, not competing implementations.

---

# 5. Owner prohibitions become executable authority

The engineering runtime extends ordinary write-root authority with a stronger rule:

> **The model can change. The app can change. The owner's NO does not.**

An explicit owner prohibition is not intended to survive merely as prose in memory.

The runtime model separates two representations:

1. **Owner-stated record** — the owner's original words and provenance.
2. **Compiled enforcement entry** — normalized operation, target, effect and scope used by the gate.

This matters because the same prohibited intent can arrive through a shell command, API call, script or renamed tool. The enforcement key is the normalized operation and target, not a particular tool name.

The owner-prohibition path is currently exercised on the CEM engineering runtime with **8 / 8 passing falsifiers**.

The full contract is dual-sided:

- **retrieval side:** prohibited or superseded material must not return to the model as current authoritative truth;
- **execution side:** a matching protected action is blocked before execution at a CEM-controlled boundary.

A control is not complete if it performs only one half.

---

# 6. Authority can expand without making the model sovereign

A useful agent eventually needs new legitimate write scope. The safe answer is not to make `authority.json` model-writable.

The engineering design uses a **propose → owner approve → deterministic apply** split:

```text
agent proposal
    |
    v
pending authority request
    |
    v
OWNER-CONTROLLED APPROVAL SURFACE
    |
    v
deterministic validation
    |
    v
atomic Tier-0 update
    |
    v
revision bump + audit receipt
```

The model may propose a new root and explain why it needs it. Proposal alone grants nothing.

The applier validates the requested target and produces an auditable state transition. The model never acquires the ability to silently rewrite the authority boundary that constrains it.

This preserves a clean invariant:

> **The agent can ask for more authority. It cannot grant itself more authority.**

---

# 7. Verification is evidence-backed, not prose-backed

CEM888 does not treat “done” as proof.

A consequential action creates a verification obligation. Where the postcondition is observable, completion is established from runtime-observed evidence rather than from the model's narration of success.

The current CEM engineering path includes:

- **53 / 53 structured-verification checks passing**;
- **4 / 4 fabricated-evidence falsifiers passing**;
- explicit rejection of caller/model-supplied output as self-proving evidence;
- receipt tracking for what was checked and what observation supported the result.

This is one of the core separations in the architecture:

```text
MODEL CLAIM:   "I changed the file."
                         |
                         v
RUNTIME:       What observable postcondition would make that true?
                         |
                         v
VERIFIER:      Read / inspect / compare the actual target.
                         |
                 +-------+-------+
                 |               |
                 v               v
             PROVEN          UNPROVEN
```

The verifier is allowed to say **UNPROVEN**. That is a feature.

A system that cannot refuse its own completion claim cannot reliably distinguish work from narration.

---

# 8. Receipts make state transitions inspectable

Every compiled context emits a receipt atomically to:

`state/context_receipts/latest.json`

The receipt records why a given reasoning event saw what it saw.

Representative fields include:

| Field | Purpose |
| --- | --- |
| `context_packet_id` | Stable identity for the compiled packet |
| `selected` / `selected_types` | What entered working context |
| `excluded` | What did not |
| `selection` | Per-candidate decision and reason |
| `section_tokens` / `packet_tokens` | Working-context cost |
| `recent_message_count` | How much transcript was carried |
| `query_sha256` | Query identity without storing raw query text |
| `provider` / `model` | Which reasoning engine received the packet |

Receipts answer questions such as:

- Why did the model receive this state?
- Why was another item excluded?
- Which decision was current?
- What evidence closed a verification obligation?
- Which runtime version or model was involved?

A receipt is provenance. A falsifier is what establishes the behavior being claimed.

---

# 9. Retries are part of the architecture

A durable agent cannot assume each request arrives exactly once.

Networks retry. Processes restart. Users repeat instructions. Tool calls time out after the effect has already happened.

CEM888 therefore treats duplicate control as a state problem rather than a prompt-writing problem.

For durable state:

- identical writes resolve to the existing durable object;
- supersession transitions are explicit;
- concurrency is tested against fresh stores rather than only warm steady state;
- race outcomes distinguish “already succeeded” from “failed.”

The objective is **effect identity**, not merely call identity.

That distinction becomes especially important in financial, legal, operational and other consequential systems where “the API was called once” is weaker than “the intended durable effect exists exactly once.”

---

# 10. Local-first execution and trust boundaries

Customer agents run on the customer's machine or customer-controlled infrastructure.

CEM888's website can distribute installers and updates, but it is not the central runtime execution path for the customer's agent.

That means the customer can retain local custody of:

- runtime state;
- durable memory;
- credentials;
- authority;
- receipts;
- model choice;
- connected data.

The model itself can be changed without changing the identity of the state/control layer.

That is the practical meaning of:

> **Models are replaceable intelligence. State is the durable operating system around them.**

---

# 11. Integration does not require replacing the partner's agent

CEM888 is designed to attach at lifecycle seams.

```text
TURN START
    resolve identity / task
    load current state
    compile bounded context

BEFORE CONSEQUENTIAL ACTION
    normalize operation / target
    resolve authority
    authorize or block

AFTER EXECUTION
    observe the postcondition
    verify the supported claim

TURN FINISH
    commit resulting state
    emit checkpoint / receipt
```

A partner can keep its own:

- UI;
- planner;
- models;
- domain workflow;
- tools;
- observability;
- proprietary business logic.

CEM888 adds the state/control contract around those systems.

The strength of action enforcement depends on the actual host seam. A native blocking hook, CEM-controlled execution path and context-only connector expose different control surfaces. The public classification is documented in the [Enforcement Matrix](./ENFORCEMENT_MATRIX.md).

---

# 12. Why the architecture is useful in serious environments

The important enterprise property is not that the agent sounds consistent.

It is that critical responsibilities have identifiable owners:

| Responsibility | Owner |
| --- | --- |
| semantic reasoning | model |
| current truth | state lifecycle |
| permissions | runtime authority |
| owner prohibitions | owner-stated authority + compiled gate |
| context selection | runtime compiler |
| retry identity | durable state machinery |
| outcome truth | observable verification |
| auditability | receipts / provenance |
| process confinement | deployment / OS controls |

That division is useful wherever an organization needs to answer:

- What did the agent believe was current?
- Who had authority to change it?
- What was the agent permitted to do?
- What did it actually do?
- What evidence supports the completion claim?
- What survives if the model, process or host changes?

CEM888 is being developed for exactly that class of long-running, data-sensitive and high-consequence agent system, including legal, financial, public-sector and regulated enterprise deployments. Sector-specific compliance remains deployment-specific; the runtime supplies the underlying state, authority, provenance and verification machinery those deployments need to reason about explicitly.

---

# 13. Public conformance

The public conformance suite currently contains **12 tests covering four invariants**:

1. Tier-0 authority;
2. authority-aware current-state retrieval;
3. bounded-context receipt provenance;
4. supersession lifecycle.

Run it from source:

```bash
python3.14 -m pip install pytest pyyaml
PYTHONPATH=src python3.14 -m pytest -q tests
```

The distinction is intentional:

> **4 invariants. 12 executable tests. 12 / 12 passing.**

See [PUBLIC_CONFORMANCE.md](./PUBLIC_CONFORMANCE.md).

---

# 14. What to inspect next

For a technical review:

1. **This document** — the architecture and the current proof boundary.
2. **[PUBLIC_CONFORMANCE.md](./PUBLIC_CONFORMANCE.md)** — runnable public falsifiers.
3. **[STATUS.md](./STATUS.md)** — artifact/release status.
4. **[ENFORCEMENT_MATRIX.md](./ENFORCEMENT_MATRIX.md)** — what can be hard-blocked at different host boundaries.
5. **[Current Engineering Status](https://github.com/CEM888AI/runtime-case-studies/blob/main/current-engineering-status.md)** — live engineering evidence and release progression.
6. **[Independent Runtime Evaluation](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation)** — 9 / 9 external evaluation artifact.
7. **[Benchmarks](https://github.com/CEM888AI/benchmarks)** — published benchmark evidence.

---

## The architectural thesis

Most agent failures that matter over long periods are not failures of language generation.

They are failures of **state, authority, lifecycle, retry handling, context discipline and evidence**.

Those responsibilities do not become reliable merely because a larger model is placed in front of them.

CEM888 makes them runtime responsibilities.

> **STATE decides what is true. MODELS decide what to do about it.**
