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
& $Python validation/verify_v047_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "v0.47 package checksum verification failed" }
& $Python validation/verify_v047_release.py
if ($LASTEXITCODE -ne 0) { throw "v0.47 scientific replay verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests/test_v047_distributed_shared_workspace.py
if ($LASTEXITCODE -ne 0) { throw "v0.47 focused tests failed" }
Write-Host "V047_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED"
