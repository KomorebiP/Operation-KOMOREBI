param([string]$PythonExecutable = "python")
$ErrorActionPreference = "Stop"
& $PythonExecutable (Join-Path $PSScriptRoot "verify_release.py") --root $PSScriptRoot
if ($LASTEXITCODE -ne 0) {
    throw "Offline verification failed with exit code $LASTEXITCODE."
}
