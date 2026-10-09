[CmdletBinding()]
param(
    [string]$Wheelhouse = (Join-Path (Split-Path -Parent $PSScriptRoot) "wheelhouse"),
    [string]$Environment = (Join-Path (Split-Path -Parent $PSScriptRoot) ".venv"),
    [string]$PythonVersion = "3.13"
)
$ErrorActionPreference = "Stop"
& py "-$PythonVersion" -m venv $Environment
if ($LASTEXITCODE -ne 0) { throw "Could not create the requested Python environment" }
$Python = Join-Path $Environment "Scripts\python.exe"
$ReleaseLock = Join-Path (Split-Path -Parent $PSScriptRoot) "requirements-release-lock.txt"
& $Python -m pip install --no-index --only-binary=:all: --find-links $Wheelhouse --constraint $ReleaseLock "komorebi-am-spd==1.0.0"
if ($LASTEXITCODE -ne 0) { throw "Offline wheel installation failed; check interpreter and wheelhouse compatibility" }
& $Python -m am_spd verify --full
if ($LASTEXITCODE -ne 0) { throw "Installed package verification failed" }
& $Python -m am_spd info
if ($LASTEXITCODE -ne 0) { throw "Installed package metadata check failed" }
