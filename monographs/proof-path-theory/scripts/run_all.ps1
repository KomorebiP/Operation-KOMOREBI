# Publication checks; Lean replay is an explicit separate operation.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    $env:PYTHONPATH = Join-Path $root "src"
    python -m pytest -o addopts='' -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
    foreach ($script in @("deep_validation.py", "verify_bridge.py", "check_recovery_extension.py", "check_trace_exchange.py", "verify_publication_edition.py")) {
        python (Join-Path $PSScriptRoot $script)
        if ($LASTEXITCODE -ne 0) { throw "$script failed" }
    }
} finally { Pop-Location }
