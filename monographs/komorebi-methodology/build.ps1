$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    python build.py
    if ($LASTEXITCODE -ne 0) { throw "Build failed. See the output and audit logs." }
} finally {
    Pop-Location
}
