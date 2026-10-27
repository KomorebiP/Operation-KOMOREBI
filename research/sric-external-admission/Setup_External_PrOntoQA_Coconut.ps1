param(
    [string]$RuntimeRoot = (Join-Path $PSScriptRoot "external_runtime"),
    [string]$PythonExe = "",
    [string]$TorchIndexUrl = "https://download.pytorch.org/whl/cu124",
    [switch]$CpuOnly,
    [switch]$DisableXet,
    [switch]$LocalFilesOnly
)

$ErrorActionPreference = "Stop"
$Commit = "32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
$RepoUrl = "https://github.com/connordilgren/are-lrms-easily-interpretable.git"

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory=$true)][string]$Program,
        [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
    )
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE: $Program $($Arguments -join ' ')"
    }
}

function Test-CompatiblePython {
    param([string]$Program, [string[]]$PrefixArgs)
    try {
        $v = (& $Program @PrefixArgs -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null).Trim()
        if ($LASTEXITCODE -ne 0) { return $null }
        if ($v -in @("3.10", "3.11", "3.12")) {
            return [pscustomobject]@{ Program=$Program; PrefixArgs=$PrefixArgs; Version=$v }
        }
    } catch { }
    return $null
}

function Resolve-CompatiblePython {
    if (-not [string]::IsNullOrWhiteSpace($PythonExe)) {
        $resolved = Test-CompatiblePython -Program $PythonExe -PrefixArgs @()
        if ($null -eq $resolved) {
            throw "PythonExe must resolve to Python 3.10, 3.11, or 3.12: $PythonExe"
        }
        return $resolved
    }

    $candidates = @(
        @{ Program="py"; Args=@("-3.12") },
        @{ Program="py"; Args=@("-3.11") },
        @{ Program="py"; Args=@("-3.10") },
        @{ Program="python3.12"; Args=@() },
        @{ Program="python3.11"; Args=@() },
        @{ Program="python3.10"; Args=@() },
        @{ Program="python"; Args=@() }
    )
    foreach ($candidate in $candidates) {
        if ($null -eq (Get-Command $candidate.Program -ErrorAction SilentlyContinue)) { continue }
        $resolved = Test-CompatiblePython -Program $candidate.Program -PrefixArgs $candidate.Args
        if ($null -ne $resolved) { return $resolved }
    }
    throw "No compatible Python found. Install Python 3.10, 3.11, or 3.12, or pass -PythonExe C:\path\python.exe."
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
$RuntimeRoot = (Resolve-Path $RuntimeRoot).Path
$Venv = Join-Path $RuntimeRoot ".venv"
$ExternalRepo = Join-Path $RuntimeRoot "are-lrms-easily-interpretable"
$PathsFile = Join-Path $RuntimeRoot "runtime_paths.json"

if (-not (Test-Path $Venv)) {
    $BasePython = Resolve-CompatiblePython
    Write-Host "Using Python $($BasePython.Version): $($BasePython.Program) $($BasePython.PrefixArgs -join ' ')"
    $BaseProgram = $BasePython.Program
    $BasePrefixArgs = @($BasePython.PrefixArgs)
    & $BaseProgram @BasePrefixArgs -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual-environment creation failed." }
}

$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Py)) { throw "Virtual-environment Python is missing: $Py" }
$Version = (& $Py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
if ($Version -notin @("3.10", "3.11", "3.12")) {
    throw "Use Python 3.10-3.12 for the pinned torch==2.5.1 runtime; found Python $Version."
}

Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
if ($CpuOnly) {
    Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "install", "torch==2.5.1")
} else {
    Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "install", "torch==2.5.1", "--index-url", $TorchIndexUrl)
}
Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "install", "-r", (Join-Path $PSScriptRoot "requirements-real-no-torch.txt"))
Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "install", "-e", $PSScriptRoot)
Invoke-NativeChecked -Program $Py -Arguments @("-m", "pip", "check")

if (-not (Test-Path (Join-Path $ExternalRepo ".git"))) {
    if ($LocalFilesOnly) {
        throw "LocalFilesOnly requested, but the pinned external repository is absent: $ExternalRepo"
    }
    Invoke-NativeChecked -Program "git" -Arguments @("clone", $RepoUrl, $ExternalRepo)
}
$Dirty = git -C $ExternalRepo status --porcelain
if ($LASTEXITCODE -ne 0) { throw "Unable to inspect external repository: $ExternalRepo" }
if ($Dirty) { throw "External repository has uncommitted changes: $ExternalRepo" }
if ($LocalFilesOnly) {
    & git -C $ExternalRepo cat-file -e "$Commit^{commit}"
    if ($LASTEXITCODE -ne 0) {
        throw "LocalFilesOnly requested, but the pinned commit is absent from the local repository."
    }
} else {
    Invoke-NativeChecked -Program "git" -Arguments @("-C", $ExternalRepo, "fetch", "origin", $Commit)
}
Invoke-NativeChecked -Program "git" -Arguments @("-C", $ExternalRepo, "checkout", "--detach", $Commit)
$ActualCommit = (git -C $ExternalRepo rev-parse HEAD).Trim()
if ($ActualCommit -ne $Commit) { throw "Commit verification failed: $ActualCommit" }

$DownloadArgs = @(
    (Join-Path $PSScriptRoot "download_external_assets.py"),
    "--runtime-root", $RuntimeRoot,
    "--external-repo", $ExternalRepo,
    "--source-lock", (Join-Path $PSScriptRoot "external_source_lock.json")
)
if ($LocalFilesOnly) { $DownloadArgs += "--local-files-only" }
if ($DisableXet) { $DownloadArgs += "--disable-xet" }

& $Py @DownloadArgs
$DownloadExit = $LASTEXITCODE
if (($DownloadExit -ne 0) -and (-not $DisableXet) -and (-not $LocalFilesOnly)) {
    Write-Warning "The default Hugging Face/Xet transfer failed. Retrying through the standard HTTP/LFS path."
    $RetryArgs = @($DownloadArgs) + "--disable-xet"
    & $Py @RetryArgs
    $DownloadExit = $LASTEXITCODE
}
if ($DownloadExit -ne 0) {
    throw "Exact external-asset download failed. No model-level interpretation may be made from this setup failure."
}
if (-not (Test-Path $PathsFile)) { throw "Asset receipt was not produced: $PathsFile" }
$Paths = Get-Content -Raw $PathsFile | ConvertFrom-Json

Invoke-NativeChecked -Program $Py -Arguments @((Join-Path $PSScriptRoot "capture_environment.py"), "--output", (Join-Path $RuntimeRoot "environment.json"))
Invoke-NativeChecked -Program $Py -Arguments @("-m", "sric_real_lrm", "verify-source", "--external-repo", $ExternalRepo, "--dataset-key", "prontoqa_test")
Invoke-NativeChecked -Program $Py -Arguments @("-m", "sric_real_lrm", "preflight", "--external-repo", $ExternalRepo, "--checkpoint", $Paths.checkpoint, "--data", $Paths.data)

Write-Host "SRIC_BLOCK24_EXTERNAL_SETUP=PASS"
Write-Host "runtime_paths=$PathsFile"
Write-Host "python=$Py"
Write-Host "external_repo=$ExternalRepo"
Write-Host "checkpoint=$($Paths.checkpoint)"
Write-Host "checkpoint_sha256=$($Paths.checkpoint_sha256)"
Write-Host "base_model=$($Paths.base_model)"
Write-Host "base_model_tree_sha256=$($Paths.base_model_tree_sha256)"
Write-Host "data=$($Paths.data)"
