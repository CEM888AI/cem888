# Install / delivery acceptance — 2026-10-19 (all four platform tracks)

**Status:** PASSED — OWNER-RUN, ON REAL HARDWARE, ON EVERY PLATFORM TRACK

This record is different in kind from [Fresh-install acceptance — 2026-10-01](./FRESH_INSTALL_ACCEPTANCE_2026-10-01.md).
That document is a deep runtime/continuity run performed by the operator on one machine. **This** document
records the owner of the company downloading the published product and running it on four separate
machines, one per platform track. It is the strongest class of evidence this repository has: the customer
download path, executed by the customer, on hardware no CI can substitute for.

## Owner's report — verbatim, 2026-10-19

> "all four of the machines downloaded successful apps with working agents and updater, buttons,
> Windows, Linux, max, silicon and Mac Intel. They all downloaded with success."

## What was observed, per track

| Track | Download | App | Agent | Updater | UI buttons |
| --- | --- | --- | --- | --- | --- |
| Windows (x64) | completed | installed and opened | working | working | working |
| Linux (x86_64) | completed | installed and opened | working | working | working |
| macOS — Apple Silicon (arm64) | completed | installed and opened | working | working | working |
| macOS — Intel (x86_64) | completed | installed and opened | working | working | working |

## What this establishes

- The **published download path works on all four platform tracks** — the step that was `[OPEN]` in the
  release ladder until today. Nothing on the delivery chain fails silently per-platform.
- The **desktop app installs and launches** on every track, and its **UI is live** (buttons respond), not
  an empty shell. This is the class of defect that previously shipped a page whose script died on one bad
  line, and an app that opened empty because it read `HOME` on Windows.
- The **installed agent is functional**, not mute — the failure mode where a paid install landed an agent
  with no shell, no skills and no provider key is not present on any of the four machines.
- The **updater works** from a customer machine, which was only ever proven from a CLI in source before.

## What this does NOT establish

- **It is not a pass of the runtime acceptance standard.** The ten-item deep run (typed-state write,
  automatic exhale, supersession, retrieval surfaces, evidence-verified action, duplicate/retry, restart
  continuity) has still not been re-executed unchanged against this release line. That run's last complete
  record is 1.0.41 (2026-10-01), with its defect list.
- **It does not certify the paid carrier end to end.** The paid lane's own wheel/lock mismatch is a separate
  open item; a successful customer install does not prove the entitlement chain.
- **The download source was not instrumented.** On 2026-10-19 the two published sources served
  `free-v1.0.48` (GitHub release, four platform bundles + `SHA256SUMS`) and the site manifest at revision
  `79c6fa2b` / wheel `1.0.49` (four platform bundles). The four tracks are the claim here; pinning the exact
  wheel per machine is a follow-up, not a substitute for the pass.

## Why this is recorded at all

Because the repository has repeatedly paid for green-but-unchanged claims: a green gate over an
out-of-scope directory, a version-string comparison that said "up to date" forever, an installer that
judged success on an exit code after silently skipping the artifact it was supposed to install. The
counter-discipline is to record what was actually run, on what, by whom — and to name what is still open
in the same breath.

Artifact-level detail for the deeper run remains the 2026-10-01 record. This document closes the install
and delivery step of the release ladder, and nothing more.
