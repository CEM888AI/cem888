# CEM888 Integration Contract

CEM888 is intended to sit underneath or beside an existing agent without requiring the partner to rewrite the agent's business logic.

> **Status note:** this document defines the public lifecycle/control contract. Some mechanisms are implemented on the CEM engineering path; some controls are still being hardened; native third-party host adapters are planned after the current DeepSeek-first customer release gate. A documented contract is not automatically a customer-certified capability.

## Canonical lifecycle seams

### 1. Turn start

The host provides the principal / agent / task identity needed to resolve current runtime state.

CEM888 supplies the current authoritative working state and bounded context required for the turn.

### 2. Before consequential action

The proposed action and target enter the CEM authority boundary **where the integration exposes an enforceable pre-action seam**.

The runtime resolves scope and permission before execution.

### 3. After execution

Observable execution evidence is returned to the verification boundary.

The verifier evaluates only what the available postcondition evidence supports.

### 4. Turn finish / checkpoint

The resulting state transition, checkpoint and receipt are committed to durable state.

## Conceptual flow

```text
TURN START
  -> resolve identity / task
  -> load authoritative state
  -> compile bounded context
  -> model reasons / proposes
  -> runtime authorizes where enforceable
  -> tool executes
  -> runtime observes evidence
  -> runtime verifies what evidence supports
  -> state transition / receipt
```

## Enforcement boundary

CEM888 can only claim a hard block for actions that actually cross a CEM-controlled or host-enforceable boundary.

A host may expose:

- a blocking pre-action hook;
- only CEM/MCP-mediated actions;
- context/retrieval integration without action interception;
- no useful enforcement seam at all.

Those are materially different integration classes.

See **[ENFORCEMENT_MATRIX.md](./ENFORCEMENT_MATRIX.md)** for the public classification model.

## Owner prohibition authority

### Specified control contract — customer certification pending

The intended owner-prohibition contract is:

```text
OWNER: "do not / never / stop / block X"
  -> canonical customer-owned prohibition state
  -> active current constraint
  -> protected action proposed
  -> prohibition check at an enforceable boundary
  -> block before execution
  -> structured denial / owner recovery path
```

A standing prohibition is intended to survive turns, sessions, restarts, model changes and supported host changes until the authenticated owner explicitly revokes it or grants a narrower exception.

Generic model reasoning, stale history, another agent, tool output or a broad instruction such as "finish it" must not silently widen that authority.

### Dual proof requirement

A hard-NO claim is incomplete if CEM blocks execution but still promotes conflicting material back into the model's current authoritative packet.

Certification therefore requires **both**:

1. **current-truth falsifier** — prohibited/conflicting material is not promoted as current authoritative working state; and
2. **action falsifier** — a matching protected action is refused before execution at the claimed enforcement boundary.

Historical/provenance access may retain superseded material with explicit non-current status.

This dual prohibition control is **specified**, but it must not be represented as customer-certified end to end until both falsifiers pass on the exact installed artifact.

## Partner responsibility split

A partner can continue to own:

- UI and user experience;
- planner;
- agent logic;
- model/provider selection;
- tool implementations;
- observability;
- domain workflow;
- proprietary business logic.

CEM888 provides the state/control lifecycle boundary around those systems.

## Integration principle

The model is replaceable intelligence.

Authoritative state, action scope, continuity and verification are runtime responsibilities **to the extent the integration surface actually exposes those controls**.

## First evaluation

A useful technical pilot should answer:

1. What system owns current authoritative state?
2. What lifecycle boundary can CEM observe or block?
3. Which host-native actions bypass CEM entirely?
4. What postcondition evidence is observable?
5. How are retries prevented from duplicating durable effects?
6. What survives a fresh session or host restart?
7. Which claims are ENFORCED, MEDIATED-ONLY or ADVISORY on this host?

The goal is not to force a partner into a new agent architecture. It is to make the reliability boundary explicit and measurable.
