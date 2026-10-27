$ErrorActionPreference = "Stop"
$SourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PreviousSourceDateEpoch = [Environment]::GetEnvironmentVariable(
    "SOURCE_DATE_EPOCH", "Process"
)
$PreviousMatplotlibBackend = [Environment]::GetEnvironmentVariable(
    "MPLBACKEND", "Process"
)
$PreviousNoBytecode = [Environment]::GetEnvironmentVariable(
    "PYTHONDONTWRITEBYTECODE", "Process"
)
$ScratchRoot = Join-Path ([System.IO.Path]::GetTempPath()) `
    ("paper1_verify_" + [System.Guid]::NewGuid().ToString("N"))
$WorkRoot = Join-Path $ScratchRoot (Split-Path -Leaf $SourceRoot)

function Get-NativeCommandPath {
    param([Parameter(Mandatory = $true)][string]$Name)

    $Command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue
    if (-not $Command) {
        throw "$Name is required"
    }
    return $Command.Source
}

function Invoke-CheckedNative {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Native command failed with exit code ${LASTEXITCODE}: $Executable"
    }
}

$BootstrapPython = Get-NativeCommandPath "python"
$Lake = Get-NativeCommandPath "lake"
$Latexmk = Get-NativeCommandPath "latexmk"

New-Item -ItemType Directory -Force -Path $ScratchRoot | Out-Null
try {
    if ($null -eq $PreviousSourceDateEpoch) {
        $env:SOURCE_DATE_EPOCH = "1788393600"
    }
    $env:MPLBACKEND = "Agg"
    $env:PYTHONDONTWRITEBYTECODE = "1"

    Copy-Item -LiteralPath $SourceRoot -Destination $WorkRoot -Recurse -Force
    Remove-Item -LiteralPath (Join-Path $WorkRoot "formalization\lean\.lake") `
        -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $WorkRoot ".verification-venv") `
        -Recurse -Force -ErrorAction SilentlyContinue

    $VerifyEnv = Join-Path $WorkRoot ".verification-venv"
    $Python = Join-Path $VerifyEnv "Scripts\python.exe"
    $PythonRoot = Join-Path $WorkRoot "code\python"
    $LeanRoot = Join-Path $WorkRoot "formalization\lean"
    $PaperRoot = Join-Path $WorkRoot "paper"
    $WheelRoot = Join-Path $PythonRoot "dist"
    $WheelPath = Join-Path $WheelRoot `
        "projector_seed_calculus-1.1.1-py3-none-any.whl"
    $TheoremMap = Join-Path $LeanRoot "LEAN_THEOREM_MAP_v1.0.1.md"

    if (-not (Test-Path -LiteralPath $TheoremMap -PathType Leaf)) {
        throw "Missing theorem map: $TheoremMap"
    }

    Invoke-CheckedNative $BootstrapPython @("-m", "venv", $VerifyEnv)
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        throw "Virtual-environment Python was not created: $Python"
    }
    Invoke-CheckedNative $Python @(
        "-m", "pip", "install", "--disable-pip-version-check",
        "--requirement", (Join-Path $PythonRoot "requirements.lock.txt")
    )

    Invoke-CheckedNative $Python @((Join-Path $PythonRoot "run_all.py"))
    Remove-Item -LiteralPath $WheelRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $WheelRoot | Out-Null
    Invoke-CheckedNative $Python @(
        "-m", "pip", "wheel", $PythonRoot, "--no-deps", "--no-build-isolation",
        "--wheel-dir", $WheelRoot
    )
    if (-not (Test-Path -LiteralPath $WheelPath -PathType Leaf)) {
        throw "Missing built wheel: $WheelPath"
    }
    Invoke-CheckedNative $Python @(
        "-m", "pip", "install", "--force-reinstall", "--no-deps", $WheelPath
    )
    Invoke-CheckedNative $Python @(
        "-c", "import seed_calculus; assert seed_calculus.__version__ == '1.1.1'"
    )
    Push-Location $ScratchRoot
    try {
        Invoke-CheckedNative $Python @(
            "-m", "pytest", "-q", "-W", "error", "-p", "no:cacheprovider",
            "--import-mode=importlib", (Join-Path $PythonRoot "tests")
        )
    }
    finally {
        Pop-Location
    }
    Invoke-CheckedNative $Python @("-m", "pip", "check")

    Push-Location $LeanRoot
    try {
        Invoke-CheckedNative $Lake @("--wfail", "build")
        Invoke-CheckedNative $Python @("scripts\verify_theorem_map.py")
        Invoke-CheckedNative $Lake @(
            "env", "lean", "-E", "warning", "KomorebiVerification\KernelAudit.lean"
        )
    }
    finally {
        Pop-Location
    }

    Push-Location $PaperRoot
    try {
        Invoke-CheckedNative $Latexmk @(
            "-C", "Projector_Resolved_Seed_Calculus_I.tex"
        )
        Invoke-CheckedNative $Latexmk @(
            "-pdf", "-interaction=nonstopmode", "-halt-on-error",
            "Projector_Resolved_Seed_Calculus_I.tex"
        )
    }
    finally {
        Pop-Location
    }

    Write-Host "Paper I verification completed successfully in an isolated copy."
}
finally {
    Remove-Item -LiteralPath $ScratchRoot -Recurse -Force -ErrorAction SilentlyContinue
    if ($null -eq $PreviousSourceDateEpoch) {
        Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
    }
    else {
        $env:SOURCE_DATE_EPOCH = $PreviousSourceDateEpoch
    }
    if ($null -eq $PreviousMatplotlibBackend) {
        Remove-Item Env:MPLBACKEND -ErrorAction SilentlyContinue
    }
    else {
        $env:MPLBACKEND = $PreviousMatplotlibBackend
    }
    if ($null -eq $PreviousNoBytecode) {
        Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONDONTWRITEBYTECODE = $PreviousNoBytecode
    }
}
