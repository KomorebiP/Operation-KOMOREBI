param(
    [string]$EnvName = "arc3-offline",
    [ValidateSet("quick", "balanced", "thorough")]
    [string]$Profile = "balanced",
    [ValidateSet("easy", "hard", "id")]
    [string]$Order = "easy",
    [int]$Seed = 0,
    [switch]$Fresh,
    [switch]$RerunUnsolved
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work "results\suite_25"

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

$Arguments = @(
    "-m", "komorebi_arc3_offline", "suite-run",
    "--environments-dir", $EnvironmentsDir,
    "--output", $Output,
    "--profile", $Profile,
    "--order", $Order,
    "--seed", $Seed
)
if ($Fresh) {
    $Arguments += "--no-resume"
}
if ($RerunUnsolved) {
    $Arguments += "--rerun-unsolved"
}

& conda run --no-capture-output -n $EnvName python @Arguments
$ExitCode = $LASTEXITCODE
if ($ExitCode -gt 1) {
    throw "The 25-game suite failed with exit code $ExitCode."
}
if ($ExitCode -eq 1) {
    Write-Host "The suite reached the end, but at least one game raised an exception. Completed games are checkpointed." -ForegroundColor Yellow
} else {
    Write-Host "The 25-game suite completed without runtime exceptions." -ForegroundColor Green
}
Write-Host "Run the same command again to resume and skip recorded games."
Write-Host "Use -RerunUnsolved to repeat only games that have a result but were not solved."
Write-Host "Results: $Output"
