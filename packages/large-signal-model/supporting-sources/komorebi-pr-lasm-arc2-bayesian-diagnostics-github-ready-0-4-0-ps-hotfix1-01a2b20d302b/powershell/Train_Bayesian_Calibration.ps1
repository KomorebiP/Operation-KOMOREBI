param(
  [Parameter(Mandatory=$true)][string]$DataDir,
  [string]$Environment="komorebi-full",
  [double]$TimeLimit=0.05,
  [int]$MaximumCandidates=16,
  [string]$CondaExecutable=""
)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "Conda_Runtime.ps1")
$Conda=Resolve-KomorebiCondaExecutable -ExplicitPath $CondaExecutable
Write-Host "Using Conda executable: $Conda"
$Root=Split-Path -Parent $PSScriptRoot
$Challenges=Join-Path $DataDir "arc-agi_training_challenges.json"
$Solutions=Join-Path $DataDir "arc-agi_training_solutions.json"
if(-not (Test-Path -LiteralPath $Challenges -PathType Leaf)){throw "Challenge file was not found: $Challenges"}
if(-not (Test-Path -LiteralPath $Solutions -PathType Leaf)){throw "Solution file was not found: $Solutions"}
$Output=Join-Path $Root "src\komorebi_arc2\data\bayesian_lasm_calibration.json"
$Report=Join-Path $Root "benchmarks\bayesian_calibration_report.json"
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments @(
  "run","-n",$Environment,"python",(Join-Path $Root "scripts\train_bayesian_lasm.py"),
  "--challenges",$Challenges,"--solutions",$Solutions,"--output",$Output,
  "--report",$Report,"--holdout-fraction","0.20","--time-limit",$TimeLimit,
  "--maximum-candidates",$MaximumCandidates
)
