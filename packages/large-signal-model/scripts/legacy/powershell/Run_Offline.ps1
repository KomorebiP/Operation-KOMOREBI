param(
    [Parameter(Mandatory=$true)]
    [string]$Game,
    [string]$EnvName = "arc3-offline",
    [string]$EnvironmentsDir = "",
    [string]$Output = "",
    [int]$MaxActions = 500,
    [int]$InitialProbes = 8,
    [int]$Probes = 2,
    [int]$ProbeInterval = 4,
    [int]$Seed = 0,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($EnvironmentsDir)) {
    $EnvironmentsDir = Join-Path $Work "environment_files"
}
if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $Work ("results\" + $Game)
}
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

$Arguments = @(
    "-m", "komorebi_arc3_offline", "run",
    "--game", $Game,
    "--environments-dir", $EnvironmentsDir,
    "--output", $Output,
    "--max-actions", $MaxActions,
    "--initial-probes", $InitialProbes,
    "--probes", $Probes,
    "--probe-interval", $ProbeInterval,
    "--seed", $Seed
)
if ($Verbose) {
    $Arguments += "--verbose"
}
& conda run --no-capture-output -n $EnvName python @Arguments
$ExitCode = $LASTEXITCODE
if ($ExitCode -gt 1) {
    throw "Offline ARC-AGI-3 run failed with exit code $ExitCode."
}
if ($ExitCode -eq 1) {
    Write-Host "Run completed without solving the game. Results are in $Output" -ForegroundColor Yellow
} else {
    Write-Host "Game solved. Results are in $Output" -ForegroundColor Green
}
