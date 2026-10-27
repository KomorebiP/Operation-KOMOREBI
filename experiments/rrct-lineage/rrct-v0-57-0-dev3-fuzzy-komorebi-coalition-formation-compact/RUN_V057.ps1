param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
    } else {
        throw "Python was not found"
    }
}
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = Join-Path $Root "src"
& $Python validation/verify_preoutcome.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/run_holdout.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/analyze_holdout.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest -q -p no:cacheprovider tests/test_v057.py
exit $LASTEXITCODE
