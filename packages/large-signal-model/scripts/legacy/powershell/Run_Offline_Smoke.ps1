param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"
& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline smoke `
    --output (Join-Path $Work "results\smoke") `
    --max-actions 20 `
    --initial-probes 8
if ($LASTEXITCODE -ne 0) {
    throw "Offline smoke test failed."
}
