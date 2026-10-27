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
$env:PYTHONPATH = (Join-Path $Root "reference")
& $Python reference/generate_v03_evidence.py
if ($LASTEXITCODE -ne 0) { throw "OSL-Core certificate generation failed" }
& $Python reference/verify_osl_core_v03.py --output V03_UNIFIED_VERIFICATION.json
if ($LASTEXITCODE -ne 0) { throw "OSL-Core unified verification failed" }
& $Python reference/generate_test_report.py
if ($LASTEXITCODE -ne 0) { throw "OSL-Core tests failed" }
& $Python reference/verify_sources.py
if ($LASTEXITCODE -ne 0) { throw "Python source validation failed" }
Write-Host "OSL_CORE_0_3_FINITE_METATHEORY_PASS"
