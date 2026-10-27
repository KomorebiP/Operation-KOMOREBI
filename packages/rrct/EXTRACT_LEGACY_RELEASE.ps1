param([Parameter(Mandatory=$true)][string]$Version,[string]$Destination="",[string]$Python="")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Destination)) { $Destination = Join-Path $Root "runs\legacy_$Version" }
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = (Get-Command python).Source }
    else { throw "Python was not found" }
}
$env:PYTHONPATH = Join-Path $Root "src"
& $Python -m rrct_lab legacy extract $Version $Destination
if ($LASTEXITCODE -ne 0) { throw "Legacy release extraction failed" }
