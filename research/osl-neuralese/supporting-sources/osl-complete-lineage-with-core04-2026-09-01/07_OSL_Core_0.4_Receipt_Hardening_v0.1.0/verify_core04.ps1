$ErrorActionPreference = "Stop"
$ReleaseRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ReleaseRoot
try {
    $env:PYTHONPATH = Join-Path $ReleaseRoot "reference"
    python reference/verify_core04_package.py
    if ($LASTEXITCODE -ne 0) { throw "Package integrity verification failed." }
    python reference/generate_core04_evidence.py
    if ($LASTEXITCODE -ne 0) { throw "Conformance evidence regeneration failed." }
    python reference/generate_core04_bridge_report.py
    if ($LASTEXITCODE -ne 0) { throw "Discovery Bridge verification failed." }
    python reference/generate_core04_adversarial_report.py
    if ($LASTEXITCODE -ne 0) { throw "Adversarial regression verification failed." }
    python reference/generate_test_report.py
    if ($LASTEXITCODE -ne 0) { throw "Test verification failed." }
    python reference/verify_core04_package.py
    if ($LASTEXITCODE -ne 0) { throw "Regenerated evidence differs from the manifest." }
} finally {
    Pop-Location
}
