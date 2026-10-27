param(
    [string]$EnvName = "arc3-offline",
    [ValidateSet("quick", "balanced", "thorough")]
    [string]$Profile = "balanced",
    [int]$Seed = 0
)

$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
& "$Work\5_Run_All_25_Offline.ps1" `
    -EnvName $EnvName `
    -Profile $Profile `
    -Seed $Seed
exit $LASTEXITCODE
