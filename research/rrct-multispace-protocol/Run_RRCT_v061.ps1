param(
    [ValidateSet("verify", "synthetic", "qwen-smoke")]
    [string]$Profile = "verify",
    [string]$Python = "python",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [string]$ModelPath = "",
    [string]$LensPath = "",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = $PSScriptRoot

if (-not $OutputPath) {
    $parent = Split-Path -Parent $root
    $OutputPath = Join-Path $parent ("RRCT_v061_RESULTS_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
}
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:TOKENIZERS_PARALLELISM = "false"

& $Python (Join-Path $root "tools\validate_protocol.py")
if ($LASTEXITCODE -ne 0) { throw "RRCT v0.61 protocol validation failed" }

if ($Profile -in @("synthetic", "qwen-smoke")) {
    & $Python (Join-Path $root "tools\run_synthetic_validation.py") --output (Join-Path $OutputPath "synthetic_validation_results.json")
    if ($LASTEXITCODE -ne 0) { throw "RRCT v0.61 synthetic validation failed" }
}

if ($Profile -eq "qwen-smoke") {
    if (-not $ModelPath) { throw "-ModelPath is required for qwen-smoke" }
    if (-not $LensPath) { throw "-LensPath is required for qwen-smoke" }
    & $Python (Join-Path $root "tools\run_qwen_multispace_smoke.py") --model $ModelPath --lens $LensPath --output (Join-Path $OutputPath "qwen_multispace_smoke") --device $Device
    if ($LASTEXITCODE -ne 0) { throw "RRCT v0.61 Qwen smoke failed" }
}

Write-Host "RRCT_V061_RUN=PASS"
Write-Host "PROFILE=$Profile"
Write-Host "OUTPUT_PATH=$OutputPath"

