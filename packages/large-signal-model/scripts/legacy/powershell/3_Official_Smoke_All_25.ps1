param(
    [string]$EnvName = "arc3-offline",
    [int]$Seed = 0
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work "validation\official_smoke_25.json"

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline suite-smoke `
    --environments-dir $EnvironmentsDir `
    --output $Output `
    --seed $Seed
$ExitCode = $LASTEXITCODE
if ($ExitCode -gt 1) {
    throw "The 25-environment official adapter smoke test failed with exit code $ExitCode."
}
if ($ExitCode -eq 1) {
    Write-Host "At least one environment failed to load, reset, or step. See $Output." -ForegroundColor Yellow
} else {
    Write-Host "All 25 environments loaded, reset, and stepped through the official local wrapper." -ForegroundColor Green
}
