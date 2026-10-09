param(
    [string[]]$Cases = @(),
    [string]$OutputDirectory = "artifacts\paper-replay",
    [switch]$IncludeInput
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$Arguments = @("-m", "am_spd", "reproduce-paper", "--output-dir", $OutputDirectory, "--strict-reference")
if ($Cases.Count -gt 0) { $Arguments += @("--cases") + $Cases }
if ($IncludeInput) { $Arguments += "--include-input" }
& python @Arguments
if ($LASTEXITCODE -ne 0) { throw "Paper replay failed" }
