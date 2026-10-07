param([switch]$Tests)
$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
$useLauncher = $false
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    $useLauncher = $true
}
if (-not $python) { throw "Python was not found. Install or activate Python before checking the bundle." }
$arguments = @()
if ($useLauncher) { $arguments += "-3" }
$arguments += (Join-Path $PSScriptRoot "scripts/check_bundle.py")
if ($Tests) { $arguments += "--tests" }
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw "Bundle check failed with exit code $LASTEXITCODE." }
