param(
    [string]$EnvName = "arc3-offline",
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $Work "results\suite_25"
}

& conda run --no-capture-output -n $EnvName python -m komorebi_arc3_offline suite-summary `
    --output $Output
if ($LASTEXITCODE -ne 0) {
    throw "No suite summary was found under $Output."
}

Write-Host "Detailed table: $Output\suite_index.csv"
