param(
    [ValidateSet("smoke", "pilot", "full", "confirmatory")]
    [string]$Profile = "pilot",
    [string]$Python = "",
    [string]$Output = "",
    [ValidateSet("auto", "cpu", "cuda")]
    [string]$Device = "auto",
    [int]$BatchSize = 0,
    [Nullable[int]]$Seed = $null,
    [string]$Arms = "",
    [string]$TorchIndexUrl = "https://download.pytorch.org/whl/cu126",
    [switch]$SkipInstall,
    [switch]$Resume,
    [switch]$AllowCPUFull,
    [switch]$Nondeterministic,
    [string[]]$ExtraArgs = @()
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"

if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX) {
        $candidate = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    }
    if ([string]::IsNullOrWhiteSpace($Python)) { $Python = "python" }
}
if ($Resume -and [string]::IsNullOrWhiteSpace($Output)) {
    throw "Resume requires -Output pointing to the interrupted results directory"
}
if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $root "results_${Profile}_${stamp}"
}
$Output = [System.IO.Path]::GetFullPath($Output)
if ((-not $Resume) -and (Test-Path -LiteralPath $Output) -and (Get-ChildItem -LiteralPath $Output -Force | Select-Object -First 1)) {
    throw "Output directory is not empty: $Output"
}

# Keep the live transcript outside the immutable source tree. On failure it is
# copied into the diagnostic ZIP, so it remains easy to return for analysis.
$transcript = Join-Path ([System.IO.Path]::GetTempPath()) "OSL_HF_V03_WINDOWS_TRANSCRIPT_${stamp}.txt"
$failed = $false
$failureMessage = ""
Start-Transcript -Path $transcript -Force | Out-Null
try {
    & $Python --version
    if ($LASTEXITCODE -ne 0) { throw "Python could not be started with: $Python" }
    & $Python verify_package.py --package $root
    if ($LASTEXITCODE -ne 0) { throw "Package verification failed" }

    if (-not $SkipInstall) {
        & $Python -c "import torch" 2>$null
        if ($LASTEXITCODE -ne 0) {
            & $Python -m pip install torch --index-url $TorchIndexUrl
            if ($LASTEXITCODE -ne 0) { throw "PyTorch installation failed" }
        }
        & $Python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
    }

    & $Python -c "import sys,torch,transformers,numpy,sklearn; print('python',sys.version); print('torch',torch.__version__); print('transformers',transformers.__version__); print('numpy',numpy.__version__); print('sklearn',sklearn.__version__); print('cuda_available',torch.cuda.is_available()); print('cuda_version',torch.version.cuda); print('gpu',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
    if ($LASTEXITCODE -ne 0) { throw "Dependency preflight failed" }

    & $Python -c "import sys,torch; sys.exit(0 if torch.cuda.is_available() else 1)"
    $cudaAvailable = $LASTEXITCODE -eq 0
    if (($Profile -in @("full", "confirmatory")) -and (-not $cudaAvailable) -and (-not $AllowCPUFull)) {
        throw "$Profile requires CUDA by default. Use -AllowCPUFull only if the long CPU runtime is intentional."
    }
    if (($Device -eq "cuda") -and (-not $cudaAvailable)) {
        throw "-Device cuda was requested, but CUDA is unavailable"
    }

    & $Python smoke_tests.py
    if ($LASTEXITCODE -ne 0) { throw "Source smoke tests failed" }

    $experimentArgs = @("--profile", $Profile, "--output", $Output, "--device", $Device)
    if ($Resume) { $experimentArgs += "--resume" }
    if ($BatchSize -gt 0) { $experimentArgs += @("--batch-size", "$BatchSize") }
    if ($null -ne $Seed) { $experimentArgs += @("--seed", "$Seed") }
    if (-not [string]::IsNullOrWhiteSpace($Arms)) { $experimentArgs += @("--arms", $Arms) }
    if ($Nondeterministic) { $experimentArgs += "--nondeterministic" }
    $experimentArgs += $ExtraArgs
    & $Python run_experiment.py @experimentArgs
    if ($LASTEXITCODE -ne 0) { throw "Experiment failed" }

    & $Python verify_results.py --results $Output
    if ($LASTEXITCODE -ne 0) { throw "Result verification failed" }

    $returnZip = Join-Path $Output "RETURN_THIS_OSL_HF_RESULTS.zip"
    Write-Host "Completed and verified"
    Write-Host "Return this file to ChatGPT: $returnZip"
    Write-Host "Full local results: $Output"
} catch {
    $failed = $true
    $failureMessage = $_.Exception.Message
    Write-Host "FAILED: $failureMessage"
} finally {
    Stop-Transcript | Out-Null
}

if ($failed) {
    $diagnosticZip = Join-Path $root "FAILED_OSL_HF_V03_${stamp}.zip"
    $diagnosticFiles = @($transcript)
    if (Test-Path -LiteralPath $Output) {
        foreach ($name in @("PREOUTCOME_FREEZE.json", "DATASET_AUDIT.json", "RESUME_PROVENANCE.json")) {
            $path = Join-Path $Output $name
            if (Test-Path -LiteralPath $path) { $diagnosticFiles += $path }
        }
    }
    Compress-Archive -LiteralPath $diagnosticFiles -DestinationPath $diagnosticZip -Force
    Write-Host "Failure diagnostics: $diagnosticZip"
    if ((Test-Path -LiteralPath (Join-Path $Output "PREOUTCOME_FREEZE.json")) -and (Test-Path -LiteralPath (Join-Path $Output "DATASET_AUDIT.json"))) {
        $resumeCommand = "& `"$root\Run_OSL_HF_Test.ps1`" -Profile $Profile -Python `"$Python`" -Output `"$Output`" -Device $Device -Resume -SkipInstall"
        if ($BatchSize -gt 0) { $resumeCommand += " -BatchSize $BatchSize" }
        if ($null -ne $Seed) { $resumeCommand += " -Seed $Seed" }
        if (-not [string]::IsNullOrWhiteSpace($Arms)) { $resumeCommand += " -Arms `"$Arms`"" }
        if ($AllowCPUFull) { $resumeCommand += " -AllowCPUFull" }
        if ($Nondeterministic) { $resumeCommand += " -Nondeterministic" }
        Write-Host "Resume command: $resumeCommand"
    }
    throw $failureMessage
}
