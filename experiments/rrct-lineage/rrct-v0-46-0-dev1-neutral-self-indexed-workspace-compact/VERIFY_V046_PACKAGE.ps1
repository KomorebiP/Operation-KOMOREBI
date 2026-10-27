param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = (Get-Command py).Source
    } else {
        throw "Python was not found"
    }
}
$env:PYTHONPATH = Join-Path $Root "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python validation/verify_v046_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "Package checksum verification failed" }
& (Join-Path $Root "RUN_V046_NEUTRAL_WORKSPACE.ps1") -Python $Python
if ($LASTEXITCODE -ne 0) { throw "v0.46 scientific verification failed" }
& $Python validation/audit_v046_postoutcome.py
if ($LASTEXITCODE -ne 0) { throw "v0.46 post-outcome audit failed" }
& $Python validation/verify_v046_wheel.py
if ($LASTEXITCODE -ne 0) { throw "v0.46 wheel verification failed" }
& $Python validation/verify_v046_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "Package changed during verification" }
Write-Host "V046_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED"
