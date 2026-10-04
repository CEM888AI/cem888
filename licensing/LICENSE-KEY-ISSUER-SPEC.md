# CEM888 License Key — Issuer / Verifier Spec
_2026-10-04 · CEM-288 (Plane). Ed25519-signed JSON. Offline verification. No phone-home._

## 0. Principles
1. **The runtime is sovereign.** Verification is **local and offline**. No per-turn
   call home. (The capability manifest already promises: "the installed runtime
   never needs [the network] and makes no per-turn phone-home".)
2. **The License Key is the product.** It carries entitlements; the gate reads it.
3. **Verify at a boundary that already exists.** CEM888 already has a
   deterministic tool-boundary gate (`owner-prohibition`, hooks `pre_llm_call` +
   `pre_tool_call`). License enforcement is a **second gate at the same seam** — not
   a new architecture.
4. **Fail closed on tamper, fail open to Free on absence.** A missing/garbage
   license = Free tier. A **forged or altered** license = refuse the paid
   entitlements, log a failure receipt. (Mirrors owner-prohibition: an unreadable
   store is a reported failure, never a permission.)

## 1. The artifact — `license.json`
Lives at `<profile>/state/license.json`. Example:
```json
{
  "v": 1,
  "license_id": "lic_7Yq2mK...",
  "issuer": "CEM888.AI",
  "issued_to": { "org": "Acme LLC", "contact": "Jane Doe", "email": "jane@acme.com" },
  "tier": "pro",
  "entitlements": {
    "connectors": ["claude", "codex", "deepseek"],
    "profiles": -1,
    "remote_mcp_sync": true,
    "policy_customization": true,
    "seats": 1,
    "client_deployments": 0,
    "white_label": false
  },
  "issued_at": 1767225600,
  "not_before": 1767225600,
  "expires_at": 1798761600,
  "maintenance_until": 1798761600,
  "perpetual_floor_version": "1.2.0",
  "key_id": "cem888-2026-A",
  "signature": "base64url(Ed25519(payload))"
}
```
- `-1` = unlimited. `connectors` = allow-list; `"*"` = all.
- `expires_at: null` = perpetual right (Free tier, or a bought-out license).
- `maintenance_until` = how long **Updates** are entitled (the §4 perpetual-fallback
  clock). Distinct from `expires_at` (the right to *run* the tier).
- `perpetual_floor_version` = last version the key may run after maintenance lapses.
- `signature` covers the payload object **excluding** the `signature` field.

## 2. Signing
- **Algorithm:** Ed25519 (`cryptography` lib — already a runtime dep candidate).
- **Canonicalization:** RFC 8785 (JCS) over the payload object minus `signature`.
  Deterministic bytes → stable signature. Do not hand-roll key order.
- **Signature encoding:** base64url, no padding.
- **Public keys:** shipped in the runtime trust store
  `<profile>/state/license_trust.json`:
  ```json
  { "keys": [ { "key_id": "cem888-2026-A", "alg": "ed25519", "pubkey": "base64url..." } ] }
  ```
  Ship ≥2 keys (current + next) so rotation never breaks existing licenses.

## 3. Key hierarchy & rotation
- **Root key** — offline (stored in a safe / hardware token). Never signs licenses.
  Signs and certifies **release signing keys**.
- **Release signing key(s)** (`key_id` = `cem888-<year>-<letter>`) — sign license
  files for a release line. One per major version.
- **Rotation:** publish the new public key in a runtime update *before* issuing
  licenses signed by it. Old keys stay in the trust store until their licenses
  expire. Never remove a key still in use.

## 4. Verification algorithm (runtime)
1. Read `<profile>/state/license.json`. Missing → **Free tier**.
2. Parse + schema-validate (`v`, required fields). Malformed → Free + receipt.
3. Look up `key_id` in `license_trust.json`. Unknown key → Free + receipt.
4. Recompute JCS bytes (payload minus `signature`); verify Ed25519 signature.
   **Invalid → refuse paid entitlements, emit failure receipt.**
5. Check `not_before ≤ now ≤ expires_at` (if expires set). Expired → **perpetual
   floor**: allow running if current version ≤ `perpetual_floor_version`; else Free.
6. Compute effective entitlements → cache to `state/license_state.json`.
7. Write a verification receipt (tier, key_id, result, timestamp).

## 5. Runtime integration — plugin `license-gate`
Mirror the `owner-prohibition` seam exactly:
```yaml
name: license-gate
provides_hooks: [ on_session_start, pre_tool_call ]
```
- **`on_session_start`** — run §4 once; cache entitlements; emit receipt. (Boot,
  not per turn → still offline, still no phone-home.)
- **`pre_tool_call`** — normalize the proposed action (`normalize_action`, same
  shape as owner-prohibition: **shell spelling and argv normalize identically**, so
  an alternate route can't dodge the gate). Match against entitlements. On miss →
  **HARD BLOCK** with class `license tier`. Return the upgrade path in the message.

### Enforcement mapping (action → required entitlement)
| Proposed action | Requires |
|---|---|
| Add a host connector other than DeepSeek | `connectors` |
| Create a 2nd agent profile | `profiles` |
| Enable remote MCP sync | `remote_mcp_sync` |
| Edit policy / prohibition-gate config | `policy_customization` |
| Register > N seats | `seats` |
| Deploy for a client | `client_deployments` |
| White-label / remove branding | `white_label` |

## 6. Issuer — the admin dashboard (CEM-288)
Deliverable: a signing service + UI.
- Generate/rotate keypairs (root offline; release keys online).
- Issue a license: pick tier → sets `entitlements` → sign → return `license.json`.
- **Registry**: every `license_id`, org, tier, dates, seats, client count.
- **Per-client issuance for resellers**: partner portal issues N client keys under
  the partner's agreement (this is the per-client toll, operationalized).
- **Revocation** — see §7.

## 7. Revocation (the offline tradeoff — decide)
No phone-home means you cannot revoke instantly. Options:
- **(a) Short expiry** — annual keys; the clock is the revocation mechanism.
  Simple, offline-honest. *Default.*
- **(b) Optional CRL URL** — key may carry `revocation_url`; runtime checks it
  **only if** the user opts into a connectivity check. Enterprise tier only.
- **(c) Contract + audit** — legal enforcement for the determined infringer.
Recommendation: **(a) by default, (b) opt-in for Enterprise, (c) always in the
reseller/OEM agreement.**

## 8. Machine binding (optional — decide)
A key can optionally bind to a machine fingerprint hash.
- **Pro:** slows casual key-sharing.
- **Con:** breaks "move it to your own hardware" — antithetical to sovereignty.
Recommendation: **off by default**; offer as an Enterprise control. Leakage is
better handled by the annual expiry clock + audit clauses than by DRM.

## 9. Acceptance tests
- [ ] Valid Pro key unlocks connectors + remote sync; Free blocks them.
- [ ] Tampered payload (change `tier`→`oem`) → signature fails, paid features
      refused, failure receipt written.
- [ ] Expired key, version ≤ floor → runs; version > floor → Free.
- [ ] Unknown `key_id` → Free + receipt, no crash.
- [ ] Shell spelling and argv spelling of the same action both blocked identically.
- [ ] No network access during any verification (prove it — offline test).
- [ ] Missing `license.json` → Free tier, runtime fully functional at Free limits.

## 10. Dependencies / where it lands
- New plugin: `<profile>/plugins/license-gate/` (ships in the bundle).
- Trust store + license: `<profile>/state/license_trust.json`, `state/license.json`.
- Issuer service: separate repo/deploy (the dashboard).
- Ship the **verifier in the runtime** and the **issuer privately** — never ship
  the signing private key in the wheel.
