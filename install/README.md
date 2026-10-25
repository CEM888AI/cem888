# Free agent install — agent only, no desktop app, no subscription

> **The free agent is supported, and there are two places to get it:** the free account at **[cem888.ai](https://cem888.ai)** — no payment — or this repository's [releases](https://github.com/CEM888AI/cem888/releases). These scripts install **the agent only**: no desktop app, no subscription. The **paid desktop app** is cem888.ai only and is **not** published on GitHub.

The free lane is **the agent**: terminal chat, or connect it to Telegram. It does **not** include the desktop app, and the app has no free download.

Bring your own model key. Nothing is proxied through CEM888 — the agent talks to the provider you choose.

```bash
curl -fsSL https://raw.githubusercontent.com/CEM888AI/cem888/main/install/free.sh | bash
```

### Windows (PowerShell, x86_64)

```powershell
irm https://raw.githubusercontent.com/CEM888AI/cem888/main/install/free.ps1 | iex
```

Same five prompts as the shell installer. Windows 10 1803 or newer. **Not yet accepted on real
Windows hardware** — the first acceptance run is pending, and this line changes when it passes or
fails. Windows arm64 is not in this release: the published wheel set is `windows-amd64`.

## What it asks you

Five prompts, in this order:

1. **Agent name** — what you want to call it.
2. **Your name** — becomes the owner in the profile.
3. **What is this agent's job?** — press enter to skip.
4. **Provider** — suggested cheapest-first:
   - **DeepSeek Flash** — lowest cost per token, strong tool use *(recommended)*
   - **GLM Flash** — very cheap, good long context
   - **GPT Luna** — cheap tier, strong instruction following
   - Also: OpenAI · Anthropic · OpenRouter · any OpenAI-compatible endpoint
5. **API key** — hidden input, written to `~/.cem888/.env` with mode `600`.

Telegram bot token is optional; leave it blank for terminal-only.

## Why the suggested models are the cheap ones

Most of an agent's turns are cheap: tool calls, file reads, short replies. Paying frontier prices for those is how people burn a budget in a week. The free lane is tuned for cheap, fast models on purpose.

When a task genuinely needs deep reasoning, you do not reinstall anything:

```bash
cem888 model        # switch default provider/model
cem888 fallback     # wire a big model in behind the cheap one
```

A fallback is only reached when the primary fails or the task is flagged hard — so the strong model costs you money only when it earns it.

## What it downloads

One release asset per platform (~170–190MB), plus `SHA256SUMS`:

| Platform | Bundle |
| --- | --- |
| Linux x86_64 | `cem888-free-v<version>-linux-x86_64.tar.gz` |
| macOS Apple silicon | `cem888-free-v<version>-darwin-arm64.tar.gz` |
| macOS Intel | `cem888-free-v<version>-darwin-x86_64.tar.gz` |
| Windows x86_64 | `cem888-free-v<version>-windows-amd64.tar.gz` |

The installer takes the newest `free-v*` release ([latest](https://github.com/CEM888AI/cem888/releases/latest)); set `CEM888_FREE_VERSION=1.0.55` to pin one.

Each bundle carries the engine wheel, the signed dependency lock for that platform, and the vendored wheels.

**The engine ships as CPython 3.14 bytecode — there is no engine `.py` source in the bundle.** The rest of the runtime source stays proprietary; what you get is the same artefact a customer install receives.

## How the install stays honest

- **No package index, ever.** Dependencies come from `requirements-lock.hashes.txt` inside the bundle, installed with `--require-hashes --no-index --find-links`. The engine wheel lands with `--no-deps` so the lock stays the single authority.
- **Checksum before extraction.** The bundle is verified against `SHA256SUMS` from the release; a mismatch aborts.
- **Python 3.14 is provisioned with `uv`** if you don't have it, and the venv lives at `~/.cem888/venv`, not in your system Python.
- **The model id is checked against the provider.** After you paste a key, the installer reads that provider's own model list. If the suggested model isn't offered, it shows you what is and lets you pick — so a guessed model name can never leave you with a broken install.

Everything lands under `~/.cem888/` and can be removed by deleting that directory.

## Update

The free agent is maintained: fixes and new releases are published here regularly as `free-v*` releases, each with `SHA256SUMS`.

```bash
cem888 update
```

An install made before 2026-10-25 runs the updater once by hand; after that, `cem888 update` works:

```bash
curl -fsSL https://raw.githubusercontent.com/CEM888AI/cem888/main/install/update.sh | bash
```

`--check` reports whether a newer release exists without changing anything.

What the update does, in order:

- Finds the newest `free-v*` release and stops if you already have it.
- Downloads your platform's bundle and verifies it against `SHA256SUMS` before extracting.
- Refuses to swap the engine while an agent from this install is running (`--force` overrides).
- Installs the dependencies from the bundle's signed lock and the new engine wheel into `~/.cem888/venv`, with no package index.
- Leaves every agent's `config.yaml`, `.env` (your keys), `authority.json`, memories and skills untouched. New starter skills are added, and an existing skill is never overwritten.
- Proves each agent that booted before the update still boots after it. If one does not, the previous engine is put back.
- Writes a receipt line to `~/.cem888/free/update-history.log`, and keeps the previous release on disk for rollback.

Windows: a one-command updater is not published yet.

## Uninstall

```bash
rm -rf ~/.cem888
```

## Windows

The PowerShell installer **is** published: `install/free.ps1`, the same five-prompt flow as the shell
installer. It mints the Tier-0 authority manifest, refuses a malformed `CEM888_HOME` instead of
installing into a junk folder, installs a `cem888` shim so `cem888 chat` works in a new PowerShell
window, and runs the agent's own boot line (`load_agent_authority(required=True)`) before it reports
success — so a broken install fails with the reason instead of handing over a terminal that says
"Failed to initialize agent".

**It has not yet passed an end-to-end run on real Windows hardware.** The first acceptance run is
pending, and this section changes when it passes or fails. Shipping the script is honest; claiming
it is verified is not.

## Licence

The runtime is proprietary and licensed under the [CEM888 Source-Available Commercial License](../LICENSE): free for personal, non-commercial use. Business production use, paid client work, embedding, resale, white-labeling, OEM distribution and hosted service require a licence key or a commercial licence — **creator@cem888.ai**.
