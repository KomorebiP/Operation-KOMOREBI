param(
    [string]$PythonExe = "python",
    [string]$KomorebiSrc = $env:KOMOREBI_MATH_SRC,
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Runner = Join-Path $Root "scripts\run_synthetic.py"
$Report = Join-Path $Root "outputs\synthetic_summary.json"

$Arguments = @($Runner, "--output", $Report)
if ($KomorebiSrc) {
    $Arguments += @("--komorebi-src", $KomorebiSrc)
}

& $PythonExe @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Synthetic acceptance suite failed."
}

if ($RunTests) {
    Push-Location $Root
    try {
        & $PythonExe -m pytest -q
        if ($LASTEXITCODE -ne 0) {
            throw "Unit tests failed."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "All requested checks passed. Report: $Report"
