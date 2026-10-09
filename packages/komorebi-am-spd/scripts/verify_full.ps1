$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Root "research\original"
if (-not (Test-Path -LiteralPath (Join-Path $Source "verify_am_spd_final.py"))) {
    throw "Historical verification requires the full source bundle containing research/original. Use python -m am_spd verify --full for the installed package."
}
$Stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$Artifact = Join-Path $Root "artifacts\verification"
New-Item -ItemType Directory -Force -Path $Artifact | Out-Null
$RunDirectory = Join-Path $Artifact ("run_" + $Stamp + "_" + [Guid]::NewGuid().ToString("N"))
$WorkingSource = Join-Path $RunDirectory "research"
New-Item -ItemType Directory -Path $WorkingSource -Force | Out-Null
Get-ChildItem -LiteralPath $Source -Force | Copy-Item -Destination $WorkingSource -Recurse -Force
$Log = Join-Path $RunDirectory "full_verification.log"
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
function Invoke-PythonLogged {
    param([string[]]$Arguments, [switch]$Append)
    if ($Append) {
        & python @Arguments 2>&1 | Tee-Object -FilePath $Log -Append
    } else {
        & python @Arguments 2>&1 | Tee-Object -FilePath $Log
    }
    if ($LASTEXITCODE -ne 0) { throw "Python command failed: python $($Arguments -join ' ')" }
}
Push-Location $Root
try {
    Invoke-PythonLogged -Arguments @("-m", "am_spd", "verify", "--full")
} finally {
    Pop-Location
}
Push-Location $WorkingSource
try {
    Invoke-PythonLogged -Arguments @("infinite_packet_gibbs_reconstruction.py", "--tests-only") -Append
    Invoke-PythonLogged -Arguments @("verify_singular_packet_decomposition.py") -Append
    Invoke-PythonLogged -Arguments @("verify_am_spd.py") -Append
    Invoke-PythonLogged -Arguments @("verify_am_spd_final.py") -Append
} finally {
    Pop-Location
}
Write-Host $Log
