# Security Policy

CEM888 is in public beta. Security-sensitive controls are developed with explicit scope and falsification tests, but this repository does **not** claim independent security certification or regulated-sector compliance.

## Reporting a vulnerability

Please report security issues privately to:

**creator@cem888.ai**

Include, where possible:

- affected component / artifact;
- reproducible steps;
- expected vs observed behavior;
- impact;
- relevant logs or receipts with secrets removed.

Please do **not** place credentials, tokens, customer data or exploit details for an unpatched issue in a public GitHub issue.

## High-priority security reports

Reports are especially useful when they involve:

- cross-customer or cross-agent data exposure;
- authentication / identity-binding bypass;
- raw secret leakage;
- action-authority or prohibition bypass;
- verification accepting fabricated/unobserved evidence;
- duplicate consequential effects on retry/replay;
- installer/update integrity;
- dependency or supply-chain compromise;
- a host integration claiming an enforcement boundary it does not actually control.

## Security model

CEM888's public security posture is boundary-specific.

A CEM-controlled action path, a native host hook, an MCP-only integration and a context-only integration do not provide the same enforcement guarantees.

See:

- **[Technical Status](./docs/STATUS.md)**
- **[Enforcement Matrix](./docs/ENFORCEMENT_MATRIX.md)**
- **[Native Host Adapters](./docs/HOST_ADAPTERS.md)**

## Responsible testing

Please avoid destructive testing against shared/public infrastructure or third-party systems without authorization.

If a report requires proof against a live/customer environment, contact us first so the test can be scoped safely.

## Disclosure

CEM888 prefers evidence-backed disclosure over broad security claims. A mechanism being present in source does not by itself make it certified on a customer artifact or third-party host.
