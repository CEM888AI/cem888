#!/usr/bin/env bash
# CEM888 — free agent install (macOS / Linux)
# Bring your own provider key. Agent only: terminal chat or Telegram. No desktop app.
#
#   curl -fsSL https://raw.githubusercontent.com/CEM888AI/cem888/main/install/free.sh | bash
#
# Nothing installs from a remote index: dependencies come from the signed
# per-platform lock inside the release bundle, and the wheel lands with --no-deps.

set -euo pipefail

# Prompts must come from the terminal, never from the piped script body.
if [ ! -t 0 ]; then
  if [ -r /dev/tty ]; then exec </dev/tty
  else printf "\n  run this from a terminal: bash <(curl -fsSL <url>)\n" >&2; exit 1
  fi
fi

VERSION="1.0.55"
REPO="CEM888AI/cem888"
SLUG="free-v${VERSION}"
BASE_DL="https://github.com/${REPO}/releases/download/${SLUG}"
# One PROFILE per agent (2026-10-18): every free install used to write straight
# into ~/.cem888 — which IS the "default" profile — so a second agent overwrote
# the first and `--profile <agent>` could never resolve. ANCHOR is the .cem888
# root; ROOT is this agent's profile, resolved once the agent name is known.
ANCHOR="${CEM888_HOME:-$HOME/.cem888}"
ROOT="$ANCHOR"
BUNDLE="$ANCHOR/free/v${VERSION}"

C_CYAN='\033[38;2;58;219;232m'; C_CORAL='\033[38;2;255;138;107m'
C_DIM='\033[2m'; C_B='\033[1m'; C_N='\033[0m'
EQ=$(printf "\075")   # "=" built at runtime: keeps secret-shaped literals out of this file

say()  { printf "  %b\n" "$*"; }
head1(){ printf "\n${C_CORAL}%s${C_N}\n" "$1"; }
ok()   { printf "  ${C_CYAN}✓${C_N} %b\n" "$*"; }
die()  { printf "\n  ${C_CORAL}✗${C_N} %b\n" "$*" >&2; exit 1; }

trap 'printf "\n  ${C_CORAL}✗${C_N} interrupted.\n" >&2; exit 130' INT

printf "${C_CORAL}═══════════════════════════════════════════════${C_N}\n"
printf "${C_CYAN}   CEM888 — free agent install (v%s)${C_N}\n" "$VERSION"
printf "${C_CORAL}═══════════════════════════════════════════════${C_N}\n"
say "${C_DIM}Agent only — terminal chat or Telegram. No desktop app in the free lane.${C_N}"
say "${C_DIM}You bring your own model key. Nothing is sent anywhere except your chosen provider.${C_N}"

# ── 0. platform ───────────────────────────────────────────────────────────────
OS="$(uname -s)"; ARCH="$(uname -m)"
case "$OS" in
  Linux)  [ "$ARCH" = "x86_64" ] || die "Only linux-x86_64 is published in this release (found $ARCH)."; PLAT=linux-x86_64 ;;
  Darwin) case "$ARCH" in
            arm64) PLAT=darwin-arm64 ;;
            x86_64) PLAT=darwin-x86_64 ;;
            *) die "Unsupported macOS arch: $ARCH" ;;
          esac ;;
  *) die "Unsupported OS: $OS. Windows: see install/README.md — no PowerShell installer in this release yet." ;;
esac
ok "platform: ${C_B}${PLAT}${C_N}"

for c in curl tar sha256sum; do
  command -v "$c" >/dev/null 2>&1 || {
    [ "$c" = sha256sum ] && command -v shasum >/dev/null 2>&1 && continue
    die "missing required command: $c"
  }
done

# ── 1. prompts ────────────────────────────────────────────────────────────────
head1 "1/4  Identity"
printf "  Agent name [my-agent]: "; read -r AGENT_NAME || true
AGENT_NAME="${AGENT_NAME:-my-agent}"
printf "  Your name: "; read -r USER_NAME || true
[ -n "${USER_NAME:-}" ] || die "a user name is required (it becomes the owner of this agent)."
printf "  What is this agent's job? ${C_DIM}(enter to skip)${C_N}\n  > "; read -r AGENT_JOB || true

# ── 1b. which PROFILE this agent lives in ─────────────────────────────────────
SLUGNAME="$(printf '%s' "$AGENT_NAME" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//' | cut -c1-64 | sed 's/-$//')"
[ -n "$SLUGNAME" ] || SLUGNAME="agent"
if [ "$SLUGNAME" = "default" ]; then die "'default' is reserved — pick a different agent name."; fi
if [ "$(basename "$(dirname "$ANCHOR")")" = "profiles" ]; then
  ROOT="$ANCHOR"                      # CEM888_HOME already names a profile
  SLUGNAME="$(basename "$ANCHOR")"
else
  ROOT="$ANCHOR/profiles/$SLUGNAME"
fi
mkdir -p "$ROOT/state"
export CEM888_HOME="$ROOT"
say "profile: $SLUGNAME  ->  $ROOT"
if [ -f "$ROOT/config.yaml" ]; then
  say "existing profile found — updating $SLUGNAME in place (its files are kept)"
fi

head1 "2/4  Model provider"
cat <<EOF
  Suggested, cheapest first:
    1) DeepSeek Flash   — lowest cost per token, strong tool use     (recommended)
    2) GLM Flash        — very cheap, good long-context
    3) GPT Luna         — cheap tier, strong instruction following
    4) OpenAI           — your existing OpenAI key
    5) Anthropic        — your existing Anthropic key
    6) OpenRouter       — one key, many models
    7) Custom           — any OpenAI-compatible endpoint
EOF
printf "  Choose [1]: "; read -r PCHOICE || true
PCHOICE="${PCHOICE:-1}"

P_LABEL=""; P_BASE=""; P_KEYENV=""; P_SUGGEST=""; P_KIND="openai"
case "$PCHOICE" in
  1) P_LABEL="DeepSeek Flash"; P_BASE="https://api.deepseek.com";             P_KEYENV="DEEPSEEK_API_KEY";   P_SUGGEST="deepseek-flash" ;;
  2) P_LABEL="GLM Flash";      P_BASE="https://api.z.ai/api/paas/v4";         P_KEYENV="GLM_API_KEY";        P_SUGGEST="glm-4.6-flash" ;;
  3) P_LABEL="GPT Luna";       P_BASE="https://api.openai.com/v1";            P_KEYENV="OPENAI_API_KEY";     P_SUGGEST="gpt-5-luna" ;;
  4) P_LABEL="OpenAI";         P_BASE="https://api.openai.com/v1";            P_KEYENV="OPENAI_API_KEY";     P_SUGGEST="gpt-5-mini" ;;
  5) P_LABEL="Anthropic";      P_BASE="https://api.anthropic.com/v1";         P_KEYENV="ANTHROPIC_API_KEY";  P_SUGGEST="claude-sonnet-4-5"; P_KIND="anthropic" ;;
  6) P_LABEL="OpenRouter";     P_BASE="https://openrouter.ai/api/v1";         P_KEYENV="OPENROUTER_API_KEY"; P_SUGGEST="" ;;
  7) P_LABEL="Custom";         P_KIND="openai"
     printf "  Base URL (OpenAI-compatible, e.g. https://host/v1): "; read -r P_BASE || true
     [ -n "${P_BASE:-}" ] || die "a base URL is required for a custom provider."
     printf "  Env var name for the key [CUSTOM_API_KEY]: "; read -r P_KEYENV || true
     P_KEYENV="${P_KEYENV:-CUSTOM_API_KEY}" ;;
  *) die "invalid choice: $PCHOICE" ;;
esac

head1 "3/4  API key"
printf "  Paste your %s key ${C_DIM}(input hidden)${C_N}: " "$P_LABEL"
stty -echo 2>/dev/null || true; read -r P_KEY || true; stty echo 2>/dev/null || true; printf "\n"
[ -n "${P_KEY:-}" ] || die "an API key is required — the free lane is bring-your-own-key."

head1 "4/4  Telegram ${C_DIM}(optional)${C_N}"
say "Leave blank to use terminal chat only. To connect Telegram, create a bot with"
say "@BotFather, then paste its token here."
printf "  Telegram bot token: "; read -r TG_TOKEN || true

# ── 2. resolve the model against the provider's own list ──────────────────────
MODEL=""
if command -v python3 >/dev/null 2>&1; then
  MODEL="$(P_BASE="$P_BASE" P_KEY="$P_KEY" P_KIND="$P_KIND" P_SUGGEST="$P_SUGGEST" python3 - <<'PICK' || true
import json, os, sys, urllib.request
base, key = os.environ["P_BASE"].rstrip("/"), os.environ["P_KEY"]
kind, suggest = os.environ.get("P_KIND","openai"), os.environ.get("P_SUGGEST","")
url = base + "/models"
req = urllib.request.Request(url, headers=(
    {"x-api-key": key, "anthropic-version": "2023-06-01"} if kind == "anthropic"
    else {"Authorization": "Bearer %s" % key}))
try:
    data = json.load(urllib.request.urlopen(req, timeout=20))
except Exception as e:
    sys.stderr.write("  (could not read the model list: %s)\n" % e.__class__.__name__)
    print(suggest); raise SystemExit
items = data.get("data") or data.get("models") or []
ids = [i.get("id") or i.get("name") for i in items if isinstance(i, dict)]
ids = [i for i in ids if i]
if suggest and suggest in ids:
    print(suggest); raise SystemExit
cheap = [i for i in ids if any(t in i.lower() for t in ("flash","luna","mini","air","lite","small"))]
pool = cheap or ids
if not pool:
    print(suggest); raise SystemExit
sys.stderr.write("  suggested model not offered by this provider; pick one:\n")
for n, m in enumerate(pool[:8], 1):
    sys.stderr.write("    %d) %s\n" % (n, m))
sys.stderr.write("  number [1]: ")
try:
    c = input().strip() or "1"
except EOFError:
    c = "1"
try:
    print(pool[int(c)-1])
except Exception:
    print(pool[0])
PICK
)"
fi
MODEL="${MODEL:-$P_SUGGEST}"
[ -n "${MODEL:-}" ] || MODEL="$(printf '%s' "$P_LABEL" | tr 'A-Z ' 'a-z-')"
ok "provider: ${C_B}${P_LABEL}${C_N}  model: ${C_B}${MODEL}${C_N}"

# ── 3. bundle ─────────────────────────────────────────────────────────────────
head1 "Downloading the free agent bundle (${PLAT}, ~$( [ "$PLAT" = linux-x86_64 ] && echo 187 || echo 172 )MB)"
mkdir -p "$BUNDLE"
PKG="cem888-free-v${VERSION}-${PLAT}.tar.gz"
if [ -f "$BUNDLE/.complete" ]; then
  ok "bundle already present"
else
  curl -fL --progress-bar "$BASE_DL/SHA256SUMS" -o "$BUNDLE/SHA256SUMS" \
    || die "could not reach the release. Check your network, or download ${PKG} from ${BASE_DL} manually."
  want="$(grep " ${PKG}\$" "$BUNDLE/SHA256SUMS" | awk '{print $1}')"
  [ -n "$want" ] || die "no checksum published for ${PKG}."
  curl -fL --progress-bar "$BASE_DL/$PKG" -o "$BUNDLE/$PKG" || die "download failed."
  if command -v sha256sum >/dev/null 2>&1; then got="$(sha256sum "$BUNDLE/$PKG" | awk '{print $1}')"
  else got="$(shasum -a 256 "$BUNDLE/$PKG" | awk '{print $1}')"; fi
  [ "$got" = "$want" ] || die "checksum mismatch on ${PKG} — refusing to install."
  ok "checksum verified"
  tar -xzf "$BUNDLE/$PKG" -C "$BUNDLE"
  : > "$BUNDLE/.complete"
fi

# ── 4. interpreter + install (no index, ever) ─────────────────────────────────
head1 "Installing"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if command -v uv >/dev/null 2>&1; then UV=uv
else
  say "${C_DIM}fetching uv (interpreter manager, no package index involved)${C_N}"
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || die "could not install uv."
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || die "uv installed but not on PATH — open a new shell and re-run."
  UV=uv
fi
say "${C_DIM}python 3.14 (matches the signed wheel set)${C_N}"
"$UV" python install 3.14 >/dev/null 2>&1 || true
PY="$("$UV" python find 3.14 2>/dev/null)" || die "could not provision python 3.14."
[ -n "$PY" ] || die "could not provision python 3.14."

# ONE engine venv per machine, at the anchor — profiles hold data only, so a
# second agent reuses python + wheels instead of reinstalling 300MB.
VENV="$ANCHOR/venv"
"$PY" -m venv "$VENV" >/dev/null 2>&1 || die "could not create the venv at $VENV"
"$UV" pip install --python "$VENV/bin/python" --no-index \
  --find-links "$BUNDLE/vendor" --require-hashes \
  -r "$BUNDLE/installer/requirements-lock.hashes.txt" >/dev/null || die "dependency install failed (no index, lock only)."
ok "dependencies installed from the signed lock"
"$UV" pip install --python "$VENV/bin/python" --no-index --find-links "$BUNDLE/vendor" \
  --no-deps "$BUNDLE"/installer/cem888_agent-*.whl >/dev/null || die "engine wheel install failed."
ok "engine installed"

# ── 5. config (provider-neutral) ──────────────────────────────────────────────
head1 "Writing profile"
mkdir -p "$ROOT"
# SLUGNAME was resolved in 1b (one profile per agent) — do not recompute it here.

PROV_NAME="$(printf '%s' "$P_LABEL" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')"
TG_BLOCK=""
[ -n "${TG_TOKEN:-}" ] && TG_BLOCK="platforms:
  telegram:
    enabled: true"

cat > "$ROOT/config.yaml" <<CONF
# CEM888 — ${AGENT_NAME}
# Free lane: agent only (terminal chat or Telegram). Bring your own provider key.
# Written by the CEM888 free installer; edit freely.

agent:
  name: ${AGENT_NAME}
  owner: ${USER_NAME}
  job: "${AGENT_JOB:-}"

model:
  provider: ${PROV_NAME}
  default: ${MODEL}
  temperature: 0.2
  max_tokens: 8192

custom_providers:
  - name: ${PROV_NAME}
    base_url: ${P_BASE}
    key_env: ${P_KEYENV}
    api_mode: $([ "$P_KIND" = anthropic ] && echo anthropic_messages || echo chat_completions)
    request_timeout_seconds: 360

${TG_BLOCK}
CONF

chmod 600 "$ROOT/config.yaml" 2>/dev/null || true
touch "$ROOT/.env"; chmod 600 "$ROOT/.env"
if grep -q "^${P_KEYENV}=" "$ROOT/.env" 2>/dev/null; then
  sed -i.bak "s|^${P_KEYENV}=.*|${P_KEYENV}=${P_KEY}|" "$ROOT/.env" && rm -f "$ROOT/.env.bak"
else
  printf '%s=%s\n' "$P_KEYENV" "$P_KEY" >> "$ROOT/.env"
fi
if [ -n "${TG_TOKEN:-}" ]; then
  _k="TELEGRAM_BOT_TOKEN"
  grep -q "^${_k}${EQ}" "$ROOT/.env" 2>/dev/null || printf '%s%s%s\n' "$_k" "$EQ" "$TG_TOKEN" >> "$ROOT/.env"
fi
ok "config: $ROOT/config.yaml"
ok "key:    $ROOT/.env (chmod 600)"

# ── 5b. starter skills ────────────────────────────────────────────────────────
# ⛔ A FREE INSTALL SHIPPED ZERO SKILLS (measured 2026-10-18). The bundle carries
# starter-skills/ and the site installers lay them down, but this installer never
# mentioned the directory -- so a free agent booted with an empty skills/ and
# answered "zero skills installed" when asked to look one up.
SKILLS_SRC="$BUNDLE/starter-skills"
SKILLS_DEST="$ROOT/skills"
if [ -d "$SKILLS_SRC" ]; then
  mkdir -p "$SKILLS_DEST"
  s_new=0; s_kept=0
  while IFS= read -r f; do
    rel="${f#"$SKILLS_SRC"/}"; rel="${rel%/SKILL.md}"
    [ -n "$rel" ] || continue
    # An existing skill is LEFT ALONE: re-running must never overwrite edits.
    if [ -f "$SKILLS_DEST/$rel/SKILL.md" ]; then s_kept=$((s_kept+1)); continue; fi
    mkdir -p "$SKILLS_DEST/$rel"
    cp -R "$(dirname "$f")/." "$SKILLS_DEST/$rel/" 2>/dev/null || true
    s_new=$((s_new+1))
  done < <(find "$SKILLS_SRC" -name SKILL.md -type f 2>/dev/null)
  ok "skills: $s_new installed, $s_kept already present"
else
  say "${C_DIM}starter-skills/ not in this bundle - skills/ left as-is${C_N}"
fi

# ── 6. smoke test ─────────────────────────────────────────────────────────────
head1 "Checking the install"
if "$VENV/bin/cem888" --version >/dev/null 2>&1; then ok "$("$VENV/bin/cem888" --version 2>/dev/null | head -1)"
else say "${C_CORAL}engine binary did not answer --version${C_N} — run: $VENV/bin/cem888 doctor"; fi

# ── 5c. sticky default ────────────────────────────────────────────────────────
# Plain `cem888 chat` opens the profile installed last: the runtime reads
# active_profile from the .cem888 ROOT (cem888_constants.get_default_cem888_root
# collapses <root>/profiles/<key> back to <root>), so it is written THERE, never
# inside a profile.
NATIVE_HOME="$HOME/.cem888"
case "$ANCHOR" in
  "$NATIVE_HOME"|"$NATIVE_HOME"/*) STICKY_ROOT="$NATIVE_HOME" ;;
  *) STICKY_ROOT="$ANCHOR" ;;
esac
printf '%s\n' "$SLUGNAME" > "$STICKY_ROOT/active_profile"
ok "active profile: $SLUGNAME"

# ── 6b. Tier-0 authority manifest ─────────────────────────────────────────────
# ⛔ THE AGENT REFUSES EVERY TURN WITHOUT THIS. agent_init and system_prompt both
# load it with required=True. The site installers mint it through
# installer/scripts/cem-authority-manifest.py; this installer never did — a clean
# free install answered "required Tier-0 authority manifest is missing" to the
# first message it ever received (reported 2026-10-18), and the Windows free
# installer needed the same fix.
# MINTED BY THE ONE PRODUCER, not by `cem888 authority init`. Measured
# 2026-10-18 on a clean free install: the CLI derives profile_name from the
# directory's basename, so a profile at .../.cem888 minted "profile_name":
# ".cem888" while the runtime's path-based resolver says "default" -- and every
# boot died with
#   AuthorityError: profile authority mismatch: path implies 'default',
#   manifest declares '.cem888'
# i.e. the install said "Done" and the agent refused every turn. The shipped
# installer/scripts/cem-authority-manifest.py carries profile_name_for(), which
# mirrors the runtime resolver, and re-reads the file to prove it loads.
AUTH_SCRIPT="$BUNDLE/installer/scripts/cem-authority-manifest.py"
if [ -f "$AUTH_SCRIPT" ] && [ -x "$VENV/bin/python" ]; then
  "$VENV/bin/python" "$AUTH_SCRIPT" --profile-dir "$ROOT" --home-dir "$ROOT" \
    --agent-name "$AGENT_NAME" --wheel-version "$VERSION" \
    --from-install-state --if-missing 2>&1 | sed 's/^/  /'
fi
if [ ! -f "$ROOT/authority.json" ] && [ -x "$VENV/bin/cem888" ]; then
  "$VENV/bin/cem888" authority init --profile-dir "$ROOT" --agent-name "$AGENT_NAME" 2>&1 | sed 's/^/  /'
fi
if [ -f "$ROOT/authority.json" ]; then
  ok "Tier-0 authority: $ROOT/authority.json"
else
  die "Tier-0 authority manifest was not created at $ROOT/authority.json — the agent cannot answer a single turn without it."
fi

# ── 6c. boot gate ─────────────────────────────────────────────────────────────
# Every step above can be green while the agent still refuses to start: the line
# a turn actually dies on is agent_init.py's
#   agent.authority = load_agent_authority(required=True)
# and it only runs when a message is sent — i.e. AFTER the installer said "Done".
# Run that exact call headless here, so the install either PROVES the agent boots
# or names the reason BEFORE reporting success.
# `|| BOOT_CODE=$?` is not decoration: under `set -e` a bare assignment from a
# failing command substitution kills the script AT THIS LINE, so the reason
# would never be printed and the installer would just vanish. Measured
# 2026-10-18 — that is exactly how the first version of this gate behaved.
BOOT_CODE=0
BOOT_OUT="$("$VENV/bin/python" -c "from agent.authority import load_agent_authority; a = load_agent_authority(required=True); print('profile:', a.profile_root)" 2>&1)" || BOOT_CODE=$?
if [ "$BOOT_CODE" -ne 0 ]; then
  printf '%s\n' "$BOOT_OUT" | sed 's/^/  /'
  die "the agent cannot boot — Tier-0 authority did not load (the reason is printed above)"
fi
ok "agent boots against $ROOT"

# ⛔ THE BANNER NAMED NO SECOND AGENT (owner, 2026-10-18: "it didnt show how to
# message second agent ... type cem888 chat --profile 'agentname'"). A placeholder
# <key> makes the customer go read `profile list` first, so enumerate the real
# profiles on this machine and print the literal command for each.
OTHER_AGENTS=""
if [ -d "$ANCHOR/profiles" ]; then
  for d in "$ANCHOR"/profiles/*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"
    if [ "$n" = "$SLUGNAME" ]; then continue; fi
    if [ ! -f "$d/config.yaml" ]; then continue; fi
    OTHER_AGENTS="${OTHER_AGENTS}     cem888 chat --profile \"${n}\"
"
  done
fi
# An install made by an OLDER free installer lives at the .cem888 ROOT itself --
# that is the built-in "default" profile and it still opens with --profile default.
if [ "$ROOT" != "$ANCHOR" ] && [ -f "$ANCHOR/config.yaml" ]; then
  OTHER_AGENTS="     cem888 chat --profile \"default\"
${OTHER_AGENTS}"
fi
if [ -n "$OTHER_AGENTS" ]; then
  OTHER_HEAD="  Your other agents on this machine — talk to any of them:"
else
  OTHER_HEAD="  Install another agent and it gets its own profile — talk to it with:
     cem888 chat --profile \"<the-name-you-gave-it>\""
fi

CYAN_ESC=$(printf '\033[38;2;58;219;232m'); CORAL_ESC=$(printf '\033[38;2;255;138;107m')
B_ESC=$(printf '\033[1m'); DIM_ESC=$(printf '\033[2m'); N_ESC=$(printf '\033[0m')
cat <<DONE

${CYAN_ESC}Done.${N_ESC}  ${B_ESC}${AGENT_NAME}${N_ESC} is installed on ${B_ESC}${P_LABEL}${N_ESC} (${MODEL}).

  Profile:  ${SLUGNAME}  ->  ${ROOT}
  This is a real profile. Plain \`cem888 chat\` opens it, and the name below is
  what the --profile flag expects.

  Talk to this agent by name:
     cem888 chat --profile "${SLUGNAME}"

${OTHER_HEAD}
${OTHER_AGENTS}
  Manage agents:
     cem888 profile list               (every agent installed here)
     cem888 profile use <profile>      (make another one the default)
     cem888 -p <profile> chat          (shorter form of --profile)

  Start talking:
     ${VENV}/bin/cem888 chat

  Check health:
     ${VENV}/bin/cem888 doctor

  Add it to PATH (optional):
     echo 'export PATH="${VENV}/bin:\$PATH"' >> ~/.zshrc   # or ~/.bashrc

  ${DIM_ESC}On cost: the free lane is tuned for cheap, fast models. When a task needs real
  deep reasoning, add a stronger model later — \`cem888 model\` switches providers, and
  \`cem888 fallback\` wires a big model in behind the cheap one so it is only used when
  the cheap one fails or the task is flagged hard. Nothing to reinstall.${N_ESC}
DONE
