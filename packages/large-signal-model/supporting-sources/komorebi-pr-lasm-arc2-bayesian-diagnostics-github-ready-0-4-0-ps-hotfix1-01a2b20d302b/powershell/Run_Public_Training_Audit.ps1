param(
  [Parameter(Mandatory=$true)][string]$DataDir,
  [string]$Environment="komorebi-full",
  [double]$TimeLimit=0.05,
  [int]$MaxTasks=0,
  [int]$ReportFailures=25,
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
$Output=Join-Path $Root "results\public_training_submission.json"
$Report=Join-Path $Root "results\public_training_report.json"
$Diagnostics=Join-Path $Root "results\public_training_posterior_diagnostics.json"
$Arguments=@(
  "run","-n",$Environment,"python","-m","komorebi_arc2",
  "--input",$Challenges,"--solutions",$Solutions,"--output",$Output,
  "--report",$Report,"--posterior-diagnostics",$Diagnostics,
  "--time-limit",$TimeLimit,"--report-failures",$ReportFailures
)
if($MaxTasks -gt 0){$Arguments += @("--max-tasks",$MaxTasks)}
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments $Arguments
