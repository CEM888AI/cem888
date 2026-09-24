# CEM888 Native Host Adapters

> **Roadmap status:** native third-party host adapters are not the current release lane. The immediate product objective is the DeepSeek Flash customer install. Claude Code and Codex are the first planned deep adapters after that artifact passes internal certification and external beta testing.

## Purpose

CEM888 is designed to connect to an existing AI host without replacing that host's UI, model, planner, prompts or tools.

A native adapter should add the strongest lifecycle participation the host actually permits:

- host discovery;
- local MCP / supported registration;
- lifecycle hooks or plugin events;
- customer + agent identity binding;
- current-state/context supply;
- pre-action scope/authority checks where enforceable;
- post-action evidence capture where observable;
- durable state commit / continuity;
- integration health and revoke/repair behavior.

MCP connectivity alone is **not** sufficient to claim full CEM behavior.

## Two separate classifications

Public host support uses two axes so "how much can CEM control?" is not confused with "how mature is the integration?"

### Enforcement class

- **ENFORCED** — the claimed action crosses a CEM-controlled boundary and can be blocked before execution.
- **HOOK-GATED** — the host exposes a blocking lifecycle hook that can enforce the claimed action class; certification must prove the hook is live and define its bypass boundary.
- **MEDIATED-ONLY** — CEM can control actions routed through CEM, but host-native tools or other connectors outside that path are not governed by the CEM gate.
- **ADVISORY** — CEM can supply state/context or warnings but cannot hard-block the host action.

### Maturity

- **CERTIFIED** — the declared lifecycle/enforcement behavior has passed the host-specific conformance suite.
- **BETA** — implementation exists, but certification is incomplete.
- **PLANNED** — roadmap work; not shipped.
- **HOST-RESTRICTED** — the host does not expose a lifecycle surface required for the stronger claim.

A host can therefore be, for example, **MEDIATED-ONLY + CERTIFIED** or **HOOK-GATED + BETA**. The labels answer different questions.

## Canonical target lifecycle

Where the host exposes the required seams:

```text
HOST TURN START
  -> resolve customer + selected CEM agent + task/project scope
  -> load current authoritative state
  -> compile bounded working context

HOST TOOL / ACTION
  -> pre-action authority check at available boundary
  -> host/tool executes
  -> capture observable postcondition
  -> verification / receipt

HOST TURN FINISH
  -> bounded state delta
  -> durable checkpoint / state commit
```

Retries/replays must not duplicate durable state or consequential effects.

## Current roadmap

| Surface | Enforcement class | Maturity | Public claim |
| --- | --- | --- | --- |
| **DeepSeek Flash standalone customer path** | CEM-controlled execution boundary | **Certification in progress** | Current release lane |
| **Claude Code native adapter** | To be measured from supported hooks | **PLANNED** | No full-control claim until conformance |
| **Codex native adapter** | To be measured from supported plugin/hook/MCP surfaces | **PLANNED** | No full-control claim until conformance |
| **MCP-only host integration** | MEDIATED-ONLY by default | Host-specific | CEM does not control unrelated native tools |
| **Context-only integration** | ADVISORY | Host-specific | No hard action-enforcement claim |

## Host-adapter acceptance contract

A serious native adapter should prove, where the host permits:

1. **Detection** — host availability is discovered deterministically.
2. **Configuration** — supported integration surfaces are registered idempotently.
3. **Identity binding** — the connection is bound to the correct customer + CEM agent.
4. **Lifecycle mapping** — host events map to the CEM begin/action/finish contract.
5. **Authority behavior** — claimed protected actions produce a measurable block when denied.
6. **Evidence capture** — the verifier receives runtime-observable postconditions rather than model narration.
7. **Retry/idempotency behavior** — repeated delivery does not duplicate durable effects.
8. **Continuity** — a fresh session can recover current state.
9. **Health + repair** — connected/degraded/revoked states are visible and recoverable.
10. **Honest classification** — unsupported lifecycle surfaces remain explicitly limited.

## Standing authorization

CEM888 should not add approval noise to normal work that is already inside a user's granted scope.

The target behavior is:

> **Connect once. Authorize once for the agreed scope. Ask again only when the scope, identity or credential state materially changes.**

Host/provider/OS consent requirements still apply.

## Credential handling

Where an integration uses a user-supplied API key/token, the target contract is secure custody and minimal exposure:

- accept it from the authenticated user;
- move/store it promptly in the approved customer-local secret path;
- persist a secret reference rather than raw credential in normal runtime state;
- avoid echoing or logging the raw secret;
- prevent cross-customer/agent exposure.

## Owner prohibitions

The dual owner-prohibition contract applies only to the enforcement surface a host actually exposes.

A native-host certification cannot claim a hard NO unless it proves both:

- conflicting prohibited material is not promoted as current authoritative working state; and
- matching protected actions are refused at the claimed pre-action boundary.

See **[ENFORCEMENT_MATRIX.md](./ENFORCEMENT_MATRIX.md)**.

## Release sequencing

1. **Now:** finish and certify the DeepSeek Flash customer artifact.
2. **Then:** capture external beta evidence on that exact customer path.
3. **Next:** expand alternate standalone providers from measured demand.
4. **After the release gate:** implement and certify native existing-host adapters.

No native-host integration should be advertised as shipped merely because an MCP server can connect.

## Proof standard

For every supported host, the comparison should use the same representative task and repository and measure what is actually observable:

- token/usage where available;
- prompt/context size;
- repeated reads/searches;
- tool calls;
- retries;
- wall-clock time;
- fresh-session recovery;
- stale/superseded-state mistakes;
- verified completion;
- human intervention.

No savings or reliability percentage should be promoted until measured on the named host and artifact.
