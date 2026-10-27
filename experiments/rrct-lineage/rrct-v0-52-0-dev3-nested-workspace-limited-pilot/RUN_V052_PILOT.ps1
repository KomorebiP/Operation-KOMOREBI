param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } else {
        $Python = "python"
    }
}
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = $Root
& $Python VERIFY_PACKAGE.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python run_pilot.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest -q -p no:cacheprovider tests/test_nested_workspace_pilot.py
exit $LASTEXITCODE
