# CEM888 Integration Setup Recipe Contract

## Purpose

Every customer-facing integration card should provide a copyable setup prompt that the customer can give to their installed CEM888 agent.

The prompt is an execution recipe, not generic documentation.

## Required recipe behavior

A setup recipe must instruct the CEM agent to:

1. inspect the existing runtime and integration configuration before changing anything;
2. detect whether the target host / service is installed or available;
3. explain the initial requested permissions/scopes and why they are needed;
4. obtain the user's approval for the initial connection and agreed scope where required;
5. reuse standing authorization afterward rather than repeatedly prompting for the same approved capability;
6. where a user provides an API key/token/credential, accept it and place it promptly into the approved secure secret store;
7. persist/use only a secret reference in normal runtime state after secure ingestion;
8. use the canonical CEM888 integration adapter and provisioning path;
9. bind the integration to the correct customer and selected CEM agent;
10. register capability / health state;
11. use canonical breathing when the integration creates a new agent turn;
12. inherit the parent CEM turn when the integration is only a tool inside an active turn;
13. run conformance tests before claiming the integration is connected;
14. report exactly what succeeded, what remains manual, and what the host restricts;
15. write a structured connection receipt;
16. support repair, reinstall, revoke, and uninstall.

## Standing permission rule

Once the user has authorized the integration and agreed scopes, the adapter should continue normal work without repeatedly asking permission or re-authenticating.

Ask again only for:
- a new/expanded capability or scope;
- a different customer/account/agent binding;
- credential expiry/revocation;
- an action outside existing standing authority;
- a consent event forced by the host/provider/OS.

Routine CEM continuity calls, inhale/exhale, verification, and already-authorized host actions should happen automatically.

## Credential rule

CEM agents are allowed to handle user-provided API keys/tokens when that is the selected connection path.

The agent should:
- accept the credential;
- store it promptly in the approved secret store/broker;
- keep only a secret reference in normal state;
- use the credential automatically afterward;
- avoid unnecessary echo/re-display;
- never persist raw credentials in durable conversational memory, receipts, normal logs, public artifacts, Linear, Airtable, or unrelated/cross-agent context.

The rule is secure custody, not refusal to handle secrets.

## Integration-card UX

Each integration card should display:

- integration name
- what it connects
- capability class: TOOL / EVENT / AI HOST / HYBRID
- support state: CERTIFIED / PARTIAL / HOST-RESTRICTED / BETA / COMING SOON
- permissions/scopes in plain English
- **Copy setup prompt**
- connect / repair / revoke instructions
- last certification / compatibility note

## Generic setup prompt template

```text
Connect my selected CEM888 agent to <INTEGRATION> using the certified CEM888 integration path.

Before changing anything:
1. Inspect the current CEM888 runtime, agent binding, existing integration configuration, and current <INTEGRATION> installation/account state.
2. Tell me what initial permissions, scopes, login steps, hooks, plugins, credentials, or local configuration changes are required and why.
3. If I provide an API key, token, or other credential, accept it and place it promptly into the approved secure secret store. Keep only a secret reference in normal runtime state afterward.
4. Obtain my approval for the initial connection and agreed scopes where required. After that, reuse standing authorization and do not repeatedly ask me to approve the same already-authorized capability.
5. If the provider requires its own human login/consent flow, direct me through that flow.
6. Use the canonical CEM888 adapter/provisioning path. Do not create a second memory/state system.
7. Bind the connection only to my authenticated customer identity and currently selected CEM agent.
8. Where <INTEGRATION> creates a new agent turn, use the canonical CEM inhale -> execute -> verify -> exhale lifecycle exactly once.
9. Where <INTEGRATION> is only a tool inside an existing CEM turn, inherit the parent turn and do not create a nested breathing cycle.
10. Configure only the scopes I authorize.
11. After setup, run the integration's certification/conformance checks.
12. Do not say "connected" unless those checks pass.
13. Report:
   - what was detected
   - what was configured
   - permissions/scopes granted
   - current health
   - certification state
   - any host restriction
   - how to repair/revoke/uninstall the connection
14. Write a structured CEM connection receipt and update capability discovery.
```

## First recipes

1. Claude Code
2. Codex
3. ChatGPT / ChatGPT Work
4. Claude app
5. GitHub
6. Linear
7. Airtable
8. Gmail
9. Google Calendar
10. Slack
11. JetBrains
12. Cursor
13. VS Code / GitHub Copilot
14. Microsoft Copilot / Copilot Studio

Linear: CEM-257.
