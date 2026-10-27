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
    } else { throw "Python was not found" }
}
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = Join-Path $Root "src"
& $Python validation/verify_v049_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "Package checksum verification failed" }
& $Python validation/verify_v049_results.py
if ($LASTEXITCODE -ne 0) { throw "Scientific result verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests/test_v049_instrumented_transformer_dyad.py
if ($LASTEXITCODE -ne 0) { throw "Focused tests failed" }
Write-Host "V049_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED"
