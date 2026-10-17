# Free install — agent only

The free lane is **the agent**: terminal chat, or connect it to Telegram. It does **not** include the desktop app, and the app has no free download.

Bring your own model key. Nothing is proxied through CEM888 — the agent talks to the provider you choose.

```bash
curl -fsSL https://raw.githubusercontent.com/CEM888AI/cem888/main/install/free.sh | bash
```

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
| Linux x86_64 | `cem888-free-v1.0.47-linux-x86_64.tar.gz` |
| macOS Apple silicon | `cem888-free-v1.0.47-darwin-arm64.tar.gz` |
| macOS Intel | `cem888-free-v1.0.47-darwin-x86_64.tar.gz` |

Each bundle carries the engine wheel, the signed dependency lock for that platform, and the vendored wheels.

**The engine ships as CPython 3.14 bytecode — there is no `.py` source in the bundle.** The rest of the runtime source stays proprietary; what you get is the same artefact a customer install receives.

## How the install stays honest

- **No package index, ever.** Dependencies come from `requirements-lock.hashes.txt` inside the bundle, installed with `--require-hashes --no-index --find-links`. The engine wheel lands with `--no-deps` so the lock stays the single authority.
- **Checksum before extraction.** The bundle is verified against `SHA256SUMS` from the release; a mismatch aborts.
- **Python 3.14 is provisioned with `uv`** if you don't have it, and the venv lives at `~/.cem888/venv`, not in your system Python.
- **The model id is checked against the provider.** After you paste a key, the installer reads that provider's own model list. If the suggested model isn't offered, it shows you what is and lets you pick — so a guessed model name can never leave you with a broken install.

Everything lands under `~/.cem888/` and can be removed by deleting that directory.

## Uninstall

```bash
rm -rf ~/.cem888
```

## Windows

The Windows vendor bundle is published, but **the PowerShell installer is not in this release yet** — it is not tested end to end, and shipping an untested installer is worse than shipping none. Windows support lands when that script has actually been run on a Windows box.

## Licence

The runtime is proprietary and licensed under the [CEM888 Source-Available Commercial License](../LICENSE): free for personal, non-commercial use. Business production use, paid client work, embedding, resale, white-labeling, OEM distribution and hosted service require a licence key or a commercial licence — **creator@cem888.ai**.
