#!/usr/bin/env bash
# CEM888 — free agent UPDATE (macOS / Linux)
# Updates an agent installed from GitHub (install/free.sh) to the newest free
# release. Agent only: no desktop app. Nothing you made is touched: config.yaml,
# .env (your keys), authority.json, memories and your own skills stay exactly
# as they are. New starter skills are added; existing ones are never overwritten.
#
#   curl -fsSL https://raw.githubusercontent.com/CEM888AI/cem888/main/install/update.sh | bash
#   cem888 update            (once this updater has run one time)
#
# Options:  --check  report only   --force  reinstall even if current
#
# Like the installer, nothing installs from a remote index: dependencies come
# from the signed per-platform lock inside the release bundle, checksum-verified.

set -euo pipefail

# CEM888-GITHUB-FREE-UPDATER  (marker: lets the installer recognise its own updater)
REPO="CEM888AI/cem888"
RAW="https://raw.githubusercontent.com/${REPO}/main/install/update.sh"

C_CYAN='\033[38;2;58;219;232m'; C_CORAL='\033[38;2;255;138;107m'
C_DIM='\033[2m'; C_B='\033[1m'; C_N='\033[0m'
say()  { printf "  %b\n" "$*"; }
head1(){ printf "\n${C_CORAL}%s${C_N}\n" "$1"; }
ok()   { printf "  ${C_CYAN}✓${C_N} %b\n" "$*"; }
die()  { printf "\n  ${C_CORAL}✗${C_N} %b\n" "$*" >&2; exit 1; }

CHECK=0; FORCE=0
for a in "$@"; do
  case "$a" in
    --check) CHECK=1 ;;
    --force) FORCE=1 ;;
    -*) die "unknown option: $a" ;;
    *) : ;;  # `cem888 update` passes the profile name; the engine is shared, so every profile is updated
  esac
done

# ── 1. find the install ───────────────────────────────────────────────────────
ANCHOR="${CEM888_HOME:-$HOME/.cem888}"
case "$ANCHOR" in */profiles/*) ANCHOR="${ANCHOR%/profiles/*}" ;; esac
VENV="$ANCHOR/venv"
[ -x "$VENV/bin/python" ] || die "no free agent found at $ANCHOR.
    Install one:  curl -fsSL https://raw.githubusercontent.com/${REPO}/main/install/free.sh | bash"
ls -d "$ANCHOR"/free/v*/ >/dev/null 2>&1 || die "the agent at $ANCHOR was not installed from GitHub.
    Update it from where you installed it (cem888.ai installs: cem888 update)."

CUR="$("$VENV/bin/python" -c 'import importlib.metadata as m; print(m.version("cem888-agent"))' 2>/dev/null)" \
  || die "could not read the installed engine version from $VENV."

OS="$(uname -s)"; ARCH="$(uname -m)"
case "$OS" in
  Linux)  [ "$ARCH" = "x86_64" ] || die "Only linux-x86_64 is published (found $ARCH)."; PLAT=linux-x86_64 ;;
  Darwin) case "$ARCH" in
            arm64) PLAT=darwin-arm64 ;;
            x86_64) PLAT=darwin-x86_64 ;;
            *) die "unsupported macOS arch: $ARCH" ;;
          esac ;;
  *) die "unsupported OS: $OS (Windows: use install/free.ps1)" ;;
esac

# ── 2. newest published free release ─────────────────────────────────────────
head1 "Checking for a newer free agent"
NEW="${CEM888_FREE_VERSION:-}"
if [ -z "$NEW" ]; then
  NEW="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases?per_page=30" 2>/dev/null \
    | "$VENV/bin/python" -c '
import json, sys
for r in json.load(sys.stdin):
    t = r.get("tag_name", "")
    if t.startswith("free-v") and not r.get("draft") and not r.get("prerelease"):
        print(t[len("free-v"):]); break
' 2>/dev/null)" || true
fi
[ -n "$NEW" ] || die "could not reach GitHub to find the newest release. Check your network and re-run."

NEWER="$("$VENV/bin/python" -c '
import sys
v = lambda s: tuple(int(p) for p in s.split(".") if p.isdigit())
print(1 if v(sys.argv[2]) > v(sys.argv[1]) else 0)' "$CUR" "$NEW")"
say "installed: ${C_B}${CUR}${C_N}   newest: ${C_B}${NEW}${C_N}"
if [ "$NEWER" != 1 ] && [ "$FORCE" != 1 ]; then ok "already up to date"; CHECK=2; fi
if [ "$CHECK" = 1 ]; then say "update available — run without --check to install it"; exit 0; fi

# ── 3. the updater installs itself, so `cem888 update` works from now on ─────
# Before this file existed a GitHub install had no updater on disk, so
# `cem888 update` fell through to a PyPI upgrade of a package name CEM888 does
# not publish there. Placing it (and stamping the method) routes that command
# here instead. A different updater already in place (a cem888.ai install) is
# never replaced.
mkdir -p "$ANCHOR/scripts"
SHIM="$ANCHOR/scripts/cem888-update.sh"
if [ ! -e "$SHIM" ] || grep -q "CEM888-GITHUB-FREE-UPDATER" "$SHIM" 2>/dev/null; then
  cat > "$SHIM" <<SH
#!/usr/bin/env bash
# CEM888-GITHUB-FREE-UPDATER shim — always runs the newest published updater.
exec bash <(curl -fsSL "${RAW}") "\$@"
SH
  chmod 755 "$SHIM"
  [ -s "$ANCHOR/.install_method" ] || printf 'bundle\n' > "$ANCHOR/.install_method"
  ok "\`cem888 update\` now runs this updater"
fi
[ "$CHECK" = 2 ] && exit 0

# ── 4. refuse to swap the engine under a running agent ───────────────────────
if pgrep -f "$VENV/bin/" >/dev/null 2>&1 && [ "$FORCE" != 1 ]; then
  die "an agent from this install is running. Stop it first (exit the chat / stop the gateway), then re-run.
    Or re-run with --force to update anyway."
fi

# ── 5. download + verify ─────────────────────────────────────────────────────
BUNDLE="$ANCHOR/free/v${NEW}"
BASE_DL="https://github.com/${REPO}/releases/download/free-v${NEW}"
PKG="cem888-free-v${NEW}-${PLAT}.tar.gz"
head1 "Downloading free agent ${NEW} (${PLAT})"
mkdir -p "$BUNDLE"
if [ -f "$BUNDLE/.complete" ]; then
  ok "bundle already present"
else
  curl -fL --progress-bar "$BASE_DL/SHA256SUMS" -o "$BUNDLE/SHA256SUMS" || die "could not reach the release."
  want="$(grep " ${PKG}\$" "$BUNDLE/SHA256SUMS" | awk '{print $1}')"
  [ -n "$want" ] || die "no checksum published for ${PKG}."
  curl -fL --progress-bar "$BASE_DL/$PKG" -o "$BUNDLE/$PKG" || die "download failed."
  if command -v sha256sum >/dev/null 2>&1; then got="$(sha256sum "$BUNDLE/$PKG" | awk '{print $1}')"
  else got="$(shasum -a 256 "$BUNDLE/$PKG" | awk '{print $1}')"; fi
  [ "$got" = "$want" ] || { rm -f "$BUNDLE/$PKG"; die "checksum mismatch on ${PKG} — refusing to install."; }
  ok "checksum verified"
  tar -xzf "$BUNDLE/$PKG" -C "$BUNDLE"
  rm -f "$BUNDLE/$PKG"
  : > "$BUNDLE/.complete"
fi

# ── 6. install into the existing engine venv ─────────────────────────────────
head1 "Updating"
boots() { CEM888_HOME="$1" "$VENV/bin/python" -c "from agent.authority import load_agent_authority; load_agent_authority(required=True)" >/dev/null 2>&1; }
# Only an agent that boots NOW must boot after: one already broken before the
# update is reported, never allowed to block (or roll back) everyone else's.
PROFILES=(); PRE_OK=" "
[ -f "$ANCHOR/config.yaml" ] && PROFILES+=("$ANCHOR")
for d in "$ANCHOR"/profiles/*/; do [ -f "$d/config.yaml" ] && PROFILES+=("${d%/}"); done
[ "${#PROFILES[@]}" -gt 0 ] || say "${C_DIM}no agent profiles found — engine updated only${C_N}"
for P in ${PROFILES[@]+"${PROFILES[@]}"}; do boots "$P" && PRE_OK="$PRE_OK$P "; done
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
command -v uv >/dev/null 2>&1 || die "uv is not on PATH (the installer put it in ~/.local/bin). Open a new shell and re-run."
OLD_WHEEL="$(ls "$ANCHOR/free/v${CUR}"/installer/cem888_agent-*.whl 2>/dev/null | head -1 || true)"
HIST="$ANCHOR/free/update-history.log"

rollback() {
  if [ -n "$OLD_WHEEL" ]; then
    uv pip install -q --python "$VENV/bin/python" --no-index --no-deps --reinstall \
      --find-links "$ANCHOR/free/v${CUR}/vendor" "$OLD_WHEEL" >/dev/null 2>&1 \
      && say "${C_CORAL}rolled back to ${CUR}${C_N}"
  fi
  printf '%s %s -> %s FAILED (%s)\n' "$(date -u +%FT%TZ)" "$CUR" "$NEW" "$1" >> "$HIST"
  die "$1"
}

uv pip install -q --python "$VENV/bin/python" --no-index \
  --find-links "$BUNDLE/vendor" --require-hashes \
  -r "$BUNDLE/installer/requirements-lock.hashes.txt" >/dev/null \
  || rollback "dependency install failed (no index, lock only)"
ok "dependencies updated from the signed lock"
uv pip install -q --python "$VENV/bin/python" --no-index --no-deps --reinstall \
  --find-links "$BUNDLE/vendor" "$BUNDLE"/installer/cem888_agent-*.whl >/dev/null \
  || rollback "engine wheel install failed"
ok "engine ${NEW} installed"

# ── 7. every agent on this machine: new skills + prove it still boots ────────

SKILLS_SRC="$BUNDLE/starter-skills"
for P in ${PROFILES[@]+"${PROFILES[@]}"}; do
  name="$(basename "$P")"; [ "$P" = "$ANCHOR" ] && name="default"
  s_new=0
  if [ -d "$SKILLS_SRC" ]; then
    while IFS= read -r f; do
      rel="${f#"$SKILLS_SRC"/}"; rel="${rel%/SKILL.md}"
      [ -n "$rel" ] || continue
      [ -f "$P/skills/$rel/SKILL.md" ] && continue   # never overwrite your edits
      mkdir -p "$P/skills/$rel"
      cp -R "$(dirname "$f")/." "$P/skills/$rel/" 2>/dev/null || true
      s_new=$((s_new+1))
    done < <(find "$SKILLS_SRC" -name SKILL.md -type f 2>/dev/null)
  fi
  case "$PRE_OK" in
    *" $P "*) : ;;
    *) say "${C_CORAL}${name}: did not boot before this update either — left as it was${C_N} (run: cem888 -p ${name} doctor)"; continue ;;
  esac
  BOOT_CODE=0
  BOOT_OUT="$(CEM888_HOME="$P" "$VENV/bin/python" -c "from agent.authority import load_agent_authority; load_agent_authority(required=True)" 2>&1)" || BOOT_CODE=$?
  if [ "$BOOT_CODE" -ne 0 ]; then
    printf '%s\n' "$BOOT_OUT" | tail -5 | sed 's/^/    /'
    rollback "agent '${name}' does not boot on ${NEW}"
  fi
  ok "${name}: boots on ${NEW}  (${s_new} new skills)"
done

# ── 8. receipt + tidy (keep this release and the one before, for rollback) ──
printf '%s %s -> %s ok\n' "$(date -u +%FT%TZ)" "$CUR" "$NEW" >> "$HIST"
for d in "$ANCHOR"/free/v*/; do
  v="$(basename "$d")"
  [ "$v" = "v${NEW}" ] || [ "$v" = "v${CUR}" ] || rm -rf "$d"
done

printf "\n${C_CYAN}Updated.${C_N}  ${C_B}${CUR} -> ${NEW}${C_N}\n"
say "receipt: $HIST"
say "restart any running chat or gateway to use the new engine."
say "${C_DIM}next time, just run: cem888 update${C_N}"
