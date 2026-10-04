# CEM888 Source-Available Commercial License

**Version:** 1.0 — DRAFT for review
**Effective Date:** [PLACEHOLDER: date]
**Licensor:** [PLACEHOLDER: legal entity, e.g. "CEM888.AI, LLC"]
**License Type:** Source-Available. Commercial. **Not open source.**
**Canonical URL:** [PLACEHOLDER: https://cem888.ai/LICENSE.md]

---

## 0. Plain-language summary (not a substitute for the terms below)
CEM888 is **source-available**: you can read, audit, and modify the source. It is
**free** for personal use and for running the **Free tier** of your own agent on
your own machine. To use **Pro/Business** features, or to deploy CEM888 **for other
people** (clients, customers, or as a service), you need a paid license. You may
**not** host CEM888 as a service, run other people's accounts on it, rebrand it, or
sell it without a Reseller/OEM license. The **License Key** governs exactly which
features you are entitled to.

---

## 1. Definitions
- **Software** — the CEM888 agent runtime, CLI, plugins, connectors, source code,
  binaries, updates, and documentation.
- **Source** — the human-readable source of the Software, published for audit.
- **License Key** — the Ed25519-signed JSON file that states your tier,
  entitlements, seats, and expiry. See `LICENSE-KEY-ISSUER-SPEC.md`.
- **Internal Use** — use within one organization for that organization's own
  operations, not for external parties.
- **Commercial Use** — any use by or for a business (including a sole
  proprietorship) for revenue-generating purposes.
- **Client Deployment** — provisioning, configuring, or running the Software for,
  or making it available to, any person or entity other than the licensee.
- **Hosted Service** — making the Software's functionality available to anyone over
  a network (SaaS, managed hosting, or platform), including multi-tenant instances.
- **Multi-tenant** — hosting more than one separate client account or organization
  on a shared instance.
- **Update** — any release of the Software the Licensor publishes while your
  license is active.

## 2. Grant
Subject to this License and to a valid License Key, the Licensor grants you a
non-exclusive, non-transferable, revocable license to:
1. read, audit, and modify the Source;
2. install and run the Software on hardware you control, for personal use and for
   the Free tier;
3. use Pro and Business tiers **only while a valid License Key for that tier is
   present**; and
4. exercise Reseller and OEM rights **only** under a separate written agreement.

## 3. Free tier (no License Key required)
The Free tier is granted at no charge and is limited to: **one host connector
(DeepSeek only)**, **one agent profile**, **local continuity only (no remote MCP
sync)**, and **no policy/prohibition-gate customization**. Full limits are in
`TIER-MATRIX.md`, which is incorporated by reference.

## 4. Paid tiers — annual license with perpetual fallback
1. An annual license entitles you to run the licensed tier and to receive Updates
   while the license is active.
2. If you do **not** renew, your license converts to a **perpetual right to keep
   running the last version you were licensed for** (the "perpetual floor"). You
   may keep running that version indefinitely; you do **not** receive further
   Updates or support.
3. Expiry is enforced **locally** from the License Key. The Software makes **no
   per-turn phone-home call** to verify licensing. (See the one-time installer
   claim in the capability manifest; licensing itself is offline.)

## 5. Permitted uses
You **may**: run the Software on hardware you control; audit and modify the Source
for your own use; use it for personal and Internal Use; receive and use Updates
while licensed; and exercise Reseller/OEM rights while a valid agreement for those
rights is in force.

## 6. Prohibited uses
You **may not**:
1. offer the Software, or its functionality, as a **Hosted Service**;
2. run **multi-tenant** instances;
3. **rebrand, redistribute, or fork** the Software under another name;
4. **resell, sublicense, or perform Client Deployments** without a Reseller/OEM
   license;
5. circumvent, disable, or alter any **feature gate**, or forge, alter, or
   reuse a License Key you are not entitled to;
6. remove or modify any copyright, license, or attribution notice; or
7. use "CEM888" and related marks in derivative products without written consent.

## 7. License Keys govern
Where this text and a License Key conflict on entitlements, the License Key
governs. A License Key is **evidence of entitlements, not of ownership**; it must
be verified against the Licensor's published public key and may be revoked on
breach or expiry.

## 8. Attribution
Public-facing uses must preserve the CEM888 copyright and license notices. A
"Powered by CEM888" attribution [PLACEHOLDER: required? / optional?] where end
users can see the Software. — *Decision pending; see TIER-MATRIX §Attribution.*

## 9. Term and termination
This License runs while you comply with it and while any License Key is valid.
It **terminates automatically** if you breach it. On termination you must stop all
use beyond the Free tier and destroy copies, except that the §4.2 perpetual floor
survives for versions you validly licensed.

## 10. Warranty disclaimer and limitation of liability
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE LICENSOR BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.

## 11. Governing law
[PLACEHOLDER: jurisdiction — e.g. "the laws of the State of [X], United States,
without regard to conflict-of-law principles." AGNT uses Delaware; pick
deliberately with counsel.]

## 12. Contact
**CEM888.AI Licensing** — [PLACEHOLDER: legal@cem888.ai]

---
© 2026 [PLACEHOLDER: entity]. All rights reserved.
"CEM888" and related marks are trademarks of [PLACEHOLDER: entity].
