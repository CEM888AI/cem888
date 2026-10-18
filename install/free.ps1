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

$Version = '1.0.48'
$Repo    = 'CEM888AI/cem888'
$Slug    = "free-v$Version"
$BaseDl  = "https://github.com/$Repo/releases/download/$Slug"
$Root    = if ($env:CEM888_HOME) { $env:CEM888_HOME } else { Join-Path $env:USERPROFILE '.cem888' }
$Bundle  = Join-Path $Root "free\v$Version"
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

$Venv = Join-Path $Root 'venv'
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

$wheel = Get-ChildItem -Path (Join-Path $Bundle 'installer') -Filter 'cem888_agent-*.whl' | Select-Object -First 1
if (-not $wheel) { Die "engine wheel not found in the bundle." }
& $Uv pip install --python $VenvPy --no-index --find-links $vendor --no-deps $wheel.FullName 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Die "engine wheel install failed." }
Ok "engine installed"

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

# -- 6. launcher + smoke test ----------------------------------------------
$Cem = Join-Path $Venv 'Scripts\cem888.exe'
$Shim = Join-Path $Root 'cem888.cmd'
[IO.File]::WriteAllText($Shim, "@echo off`r`n`"$Cem`" %*`r`n", $utf8NoBom)

Head1 "Checking the install"
$verOut = ''
if (Test-Path $Cem) { $verOut = (& $Cem --version 2>&1 | Select-Object -First 1) }
if ($verOut) { Ok "$verOut" } else { Write-Host "  $C_CORAL[x] engine binary did not answer --version - run: `"$Cem`" doctor$C_N" }

Write-Host ""
Write-Host "  $C_CYAN Done. " -NoNewline
Write-Host "$AgentName is installed on $PLabel ($Model).$C_N"
Write-Host ""
Write-Host "  Start talking:"
Write-Host "     `"$Cem`" chat"
Write-Host ""
Write-Host "  Check health:"
Write-Host "     `"$Cem`" doctor"
Write-Host ""
Write-Host "  Shortcut for a plain 'cem888':"
# The console script lands in the PRIVATE venv's Scripts dir, which nothing has on
# PATH, so `cem888 chat` answered CommandNotFoundException (reported 2026-10-18).
# Same remedy as the site installer: a .cmd shim in ~\.local\bin, which the uv
# installer already puts on PATH.
$ShimDir = Join-Path $env:USERPROFILE '.local\bin'
New-Item -ItemType Directory -Force -Path $ShimDir | Out-Null
$Shim = Join-Path $ShimDir 'cem888.cmd'
Set-Content -Path $Shim -Encoding ASCII -Value @('@echo off', "`"$Cem`" %*")
try {
    $UserPath = [Environment]::GetEnvironmentVariable('Path','User')
    if (-not $UserPath) { $UserPath = '' }
    $PathParts = @($UserPath -split ';' | Where-Object { $_ -ne '' })
    if ($PathParts -notcontains $ShimDir) {
        [Environment]::SetEnvironmentVariable('Path', (@($PathParts + $ShimDir) -join ';'), 'User')
        Write-Host "  $C_CYAN[ok] added to your PATH:$C_N $ShimDir"
    } else {
        Write-Host "  $C_CYAN[ok] already on your PATH:$C_N $ShimDir"
    }
} catch {
    Write-Host "  $C_CORAL[x] could not update the user PATH: $($_.Exception.Message)$C_N"
}
$env:Path = "$ShimDir;$env:Path"
Write-Host "  $C_CYAN[ok] command installed:$C_N $Shim"
Write-Host "       open a NEW PowerShell window, then just type:  cem888 chat"
Write-Host "  or right now, in this window:"
Write-Host "     cem888 chat"
Write-Host ""
Write-Host "  $C_DIM On cost: the free lane is tuned for cheap, fast models. When a task needs real$C_N"
Write-Host "  $C_DIM deep reasoning, add a stronger model later - 'cem888 model' switches providers, and$C_N"
Write-Host "  $C_DIM 'cem888 fallback' wires a big model in behind the cheap one so it is only used when$C_N"
Write-Host "  $C_DIM the cheap one fails or the task is flagged hard. Nothing to reinstall.$C_N"
