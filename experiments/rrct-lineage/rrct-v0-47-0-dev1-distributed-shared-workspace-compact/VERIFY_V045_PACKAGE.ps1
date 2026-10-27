param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    else { throw "Python was not found" }
}
$env:PYTHONPATH = (Join-Path $Root "src")
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python validation/verify_v045_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "Package checksum verification failed" }
& $Python validation/verify_v045_built_wheel.py
if ($LASTEXITCODE -ne 0) { throw "Built-wheel verification failed" }
& (Join-Path $Root "RUN_V045_KOMOREBI_OPERATOR.ps1") -Python $Python
if ($LASTEXITCODE -ne 0) { throw "Scientific evidence verification failed" }
Write-Host "V045_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED"
