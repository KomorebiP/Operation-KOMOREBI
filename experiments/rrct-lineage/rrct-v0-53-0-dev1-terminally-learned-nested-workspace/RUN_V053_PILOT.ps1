param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    else { throw "Python was not found" }
}
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python -m pytest -q -p no:cacheprovider tests/test_v053.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/verify_package.py
exit $LASTEXITCODE
