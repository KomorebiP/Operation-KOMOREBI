param(
  [string]$Environment="komorebi-full",
  [string]$CondaExecutable=""
)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "Conda_Runtime.ps1")
$Conda=Resolve-KomorebiCondaExecutable -ExplicitPath $CondaExecutable
Write-Host "Using Conda executable: $Conda"
$Root=Split-Path -Parent $PSScriptRoot
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","pip","install","--no-deps","--no-build-isolation","-e",$Root)
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","komorebi_arc2","--self-test")
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @("run","-n",$Environment,"python","-m","pytest",(Join-Path $Root "tests"),"-q")
