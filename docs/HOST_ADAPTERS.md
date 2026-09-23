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

## Security requirements

- explicit user approval before vendor OAuth, executable hook installation, plugin installation, or host configuration changes
- secrets never enter model-visible prompts, durable memory, receipts, or logs
- fail closed on ambiguous customer / agent binding
- least privilege
- tenant isolation
- deterministic uninstall / revoke
- no provider-specific memory silo

## Architectural invariant

**Keep the agent. Add the reliability layer.**

The host remains the user's normal working surface. CEM888 remains the authoritative continuity, state, control, and verification layer around it.
