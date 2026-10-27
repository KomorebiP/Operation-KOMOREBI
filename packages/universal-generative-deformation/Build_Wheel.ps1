$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
    Remove-Item .\dist\* -Force -ErrorAction SilentlyContinue
    python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .\dist
}
finally {
    Pop-Location
}
