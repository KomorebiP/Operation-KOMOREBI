param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
& (Join-Path $Work "Install_or_Repair_Arc3_Offline.ps1") -EnvName $EnvName
& (Join-Path $Work "Check_Offline_Environment.ps1") -EnvName $EnvName
& (Join-Path $Work "Run_Tests.ps1") -EnvName $EnvName
& (Join-Path $Work "1_Validate_25_Tests.ps1") -EnvName $EnvName
& (Join-Path $Work "2_List_25_Tests.ps1") -EnvName $EnvName

Write-Host "Preflight completed. The next step is 3_Official_Smoke_All_25.ps1." -ForegroundColor Green
