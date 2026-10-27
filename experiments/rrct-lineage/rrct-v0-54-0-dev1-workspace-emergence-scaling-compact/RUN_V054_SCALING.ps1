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
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = "$Root\src"
& $Python "$Root\analysis\uncertainty_analysis.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python "$Root\analysis\validate_scaling_law.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest -q -p no:cacheprovider "$Root\tests\test_v054_scaling.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python "$Root\validation\verify_v054_release.py"
exit $LASTEXITCODE
