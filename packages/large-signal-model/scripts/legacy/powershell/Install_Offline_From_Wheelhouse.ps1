param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$Wheelhouse = Join-Path $Work "wheelhouse"
if (-not (Test-Path $Wheelhouse)) {
    throw "Wheelhouse not found: $Wheelhouse"
}

& conda run -n $EnvName python -m pip install `
    --no-index `
    --find-links $Wheelhouse `
    "arc-agi==0.9.9" `
    "arcengine==0.9.3" `
    "komorebi-arc3-offline==1.1.0"
if ($LASTEXITCODE -ne 0) {
    throw "Offline wheelhouse installation failed."
}
Write-Host "Offline installation completed in '$EnvName'." -ForegroundColor Green
