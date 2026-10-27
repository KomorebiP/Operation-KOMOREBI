param(
    [ValidateSet("smoke", "pilot", "full", "confirmatory")]
    [string]$Profile = "pilot",
    [string]$Python = "python",
    [string]$Output = "",
    [string]$TorchIndexUrl = "",
    [switch]$SkipInstall,
    [switch]$Resume,
    [string[]]$ExtraArgs = @()
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"

if ($Resume -and [string]::IsNullOrWhiteSpace($Output)) {
    throw "Resume requires -Output pointing to the interrupted results directory"
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $root "results_${Profile}_${stamp}"
}

New-Item -ItemType Directory -Path $Output -Force | Out-Null
$transcript = Join-Path $root "OSL_HF_WINDOWS_RUN_TRANSCRIPT_${stamp}.txt"
Start-Transcript -Path $transcript -Force | Out-Null

try {
    & $Python --version
    if ($LASTEXITCODE -ne 0) { throw "Python could not be started with: $Python" }

    if (-not $SkipInstall) {
        & $Python -c "import torch" 2>$null
        if ($LASTEXITCODE -ne 0) {
            if ([string]::IsNullOrWhiteSpace($TorchIndexUrl)) {
                & $Python -m pip install torch
            } else {
                & $Python -m pip install torch --index-url $TorchIndexUrl
            }
            if ($LASTEXITCODE -ne 0) { throw "PyTorch installation failed" }
        }
        & $Python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
    }

    & $Python -c "import torch, transformers, numpy, sklearn; print('torch',torch.__version__); print('transformers',transformers.__version__); print('numpy',numpy.__version__); print('sklearn',sklearn.__version__); print('cuda_available',torch.cuda.is_available()); print('cuda_version',torch.version.cuda); print('gpu',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
    if ($LASTEXITCODE -ne 0) { throw "Dependency preflight failed" }

    & $Python smoke_tests.py
    if ($LASTEXITCODE -ne 0) { throw "Source smoke tests failed" }

    $experimentArgs = @("--profile", $Profile, "--output", $Output)
    if ($Resume) { $experimentArgs += "--resume" }
    $experimentArgs += $ExtraArgs
    & $Python run_experiment.py @experimentArgs
    if ($LASTEXITCODE -ne 0) { throw "Experiment failed" }

    & $Python verify_results.py --results $Output
    if ($LASTEXITCODE -ne 0) { throw "Result verification failed" }

    $returnZip = Join-Path $Output "RETURN_THIS_OSL_HF_RESULTS.zip"
    Write-Host "Completed"
    Write-Host "Return this file to ChatGPT: $returnZip"
    Write-Host "Full local results: $Output"
} finally {
    Stop-Transcript | Out-Null
}
