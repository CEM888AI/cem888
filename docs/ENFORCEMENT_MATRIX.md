# CEM888 Enforcement Matrix

**Purpose:** describe what CEM888 can honestly claim at different integration boundaries.

This is a public architectural classification, not a certification list. Actual support must be proven per host, action class and artifact.

## Core rule

> **CEM888 can only hard-block an action that crosses a boundary CEM can actually intercept before execution.**

The same host may expose strong enforcement for one action class and only advisory behavior for another.

## Integration classes

| Integration boundary | What CEM can provide | What CEM must not claim | Class |
| --- | --- | --- | --- |
| **CEM-controlled standalone execution path** | Current-state resolution, bounded context, CEM pre-action gate, observable verification where coverage exists | Universal OS-level confinement or coverage outside CEM-controlled actions | **ENFORCED** for the named CEM-controlled action class |
| **Native host with a proven blocking pre-action hook** | Host lifecycle integration and hard block for actions that actually cross the hook | Control over actions that bypass the hook or use an unobserved route | **HOOK-GATED** |
| **MCP / tool-mediated integration without host-wide interception** | Current-state/context supply and enforcement for CEM-mediated actions | Control over the host's unrelated native tools, shell, connectors or side effects | **MEDIATED-ONLY** |
| **Context/retrieval integration without action interception** | Current state, bounded context, warnings, provenance | Hard action blocking | **ADVISORY** |
| **Host lacking a required lifecycle surface** | Whatever smaller subset is measurable | FULL lifecycle/control semantics | **HOST-RESTRICTED** for the missing capability |

## Dual owner-prohibition proof

A hard owner prohibition has two independent proof obligations:

### 1. Current-truth obligation

Conflicting prohibited/superseded material must not be promoted back into the model's **current authoritative working packet** merely because it is relevant, similar, old code or convenient.

Historical/provenance access may retain the material with explicit non-current status.

### 2. Action obligation

If the host proposes a matching protected action, the action must be refused **before execution** at the claimed enforcement boundary.

A host cannot be certified for the hard-NO capability by passing only one half.

## Fail-mode policy

For consequential actions inside a claimed enforcement surface:

- inability to resolve identity/scope is not permission;
- inability to load required authority is not permission;
- an integration should not be promoted as CERTIFIED until liveness testing proves the gate produces a real measurable effect.

The exact fail mode remains capability- and host-specific and must be named by the certification evidence.

## Maturity is separate from enforcement

Enforcement class describes **what the integration can control**.

Maturity describes **how proven the integration is**:

- **CERTIFIED**
- **BETA**
- **PLANNED**
- **HOST-RESTRICTED**

Do not collapse those axes into one label.

## Current public status

- DeepSeek Flash standalone customer path: **current certification lane**.
- Claude Code native adapter: **planned; classification will be measured**.
- Codex native adapter: **planned; classification will be measured**.
- Generic MCP connectivity: **not evidence of full host enforcement**.

See **[STATUS.md](./STATUS.md)** and **[HOST_ADAPTERS.md](./HOST_ADAPTERS.md)**.
