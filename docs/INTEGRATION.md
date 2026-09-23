# CEM888 Integration Contract

CEM888 is intended to sit underneath or beside an existing agent without requiring the partner to rewrite the agent's business logic.

## Lifecycle seams

### 1. Turn start

The host provides the principal / agent / task identity needed to resolve current runtime state.

CEM888 returns the current authoritative working state and bounded context required for the turn.

### 2. Before consequential action

The proposed action and target enter the runtime authority boundary.

The runtime resolves scope and permission before execution.

### 3. After execution

Observable execution evidence is returned to the runtime verification boundary.

The verifier evaluates what the runtime can actually assert from the observed postcondition.

### 4. Turn finish / checkpoint

The resulting state transition, checkpoint, and receipt are committed to durable state.

## Conceptual flow

```text
TURN START
  -> resolve identity / task
  -> load authoritative state
  -> compile bounded context
  -> model reasons / proposes
  -> runtime authorizes
  -> tool executes
  -> runtime observes evidence
  -> runtime verifies
  -> state transition / receipt
```


## Owner prohibition authority

CEM888 treats explicit owner prohibitions as runtime authority.

OWNER: "do not / never / stop / block X"
-> canonical customer-owned prohibition state
-> same-turn activation
-> proposed protected action
-> deterministic prohibition check
-> BLOCK before execution
-> structured denial / ask-owner recovery

A prohibition persists across turns, sessions, restarts, models, and supported hosts until the authenticated owner explicitly revokes it or grants a scoped exception. Generic task language, model reasoning, another agent, historical context, or tool output cannot silently widen authority.

A one-use or task-scoped exception is narrower than the standing prohibition and expires with its scope.

For protected/consequential actions, inability to load or evaluate prohibition authority is not permission: execution fails closed and the host may continue conversation or ask the owner.

External hosts such as Claude, ChatGPT, Codex, and future adapters consume the same CEM888 authority state. CEM888 can guarantee a hard block only where the proposed action crosses an enforceable CEM-controlled boundary. Hosts without such a boundary must be labeled PARTIAL or HOST-RESTRICTED for that capability.

## What the partner keeps

A partner can continue to own:

- UI and user experience
- planner
- agent logic
- model/provider selection
- tool implementations
- observability
- domain workflow
- proprietary business logic

CEM888 provides the reliability/control boundary around those systems.

## Integration principle

The model is replaceable intelligence.

Authoritative state, action scope, continuity, and verification remain runtime responsibilities.
