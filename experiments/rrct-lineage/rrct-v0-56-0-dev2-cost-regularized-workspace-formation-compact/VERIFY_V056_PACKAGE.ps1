param([string]$Python = "$env:CONDA_PREFIX\python.exe")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
& $Python validation/verify_build_manifest.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/verify_freeze.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/verify_results.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python validation/verify_syntax.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = "$Root\src"
& $Python -m pytest -q -p no:cacheprovider tests/test_v056.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "V056_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED"
