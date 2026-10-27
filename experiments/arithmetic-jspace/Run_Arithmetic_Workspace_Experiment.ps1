param(
    [ValidateSet("workspace_smoke", "carry_discovery", "carry_confirmatory")]
    [string]$Profile = "workspace_smoke",
    [string]$Python = "",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [string]$Output = "",
    [int]$Seed = 0,
    [string]$LockFile = "",
    [switch]$SkipInstall,
    [switch]$NoResume
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Resolve-PythonCommand {
    param([string]$Requested)

    if (-not [string]::IsNullOrWhiteSpace($Requested)) {
        if (($Requested -match '[\\/]') -and -not (Test-Path -LiteralPath $Requested -PathType Leaf)) {
            throw "Requested Python executable does not exist: $Requested"
        }
        return $Requested
    }

    $preferred = Join-Path $env:USERPROFILE "miniconda3\envs\komorebi-full\python.exe"
    if (Test-Path -LiteralPath $preferred -PathType Leaf) {
        return $preferred
    }
    if (-not [string]::IsNullOrWhiteSpace($env:VIRTUAL_ENV)) {
        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($env:CONDA_PREFIX)) {
        $candidate = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $command) {
        return $command.Source
    }
    throw "No Python executable was found. Supply -Python with an absolute path."
}

$Python = Resolve-PythonCommand -Requested $Python

$runRoot = Join-Path $env:USERPROFILE "Downloads\Arithmetic_Workspace_Runs"
if ([string]::IsNullOrWhiteSpace($Output)) {
    $runName = $Profile
    if ($Seed -gt 0) {
        $runName += "_seed$Seed"
    }
    $Output = Join-Path $runRoot $runName
}
$Output = [System.IO.Path]::GetFullPath($Output)

$configPath = Join-Path $PSScriptRoot "configs\$Profile.json"
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Profile config is missing: $configPath"
}
$entryPoint = Join-Path $PSScriptRoot "run_workspace_experiment.py"
if (-not (Test-Path -LiteralPath $entryPoint -PathType Leaf)) {
    throw "Experiment entry point is missing: $entryPoint"
}

if ($Profile -eq "carry_confirmatory") {
    if ([string]::IsNullOrWhiteSpace($LockFile)) {
        $LockFile = Join-Path $runRoot "carry_discovery\workspace_lock.json"
    }
    $LockFile = [System.IO.Path]::GetFullPath($LockFile)
    if (-not (Test-Path -LiteralPath $LockFile -PathType Leaf)) {
        throw "Confirmatory analysis requires the frozen discovery lock. Supply -LockFile or run carry_discovery first. Expected: $LockFile"
    }
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:TOKENIZERS_PARALLELISM = "false"
$env:PYTHONHASHSEED = if ($Seed -gt 0) { [string]$Seed } else { "0" }
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"

Push-Location $PSScriptRoot
try {
    Write-Host "PROFILE=$Profile"
    Write-Host "PYTHON_COMMAND=$Python"
    Write-Host "DEVICE=$Device"
    Write-Host "OUTPUT=$Output"
    if ($Seed -gt 0) {
        Write-Host "SEED_OVERRIDE=$Seed"
    } else {
        Write-Host "SEEDS=PROFILE_CONFIG"
    }
    if ($Profile -eq "carry_confirmatory") {
        Write-Host "LOCK_FILE=$LockFile"
    }
    Write-Host "PROGRESS_EVERY_STEPS=100"

    & $Python --version
    if ($LASTEXITCODE -ne 0) {
        throw "Selected Python could not run"
    }

    & $Python verify_package.py
    if ($LASTEXITCODE -ne 0) {
        throw "Package verification failed"
    }

    & $Python preflight.py --device $Device
    $preflightExitCode = $LASTEXITCODE
    if ($preflightExitCode -ne 0) {
        if ($SkipInstall) {
            throw "Runtime preflight failed with exit code $preflightExitCode and -SkipInstall was selected"
        }
        if (($preflightExitCode -ne 2) -and ($preflightExitCode -ne 4)) {
            throw "Runtime preflight failed with exit code $preflightExitCode; automatic dependency installation was not attempted"
        }
        Write-Host "INSTALLING_MISSING_RUNTIME_PACKAGES=True"
        & $Python -m pip install torch numpy
        if ($LASTEXITCODE -ne 0) {
            throw "Runtime dependency installation failed"
        }
        & $Python preflight.py --device $Device
        if ($LASTEXITCODE -ne 0) {
            throw "Runtime preflight still fails after dependency installation"
        }
    }

    $arguments = @(
        "-u",
        "run_workspace_experiment.py",
        "--profile", $Profile,
        "--output", $Output,
        "--device", $Device
    )
    if ($Seed -gt 0) {
        $arguments += @("--seed", [string]$Seed)
    }
    if ($Profile -eq "carry_confirmatory") {
        $arguments += @("--lock-file", $LockFile)
    }
    if ($NoResume) {
        $arguments += "--no-resume"
    }

    & $Python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Arithmetic workspace experiment failed with exit code $LASTEXITCODE"
    }
    Write-Host "EXPERIMENT_RUN=PASS"
    Write-Host "RESULT_PATH=$Output"
} catch {
    Write-Host "EXPERIMENT_RUN=FAIL"
    Write-Host "PARTIAL_RESULT_PATH=$Output"
    Write-Host "IF_INTERRUPTED_RERUN_IDENTICAL_COMMAND_TO_RESUME=True"
    throw
} finally {
    Pop-Location
}
