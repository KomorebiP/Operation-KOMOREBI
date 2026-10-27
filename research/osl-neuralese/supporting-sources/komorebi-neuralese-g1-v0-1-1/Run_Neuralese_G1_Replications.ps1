param(
    [string]$Model = "",
    [string]$OutputRoot = "",
    [string]$Python = "",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $Python) {
    $RawPythonCandidates = @(
        "$env:USERPROFILE\miniconda3\envs\komorebi-full\python.exe",
        "$env:USERPROFILE\anaconda3\envs\komorebi-full\python.exe",
        "$env:LOCALAPPDATA\miniconda3\envs\komorebi-full\python.exe"
    )
    $PythonCandidates = @($RawPythonCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Sort-Object -Unique)
    if ($PythonCandidates.Count -ne 1) {
        throw "Could not identify exactly one komorebi-full Python. Pass -Python explicitly."
    }
    $Python = $PythonCandidates[0]
}

if (-not $OutputRoot) {
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputRoot = "$env:USERPROFILE\Downloads\Neuralese_G1_Replications\$Timestamp"
}

$Seeds = @(711001, 711002, 711003)
$RunDirectories = @()
foreach ($RegisteredSeed in $Seeds) {
    $RunDirectory = Join-Path $OutputRoot "pilot-$RegisteredSeed"
    $RunParameters = @{
        Profile = "pilot"
        Output = $RunDirectory
        Python = $Python
        Device = $Device
        Seed = $RegisteredSeed
    }
    if ($Model) {
        $RunParameters["Model"] = $Model
    }
    & "$Root\Run_Neuralese_G1.ps1" @RunParameters
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $RunDirectories += $RunDirectory
}

$Aggregate = Join-Path $OutputRoot "replication_summary.json"
& $Python "$Root\aggregate_replications.py" --runs @RunDirectories --output $Aggregate
exit $LASTEXITCODE
