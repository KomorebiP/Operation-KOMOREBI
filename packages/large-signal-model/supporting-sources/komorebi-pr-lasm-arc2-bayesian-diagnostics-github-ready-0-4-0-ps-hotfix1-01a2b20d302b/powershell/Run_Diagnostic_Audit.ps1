param(
  [Parameter(Mandatory=$true)][string]$DataDir,
  [string]$Environment="komorebi-full",
  [double]$TimeLimit=0.05,
  [int]$MaxTasks=100,
  [int]$ReportFailures=25,
  [int]$DiagnosticLimit=100,
  [switch]$IncludeSolved,
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
$Results=Join-Path $Root "results"
$Output=Join-Path $Results "diagnostic_submission.json"
$Report=Join-Path $Results "diagnostic_report.json"
$Posterior=Join-Path $Results "diagnostic_posterior.json"
$Atlas=Join-Path $Results "diagnostic_atlas"
New-Item -ItemType Directory -Force -Path $Results | Out-Null
$Arguments=@(
  "run","-n",$Environment,"python","-m","komorebi_arc2",
  "--input",$Challenges,
  "--solutions",$Solutions,
  "--output",$Output,
  "--report",$Report,
  "--posterior-diagnostics",$Posterior,
  "--diagnostics-dir",$Atlas,
  "--time-limit",$TimeLimit,
  "--report-failures",$ReportFailures
)
if($MaxTasks -gt 0){$Arguments += @("--max-tasks",$MaxTasks)}
if($DiagnosticLimit -gt 0){$Arguments += @("--diagnostic-limit",$DiagnosticLimit)}
if($IncludeSolved){$Arguments += "--include-solved-diagnostics"}
Invoke-KomorebiConda -CondaExecutable $Conda -Arguments $Arguments
$Index=Join-Path $Atlas "index.html"
if(-not (Test-Path -LiteralPath $Index -PathType Leaf)){throw "Diagnostic audit completed without creating: $Index"}
Write-Host "Diagnostic atlas: $Index"
