# Documentation

Start here. Every claim in the [README](../README.md) points into one of these files.

## Understand it

| Document | What it answers |
| --- | --- |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | The four questions, the turn lifecycle, what a receipt contains |
| [CAPABILITY_MATRIX.md](./CAPABILITY_MATRIX.md) | Implemented · customer-certified · specified · planned — per capability |
| [ENFORCEMENT_MATRIX.md](./ENFORCEMENT_MATRIX.md) | What can actually be blocked, per host, and what honestly cannot |

## Integrate it

| Document | What it answers |
| --- | --- |
| [INTEGRATION.md](./INTEGRATION.md) | The integration contract and the four lifecycle seams |
| [INTEGRATION_RECIPES.md](./INTEGRATION_RECIPES.md) | Worked recipes per host |
| [HOST_ADAPTERS.md](./HOST_ADAPTERS.md) | Claude Code · Codex · Cursor · Copilot — what each host exposes |

## Verify it

| Document | What it answers |
| --- | --- |
| [PUBLIC_CONFORMANCE.md](./PUBLIC_CONFORMANCE.md) | The 15-check suite: what each check falsifies |
| [STATUS.md](./STATUS.md) | What is certified right now, including known defects |
| [FRESH_INSTALL_ACCEPTANCE_2026-10-01.md](./FRESH_INSTALL_ACCEPTANCE_2026-10-01.md) | A full acceptance run, written as it happened |

## Artifacts

- [../examples/context-packet.json](../examples/context-packet.json) — one turn's packet
- [../examples/receipt.json](../examples/receipt.json) — a verified action
- [../examples/blocked-action.json](../examples/blocked-action.json) — a denial at the boundary

## Elsewhere

[Engineering case studies](https://github.com/CEM888AI/runtime-case-studies) · [Benchmarks and per-question data](https://github.com/CEM888AI/benchmarks) · [Independent runtime evaluation](https://huggingface.co/datasets/CEM888AI/cem888-independent-runtime-evaluation) · [Legal](https://github.com/CEM888AI/legal) · [Runtime case studies index](https://github.com/CEM888AI/agent-systems-lab)
