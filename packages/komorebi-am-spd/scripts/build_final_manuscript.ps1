$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Root "docs\paper\final"
Push-Location $Source
try {
    & .\build.ps1
    if ($LASTEXITCODE -ne 0) { throw "Final manuscript build failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
