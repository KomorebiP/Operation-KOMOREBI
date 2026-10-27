param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline list `
    --environments-dir $EnvironmentsDir
if ($LASTEXITCODE -ne 0) {
    throw "The official toolkit could not load the 25 local environments."
}
