# Customer runtime provenance

This source tree is the identity-neutral execution layer paired with the
customer-neutral CEM profile blueprint and rebuilt only with Python 3.14.
CEM itself is constructed from its tracked profile repository; it is not
treated as a wheel or package artifact.

- CEM profile blueprint revision: `4f51beef8410ecaf311b070b11623d807ce4e4d7`
- Execution source files: 391 Python files
- Live execution source snapshot digest: `27d44e2a3f1fa69e402e172c98383e2c728c94cdc75d647e449885a7c3f267a1`
- Rebuilt source digest: `8047698c9636a8d352f78578c3f482744f415162835b4667d9f7c5b1c523befd`
- Customer rebuild version: `1.0.3`
- Required interpreter: `CPython 3.14`

The profile blueprint contributes generic configuration topology and runtime
plugin behavior only. It does not contribute identity or durable state.
The only execution-source change is the neutral customer release version in
`cem888_cli/__init__.py`.

Only distribution-owned program files were copied. No profile, vault, memory,
state database, session, log, credential, token, personal skill, configuration,
or machine-specific runtime artifact is part of this tree.
