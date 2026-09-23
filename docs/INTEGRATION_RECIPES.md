# CEM888 Integration Setup Recipe Contract

## Purpose

Every customer-facing integration card should provide a copyable setup prompt that the customer can give to their installed CEM888 agent.

The prompt is an execution recipe, not generic documentation.

## Required recipe behavior

A setup recipe must instruct the CEM agent to:

1. inspect the existing runtime and integration configuration before changing anything;
2. detect whether the target host / service is installed or available;
3. explain requested permissions and why they are needed;
4. obtain explicit user approval before OAuth, vendor login, executable hooks/plugins, or host configuration changes;
5. direct the user to the official vendor authorization page when human authentication is required;
6. never request that raw credentials or secrets be pasted into model context;
7. use the canonical CEM888 integration adapter and provisioning path;
8. bind the integration to the correct customer and selected CEM agent;
9. register capability / health state;
10. use canonical breathing when the integration creates a new agent turn;
11. inherit the parent CEM turn when the integration is only a tool inside an active turn;
12. run conformance tests before claiming the integration is connected;
13. report exactly what succeeded, what remains manual, and what the host restricts;
14. write a structured connection receipt;
15. support repair, reinstall, revoke, and uninstall.

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
2. Tell me exactly what permissions, scopes, login steps, hooks, plugins, or local configuration changes are required and why.
3. Do not ask me to paste passwords, OAuth tokens, API keys, or other raw secrets into chat.
4. If human authentication is required, direct me to the official authorization/login flow and wait for my approval before continuing.
5. Use the canonical CEM888 adapter/provisioning path. Do not create a second memory/state system.
6. Bind the connection only to my authenticated customer identity and currently selected CEM agent.
7. Where <INTEGRATION> creates a new agent turn, use the canonical CEM inhale -> execute -> verify -> exhale lifecycle exactly once.
8. Where <INTEGRATION> is only a tool inside an existing CEM turn, inherit the parent turn and do not create a nested breathing cycle.
9. Configure only the least permissions required.
10. After setup, run the integration's certification/conformance checks.
11. Do not say "connected" unless those checks pass.
12. Report:
   - what was detected
   - what was configured
   - permissions granted
   - current health
   - certification state
   - any host restriction
   - how to repair/revoke/uninstall the connection
13. Write a structured CEM connection receipt and update capability discovery.
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
