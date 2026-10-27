param(
    [string]$EnvName = "arc3-offline",
    [switch]$InstallTorch
)

$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$CondaCommand = Get-Command conda -ErrorAction SilentlyContinue
if (-not $CondaCommand) {
    throw "Conda was not found. Run this from Anaconda PowerShell Prompt."
}

# Locate the local runner wheel before changing the environment.  The full
# release normally stores it under dist/, and the air-gap bundle stores a copy
# under wheelhouse/.  Root-level fallback makes the script robust to manual
# extraction or copying.
$WheelCandidates = @()
$SearchLocations = @(
    (Join-Path $Work "dist"),
    (Join-Path $Work "wheelhouse"),
    $Work,
    (Join-Path $env:USERPROFILE "Downloads")
)
foreach ($Location in $SearchLocations) {
    if (Test-Path $Location) {
        $WheelCandidates += Get-ChildItem -Path $Location -Filter "komorebi_arc3_offline-*.whl" -File -ErrorAction SilentlyContinue
    }
}
$Wheel = $WheelCandidates | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $Wheel) {
    throw @"
The local runner wheel was not found.

Expected one of:
  $Work\dist\komorebi_arc3_offline-*.whl
  $Work\wheelhouse\komorebi_arc3_offline-*.whl
  $Work\komorebi_arc3_offline-*.whl
  $env:USERPROFILE\Downloads\komorebi_arc3_offline-*.whl

This usually means only part of the release was extracted. Extract the complete
flat ZIP into a new folder, or copy the standalone wheel into $Work\dist.
"@
}
Write-Host "Local runner wheel: $($Wheel.FullName)"

$EnvironmentJson = (& conda env list --json | Out-String) | ConvertFrom-Json
$EnvironmentPath = $null
foreach ($Path in $EnvironmentJson.envs) {
    if ((Split-Path $Path -Leaf) -eq $EnvName) {
        $EnvironmentPath = $Path
        break
    }
}

if (-not $EnvironmentPath) {
    Write-Host "Creating Conda environment '$EnvName' with Python 3.12..."
    & conda create -n $EnvName --override-channels -c conda-forge `
        python=3.12 numpy scipy pillow pydantic requests flask python-dotenv `
        matplotlib pytest pip -y
    if ($LASTEXITCODE -ne 0) {
        throw "Conda environment creation failed."
    }
} else {
    Write-Host "Using existing Conda environment: $EnvironmentPath"
    Write-Host "Installing only the required support packages..."
    & conda install -n $EnvName --override-channels -c conda-forge --freeze-installed `
        numpy scipy pillow pydantic requests flask python-dotenv matplotlib pytest pip -y
    if ($LASTEXITCODE -ne 0) {
        throw "Conda support-package installation failed."
    }
}

Write-Host "Installing official local ARC packages..."
& conda run -n $EnvName python -m pip install `
    --upgrade-strategy only-if-needed `
    "arc-agi==0.9.9" `
    "arcengine==0.9.3"
if ($LASTEXITCODE -ne 0) {
    throw "The official ARC package installation failed."
}

Write-Host "Installing the local offline runner without changing dependencies..."
& conda run -n $EnvName python -m pip install --no-deps --force-reinstall $Wheel.FullName
if ($LASTEXITCODE -ne 0) {
    throw "The local runner installation failed."
}

if ($InstallTorch) {
    Write-Host "Installing optional CUDA-enabled PyTorch proposal support..."
    & conda run -n $EnvName python -m pip install `
        "torch==2.11.0+cu128" `
        --index-url "https://download.pytorch.org/whl/cu128"
    if ($LASTEXITCODE -ne 0) {
        throw "Optional PyTorch installation failed. The core runner does not require PyTorch."
    }
}

Write-Host ""
Write-Host "Environment prepared." -ForegroundColor Green
Write-Host "Environment path: $(((& conda env list --json | Out-String) | ConvertFrom-Json).envs | Where-Object { (Split-Path $_ -Leaf) -eq $EnvName })"
Write-Host ""
Write-Host "Next commands:"
Write-Host "  conda activate $EnvName"
Write-Host "  & `"$Work\Check_Offline_Environment.ps1`" -EnvName $EnvName"
Write-Host "  & `"$Work\Run_Tests.ps1`" -EnvName $EnvName"
Write-Host "  & `"$Work\Run_Offline_Smoke.ps1`" -EnvName $EnvName"
Write-Host "  & `"$Work\Run_Official_Adapter_Smoke.ps1`" -EnvName $EnvName"
