param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work "validation\suite_static_audit_runtime.json"

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline suite-audit `
    --environments-dir $EnvironmentsDir `
    --output $Output
if ($LASTEXITCODE -ne 0) {
    throw "One or more of the 25 environment files failed static validation."
}

Write-Host "All 25 environment trees passed syntax, expected-class, and offline-import validation." -ForegroundColor Green
Write-Host "Report: $Output"
