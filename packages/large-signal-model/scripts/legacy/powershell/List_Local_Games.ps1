param(
    [string]$EnvName = "arc3-offline",
    [string]$EnvironmentsDir = ""
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($EnvironmentsDir)) {
    $EnvironmentsDir = Join-Path $Work "environment_files"
}
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline list `
    --environments-dir $EnvironmentsDir
if ($LASTEXITCODE -ne 0) {
    throw "Local game listing failed."
}
