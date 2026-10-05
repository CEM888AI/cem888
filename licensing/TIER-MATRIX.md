# CEM888 Tier Matrix
_2026-10-04 · built from Chandler's 6 fork decisions. Prices marked [PROPOSAL]
are my recommendation, not settled — Chandler sets final numbers._

Model: **license the software (1) + sell resale rights (3). No hosting.** (DECIDED 2026-10-04 — unchanged.)

> 📌 **AUTHORITATIVE PRICING = Plane `CEM-295`** — *"[STRATEGY] Pricing — FINAL: $29/mo individual + company license by size"* (2026-10-04). **(A) Individual: $29/mo** (annual $290) — everything included, no tiers. **(B) Company license, ANNUAL by headcount:** <25 → **$2,500/yr** · 25–250 → **$15,000/yr** · 250+ → **$50,000+/yr** (custom); unlimited seats, admin, audit, priority support; annual only. Free tier unchanged (local runtime + DeepSeek + one host). Platform/embed licensing — companies building **their own product on the CEM888 stack** — is a **SEPARATE track** with its own numbers (still open): `CEM-185`/`CEM-174` dual license (AGPL-3.0 + paid commercial for embedding/resale/white-label) · `CEM-297` (ELv2 or custom CEM888 license — **never converts**) · `CEM-298` (reseller $1,000/yr + $12/client/mo). **Every `[PROPOSAL]` price below is my earlier recommendation and loses wherever it conflicts with CEM-295 — do not quote them as the model.**
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

### 2. Pro — **SETTLED 2026-10-05: $29/mo** · list **$348/yr** · annual **$290/yr = 2 months free** ($24.17/mo effective, −16.7%)
*(Never quote the annual without the $348 anchor — "$290/yr" alone reads as a 10-month year. The year is 12 months; $290 is 10 months of payment.)*
*(Was my proposal ~$199/yr per install — superseded by Plane CEM-344. Per install, not per seat.)*
- **All host connectors** (Claude, Codex, DeepSeek, others)
- **Unlimited agent profiles**
- **Remote MCP sync** on
- **Custom policies / prohibition-gate customization**
- Email support
- Billing unit: **per install** (a solo dev doesn't think in seats)

### 3. Business — **CEM-295 governs: annual by headcount, unlimited installs**
*(The earlier [PROPOSAL] "$99/seat/yr, min 5" is **WITHDRAWN** — it priced a Business seat at $8.25/mo, **below** a Pro licence at $29/mo, and put a 5-seat company at $495/yr against CEM-295's $2,500/yr for the same buyer. It failed both arithmetic and CEM-295.)*
- Everything in Pro, for the whole organization
- **Annual by employee count:** <25 → **$2,500/yr** · 25–250 → **$15,000/yr** · 250+ → **$50,000+/yr** (custom)
- **Unlimited installs inside the org** — there is no per-seat count to meter
- **Admin console**, central policy distribution, audit trail, priority support
- Billing unit: **the organization** — a company buys a licence for itself, not a seat

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
| **Commercial use (earn money)** | **✗ personal only** | ✓ | ✓ | ✓ | ✓ |
| **Build a business on it**     | **✗** | ✗ | ✗ | ✓ (reseller) | ✓ (OEM) |
| Host connectors               | DeepSeek only | All | All | All | All |
| Agent profiles                | 1 | Unlimited | Unlimited | Unlimited | Unlimited |
| Remote MCP sync               | ✗ | ✓ | ✓ | ✓ | ✓ |
| Custom policy / gate          | ✗ | ✓ | ✓ | ✓ | ✓ |
| Installs                      | 1 | 1 (per install) | Unlimited in org | Unlimited | Unlimited |
| Client Deployments            | ✗ | ✗ | ✗ | ✓ | ✓ |
| White-label / rebrand         | ✗ | ✗ | ✗ | ✗ | ✓ |
| Updates                       | n/a | annual | annual | annual | annual |

Gate source of truth = the **License Key entitlements**, enforced at the
`pre_tool_call` seam (same boundary as `owner-prohibition`). See
`LICENSE-KEY-ISSUER-SPEC.md`.

---

## The two ways this licence has to make money — Chandler, 2026-10-04, verbatim

> **(1) Monetize the software. (3) Monetize the right to resell. (2) Hosting — NOT doing.**

| Way | Mechanism in `LICENSE.md` | Price |
|---|---|---|
| **1 — sell the software** | §2.3 grant gated on a License Key · §3 Free = personal/non-commercial · §4 annual + perpetual floor | Pro **$29/mo · $290/yr** (2 months free vs $348) · Business by headcount (number open) |
| **2 — sell the right to resell** | §2.4 + §6.6 — Reseller/OEM rights exist **only under a separate written agreement** | Reseller partner fee + per-client toll (numbers open) |
| *(not a way)* **hosting** | §6.3 Hosted Service · §6.4 multi-tenant · §6.5 rebrand/fork | expressly forbidden — our not-hosting is a choice, not a licence we hand out |

**The owner rule that makes way 1 reachable (2026-10-05):** *"no one is allowed to make
money on it or build as a business for free."* Free tier = **personal, non-commercial
only** (§3, §6.1–6.2) — so there is no free path to revenue to undercut the licence.
Chandler's 2026-10-05 question *"how do our competitors sell people building on top of
their licences?"* is the shape of **way 2** — see
`../cem888-build-on-top-licensing-research-2026-10-05.md`.

**§11 jurisdiction — SET 2026-10-05: Delaware** (default; one-line change, affects
neither revenue way).

## Open items (not yet decided)
- [ ] Final Pro / Business numbers (I proposed; you set)
- [x] ~~**Attribution** — require "Powered by CEM888" or not?~~ **RESOLVED 2026-10-05: NOT required.** §8 now requires the copyright/license notices and sets the "Powered by" line to optional, so attribution can never contradict the Reseller/OEM white-label licences. ✅ Licensor entity filled 2026-10-05: **CEM Unlimited LLC** (operating as "CEM888.AI"). Remaining blanks before the draft can replace ELv2 on GitHub: **§12 governing jurisdiction (state)**, plus the date/canonical-URL stamp at publish.
- [x] ~~**Commercial-size clause** for Free~~ **CLOSED 2026-10-05 by the owner's rule:** *"no one is allowed to make money on it or build as a business for free."* Free is **personal, non-commercial only** (§3, §6.1–6.2 of LICENSE.md) — so a 500-person company no longer has a Free-tier path regardless of feature gates. The licensing gate, not the feature gate, is what closes it.
- [ ] One-time purchase option alongside annual? (Agencies sometimes prefer to
      buy the license outright.)
- [ ] Refund / trial policy
