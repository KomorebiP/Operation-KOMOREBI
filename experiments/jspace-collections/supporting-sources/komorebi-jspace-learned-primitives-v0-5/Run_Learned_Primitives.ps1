param(
    [ValidateSet('demo','verify','test','retrain')]
    [string]$Mode = 'demo'
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $env:OPENBLAS_NUM_THREADS = '1'
    $pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path $pythonExe)) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3 -m venv .venv
        } else {
            & python -m venv .venv
        }
        if ($LASTEXITCODE -ne 0) { throw 'Creating the Python environment failed.' }
        & $pythonExe -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Installing NumPy failed.' }
    }
    switch ($Mode) {
        'demo' { & $pythonExe demo.py }
        'verify' {
            & $pythonExe verify_delivery.py
            if ($LASTEXITCODE -ne 0) { throw 'Frozen delivery replay failed.' }
            & $pythonExe audit_admission.py
        }
        'test' { & $pythonExe -m unittest -v test_primitives.py }
        'retrain' {
            $runFolder = 'rerun_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
            & $pythonExe run_experiment.py all --output $runFolder
        }
    }
    if ($LASTEXITCODE -ne 0) { throw "The $Mode command failed." }
} finally {
    Pop-Location
}
