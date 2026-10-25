<#
  CEM888 — free agent install (Windows)

    irm https://raw.githubusercontent.com/CEM888AI/cem888/main/install/free.ps1 | iex

  Bring your own provider key. Agent only: terminal chat or Telegram. No desktop app.
  Nothing installs from a remote index: dependencies come from the signed per-platform
  lock inside the release bundle, and the wheel lands with --no-deps.

  Mirrors install/free.sh: same four steps, same prompts, same provider table.
#>

[CmdletBinding()]
param(
  [string]$AgentName,
  [string]$UserName,
  [string]$AgentJob,
  [string]$Provider,
  [string]$ApiKey,
  [string]$TelegramToken
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

$Version = '1.0.55'
$Repo    = 'CEM888AI/cem888'
$Slug    = "free-v$Version"
$BaseDl  = "https://github.com/$Repo/releases/download/$Slug"
# An inherited CEM888_HOME is used ONLY when it is a real .cem888 home. Measured
# 2026-10-18: CEM888_HOME had been left as 'C:\Users\<n>.cem888' (separator
# missing), so the whole profile -- config, key, venv, everything -- was written
# into C:\Users\<n>.cem888, a directory next to the user folder rather than
# inside it, and the runtime then disagreed with the installer about where the
# profile lived. Reject a malformed value out loud and use the default.
$DefaultRoot = Join-Path $env:USERPROFILE '.cem888'
$Anchor = $DefaultRoot
if ($env:CEM888_HOME) {
  $candidate = $env:CEM888_HOME.Trim().TrimEnd('\')
  # A valid home is either the .cem888 root itself or an EXISTING profile dir
  # (<root>\profiles\<key>) -- both are accepted so an explicit override wins.
  if ([IO.Path]::IsPathRooted($candidate) -and `
      ((Split-Path $candidate -Leaf) -eq '.cem888' -or (Split-Path (Split-Path $candidate -Parent) -Leaf) -eq 'profiles')) {
    $Anchor = $candidate
  } else {
    Write-Host "  ! ignoring CEM888_HOME=$($env:CEM888_HOME) - not a .cem888 home; using $DefaultRoot"
  }
}
# ⛔ OLD SHAPE INSTALLED EVERY AGENT INTO THE DEFAULT PROFILE (2026-10-18).
# It wrote config.yaml/.env/venv straight into ~\.cem888 -- which IS the
# "default" profile -- so a SECOND free install wrote on top of the first, and
# `--profile <agent>` could never resolve because no profiles\<key> dir existed.
# Measured against the runtime: cem888_cli/profiles.py anchors named profiles at
# <root>\profiles\<key>, and cem888_cli/main.py::_apply_profile_override reads
# <root>\active_profile when no -p is given. So: one PROFILE PER AGENT, the
# engine/bundle shared once at the anchor, and active_profile naming the last one
# installed. Re-running with the same agent name updates that agent in place.
$Root = $Anchor
$Bundle  = Join-Path $Anchor "free\v$Version"
$Pkg     = "cem888-free-v$Version-windows-amd64.tar.gz"

$ESC = [char]27
$C_CYAN  = "$ESC[38;2;58;219;232m"   # #3ADBE8 - brand cyan
$C_CORAL = "$ESC[38;2;255;138;107m"  # #FF8A6B - brand coral
$C_DIM   = "$ESC[2m"; $C_B = "$ESC[1m"; $C_N = "$ESC[0m"

function Say  ($m) { Write-Host "  $m" }
function Head1($m) { Write-Host ""; Write-Host "  $C_CORAL$m$C_N" }
function Ok   ($m) { Write-Host "  $C_CYAN[ok] $m$C_N" }
function Die  ($m) { Write-Host ""; Write-Host "  $C_CORAL[x] $m$C_N"; exit 1 }

function Get-RemoteFile($Url, $Dest) {
  $dir = Split-Path -Parent $Dest
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
  if ($curl) {
    & curl.exe -fL --silent --show-error $Url -o $Dest
    if ($LASTEXITCODE -ne 0) { return $false }
  } else {
    try {
      [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
      Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing -ErrorAction Stop
    } catch { return $false }
  }
  return (Test-Path $Dest)
}

Write-Host "$C_CORAL$('=' * 53)$C_N"
Write-Host "   $C_CYAN CEM888 - free agent install (v$Version, windows-amd64)$C_N"
Write-Host "$C_CORAL$('=' * 53)$C_N"
Say "Agent only - terminal chat or Telegram. No desktop app in the free lane."
Say "You bring your own model key. Nothing is sent anywhere except your chosen provider."

# -- 0. platform ------------------------------------------------------------
if (-not [Environment]::Is64BitOperatingSystem) { Die "Only 64-bit Windows (windows-amd64) is published in this release." }
Ok "platform: windows-amd64"

$tar = Get-Command tar.exe -ErrorAction SilentlyContinue
if (-not $tar) { Die "tar.exe was not found. Windows 10 1803 or newer is required (it ships tar.exe)." }

# -- 1. prompts -------------------------------------------------------------
Head1 "1/4  Identity"
if (-not $AgentName) { $AgentName = Read-Host "  Agent name [my-agent]" }
if (-not $AgentName) { $AgentName = 'my-agent' }
if (-not $UserName) { $UserName = Read-Host "  Your name" }
if (-not $UserName) { Die "a user name is required (it becomes the owner of this agent)." }
if (-not $AgentJob) {
  Write-Host "  What is this agent's job? (enter to skip)"
  $AgentJob = Read-Host "  >"
}

# -- 1b. which PROFILE this agent lives in ----------------------------------
# Same slug rule the profile registry uses: lower-case, non-alphanumerics
# collapsed to '-', max 64 chars, must start with a letter/digit.
$SlugName = ($AgentName.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if (-not $SlugName) { $SlugName = 'agent' }
if ($SlugName.Length -gt 64) { $SlugName = $SlugName.Substring(0, 64).Trim('-') }
if ($SlugName -eq 'default') { Die "'default' is reserved - pick a different agent name." }

$ProfilesRoot = Join-Path $Anchor 'profiles'
if ((Split-Path (Split-Path $Anchor -Parent) -Leaf) -eq 'profiles') {
  # CEM888_HOME already names a profile dir: install exactly there.
  $Root = $Anchor
  $SlugName = Split-Path $Anchor -Leaf
  $ProfilesRoot = Split-Path $Anchor -Parent
} else {
  $Root = Join-Path $ProfilesRoot $SlugName
}
New-Item -ItemType Directory -Force -Path $Root | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Root 'state') | Out-Null
$env:CEM888_HOME = $Root
Say "profile: $SlugName  ->  $Root"
if (Test-Path (Join-Path $Root 'config.yaml')) {
  Say "existing profile found - updating $SlugName in place (its files are kept)"
}

Head1 "2/4  Model provider"
Write-Host @"
  Suggested, cheapest first:
    1) DeepSeek Flash   - lowest cost per token, strong tool use     (recommended)
    2) GLM Flash        - very cheap, good long-context
    3) GPT Luna         - cheap tier, strong instruction following
    4) OpenAI           - your existing OpenAI key
    5) Anthropic        - your existing Anthropic key
    6) OpenRouter       - one key, many models
    7) Custom           - any OpenAI-compatible endpoint
"@

if (-not $Provider) { $Provider = Read-Host "  Choose [1]" }
if (-not $Provider) { $Provider = '1' }

$PLabel = ''; $PBase = ''; $PKeyEnv = ''; $PSuggest = ''; $PKind = 'openai'
switch ($Provider.Trim()) {
  '1' { $PLabel='DeepSeek Flash'; $PBase='https://api.deepseek.com';      $PKeyEnv='DEEPSEEK_API_KEY';   $PSuggest='deepseek-flash' }
  '2' { $PLabel='GLM Flash';      $PBase='https://api.z.ai/api/paas/v4';  $PKeyEnv='GLM_API_KEY';        $PSuggest='glm-4.6-flash' }
  '3' { $PLabel='GPT Luna';       $PBase='https://api.openai.com/v1';     $PKeyEnv='OPENAI_API_KEY';     $PSuggest='gpt-5-luna' }
  '4' { $PLabel='OpenAI';         $PBase='https://api.openai.com/v1';     $PKeyEnv='OPENAI_API_KEY';     $PSuggest='gpt-5-mini' }
  '5' { $PLabel='Anthropic';      $PBase='https://api.anthropic.com/v1';  $PKeyEnv='ANTHROPIC_API_KEY';  $PSuggest='claude-sonnet-4-5'; $PKind='anthropic' }
  '6' { $PLabel='OpenRouter';     $PBase='https://openrouter.ai/api/v1';  $PKeyEnv='OPENROUTER_API_KEY'; $PSuggest='' }
  '7' {
    $PLabel = 'Custom'; $PKind = 'openai'
    if (-not $PBase) { $PBase = Read-Host "  Base URL (OpenAI-compatible, e.g. https://host/v1)" }
    if (-not $PBase) { Die "a base URL is required for a custom provider." }
    $k = Read-Host "  Env var name for the key [CUSTOM_API_KEY]"
    $PKeyEnv = if ($k) { $k } else { 'CUSTOM_API_KEY' }
  }
  default { Die "invalid choice: $Provider" }
}

Head1 "3/4  API key"
if (-not $ApiKey) {
  $secure = Read-Host "  Paste your $PLabel key (input hidden)" -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try { $ApiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
  finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}
if (-not $ApiKey) { Die "an API key is required - the free lane is bring-your-own-key." }

Head1 "4/4  Telegram (optional)"
Say "Leave blank to use terminal chat only. To connect Telegram, create a bot with"
Say "@BotFather, then paste its token here."
if (-not $TelegramToken) { $TelegramToken = Read-Host "  Telegram bot token" }

# -- 2. resolve the model against the provider's own list -------------------
$Model = ''
try {
  $hdr = if ($PKind -eq 'anthropic') {
    @{ 'x-api-key' = $ApiKey; 'anthropic-version' = '2023-06-01' }
  } else {
    @{ 'Authorization' = "Bearer $ApiKey" }
  }
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $resp = Invoke-RestMethod -Uri ($PBase.TrimEnd('/') + '/models') -Headers $hdr -TimeoutSec 20 -ErrorAction Stop
  $ids = @()
  foreach ($i in @($resp.data) + @($resp.models)) { if ($i -and $i.id) { $ids += [string]$i.id } elseif ($i -and $i.name) { $ids += [string]$i.name } }
  $ids = @($ids | Where-Object { $_ })
  if ($PSuggest -and ($ids -contains $PSuggest)) { $Model = $PSuggest }
  elseif ($ids.Count -eq 0) { $Model = $PSuggest }
  else {
    $cheap = @($ids | Where-Object { $_ -match '(?i)flash|luna|mini|air|lite|small' })
    $pool  = if ($cheap.Count -gt 0) { $cheap } else { $ids }
    $Model = $pool[0]
  }
} catch {
  Write-Host "  $C_DIM(could not read the model list: $($_.Exception.GetType().Name))$C_N"
  $Model = $PSuggest
}
if (-not $Model) { $Model = ($PLabel.ToLower() -replace '[^a-z0-9]+', '-').Trim('-') }
Ok "provider: $PLabel  model: $Model"

# -- 3. bundle --------------------------------------------------------------
Head1 "Downloading the free agent bundle (windows-amd64, ~156 MB)"
if (-not (Test-Path $Bundle)) { New-Item -ItemType Directory -Force -Path $Bundle | Out-Null }
$Done = Join-Path $Bundle '.complete'
if (Test-Path $Done) {
  Ok "bundle already present"
} else {
  $sums = Join-Path $Bundle 'SHA256SUMS'
  if (-not (Get-RemoteFile "$BaseDl/SHA256SUMS" $sums)) {
    Die "could not reach the release. Check your network, or download $Pkg from $BaseDl manually."
  }
  $want = $null
  foreach ($line in Get-Content $sums) {
    $p = $line -split '\s+'
    if ($p.Count -ge 2 -and $p[-1] -eq $Pkg) { $want = $p[0] }
  }
  if (-not $want) { Die "no checksum published for $Pkg." }

  $pkgPath = Join-Path $Bundle $Pkg
  if (-not (Get-RemoteFile "$BaseDl/$Pkg" $pkgPath)) { Die "download failed." }
  $got = (Get-FileHash -Path $pkgPath -Algorithm SHA256).Hash.ToLower()
  if ($got -ne $want.ToLower()) { Die "checksum mismatch on $Pkg - refusing to install." }
  Ok "checksum verified"

  & tar.exe -xzf $pkgPath -C $Bundle
  if ($LASTEXITCODE -ne 0) { Die "could not extract $Pkg (tar exit $LASTEXITCODE)." }
  Set-Content -Path $Done -Value 'ok' -Encoding ASCII
}

# -- 4. interpreter + install (no index, ever) ------------------------------
Head1 "Installing"
$localBin = Join-Path $env:USERPROFILE '.local\bin'
if (Test-Path $localBin) { $env:PATH = "$localBin;$env:PATH" }

$uv = Get-Command uv.exe -ErrorAction SilentlyContinue
if (-not $uv) {
  Say "fetching uv (interpreter manager, no package index involved)"
  try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-RestMethod -Uri 'https://astral.sh/uv/install.ps1' -UseBasicParsing -ErrorAction Stop | Invoke-Expression
  } catch { Die "could not install uv." }
  if (Test-Path $localBin) { $env:PATH = "$localBin;$env:PATH" }
  $uv = Get-Command uv.exe -ErrorAction SilentlyContinue
  if (-not $uv) { Die "uv installed but not on PATH - open a new terminal and re-run." }
}
$Uv = $uv.Source

Say "python 3.14 (matches the signed wheel set)"
& $Uv python install 3.14 2>&1 | Out-Null
$Py = (& $Uv python find 3.14 2>$null | Select-Object -First 1)
if (-not $Py) { Die "could not provision python 3.14." }

# ONE engine venv for the whole machine, stored at the anchor -- profiles only
# hold data. A second agent reuses it instead of downloading python + 300MB of
# wheels again, and an existing root-layout install keeps the venv it already has.
$Venv = Join-Path $Anchor 'venv'
$VenvPy = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path $VenvPy)) {
  & $Py -m venv $Venv 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPy)) { Die "could not create the venv at $Venv" }
}

$vendor = Join-Path $Bundle 'vendor'
$lock   = Join-Path $Bundle 'installer\requirements-lock.hashes.txt'
& $Uv pip install --python $VenvPy --no-index --find-links $vendor --require-hashes -r $lock 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Die "dependency install failed (no index, lock only)." }
Ok "dependencies installed from the signed lock"

# ⛔ THIS STEP FAILED ON A CUSTOMER WINDOWS BOX (2026-10-18) AND TOLD NOBODY WHY.
# The old line was `... $wheel.FullName 2>&1 | Out-Null` followed by a bare
# "engine wheel install failed" -- uv's entire reason was thrown away, so the
# report was one line with nothing under it. Three things now: pick the wheel
# strictly, prove the file on disk is a real wheel BEFORE uv sees it (a truncated
# extract passes Test-Path and only fails inside uv), and KEEP uv's output so a
# failure names itself.
$wheelDir = Join-Path $Bundle 'installer'
$wheelCandidates = @(Get-ChildItem -Path $wheelDir -Filter 'cem888_agent-*.whl' -ErrorAction SilentlyContinue)
if ($wheelCandidates.Count -ne 1) {
  Die "installer bundle is incomplete - expected exactly 1 engine wheel in $wheelDir, found $($wheelCandidates.Count)."
}
$engineWheel = $wheelCandidates[0]

function Test-Cem888Wheel([string]$Path) {
  try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
    try {
      $meta = @($zip.Entries | Where-Object { $_.FullName -like '*.dist-info/METADATA' }).Count
      $rec  = @($zip.Entries | Where-Object { $_.FullName -like '*.dist-info/RECORD' }).Count
      return ($meta -ge 1 -and $rec -ge 1 -and $zip.Entries.Count -gt 10)
    } finally { $zip.Dispose() }
  } catch { return $false }
}

$wheelOk = Test-Cem888Wheel $engineWheel.FullName
if (-not $wheelOk -and (Test-Path $pkgPath)) {
  # Self-repair: the archive is already on disk, so re-extract only installer/.
  Say "engine wheel looks truncated - re-extracting installer/ from the bundle archive"
  & tar.exe -xf $pkgPath -C $Bundle './installer' 2>&1 | Out-Null
  $wheelCandidates = @(Get-ChildItem -Path $wheelDir -Filter 'cem888_agent-*.whl' -ErrorAction SilentlyContinue)
  if ($wheelCandidates.Count -eq 1) { $engineWheel = $wheelCandidates[0]; $wheelOk = Test-Cem888Wheel $engineWheel.FullName }
}
if (-not $wheelOk) {
  Die "the engine wheel on disk is not a complete wheel ($($engineWheel.FullName), $([int]($engineWheel.Length / 1KB)) KB) - delete $Bundle and run this installer again."
}
Ok "engine wheel: $($engineWheel.Name) ($([math]::Round($engineWheel.Length / 1MB, 1)) MB)"

# Installed through an ARGUMENT ARRAY (the form the site installer uses on
# working Windows boxes) and retried once: a scanner holding a just-extracted
# 7 MB file is a transient failure, not a broken bundle.
$engineArgs = @('pip', 'install', '--python', $VenvPy, '--no-index', '--no-deps', '--find-links', $vendor, $engineWheel.FullName)
$engineCode = 1
$engineOut = @()
for ($attempt = 1; $attempt -le 2; $attempt++) {
  $engineOut = @(& $Uv @engineArgs 2>&1)
  $engineCode = $LASTEXITCODE
  if ($engineCode -eq 0) { break }
  if ($attempt -lt 2) {
    Say "engine install attempt $attempt failed - retrying once"
    Start-Sleep -Seconds 3
  }
}
if ($engineCode -ne 0) {
  # Second, INDEPENDENT route: the venv's own pip. uv and pip fail for different
  # reasons, so a machine where one chokes can still end up with a working engine
  # instead of a dead installer.
  Say "uv could not install the engine - trying the venv's own pip"
  $pipOut = @(& $VenvPy -m pip install --no-index --no-deps $engineWheel.FullName 2>&1)
  $pipCode = $LASTEXITCODE
  if ($pipCode -eq 0) {
    Ok "engine installed (pip route)"
  } else {
    Write-Host "  --- uv said ---"
    $engineOut | ForEach-Object { Write-Host "  $_" }
    Write-Host "  --- pip said ---"
    $pipOut | ForEach-Object { Write-Host "  $_" }
    Die "engine wheel install failed (uv exit $engineCode, pip exit $pipCode) - the reason is above."
  }
} else {
  Ok "engine installed"
}

# -- 4b. GIT FOR WINDOWS (required, not optional) ---------------------------
# ⛔ WITHOUT THIS THE AGENT HAS NO TERMINAL AND NO FILE ACCESS. Every shell and
# file operation runs through Git Bash:
# customer-runtime/src/tools/environments/local.py::_find_bash raises
#   "Git Bash not found. CEM888 Agent requires Git for Windows on Windows."
# and searches OUR portable install FIRST --
#   %LOCALAPPDATA%\cem888\git\bin\bash.exe      (MinGit/PortableGit)
#   %LOCALAPPDATA%\cem888\git\usr\bin\bash.exe  (MinGit usr layout)
# -- under the comment "The install.ps1 installer always drops portable Git here
# when the user didn't already have a working system Git". This installer never
# did. Measured 2026-10-18: a fresh FREE install on Windows answered every
# terminal call with that exact error, so the agent could not read one file and
# reported, honestly, that it could verify nothing. The site installer got this
# block (install/windows.ps1 section 2b-pre); the free lane never did.
function Get-Cem888GitBash {
  $c = @()
  if ($env:CEM888_GIT_BASH_PATH) { $c += $env:CEM888_GIT_BASH_PATH }
  if ($env:LOCALAPPDATA) {
    $c += "$env:LOCALAPPDATA\cem888\git\bin\bash.exe"
    $c += "$env:LOCALAPPDATA\cem888\git\usr\bin\bash.exe"
  }
  $onPath = Get-Command bash.exe -ErrorAction SilentlyContinue
  if ($onPath) { $c += $onPath.Source }
  $c += "${env:ProgramFiles}\Git\bin\bash.exe"
  $c += "${env:ProgramFiles(x86)}\Git\bin\bash.exe"
  if ($env:LOCALAPPDATA) { $c += "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe" }
  foreach ($p in $c) {
    if ($p -and (Test-Path -LiteralPath $p -PathType Leaf)) { return $p }
  }
  return $null
}

Head1 "Git for Windows (the terminal runs through it)"
$GitBash = Get-Cem888GitBash
if ($GitBash) {
  Ok "Git Bash found: $GitBash"
} else {
  Say "not installed - fetching it now (the agent cannot run a command without it)"
  $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
  if ($winget) {
    # A native program: a non-zero exit does NOT throw, so the result is judged
    # on disk below, never on the exit code.
    try { & winget.exe install --id Git.Git --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null } catch { }
    for ($g = 0; $g -lt 20; $g++) {
      $GitBash = Get-Cem888GitBash
      if ($GitBash) { break }
      Start-Sleep -Seconds 3
    }
  }
  if (-not $GitBash) {
    # ⛔ MinGit CANNOT SATISFY THIS, BY CONSTRUCTION -- this block used to fetch it.
    # Measured 2026-10-18 on the pinned asset MinGit-2.56.0-64-bit.zip (39,602,073 B):
    # it carries usr/bin/sh.exe and usr/bin/dash.exe and NO bash.exe ANYWHERE. The
    # runtime requires bash.exe BY NAME (customer-runtime,
    # tools/environments/local.py::_find_bash), so a MinGit drop fails one step later,
    # at the bash probe -- on a machine that has already paid for a full reinstall.
    # The site installer measured the identical thing and moved to PortableGit
    # (59,958,024 B), whose archive ROOT carries bin\bash.exe AND usr\bin\bash.exe,
    # which is exactly the layout _find_bash probes first.
    # Git for Windows is not a Python dependency -- the --no-index rule governs the
    # wheel set, not this -- but the pin does: an explicit tag, never /latest/.
    $gitTag = 'v2.56.0.windows.1'
    $gitDest = Join-Path $env:LOCALAPPDATA 'cem888\git'
    $gitTmp = Join-Path ([System.IO.Path]::GetTempPath()) ('cem888-git-' + [Guid]::NewGuid().ToString('N'))
    try { New-Item -ItemType Directory -Force -Path $gitTmp | Out-Null } catch { }
    Say "fetching portable Git ($gitTag, ~57 MB, pinned, no elevation)"
    $sfx = Join-Path $gitTmp 'portablegit.7z.exe'
    $sfxUrl = "https://github.com/git-for-windows/git/releases/download/$gitTag/PortableGit-2.56.0-64-bit.7z.exe"
    if (Get-RemoteFile $sfxUrl $sfx) {
      try {
        New-Item -ItemType Directory -Force -Path $gitDest | Out-Null
        # A 7-Zip SFX extracts the ARCHIVE ROOT into -o<dir>, so bin\ and usr\ land
        # directly under $gitDest. -y answers its single prompt; because -o is always
        # supplied no window is ever shown. Judged ON DISK, never on an exit code.
        $null = Start-Process -FilePath $sfx -Wait -PassThru -WindowStyle Hidden -ArgumentList @('-y', ('-o"' + $gitDest + '"'))
      } catch { Say "portable Git extraction reported: $($_.Exception.Message)" }
    } else {
      Say "could not download portable Git"
    }
    Remove-Item -Recurse -Force $gitTmp -ErrorAction SilentlyContinue
    $GitBash = Get-Cem888GitBash
    if (-not $GitBash) {
      # Last route: the official installer (Inno Setup), silent and PER-USER into the
      # SAME directory. /CURRENTUSER is load-bearing -- a UAC prompt nobody can see is
      # a hang, and a hang is the failure being fixed.
      Say "portable Git did not land - using the official installer (per-user, silent)"
      $innoTmp = Join-Path ([System.IO.Path]::GetTempPath()) ('cem888-gitsetup-' + [Guid]::NewGuid().ToString('N'))
      try { New-Item -ItemType Directory -Force -Path $innoTmp | Out-Null } catch { }
      $inno = Join-Path $innoTmp 'git-setup.exe'
      $innoUrl = "https://github.com/git-for-windows/git/releases/download/$gitTag/Git-2.56.0-64-bit.exe"
      if (Get-RemoteFile $innoUrl $inno) {
        try {
          $null = Start-Process -FilePath $inno -Wait -PassThru -WindowStyle Hidden -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/NOCANCEL', '/SP-', '/CURRENTUSER', ('/DIR="' + $gitDest + '"'))
        } catch { Say "Git installer reported: $($_.Exception.Message)" }
      } else {
        Say "could not download the Git installer either"
      }
      Remove-Item -Recurse -Force $innoTmp -ErrorAction SilentlyContinue
      $GitBash = Get-Cem888GitBash
    }
    if ($GitBash) {
      foreach ($d in @("$gitDest\cmd", "$gitDest\bin", "$gitDest\usr\bin")) {
        try {
          $u = [Environment]::GetEnvironmentVariable('Path', 'User')
          if ($u -notlike "*$d*") { [Environment]::SetEnvironmentVariable('Path', ($u.TrimEnd(';') + ';' + $d), 'User') }
        } catch { }
      }
    }
  }
  if (-not $GitBash) {
    Die "Git for Windows could not be installed, so this agent would have NO terminal. Install it from https://git-scm.com/download/win and re-run this installer."
  }
  try { [Environment]::SetEnvironmentVariable('CEM888_GIT_BASH_PATH', $GitBash, 'User') } catch { }
  Ok "Git Bash installed: $GitBash"
}
$env:CEM888_GIT_BASH_PATH = $GitBash

# Prove it RUNS, not just that the file exists: a half-unpacked MinGit passes
# Test-Path and then fails every single command. Same class of check as the boot
# gate below -- the installer either proves the tool works or names the reason.
$bashProbe = @(& $GitBash -c 'echo cem888-bash-ok' 2>&1)
if (($bashProbe -join ' ') -notmatch 'cem888-bash-ok') {
  Die "Git Bash exists at $GitBash but did not run (output: $($bashProbe -join ' ')). The agent has no terminal until this works."
}
Ok "terminal backend verified"

# -- 5. config (provider-neutral) -------------------------------------------
Head1 "Writing profile"
if (-not (Test-Path $Root)) { New-Item -ItemType Directory -Force -Path $Root | Out-Null }

$SlugName = ($AgentName.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if (-not $SlugName) { $SlugName = 'agent' }
$ProvName = ($PLabel.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
$ApiMode  = if ($PKind -eq 'anthropic') { 'anthropic_messages' } else { 'chat_completions' }

$tgBlock = ''
if ($TelegramToken) { $tgBlock = "platforms:`n  telegram:`n    enabled: true`n" }

$yaml = @"
# CEM888 - $AgentName
# Free lane: agent only (terminal chat or Telegram). Bring your own provider key.
# Written by the CEM888 free installer; edit freely.

agent:
  name: $AgentName
  owner: $UserName
  job: "$AgentJob"

model:
  provider: $ProvName
  default: $Model
  temperature: 0.2
  max_tokens: 8192

custom_providers:
  - name: $ProvName
    base_url: $PBase
    key_env: $PKeyEnv
    api_mode: $ApiMode
    request_timeout_seconds: 360

$tgBlock
"@
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $Root 'config.yaml'), $yaml, $utf8NoBom)

$envLines = @()
$envFile = Join-Path $Root '.env'
if (Test-Path $envFile) {
  $envLines = @(Get-Content $envFile | Where-Object { $_ -notmatch "^$([regex]::Escape($PKeyEnv))=" })
}
$envLines += "$PKeyEnv=$ApiKey"
if ($TelegramToken) {
  $envLines = @($envLines | Where-Object { $_ -notmatch '^TELEGRAM_BOT_TOKEN=' })
  $envLines += "TELEGRAM_BOT_TOKEN=$TelegramToken"
}
[IO.File]::WriteAllText($envFile, (($envLines -join "`r`n") + "`r`n"), $utf8NoBom)
& icacls.exe $envFile /inheritance:r /grant:r "$($env:USERNAME):(R,W)" 2>&1 | Out-Null

Ok "config: $(Join-Path $Root 'config.yaml')"
Ok "key:    $envFile (current user only)"

# -- 5b. STARTER SKILLS ------------------------------------------------------
# ⛔ A FREE INSTALL SHIPPED ZERO SKILLS (measured 2026-10-18). The bundle carries
# starter-skills/ and the site installer lays it down, but this installer never
# mentioned the directory -- so a free agent booted with an empty skills/ and
# answered "zero skills installed" when asked to look one up. The bundle ships
# them; the installer dropped them on the floor.
$SkillsSrc = Join-Path $Bundle 'starter-skills'
$SkillsDest = Join-Path $Root 'skills'
if (Test-Path $SkillsSrc) {
  New-Item -ItemType Directory -Force -Path $SkillsDest | Out-Null
  $sNew = 0
  $sKept = 0
  Get-ChildItem -Path $SkillsSrc -Recurse -Filter 'SKILL.md' -File | ForEach-Object {
    $rel = $_.Directory.FullName.Substring($SkillsSrc.Length).TrimStart('\')
    if (-not $rel) { return }
    $dest = Join-Path $SkillsDest $rel
    # An existing skill is LEFT ALONE: re-running the installer must never
    # overwrite the customer's own edits.
    if (Test-Path (Join-Path $dest 'SKILL.md')) { $sKept++; return }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item -Path (Join-Path $_.Directory.FullName '*') -Destination $dest -Force -ErrorAction SilentlyContinue
    $sNew++
  }
  Ok "skills: $sNew installed, $sKept already present"
  if (($sNew + $sKept) -eq 0) { Say "starter-skills present but no SKILL.md found - bundle layout changed?" }
} else {
  Say "starter-skills/ not in this bundle - skills/ left as-is"
}

# -- 6. launcher + smoke test ----------------------------------------------
$Cem = Join-Path $Venv 'Scripts\cem888.exe'

# Put the engine's own command on PATH for this user. The console script lands in
# the SHARED venv's Scripts dir (~\.cem888\venv\Scripts), which nothing has on PATH,
# so the documented `cem888 ...` invocations answered CommandNotFoundException
# (reported 2026-10-18). A .cmd shim in ~\.local\bin fixes it -- that is the dir
# the uv installer already puts on PATH, and the same remedy the site installer
# uses. ONE shim serves every profile: it runs the shared engine, and the engine
# picks the profile from active_profile or -p.
$ShimDir = Join-Path $env:USERPROFILE '.local\bin'
$Shim = Join-Path $ShimDir 'cem888.cmd'
$ShimOk = $false
try {
    New-Item -ItemType Directory -Force -Path $ShimDir | Out-Null
    [IO.File]::WriteAllText($Shim, "@echo off`r`n`"$Cem`" %*`r`n", $utf8NoBom)
    $ShimOk = Test-Path $Shim
    $UserPath = [Environment]::GetEnvironmentVariable('Path','User')
    if (-not $UserPath) { $UserPath = '' }
    $PathParts = @($UserPath -split ';' | Where-Object { $_ -ne '' })
    if ($PathParts -notcontains $ShimDir) {
        [Environment]::SetEnvironmentVariable('Path', (@($PathParts + $ShimDir) -join ';'), 'User')
    }
    $env:Path = "$ShimDir;$env:Path"
# ⛔ A USER-LEVEL CEM888_HOME PINNED TO ONE PROFILE BREAKS MULTI-AGENT (2026-10-18):
# cem888_cli/main.py::_apply_profile_override trusts a CEM888_HOME whose parent is
# 'profiles' and returns early, so once it names ...\profiles\<a> every later shell
# opens agent <a> and -p is the only way to reach <b>. Clear that pin -- the sticky
# choice belongs in active_profile, which any profile can be switched from. A
# CEM888_HOME pointing at the .cem888 root pins nothing and is left untouched.
try {
  $uHome = [Environment]::GetEnvironmentVariable('CEM888_HOME','User')
  if ($uHome) {
    $uTrim = $uHome.Trim().TrimEnd('\')
    if ((Split-Path (Split-Path $uTrim -Parent) -Leaf) -eq 'profiles') {
      [Environment]::SetEnvironmentVariable('CEM888_HOME', $null, 'User')
      Write-Host "  $C_CYAN[ok] cleared CEM888_HOME=$uHome$C_N"
      Write-Host "       (it pinned every shell to that one profile; profiles are chosen by active_profile now)"
    }
  }
} catch {
  Write-Host "  $C_CORAL[x] could not clear the user-level CEM888_HOME: $($_.Exception.Message)$C_N"
}

} catch {
    Write-Host "  $C_CORAL[x] could not install the cem888 command: $($_.Exception.Message)$C_N"
}

# STICKY DEFAULT: plain `cem888 chat` opens the profile installed last.
# DELIBERATELY OUTSIDE the shim try/catch above: a shim failure must never also
# cost the sticky profile. The runtime reads active_profile from the .cem888 ROOT
# (cem888_constants.get_default_cem888_root collapses <root>\profiles\<key> back
# to <root>), so it is written there, never inside a profile.
$NativeHome = Join-Path $env:USERPROFILE '.cem888'
$StickyRoot = if ($Anchor.StartsWith($NativeHome, [StringComparison]::OrdinalIgnoreCase)) { $NativeHome } else { $Anchor }
try {
  [IO.File]::WriteAllText((Join-Path $StickyRoot 'active_profile'), "$SlugName`r`n", $utf8NoBom)
  Ok "active profile: $SlugName"
} catch {
  Write-Host "  $C_CORAL[x] could not write active_profile: $($_.Exception.Message)$C_N"
}

Head1 "Checking the install"
$verOut = ''
if (Test-Path $Cem) { $verOut = (& $Cem --version 2>&1 | Select-Object -First 1) }
if ($verOut) { Ok "$verOut" } else { Write-Host "  $C_CORAL[x] engine binary did not answer --version - run: `"$Cem`" doctor$C_N" }

# The Tier-0 authority manifest. The runtime refuses EVERY turn without it --
# agent_init and system_prompt both load it with required=True -- and nothing in
# the free route ever created one: the site installer mints it through
# installer/scripts/cem-authority-manifest.py, this installer did not, so a clean
# free install answered "required Tier-0 authority manifest is missing" to the
# first message it ever received (reported 2026-10-18). Minted here with the
# engine's own command so the producer and the consumer can never disagree about
# the path.
$Manifest = Join-Path $Root 'authority.json'
# MINTED BY THE ONE PRODUCER, not by `cem888 authority init`. Measured
# 2026-10-18 on a clean free install: the CLI derives profile_name from the
# directory's basename, so a profile at ...\.cem888 minted "profile_name":
# ".cem888" while the runtime's path-based resolver says "default" -- and every
# boot died with
#   AuthorityError: profile authority mismatch: path implies 'default',
#   manifest declares '.cem888'
# i.e. the installer said "Done" and the agent then refused every single turn.
# The shipped installer/scripts/cem-authority-manifest.py carries
# profile_name_for(), which mirrors the runtime resolver, and re-reads the file
# it just wrote to prove it loads.
$AuthScript = Join-Path $Bundle 'installer\scripts\cem-authority-manifest.py'
if ((Test-Path $AuthScript) -and (Test-Path $VenvPy)) {
  & $VenvPy $AuthScript --profile-dir $Root --home-dir $Root --agent-name $AgentName --wheel-version $Version --from-install-state --if-missing 2>&1 | ForEach-Object { Write-Host "  $_" }
  if ($LASTEXITCODE -ne 0) { Write-Host "  $C_CORAL[x] authority mint exited $LASTEXITCODE$C_N" }
} elseif (Test-Path $Cem) {
  # Fallback only when the bundle somehow ships no minting script.
  & $Cem authority init --profile-dir $Root --agent-name $AgentName 2>&1 | ForEach-Object { Write-Host "  $_" }
  if ($LASTEXITCODE -ne 0) { Write-Host "  $C_CORAL[x] authority init exited $LASTEXITCODE$C_N" }
}
$ManifestOk = $false
if (Test-Path $Manifest) {
  try { $null = (Get-Content -Raw $Manifest | ConvertFrom-Json); $ManifestOk = $true } catch { }
}
if (-not $ManifestOk) { Die "Tier-0 authority manifest was not created at $Manifest - the agent cannot answer a single turn without it." }

# -- 6c. boot gate ---------------------------------------------------------
# Everything above can be green while the agent still refuses to start: the line
# a turn actually dies on is agent_init.py's
#   agent.authority = load_agent_authority(required=True)
# and that only runs when a message is sent -- i.e. AFTER the installer said
# "Done" (reported 2026-10-18: install looked fine, then the TUI printed
# "Failed to initialize agent"). Run that exact call headless here, so the
# install either PROVES the agent boots or names the reason BEFORE reporting
# success.
Head1 "Proving the agent boots"
$Probe = "from agent.authority import load_agent_authority; a = load_agent_authority(required=True); print('profile:', a.profile_root)"
$ProbeOut = @(& $VenvPy -c $Probe 2>&1)
$ProbeCode = $LASTEXITCODE
$ProbeOut | ForEach-Object { Write-Host "  $_" }
if ($ProbeCode -ne 0) {
  Die "the agent cannot boot - Tier-0 authority did not load (the reason is printed above)"
}
Ok "agent boots against $Root"

Write-Host ""
Write-Host "  $C_CYAN Done. " -NoNewline
Write-Host "$AgentName is installed on $PLabel ($Model).$C_N"
Write-Host ""
# ⛔ THE OLD BANNER CAUSED A SUPPORT TICKET THE FIRST TIME A CUSTOMER READ IT (2026-10-18).
# It said "Distro is installed", the customer typed
#   cem888 chat --profile distro   ->   Error: Profile 'distro' does not exist
# because the install had put the agent in the DEFAULT profile. The installer now
# creates a real profile directory per agent, so the key below EXISTS and the two
# commands that were once wrong both work.
Write-Host "  Profile:  $SlugName  ->  $Root"
Write-Host "            This is a real profile. Plain 'cem888 chat' opens it, and the"
Write-Host "            name below is what the --profile flag expects."
Write-Host ""

# ⛔ THE BANNER NAMED NO SECOND AGENT (owner, 2026-10-18: "it didnt show how to
# message second agent ... type cem888 chat --profile 'agentname'"). Printing a
# placeholder <key> forces the customer to go read `profile list` first. So: name
# THIS profile in the exact command, then enumerate every OTHER profile that has a
# config on this machine and print its literal command.
$OtherAgents = @()
if (Test-Path $ProfilesRoot) {
  $OtherAgents = @(Get-ChildItem -Path $ProfilesRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne $SlugName -and (Test-Path (Join-Path $_.FullName 'config.yaml')) } |
    ForEach-Object { $_.Name })
}
# An install made by an OLDER free installer lives at the .cem888 ROOT itself --
# that is the built-in "default" profile and it still opens with --profile default.
if ($Root -ne $Anchor -and (Test-Path (Join-Path $Anchor 'config.yaml'))) {
  $OtherAgents = @('default') + $OtherAgents
}
$CLI = if ($ShimOk) { 'cem888' } else { "`"$Cem`"" }

Write-Host "  Talk to this agent by name:"
Write-Host "     $CLI chat --profile `"$SlugName`""
Write-Host ""
if ($OtherAgents.Count -gt 0) {
  Write-Host "  Your other agents on this machine - talk to any of them:"
  foreach ($oa in $OtherAgents) { Write-Host "     $CLI chat --profile `"$oa`"" }
  Write-Host ""
} else {
  Write-Host "  Install another agent and it gets its own profile - talk to it with:"
  Write-Host "     $CLI chat --profile `"<the-name-you-gave-it>`""
  Write-Host ""
}
Write-Host "  Manage agents:"
Write-Host "     $CLI profile list               (every agent installed here)"
Write-Host "     $CLI profile use <profile>      (make another one the default)"
Write-Host "     $CLI -p <profile> chat          (shorter form of --profile)"
Write-Host ""
Write-Host "  Start talking:"
Write-Host "     $CLI chat"
Write-Host ""
Write-Host "  Check health:"
Write-Host "     $CLI doctor"
Write-Host ""
if ($ShimOk) {
    Write-Host "  $C_CYAN[ok] cem888 command installed:$C_N $Shim"
    Write-Host "       open a NEW PowerShell window, then type:  cem888 chat"
    Write-Host ""
}
Write-Host "  $C_DIM On cost: the free lane is tuned for cheap, fast models. When a task needs real$C_N"
Write-Host "  $C_DIM deep reasoning, add a stronger model later - 'cem888 model' switches providers, and$C_N"
Write-Host "  $C_DIM 'cem888 fallback' wires a big model in behind the cheap one so it is only used when$C_N"
Write-Host "  $C_DIM the cheap one fails or the task is flagged hard. Nothing to reinstall.$C_N"
