param([string]$Python="")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    else { throw "Python was not found" }
}
$env:PYTHONPATH = Join-Path $Root "src"
& $Python -m rrct_lab verify
if ($LASTEXITCODE -ne 0) { throw "Package verification failed" }
& $Python -m pytest -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
& $Python -m rrct_lab smoke --config .\configs\00_smoke.toml
if ($LASTEXITCODE -ne 0) { throw "Smoke matrix failed" }
Write-Host "V060_LOCAL_CHECKS_PASSED"
