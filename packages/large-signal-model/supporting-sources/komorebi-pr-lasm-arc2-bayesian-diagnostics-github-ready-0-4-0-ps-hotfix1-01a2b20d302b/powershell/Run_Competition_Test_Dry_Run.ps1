param(
  [Parameter(Mandatory=$true)][string]$DataDir,
  [string]$Environment="komorebi-full",
  [double]$SoftTimeLimit=8,
  [double]$HardTimeLimit=20,
  [int]$Workers=4,
  [string]$CondaExecutable=""
)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "Conda_Runtime.ps1")
$Conda=Resolve-KomorebiCondaExecutable -ExplicitPath $CondaExecutable
Write-Host "Using Conda executable: $Conda"
$Root=Split-Path -Parent $PSScriptRoot
$Challenges=Join-Path $DataDir "arc-agi_test_challenges.json"
if(-not (Test-Path -LiteralPath $Challenges -PathType Leaf)){throw "Challenge file was not found: $Challenges"}
$Output=Join-Path $Root "results\competition_test_submission.json"
$Report=Join-Path $Root "results\competition_test_runtime.json"
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @(
  "run","-n",$Environment,"python",(Join-Path $Root "kaggle\run_submission.py"),
  "--solver",(Join-Path $Root "kaggle\arc2_entry.py"),
  "--input",$Challenges,"--output",$Output,"--report",$Report,
  "--soft-time-limit",$SoftTimeLimit,"--hard-time-limit",$HardTimeLimit,"--workers",$Workers
)
