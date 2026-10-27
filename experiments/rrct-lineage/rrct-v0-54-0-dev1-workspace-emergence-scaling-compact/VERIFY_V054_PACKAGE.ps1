param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
    } else {
        throw "Python was not found"
    }
}
& $Python "$Root\validation\verify_v054_build_manifest.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& "$Root\RUN_V054_SCALING.ps1" -Python $Python
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "V054_PACKAGE_VERIFIED"
