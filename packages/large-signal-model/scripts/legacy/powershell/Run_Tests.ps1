param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"
& conda run --no-capture-output -n $EnvName python -m pytest -q (Join-Path $Work "tests")
if ($LASTEXITCODE -ne 0) {
    throw "Test suite failed."
}
