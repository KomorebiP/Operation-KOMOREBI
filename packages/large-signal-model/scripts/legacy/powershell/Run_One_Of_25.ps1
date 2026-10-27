param(
    [Parameter(Mandatory=$true)][string]$Game,
    [ValidateSet("quick", "balanced", "thorough")][string]$Profile = "balanced",
    [string]$EnvName = "arc3-offline",
    [int]$Seed = 0,
    [switch]$NoResume,
    [switch]$RerunUnsolved,
    [switch]$Verbose
)
$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$EnvironmentDir = Join-Path $Work "environment_files"
$Output = Join-Path $Work ("results\single_" + $Game + "_" + $Profile)
$env:OPERATION_MODE = "OFFLINE"
$env:ARC_API_KEY = ""
$env:ARC_BASE_URL = "http://127.0.0.1:9"
$env:KOMOREBI_ARC3_OFFLINE_ONLY = "1"
$Args = @("-m", "komorebi_arc3_offline", "suite-run", "--environments-dir", $EnvironmentDir, "--output", $Output, "--profile", $Profile, "--game", $Game, "--seed", $Seed)
if ($NoResume) { $Args += "--no-resume" }
if ($RerunUnsolved) { $Args += "--rerun-unsolved" }
if ($Verbose) { $Args += "--verbose" }
& conda run --no-capture-output -n $EnvName python @Args
if ($LASTEXITCODE -ne 0) { throw "The selected game run failed." }
