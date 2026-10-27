param(
    [string]$EnvName = "arc3-offline",
    [ValidateSet("quick", "balanced", "thorough")]
    [string]$Profile = "quick",
    [int]$Seed = 0
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work "results\pilot_5"

$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:ENVIRONMENTS_DIR = $EnvironmentsDir
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline suite-run `
    --environments-dir $EnvironmentsDir `
    --output $Output `
    --profile $Profile `
    --order easy `
    --limit 5 `
    --seed $Seed
$ExitCode = $LASTEXITCODE
if ($ExitCode -gt 1) {
    throw "The five-game pilot failed with exit code $ExitCode."
}
if ($ExitCode -eq 1) {
    Write-Host "The pilot reached the end, but one or more games raised an exception. See suite_index.csv." -ForegroundColor Yellow
} else {
    Write-Host "The five-game pilot completed." -ForegroundColor Green
}
Write-Host "Results: $Output"
