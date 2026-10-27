$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    python run_reference_checks.py --verify-hashes
    if ($LASTEXITCODE -ne 0) { throw "Reference replay failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
