# CEM888 Native Host Adapters

## Purpose

CEM888 can connect to an existing AI host without replacing that host's UI, model, planner, prompts, or tools.

The native-host adapter layer adds automatic CEM888 lifecycle participation around the host using the strongest supported combination of:

- host discovery
- local MCP registration
- lifecycle hooks / plugin events
- identity + tenant binding
- permission / scope checks
- verification + receipts
- durable CEM888 inhale / exhale

The existing provider-neutral CEM888 continuity runtime remains authoritative. Host adapters do not create provider-specific memory or state systems.

## Installer architecture

A standalone model/API provider is optional.

CEM888 may be installed first as the customer's local state, continuity, authority, verification, and integration runtime. The installer can then connect supported AI hosts before any standalone reasoning provider is configured.

Installer choices:

1. **Recommended standalone driver — DeepSeek Flash**
   - CEM888 is currently tuned and tested most heavily for DeepSeek Flash.
2. **Bring your own provider**
   - Choose a supported provider/model and configure credentials through the supported secret-entry path.
3. **Use existing AI apps**
   - No standalone model/API key is required.
   - Detect supported local hosts such as Claude Code and Codex.
   - Obtain explicit user approval before installing hooks/plugins or changing host configuration.
   - Configure the canonical CEM MCP + host lifecycle adapter.
   - Bind the host to the authenticated customer and selected CEM agent.
   - Run the host breathing conformance test before reporting READY.

The installer must perform this bootstrap deterministically. It must not require an already-reasoning CEM agent to connect the first host.

If the customer chooses no standalone driver, the installation is not READY until at least one connected host passes the strongest honest breathing certification the host allows.

A customer may add or change a standalone driver later without replacing CEM identity or state.

## Customer experience

Target experience:

```text
Install CEM888
  -> create/select CEM agent
  -> choose reasoning mode:
       DeepSeek Flash
       another provider
       existing AI apps only
  -> detect Claude Code / Codex / other supported hosts
  -> select hosts to connect
  -> CEM explains permissions
  -> user approves vendor login / hook / plugin / config changes
  -> installer configures supported integration surfaces
  -> installer runs breathing conformance checks
  -> integration reports FULL / PARTIAL / HOST-RESTRICTED
```

After setup, the customer continues using the host normally.

## Canonical lifecycle

Where the host exposes the required lifecycle seams:

```text
HOST TURN START
  -> resolve authenticated customer + selected CEM agent + project scope
  -> CEM inhale
  -> load authoritative current state
  -> compile bounded working context

HOST REASONING / TOOL USE
  -> before consequential action: CEM authority / scope gate
  -> provider action executes
  -> after action: capture observable result
  -> CEM verification + receipt

HOST TURN FINISH
  -> bounded state delta
  -> canonical CEM exhale exactly once
  -> durable checkpoint / current-state / index updates
```

Retries and replays must preserve stable external turn identity and cannot duplicate durable writes.

## Host-adapter contract

Every native AI-host adapter must provide, where the host permits:

1. **Detection** — determine whether the host is installed / available.
2. **Configuration** — register CEM MCP / plugin / hook surfaces idempotently.
3. **Identity binding** — bind the host connection to the authenticated customer and selected CEM agent.
4. **Lifecycle mapping** — map supported host events to the canonical CEM begin / action / finish lifecycle.
5. **Authority enforcement** — use pre-action hooks where the host exposes enforceable gates.
6. **Evidence capture** — record observable post-action results for verification.
7. **Exactly-once exhale** — commit durable changes through the existing CEM lifecycle once.
8. **Health** — report detected / configured / connected / degraded / revoked.
9. **Repair** — support safe reconnect, reinstall, upgrade, and revoke.
10. **Certification** — classify support only from measured evidence.

## Support classifications

- **CERTIFIED / FULL** — required lifecycle behavior is proven end to end.
- **PARTIAL** — useful integration exists but one or more lifecycle guarantees are missing.
- **HOST-RESTRICTED** — the host does not expose a required lifecycle surface.
- **BETA** — implementation exists but certification is incomplete.
- **COMING SOON** — planned but not implemented.

MCP connectivity alone is not sufficient for FULL certification.

A connected host cannot be treated as a substitute for the standalone CEM driver unless conformance proves the required inhale, identity binding, authority, verification, exactly-once exhale, retry/idempotency, and continuity behavior available on that host.

## First native AI-host adapters

### Claude Code

Target:

- detect installed Claude Code
- configure CEM MCP
- configure supported lifecycle hooks
- inhale authoritative CEM state before substantive work
- enforce CEM authority at available pre-tool boundaries
- capture observable post-tool evidence
- exhale bounded durable state exactly once
- prove fresh-session and cross-host continuity

Linear: CEM-255.

### Codex

Target:

- detect supported Codex surface
- configure CEM MCP / plugin package
- configure supported lifecycle hooks
- bind selected CEM agent
- automatic inhale / authority / verification / exhale
- prove fresh-session and cross-host continuity

Linear: CEM-256.

Installer integration is tracked by Linear CEM-258.

## Standing authorization

CEM888 must not create repetitive permission prompts for already-authorized work.

Once a user grants an integration/capability and agreed scope to a selected CEM agent, normal operation inside that standing authority should proceed automatically.

Ask again only when materially necessary, including:
- new or expanded scope/capability;
- different customer/account/agent binding;
- credential expiry or revocation;
- action outside the existing standing authority;
- a host/provider/OS security boundary that itself requires renewed consent.

Do not add CEM-specific approval prompts for routine continuity calls, inhale/exhale, normal tool use, or already-authorized host actions.

**Connect once. Authorize once for the agreed scope. Then work quietly until the scope or credential state changes.**

## Credential handling

CEM888 agents may accept API keys, tokens, and other user-provided integration credentials when that is the selected connection path.

Required behavior:
- accept the credential from the authenticated user;
- store/move it promptly into the approved local/customer secret store or broker;
- persist only a secret reference/handle in normal runtime state;
- do not unnecessarily echo the raw credential back;
- do not persist raw credentials in durable conversational memory, receipts, normal logs, public artifacts, Linear, Airtable, or cross-agent context;
- do not expose one customer's credential to another customer/agent;
- use the stored credential automatically afterward.

The security goal is secure custody and minimal exposure, not forbidding the agent from handling credentials.


## Owner prohibition authority

An explicit owner directive such as **no**, **do not**, **never use**, **stop**, or **block** is executable runtime authority, not advisory memory.

For every customer install:

- the prohibition is captured into the customer's canonical authoritative state with provenance;
- it becomes effective in the same turn;
- every protected action crossing a CEM-controlled boundary is checked before execution;
- a matching action is hard-blocked and the host receives a structured denial;
- the prohibition survives turns, sessions, restarts, model changes, and supported host changes;
- only an authenticated explicit owner unblock or scoped exception may override it;
- generic instructions such as "finish it", "go ahead", or "do what is necessary" do not revoke it;
- a one-use or task-scoped exception does not erase the standing prohibition;
- if prohibition authority cannot be loaded or evaluated, protected/consequential actions fail closed while conversation may continue and the agent may ask the owner.

Host adapters must consume this same provider-neutral authority. They must not maintain provider-specific prohibition state.

**The model can change. The app can change. The owner's NO does not.**

Hard enforcement can only be claimed for actions that actually cross an enforceable CEM boundary. If a host can perform an action entirely outside CEM and exposes no pre-action interception point, that capability must be classified honestly as PARTIAL or HOST-RESTRICTED rather than presented as FULL.

### Dual enforcement: current truth + action

A hard NO is not complete if CEM blocks execution but still gives the connected host the prohibited material as current working truth.

For every active prohibition:

- current-state compilation must exclude conflicting prohibited material from the authoritative working packet;
- historical/provenance access may retain that material only with explicit non-current status;
- semantic similarity, stale memory, old code, alternate wording, or another model/agent cannot promote it back to current authority;
- if the host proposes using/restoring/reintroducing/deploying/certifying the prohibited material through a CEM-controlled action boundary, CEM blocks before execution;
- only an authenticated owner allow-once, scoped exception, or unblock can change the constraint.

Host certification must prove **both halves**: the prohibited item is not surfaced as current truth and the prohibited action is refused.

This control model is part of CEM888's long-term direction toward high-consequence and data-sensitive environments such as legal, financial/banking, public-sector/government, security, and regulated enterprise systems. It is an architectural direction, not a claim of current sector certification.

## Security requirements

- explicit user approval for initial connection and any materially expanded scope where required
- user-provided credentials may be securely ingested and stored by the authorized CEM agent
- raw credentials should not persist in ordinary state, memory, receipts, logs, or cross-agent context
- fail closed on ambiguous customer / agent binding
- standing authorization for already-approved capabilities
- tenant isolation
- deterministic uninstall / revoke
- no provider-specific memory silo

## Architectural invariant

**Keep the agent. Add the reliability layer.**

The host remains the user's normal working surface. CEM888 remains the authoritative continuity, state, control, and verification layer around it.

## Release sequencing — DeepSeek first

The architecture above describes the intended installer end state. It is **not** the current release sequence.

Current owner-directed sequence:

1. **Phase 1 — DeepSeek Flash customer install only.** Finish, stabilize, and certify the existing DeepSeek path on the real customer artifact.
2. **External beta proof.** After internal PASS, Anna Rock and David test that exact DeepSeek customer path.
3. **Later — alternate standalone providers.** Add only after Phase 1 is proven.
4. **Later — existing AI hosts at install time.** Claude Code/Codex host attachment remains planned architecture and must not interrupt Phase 1.

Do not describe install-time Claude Code/Codex attachment as shipped until it has been implemented and certified. The immediate product goal is a reliable, testable DeepSeek-first installer.


## Integration priority map

Build order is based on **customer adoption x architectural depth**, not popularity alone.

### Phase 0 — current release
**DeepSeek Flash standalone customer install.** Finish and certify this before host-adapter expansion. After internal PASS, Anna Rock and David test the exact DeepSeek customer path.

### Tier 1 — first host adapters after DeepSeek
1. **Claude Code** — strongest near-term combination of adoption and lifecycle-hook depth. Target automatic inhale, current-state injection, standing authority, post-tool verification, and exactly-once exhale.
2. **Codex** — strong adoption, existing CEM MCP proof, and suitable plugin/MCP/lifecycle surfaces for a second reference implementation.

### Tier 2 — high-demand developer surfaces
3. **GitHub Copilot / VS Code** — broad installed base and enterprise reach. Build to the strongest lifecycle surface actually exposed; classify PARTIAL if MCP is the only reliable boundary.
4. **Cursor** — major developer surface with MCP support and programmatic registration. Verify event/lifecycle interception depth before claiming FULL.

### Tier 3 — architecture multipliers
5. **JetBrains** — strategic because one IDE family can host Claude Agent, Codex, GitHub Copilot and ACP-connected agents. Treat it as a multiplier surface.
6. **OpenCode** — smaller adoption but unusually deep plugin hooks around prompts, model context, tools, and MCP. Strong candidate for a FULL lifecycle reference if conformance passes.

### Tier 4 — research/next expansion
- Gemini CLI / Gemini Code Assist / Google Antigravity
- Windsurf
- Microsoft Copilot / Copilot Studio
- ChatGPT Work
- Claude app / desktop surfaces
- other ACP/MCP-capable hosts

Do not assume ordinary consumer chat surfaces expose enough lifecycle control for FULL CEM behavior.

### Proof requirement

For each Tier 1 host, compare **host alone vs the same host + CEM** on the same repo/task.

Measure:
- token/usage where observable;
- prompt/context size;
- repeated reads/searches;
- tool calls;
- retries;
- wall-clock time;
- fresh-session recovery;
- drift from the current objective/state;
- verified completion;
- stale/superseded-state mistakes.

No efficiency or savings claim until measured.
