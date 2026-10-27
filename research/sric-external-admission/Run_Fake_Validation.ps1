$ErrorActionPreference = "Stop"

function Invoke-PythonChecked {
    param([Parameter(Mandatory=$true)][string[]]$Arguments)
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE: python $($Arguments -join ' ')"
    }
}

Push-Location $PSScriptRoot
try {
    $env:PYTHONPATH = $PSScriptRoot
    Invoke-PythonChecked -Arguments @("-m", "sric_real_lrm", "make-fixture", "--output", ".\data\engineered_fixture.json", "--count", "48")
    Invoke-PythonChecked -Arguments @("-m", "sric_real_lrm", "stage-fake", "--config", ".\configs\fake_fixture.json", "--data", ".\data\engineered_fixture.json", "--output", ".\frozen\fake_fixture_preaudit_seal.json")
    Invoke-PythonChecked -Arguments @("-m", "sric_real_lrm", "run-fake", "--config", ".\configs\fake_fixture.json", "--data", ".\data\engineered_fixture.json", "--output", ".\results\fake_fixture_block24.json")
    Invoke-PythonChecked -Arguments @("-m", "pytest", "-q")
    Invoke-PythonChecked -Arguments @(".\independent_verify.py")
    Invoke-PythonChecked -Arguments @(".\build_manifest.py")
    Invoke-PythonChecked -Arguments @(".\verify_package.py")
} finally {
    Pop-Location
}
