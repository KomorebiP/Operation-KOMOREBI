param(
    [ValidateSet("auto", "cpu", "cuda")][string]$Device = "auto",
    [string]$Python = "",
    [string]$OutputRoot = "results",
    [string]$OutputDirectory = "",
    [string]$Config = "configs\confirmatory.json",
    [int[]]$DataSeeds = @(1729, 2718),
    [int[]]$ModelSeeds = @(1729, 2718, 31415),
    [int]$SmokeSeed = 1729,
    [switch]$Force,
    [switch]$SkipSmoke,
    [switch]$StopOnFailure
)

$ErrorActionPreference = "Stop"
$runner = Join-Path $PSScriptRoot "PowerShell\Run_Confirmatory.ps1"
& $runner @PSBoundParameters
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
