param([ValidateSet('demo','test','verify')][string]$Mode='demo')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $env:OPENBLAS_NUM_THREADS = '1'
    $pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path $pythonExe)) {
        if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv .venv }
        else { & python -m venv .venv }
        if ($LASTEXITCODE -ne 0) { throw 'Creating the Python environment failed.' }
        & $pythonExe -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Installing NumPy failed.' }
    }
    switch ($Mode) {
        'demo' { & $pythonExe demo.py }
        'test' { & $pythonExe -m unittest -v test_machinery.py }
        'verify' { & $pythonExe verify_release.py }
    }
    if ($LASTEXITCODE -ne 0) { throw "The $Mode command failed." }
} finally { Pop-Location }
