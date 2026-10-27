Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:LabRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$script:TranscriptActive = $false
$script:NativeLog = $null

function Get-LabRoot {
    return $script:LabRoot
}

function Resolve-LabPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Base = $script:LabRoot
    )
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $Base $Path))
}

function Resolve-LabConfig {
    param([Parameter(Mandatory = $true)][ValidateSet("smoke", "standard", "confirmatory", "full")][string]$Preset)
    $path = Join-Path $script:LabRoot ("configs\{0}.json" -f $Preset)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Configuration file not found: $path"
    }
    return (Resolve-Path -LiteralPath $path).Path
}

function Resolve-LabPython {
    param([Parameter(Mandatory = $true)][string]$Python)
    if ([System.IO.Path]::IsPathRooted($Python)) {
        return $Python
    }
    if ($Python.Contains("\") -or $Python.Contains("/")) {
        $candidate = Resolve-LabPath -Path $Python
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    return $Python
}

function Resolve-ActiveLabPython {
    param([string]$Python = "")
    if ($Python) {
        return Resolve-LabPython -Python $Python
    }
    $environmentRoots = @($env:CONDA_PREFIX, $env:VIRTUAL_ENV) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    foreach ($environmentRoot in $environmentRoots) {
        foreach ($name in @("python.exe", "python")) {
            $candidate = Join-Path $environmentRoot $name
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
        }
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "No Python executable was found in the active environment or PATH."
    }
    return $command.Source
}

function Assert-LabPython {
    param([Parameter(Mandatory = $true)][string]$Python)
    $resolvedPython = Resolve-LabPython -Python $Python
    $command = Get-Command $resolvedPython -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "Python executable not found: $resolvedPython"
    }
    & $resolvedPython -c "import sys; print(sys.executable); print(sys.version)"
    if ($LASTEXITCODE -ne 0) {
        throw "Python failed its startup check: $resolvedPython"
    }
}

function New-LabRunDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$OutputRoot,
        [Parameter(Mandatory = $true)][string]$Prefix,
        [string]$OutputDirectory = ""
    )
    if ($OutputDirectory) {
        $runDirectory = Resolve-LabPath -Path $OutputDirectory
    }
    else {
        $root = Resolve-LabPath -Path $OutputRoot
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $runDirectory = Join-Path $root ("{0}_{1}_{2}" -f $Prefix, $stamp, $PID)
    }
    New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null
    return (Resolve-Path -LiteralPath $runDirectory).Path
}

function Start-LabTranscript {
    param([Parameter(Mandatory = $true)][string]$RunDirectory)
    $logDirectory = Join-Path $RunDirectory "logs"
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $transcript = Join-Path $logDirectory ("runner_{0}_{1}.log" -f $stamp, $PID)
    Set-Content -LiteralPath $transcript -Value ("OSL runner start UTC: {0}" -f ([DateTime]::UtcNow.ToString("o"))) -Encoding UTF8
    $script:TranscriptActive = $true
    $script:NativeLog = $transcript
    return $transcript
}

function Stop-LabTranscript {
    if ($script:TranscriptActive) {
        Add-Content -LiteralPath $script:NativeLog -Value ("OSL runner end UTC: {0}" -f ([DateTime]::UtcNow.ToString("o"))) -Encoding UTF8
        $script:TranscriptActive = $false
        $script:NativeLog = $null
    }
}

function Invoke-LabCli {
    param(
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string[]]$CliArguments
    )
    $Python = Resolve-LabPython -Python $Python
    $oldPythonUtf8 = $env:PYTHONUTF8
    $oldPythonHashSeed = $env:PYTHONHASHSEED
    $oldHfOffline = $env:HF_HUB_OFFLINE
    $oldTransformersOffline = $env:TRANSFORMERS_OFFLINE
    $oldDatasetsOffline = $env:HF_DATASETS_OFFLINE
    $oldMplConfigDir = $env:MPLCONFIGDIR
    $oldCublasWorkspace = $env:CUBLAS_WORKSPACE_CONFIG
    $oldPipNoIndex = $env:PIP_NO_INDEX
    $oldPipVersionCheck = $env:PIP_DISABLE_PIP_VERSION_CHECK
    $oldWandbMode = $env:WANDB_MODE
    try {
        $env:PYTHONUTF8 = "1"
        $env:PYTHONHASHSEED = "0"
        $env:HF_HUB_OFFLINE = "1"
        $env:TRANSFORMERS_OFFLINE = "1"
        $env:HF_DATASETS_OFFLINE = "1"
        $env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
        $env:PIP_NO_INDEX = "1"
        $env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
        $env:WANDB_MODE = "offline"
        $matplotlibCache = Join-Path ([System.IO.Path]::GetTempPath()) "osl-micro-emergence-matplotlib"
        New-Item -ItemType Directory -Path $matplotlibCache -Force | Out-Null
        $env:MPLCONFIGDIR = $matplotlibCache
        Push-Location $script:LabRoot
        try {
            if ($script:NativeLog) {
                $commandName = if ($CliArguments.Count -gt 0) { $CliArguments[0] } else { "unknown" }
                Add-Content -LiteralPath $script:NativeLog -Value ("command: python -m osl_lab.cli {0} [arguments recorded in run artifacts]" -f $commandName) -Encoding UTF8
                & $Python -m osl_lab.cli @CliArguments 2>&1 | Tee-Object -FilePath $script:NativeLog -Append
            }
            else {
                & $Python -m osl_lab.cli @CliArguments
            }
            $pythonExitCode = $LASTEXITCODE
            if ($pythonExitCode -ne 0) {
                throw "OSL Lab command failed with exit code $pythonExitCode."
            }
        }
        finally {
            Pop-Location
        }
    }
    finally {
        $env:PYTHONUTF8 = $oldPythonUtf8
        $env:PYTHONHASHSEED = $oldPythonHashSeed
        $env:HF_HUB_OFFLINE = $oldHfOffline
        $env:TRANSFORMERS_OFFLINE = $oldTransformersOffline
        $env:HF_DATASETS_OFFLINE = $oldDatasetsOffline
        $env:MPLCONFIGDIR = $oldMplConfigDir
        $env:CUBLAS_WORKSPACE_CONFIG = $oldCublasWorkspace
        $env:PIP_NO_INDEX = $oldPipNoIndex
        $env:PIP_DISABLE_PIP_VERSION_CHECK = $oldPipVersionCheck
        $env:WANDB_MODE = $oldWandbMode
    }
}

function Invoke-LabModule {
    param(
        [Parameter(Mandatory = $true)][string]$Python,
        [Parameter(Mandatory = $true)][string]$Module,
        [Parameter(Mandatory = $true)][string[]]$ModuleArguments
    )
    $Python = Resolve-LabPython -Python $Python
    $oldPythonUtf8 = $env:PYTHONUTF8
    $oldPythonHashSeed = $env:PYTHONHASHSEED
    $oldHfOffline = $env:HF_HUB_OFFLINE
    $oldTransformersOffline = $env:TRANSFORMERS_OFFLINE
    $oldDatasetsOffline = $env:HF_DATASETS_OFFLINE
    $oldMplConfigDir = $env:MPLCONFIGDIR
    $oldCublasWorkspace = $env:CUBLAS_WORKSPACE_CONFIG
    $oldPipNoIndex = $env:PIP_NO_INDEX
    $oldPipVersionCheck = $env:PIP_DISABLE_PIP_VERSION_CHECK
    $oldWandbMode = $env:WANDB_MODE
    try {
        $env:PYTHONUTF8 = "1"
        $env:PYTHONHASHSEED = "0"
        $env:HF_HUB_OFFLINE = "1"
        $env:TRANSFORMERS_OFFLINE = "1"
        $env:HF_DATASETS_OFFLINE = "1"
        $env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
        $env:PIP_NO_INDEX = "1"
        $env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
        $env:WANDB_MODE = "offline"
        $matplotlibCache = Join-Path ([System.IO.Path]::GetTempPath()) "osl-micro-emergence-matplotlib"
        New-Item -ItemType Directory -Path $matplotlibCache -Force | Out-Null
        $env:MPLCONFIGDIR = $matplotlibCache
        Push-Location $script:LabRoot
        try {
            & $Python -m $Module @ModuleArguments
            if ($LASTEXITCODE -ne 0) {
                throw "Python module $Module failed with exit code $LASTEXITCODE."
            }
        }
        finally {
            Pop-Location
        }
    }
    finally {
        $env:PYTHONUTF8 = $oldPythonUtf8
        $env:PYTHONHASHSEED = $oldPythonHashSeed
        $env:HF_HUB_OFFLINE = $oldHfOffline
        $env:TRANSFORMERS_OFFLINE = $oldTransformersOffline
        $env:HF_DATASETS_OFFLINE = $oldDatasetsOffline
        $env:MPLCONFIGDIR = $oldMplConfigDir
        $env:CUBLAS_WORKSPACE_CONFIG = $oldCublasWorkspace
        $env:PIP_NO_INDEX = $oldPipNoIndex
        $env:PIP_DISABLE_PIP_VERSION_CHECK = $oldPipVersionCheck
        $env:WANDB_MODE = $oldWandbMode
    }
}

function Find-LabCheckpoint {
    param(
        [Parameter(Mandatory = $true)][string]$RunDirectory,
        [ValidateSet("best", "last", "any")][string]$Preference = "best",
        [string]$Arm = ""
    )
    $matchesArm = {
        if (-not $Arm) { return $true }
        $summaryPath = Join-Path $_.DirectoryName "training_summary.json"
        if (Test-Path -LiteralPath $summaryPath -PathType Leaf) {
            try {
                $summary = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
                return [string]$summary.arm -eq $Arm
            }
            catch {
                return $false
            }
        }
        return $_.Directory.Name -eq ("transformer__{0}" -f $Arm)
    }
    if ($Preference -eq "best") {
        $preferred = Get-ChildItem -LiteralPath $RunDirectory -Filter "checkpoint.pt" -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq "checkpoint.pt" } |
            Where-Object $matchesArm |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($null -ne $preferred) { return $preferred.FullName }
    }
    if ($Preference -eq "last") {
        $preferred = Get-ChildItem -LiteralPath $RunDirectory -Filter "last_checkpoint.pt" -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object $matchesArm |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($null -ne $preferred) { return $preferred.FullName }
    }
    $patterns = @("*.pt", "*.pth", "*.ckpt")
    $files = foreach ($pattern in $patterns) {
        Get-ChildItem -LiteralPath $RunDirectory -Filter $pattern -File -Recurse -ErrorAction SilentlyContinue
    }
    $checkpoint = $files | Where-Object $matchesArm | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $checkpoint) {
        $suffix = if ($Arm) { " for arm '$Arm'" } else { "" }
        throw "No checkpoint$suffix was found under: $RunDirectory"
    }
    return $checkpoint.FullName
}

function Find-LatestLabRunWithCheckpoint {
    param([Parameter(Mandatory = $true)][string]$OutputRoot)
    $root = Resolve-LabPath -Path $OutputRoot
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        throw "Results directory not found: $root"
    }
    $directories = Get-ChildItem -LiteralPath $root -Directory | Sort-Object LastWriteTime -Descending
    foreach ($directory in $directories) {
        try {
            $null = Find-LabCheckpoint -RunDirectory $directory.FullName -Preference "any"
            if (Test-Path -LiteralPath (Join-Path $directory.FullName "train.jsonl") -PathType Leaf) {
                return $directory.FullName
            }
        }
        catch {
        }
    }
    throw "No completed run containing both a checkpoint and dataset was found under: $root"
}
