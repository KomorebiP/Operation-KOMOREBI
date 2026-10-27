param(
    [string]$EnvName = "arc3-offline"
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$CondaCommand = Get-Command conda -ErrorAction SilentlyContinue
if (-not $CondaCommand) {
    throw "Conda was not found. Run this from Anaconda PowerShell Prompt."
}

$EnvironmentJson = (& conda env list --json | Out-String) | ConvertFrom-Json
$EnvironmentPath = $null
foreach ($Path in $EnvironmentJson.envs) {
    if ((Split-Path $Path -Leaf) -eq $EnvName) {
        $EnvironmentPath = $Path
        break
    }
}
if (-not $EnvironmentPath) {
    throw "Conda environment '$EnvName' does not exist. Run Setup_Conda_OnlineOnce.ps1 first."
}

$Wheel = Get-ChildItem -Path $Work -Recurse -File -Filter "komorebi_arc3_offline-*.whl" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $Wheel) {
    throw "No komorebi_arc3_offline wheel was found under $Work."
}

Write-Host "Using Conda environment: $EnvironmentPath"
Write-Host "Installing local runner: $($Wheel.FullName)"
& conda run -n $EnvName python -m pip install --no-deps --force-reinstall $Wheel.FullName
if ($LASTEXITCODE -ne 0) {
    throw "Local runner installation failed."
}

& conda run --no-capture-output -n $EnvName python (Join-Path $Work "scripts\print_installed_versions.py")
if ($LASTEXITCODE -ne 0) {
    throw "The installed packages could not be imported."
}

Write-Host "Local runner installation is ready." -ForegroundColor Green
