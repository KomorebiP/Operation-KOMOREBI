param(
    [string]$EnvName = "arc3-offline",
    [ValidateSet("quick", "balanced", "thorough")]
    [string]$Profile = "balanced",
    [ValidateSet("easy", "hard", "id")]
    [string]$Order = "easy",
    [int]$Limit = 0
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentsDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work "results\suite_25"

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline suite-plan `
    --environments-dir $EnvironmentsDir `
    --output $Output `
    --profile $Profile `
    --order $Order `
    --limit $Limit
if ($LASTEXITCODE -ne 0) {
    throw "Suite planning failed."
}

Write-Host "Plan written to $Output\suite_plan.csv" -ForegroundColor Green
