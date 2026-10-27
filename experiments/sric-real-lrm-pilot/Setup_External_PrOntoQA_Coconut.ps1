param(
    [string]$RuntimeRoot = (Join-Path $PSScriptRoot "external_runtime"),
    [string]$Python = "python",
    [string]$TorchIndexUrl = "https://download.pytorch.org/whl/cu124",
    [switch]$CpuOnly
)

$ErrorActionPreference = "Stop"
$Commit = "32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
$RepoUrl = "https://github.com/connordilgren/are-lrms-easily-interpretable.git"
$CheckpointRepo = "connordilgren/gpt2-prontoqa-multimode-coconut"
$CheckpointFile = "checkpoint_37"
$BaseRepo = "openai-community/gpt2"

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
$RuntimeRoot = (Resolve-Path $RuntimeRoot).Path
$Venv = Join-Path $RuntimeRoot ".venv"
$ExternalRepo = Join-Path $RuntimeRoot "are-lrms-easily-interpretable"
$CheckpointDir = Join-Path $RuntimeRoot "checkpoints\gpt2_prontoqa_multimode"
$BaseModelDir = Join-Path $RuntimeRoot "models\gpt2"
$PathsFile = Join-Path $RuntimeRoot "runtime_paths.json"

if (-not (Test-Path $Venv)) {
    & $Python -m venv $Venv
}
$Py = Join-Path $Venv "Scripts\python.exe"
$Hf = Join-Path $Venv "Scripts\hf.exe"

& $Py -m pip install --upgrade pip setuptools wheel
if ($CpuOnly) {
    & $Py -m pip install torch==2.5.1
} else {
    & $Py -m pip install torch==2.5.1 --index-url $TorchIndexUrl
}
& $Py -m pip install -r (Join-Path $PSScriptRoot "requirements-real-no-torch.txt")
& $Py -m pip install -e $PSScriptRoot

if (-not (Test-Path $ExternalRepo)) {
    git clone $RepoUrl $ExternalRepo
}
git -C $ExternalRepo fetch --all --tags
$Dirty = git -C $ExternalRepo status --porcelain
if ($Dirty) {
    throw "External repository has uncommitted changes. Use a clean checkout: $ExternalRepo"
}
git -C $ExternalRepo checkout --detach $Commit
$ActualCommit = (git -C $ExternalRepo rev-parse HEAD).Trim()
if ($ActualCommit -ne $Commit) {
    throw "Commit verification failed: $ActualCommit"
}

New-Item -ItemType Directory -Force -Path $CheckpointDir, $BaseModelDir | Out-Null
& $Hf download $CheckpointRepo $CheckpointFile --local-dir $CheckpointDir
& $Hf download $BaseRepo --local-dir $BaseModelDir

$CheckpointPath = Join-Path $CheckpointDir $CheckpointFile
$DatasetPath = Join-Path $ExternalRepo "data\prontoqa_test.json"
if (-not (Test-Path $CheckpointPath)) { throw "Checkpoint download failed: $CheckpointPath" }
if (-not (Test-Path $DatasetPath)) { throw "Dataset not found: $DatasetPath" }

$Paths = [ordered]@{
    python = $Py
    external_repo = $ExternalRepo
    external_commit = $ActualCommit
    checkpoint = $CheckpointPath
    base_model = $BaseModelDir
    data = $DatasetPath
}
$Paths | ConvertTo-Json | Set-Content -Encoding UTF8 $PathsFile

& $Py (Join-Path $PSScriptRoot "capture_environment.py") --output (Join-Path $RuntimeRoot "environment.json")

Write-Host "SRIC_REAL_LRM_EXTERNAL_SETUP=PASS"
Write-Host "runtime_paths=$PathsFile"
Write-Host "python=$Py"
Write-Host "external_repo=$ExternalRepo"
Write-Host "checkpoint=$CheckpointPath"
Write-Host "base_model=$BaseModelDir"
Write-Host "data=$DatasetPath"
