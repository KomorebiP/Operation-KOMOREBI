param(
    [ValidateSet("smoke", "balanced", "symbolic_only", "deep_symbolic", "emergence_longitudinal")]
    [string]$Profile = "smoke",
    [string]$Python = "",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [string]$Output = "",
    [int]$Seed = 314159,
    [switch]$SkipInstall,
    [switch]$NoResume
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($Python)) {
    $preferred = Join-Path $env:USERPROFILE "miniconda3\envs\komorebi-full\python.exe"
    if (Test-Path -LiteralPath $preferred -PathType Leaf) {
        $Python = $preferred
    } elseif ($env:VIRTUAL_ENV) {
        $Python = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    } elseif ($env:CONDA_PREFIX) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } else {
        $Python = "python"
    }
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    $runRoot = Join-Path $env:USERPROFILE "Downloads\Arithmetic_JSpace_Runs"
    $Output = Join-Path $runRoot ($Profile + "_seed" + $Seed)
}
$Output = [System.IO.Path]::GetFullPath($Output)

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:TOKENIZERS_PARALLELISM = "false"
$env:PYTHONHASHSEED = [string]$Seed
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"

Push-Location $PSScriptRoot
try {
    Write-Host "PYTHON_COMMAND=$Python"
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
        if ($preflightExitCode -ne 2) {
            throw "Runtime preflight failed with exit code $preflightExitCode; PyTorch installation was not attempted"
        }
        Write-Host "INSTALLING_MISSING_TORCH=True"
        & $Python -m pip install torch
        if ($LASTEXITCODE -ne 0) {
            throw "PyTorch installation failed"
        }
        & $Python preflight.py --device $Device
        if ($LASTEXITCODE -ne 0) {
            throw "Runtime preflight still fails after installation"
        }
    }

    $arguments = @(
        "run_experiment.py",
        "--profile", $Profile,
        "--output", $Output,
        "--seed", [string]$Seed,
        "--device", $Device
    )
    if ($NoResume) {
        $arguments += "--no-resume"
    }
    Write-Host "PROGRESS_EVERY_STEPS=100"
    & $Python -u @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Arithmetic training experiment failed with exit code $LASTEXITCODE"
    }
    Write-Host "EXPERIMENT_RUN=PASS"
    Write-Host "RESULT_PATH=$Output"
} catch {
    Write-Host "EXPERIMENT_RUN=FAIL"
    Write-Host "PARTIAL_RESULT_PATH=$Output"
    Write-Host "IF_TRAINING_WAS_INTERRUPTED_RERUN_SAME_COMMAND_TO_RESUME=True"
    throw
} finally {
    Pop-Location
}
