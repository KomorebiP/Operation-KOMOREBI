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
& $Python validation/verify_v046_release.py
if ($LASTEXITCODE -ne 0) { throw "v0.46 release verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests/test_v046_jspace_self_indexed_workspace.py
if ($LASTEXITCODE -ne 0) { throw "v0.46 focused tests failed" }
Write-Host "V046_NEUTRAL_SELF_INDEXED_WORKSPACE_VERIFIED"
