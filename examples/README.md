# Examples

What the runtime actually emits. These are **sanitized samples**: field names, structure and verdict semantics are real; every value is redacted. Nothing here reveals an implementation detail.

| File | What it is |
| --- | --- |
| [`context-packet.json`](./context-packet.json) | What a single turn is given — fixed identity (never scored), owner rulings with authority, current checkpoints, agreement probes, and the selection rule. |
| [`receipt.json`](./receipt.json) | A verified action: what was proposed, what scope resolved, what evidence satisfied the postcondition. |
| [`blocked-action.json`](./blocked-action.json) | An action denied at the boundary, with the rule that denied it and `executed: false`. |

Three properties are visible in the shapes, which is the reason to publish them:

1. **Identity is never scored.** `profile_rules` carries `scored: false` — foundational rules are injected whole, every turn, on every host.
2. **Superseded state is excluded, not ranked lower.** A stale fact does not compete with a current one; it is not eligible.
3. **Evidence is typed, not prose.** A receipt passes on `evidence[]`, not on the model saying it worked.

→ Back to the [README](../README.md) · How this works: [ARCHITECTURE.md](../docs/ARCHITECTURE.md)
