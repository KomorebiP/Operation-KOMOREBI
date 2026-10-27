param([string]$Python = "", [switch]$FullReplay)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { $Python = (Get-Command py).Source }
    else { throw "Python was not found" }
}
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = (Join-Path $Root "reference")
$env:SOURCE_DATE_EPOCH = "1787616000"
$env:FORCE_SOURCE_DATE = "1"
$env:TZ = "UTC"

& $Python verify_release.py
if ($LASTEXITCODE -ne 0) { throw "Initial package verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests
if ($LASTEXITCODE -ne 0) { throw "Focused tests failed" }
& $Python reference/verify_sources.py
if ($LASTEXITCODE -ne 0) { throw "Source validation failed" }
& latexmk -pdf -g -interaction=nonstopmode -halt-on-error -jobname=operator_symbolic_ai_language_v0.5 main.tex
if ($LASTEXITCODE -ne 0) { throw "PDF rebuild failed" }
& $Python verify_release.py
if ($LASTEXITCODE -ne 0) { throw "Post-build package verification failed" }

if ($FullReplay) {
    & (Join-Path $Root "RUN_OSL_CORE.ps1") -Python $Python
    if ($LASTEXITCODE -ne 0) { throw "Full finite certificate replay failed" }
    & $Python verify_release.py
    if ($LASTEXITCODE -ne 0) { throw "Post-replay package verification failed" }
    Write-Host "OPERATOR_SYMBOLIC_AI_V05_FULL_REPLAY_VERIFIED"
} else {
    Write-Host "OPERATOR_SYMBOLIC_AI_V05_RELEASE_VERIFIED"
}
