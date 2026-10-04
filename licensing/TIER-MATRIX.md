# CEM888 Tier Matrix
_2026-10-04 · built from Chandler's 6 fork decisions. Prices marked [PROPOSAL]
are my recommendation, not settled — Chandler sets final numbers._

Model: **license the software (1) + sell resale rights (3). No hosting.**
Billing: **annual license with perpetual fallback** — pay annually, get Updates;
stop paying, keep the last version you paid for, no further Updates. (JetBrains
model.)

---

## Tiers

### 1. Free — $0
- **1 host connector** (DeepSeek only)
- **1 agent profile**
- **Local continuity only** — no remote MCP sync
- **No** policy / prohibition-gate customization
- Personal use + Internal Use, any org size
- Community support
- No License Key required

**The paywall moment:** "the moment someone wants Claude + Codex on the same
brain, they pay."

### 2. Pro — [PROPOSAL] ~$199/yr, per install
- **All host connectors** (Claude, Codex, DeepSeek, others)
- **Unlimited agent profiles**
- **Remote MCP sync** on
- **Custom policies / prohibition-gate customization**
- Email support
- Billing unit: **per install** (a solo dev doesn't think in seats)

### 3. Business — [PROPOSAL] ~$99/seat/yr, min 5 seats
- Everything in Pro
- **Per-seat** licensing, **admin console**
- Central policy distribution across seats
- Priority support
- Billing unit: **per seat** (a 20-engineer company thinks in seats)

### 4. Reseller / Agency — flat fee + per-client toll
- **Annual partner fee: [PROPOSAL] $500–1,000/yr** — access to the partner
  program + tooling (key issuance, per-client management)
- **Per-client license: [PROPOSAL] $10–15 / client / month** (or annual
  equivalent)
- Right to perform **Client Deployments**
- A partner with 50 clients → **~$6K–9K/yr** recurring through the channel.

### 5. OEM / White-label — custom
- Embed / rebrand rights
- Custom SLA, SSO/audit, logo removal
- Negotiated annual

---

## Feature gate → tier

| Capability                    | Free | Pro | Business | Reseller | OEM |
|-------------------------------|:----:|:---:|:--------:|:--------:|:---:|
| Host connectors               | DeepSeek only | All | All | All | All |
| Agent profiles                | 1 | Unlimited | Unlimited | Unlimited | Unlimited |
| Remote MCP sync               | ✗ | ✓ | ✓ | ✓ | ✓ |
| Custom policy / gate          | ✗ | ✓ | ✓ | ✓ | ✓ |
| Seats                         | 1 | 1 (per install) | N | N | N |
| Client Deployments            | ✗ | ✗ | ✗ | ✓ | ✓ |
| White-label / rebrand         | ✗ | ✗ | ✗ | ✗ | ✓ |
| Updates                       | n/a | annual | annual | annual | annual |

Gate source of truth = the **License Key entitlements**, enforced at the
`pre_tool_call` seam (same boundary as `owner-prohibition`). See
`LICENSE-KEY-ISSUER-SPEC.md`.

---

## Open items (not yet decided)
- [ ] Final Pro / Business numbers (I proposed; you set)
- [ ] **Attribution** — require "Powered by CEM888" or not? (§8 of LICENSE.md)
- [ ] Optional: add a **commercial-size clause** to Free (e.g. free for orgs
      <$1M & <10 people) *in addition to* feature gates — feature gates alone
      leave a 500-person company on the Free tier if they only need DeepSeek.
      You chose feature gates; flagging the gap.
- [ ] One-time purchase option alongside annual? (Agencies sometimes prefer to
      buy the license outright.)
- [ ] Refund / trial policy
