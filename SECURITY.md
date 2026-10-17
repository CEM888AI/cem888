# Security Policy

CEM888 is in public beta and maintained by one person. Security-sensitive controls are developed with explicit scope and falsification tests, but this repository does **not** claim independent security certification, a completed penetration test, or regulated-sector compliance.

## Supported versions

| Version | Security fixes |
| --- | --- |
| Latest release on [Releases](https://github.com/CEM888AI/cem888/releases) | Yes |
| Older releases | No — upgrade to the latest release |

## How to report

Email **creator@cem888.ai** with the subject line `SECURITY: <short description>`.

Include, where possible:

- affected component, file or release version;
- reproducible steps;
- expected vs observed behavior;
- impact, and who could exploit it;
- relevant logs or receipts with secrets removed.

Do **not** put credentials, tokens, customer data or exploit details for an unpatched issue in a public GitHub issue, pull request or discussion.

## What to expect

These are targets for a single-maintainer project, not a contractual SLA.

| Step | Target |
| --- | --- |
| Acknowledge your report | within 5 business days |
| Keep you updated | every reply says when you will next hear back, and no gap is longer than 14 days |
| Public disclosure | coordinated with you after a fix ships |

You will be credited in the release notes unless you ask not to be.

## In scope

- The runtime source in this repository (`src/`).
- Cross-customer or cross-agent data exposure.
- Authentication or identity-binding bypass.
- Raw secret leakage (logs, receipts, context packets, state files).
- Action-authority or owner-prohibition bypass on a boundary CEM888 claims to enforce (see the [Enforcement Matrix](./docs/ENFORCEMENT_MATRIX.md)).
- Verification accepting fabricated or unobserved evidence.
- Duplicate consequential effects on retry or replay.
- Installer or update integrity, and dependency or supply-chain compromise.
- A host integration claiming an enforcement boundary it does not actually control.

## Out of scope

- The shell authority check is an **in-process semantic boundary, not an OS security boundary** (see [PUBLIC_CONFORMANCE.md](./docs/PUBLIC_CONFORMANCE.md)). Hostile shell expansion or symlink escapes against it are known limits, not new findings, unless they bypass a control the documentation says is enforced.
- Actions on hosts or integration classes the Enforcement Matrix labels ADVISORY or MEDIATED-ONLY, for actions outside CEM-mediated paths.
- Vulnerabilities in third-party model providers, hosts or dependencies without a CEM888-specific impact (report those upstream).
- Denial of service by resource exhaustion on a machine you control.
- Social engineering, physical attacks, and findings that require an already-compromised machine.

## Testing rules (safe harbor)

Good-faith research that follows these rules will not be pursued legally by CEM Unlimited LLC:

- Test against your own local install or your own account only.
- Do not access, modify or retain data that is not yours; stop and report if you encounter it.
- Do not run destructive, high-volume or denial-of-service tests against cem888.ai or any shared infrastructure.
- If proof needs a live or shared environment, email first so the test can be scoped.

## Security model

CEM888's security posture is boundary-specific. A CEM-controlled action path, a native host hook, an MCP-only integration and a context-only integration do not provide the same guarantees. See [Technical Status](./docs/STATUS.md), [Enforcement Matrix](./docs/ENFORCEMENT_MATRIX.md), [Native Host Adapters](./docs/HOST_ADAPTERS.md) and [Architecture](./docs/ARCHITECTURE.md).

A mechanism being present in source does not by itself make it certified on a customer artifact or third-party host.
