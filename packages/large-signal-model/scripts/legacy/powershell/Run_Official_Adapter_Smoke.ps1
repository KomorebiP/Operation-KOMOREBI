param(
    [string]$EnvName = "arc3-offline",
    [string]$EnvironmentsDir = ""
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($EnvironmentsDir)) {
    $EnvironmentsDir = Join-Path $Work "test_environment_files"
}
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline official-smoke `
    --environments-dir $EnvironmentsDir `
    --output (Join-Path $Work "results\official-adapter-smoke")
if ($LASTEXITCODE -ne 0) {
    throw "The official local-adapter smoke test failed."
}
