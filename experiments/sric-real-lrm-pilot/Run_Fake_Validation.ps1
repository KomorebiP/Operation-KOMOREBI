param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python -m pip install -r .\requirements.txt
    & $Python -m sric_real_lrm make-fixture --output .\data\engineered_fixture.json --count 48
    & $Python -m sric_real_lrm run-fake --config .\configs\fake_fixture.json --data .\data\engineered_fixture.json --output .\results\fake_fixture_audit.json
    & $Python -m pytest -q
    & $Python .\independent_verify.py
    & $Python .\build_manifest.py
    & $Python .\verify_package.py
} finally {
    Pop-Location
}
