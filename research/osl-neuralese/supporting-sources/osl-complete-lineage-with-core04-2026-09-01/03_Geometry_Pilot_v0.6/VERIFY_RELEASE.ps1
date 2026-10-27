param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    else { $Python = "python" }
}
$env:PYTHONPATH = Join-Path $Root "experiment"
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python "$Root\verify_release.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest -q -p no:cacheprovider "$Root\tests"
exit $LASTEXITCODE
