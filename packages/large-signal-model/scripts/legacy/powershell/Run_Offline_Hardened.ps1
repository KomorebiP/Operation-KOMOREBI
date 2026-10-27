param(
    [Parameter(Mandatory=$true)]
    [string]$Game,
    [string]$EnvName = "arc3-offline",
    [string]$EnvironmentsDir = "",
    [string]$Output = "",
    [int]$MaxActions = 500,
    [int]$InitialProbes = 8,
    [int]$Probes = 2,
    [int]$ProbeInterval = 4,
    [int]$Seed = 0,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$RuleName = "Komorebi-ARC3-Offline-$PID"
$Python = (& conda run -n $EnvName python (Join-Path $Work "scripts\print_python_executable.py") | Select-Object -Last 1).Trim()
if ([string]::IsNullOrWhiteSpace($Python) -or -not (Test-Path $Python)) {
    throw "Could not resolve the Python executable for Conda environment '$EnvName'."
}

try {
    New-NetFirewallRule `
        -DisplayName $RuleName `
        -Direction Outbound `
        -Program $Python `
        -Action Block `
        -Profile Any | Out-Null

    $Parameters = @{
        Game = $Game
        EnvName = $EnvName
        MaxActions = $MaxActions
        InitialProbes = $InitialProbes
        Probes = $Probes
        ProbeInterval = $ProbeInterval
        Seed = $Seed
        Verbose = $Verbose
    }
    if (-not [string]::IsNullOrWhiteSpace($EnvironmentsDir)) {
        $Parameters["EnvironmentsDir"] = $EnvironmentsDir
    }
    if (-not [string]::IsNullOrWhiteSpace($Output)) {
        $Parameters["Output"] = $Output
    }
    & (Join-Path $Work "Run_Offline.ps1") @Parameters
} finally {
    Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
}
