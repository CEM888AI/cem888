# CEM888 Capability Promotion Matrix

This document tracks the release relationship between the operating CEM888 runtime and the customer-distributed artifact.

The important distinction is:

> **Runtime capability is established on the reference system first. Customer release certification proves that the packaged artifact carries it correctly.**

| Capability | Reference runtime | Customer release track |
|---|---|---|
| Authoritative current state + supersession | Established / exercised | Promote into frozen candidate and certify on install |
| Bounded replace-not-append working state | Established / exercised | Promote and certify long-horizon behavior |
| Typed active-work lifecycle | Established / exercised | Promote and certify lifecycle persistence |
| Multi-session write safety | Established / exercised | Promote and certify concurrency behavior |
| Continuity / recovery | Established in operating runtime | Certify fresh-session / restart behavior in frozen artifact |
| Action authority | Runtime control-layer capability | Certify consequential-action scope on installed artifact |
| Verification + receipts | Runtime verification capability | Certify evidence-backed result handling on installed artifact |
| Hybrid retrieval + authority reconciliation | Runtime capability | Certify installed integration path |
| Duplicate / retry protection | Runtime lifecycle capability | Certify logical-event behavior on installed artifact |
| Provider-neutral local integration | Runtime architecture | Certify supported partner-facing surface |
| Tenant / identity isolation | Product invariant | Certify adversarial customer-isolation tests |
| Artifact self-identity | Release-system capability | Require version + digest + enabled-set identity in candidate |
| Clean install / upgrade | Release engineering | Certify on supported machines before broad handoff |
| Current benchmark evidence | Historical evidence exists | Re-baseline exact frozen candidate after certification |

## Release rule

A customer artifact is certified only against its own exact build identity.

The matrix exists to prevent drift between:

```text
reference runtime
  -> customer source
  -> built artifact
  -> installed artifact
  -> certification result
```
