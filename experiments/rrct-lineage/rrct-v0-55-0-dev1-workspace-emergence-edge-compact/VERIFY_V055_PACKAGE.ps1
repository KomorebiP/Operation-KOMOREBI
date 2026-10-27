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
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = Join-Path $Root "src"
& $Python validation/verify_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "Build manifest verification failed" }
& $Python validation/verify_preoutcome.py
if ($LASTEXITCODE -ne 0) { throw "Primary source seal failed" }
& $Python validation/verify_overcomplete_freeze.py
if ($LASTEXITCODE -ne 0) { throw "Overcomplete extension seal failed" }
& $Python validation/verify_release.py
if ($LASTEXITCODE -ne 0) { throw "Scientific evidence verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests/test_v055_edge.py
if ($LASTEXITCODE -ne 0) { throw "Focused tests failed" }
Write-Host "V055_PACKAGE_VERIFIED"
