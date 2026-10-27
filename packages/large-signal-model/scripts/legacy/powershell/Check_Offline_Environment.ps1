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
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python (Join-Path $Work "scripts\check_offline_environment.py")
if ($LASTEXITCODE -ne 0) {
    throw "The offline environment check failed."
}
