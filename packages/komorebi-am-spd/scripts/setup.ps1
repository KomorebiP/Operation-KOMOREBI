$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-NativeChecked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Command $($Arguments -join ' ')"
    }
}

Invoke-NativeChecked "py" @("-m", "venv", ".venv")
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
Invoke-NativeChecked $Python @("-m", "pip", "install", "--upgrade", "pip")
Invoke-NativeChecked $Python @("-m", "pip", "install", "-e", ".[dev,research]")
Invoke-NativeChecked $Python @("-m", "pytest")
Invoke-NativeChecked $Python @("-m", "am_spd", "verify", "--full")
Write-Host "Setup and verification passed. Use .\.venv\Scripts\python.exe without activation."
