$ErrorActionPreference = "Stop"
$ReleaseRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$WheelName = "projector_seed_refinement-1.2.1-py3-none-any.whl"
$FrozenWheel = Join-Path $ReleaseRoot "code\python\dist\$WheelName"
$ChecksumFile = Join-Path $ReleaseRoot "SHA256SUMS.txt"
$PreviousSourceDateEpoch = [Environment]::GetEnvironmentVariable("SOURCE_DATE_EPOCH", "Process")
$PreviousMatplotlibBackend = [Environment]::GetEnvironmentVariable("MPLBACKEND", "Process")
$PreviousNoBytecode = [Environment]::GetEnvironmentVariable("PYTHONDONTWRITEBYTECODE", "Process")

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

function Assert-ReleaseChecksums {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Manifest
    )

    foreach ($Line in Get-Content -LiteralPath $Manifest) {
        if ([string]::IsNullOrWhiteSpace($Line)) {
            continue
        }
        if ($Line -notmatch '^(?<Hash>[0-9A-Fa-f]{64})\s+\./(?<Path>.+)$') {
            throw "Malformed checksum line: $Line"
        }
        $RelativePath = $Matches.Path.Replace(
            '/', [System.IO.Path]::DirectorySeparatorChar
        )
        $Artifact = Join-Path $Root $RelativePath
        if (-not (Test-Path -LiteralPath $Artifact -PathType Leaf)) {
            throw "Checksum target is missing: $RelativePath"
        }
        $Actual = (Get-FileHash -LiteralPath $Artifact -Algorithm SHA256).Hash
        if ($Actual -ne $Matches.Hash) {
            throw "Checksum mismatch: $RelativePath"
        }
    }
}

if (-not (Test-Path -LiteralPath $ChecksumFile -PathType Leaf)) {
    throw "Missing checksum manifest: $ChecksumFile"
}
if (-not (Test-Path -LiteralPath $FrozenWheel -PathType Leaf)) {
    throw "Missing frozen wheel: $FrozenWheel"
}

$BootstrapPython = Get-NativeCommandPath "python"
$Lake = Get-NativeCommandPath "lake"
$Latexmk = Get-NativeCommandPath "latexmk"

Assert-ReleaseChecksums $ReleaseRoot $ChecksumFile
$InitialManifestHash = (Get-FileHash -LiteralPath $ChecksumFile -Algorithm SHA256).Hash

$TempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$WorkRoot = Join-Path $TempBase ("projector-seed-II-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $WorkRoot | Out-Null

try {
    if ($null -eq $PreviousSourceDateEpoch) {
        $env:SOURCE_DATE_EPOCH = "1788393600"
    }
    $env:MPLBACKEND = "Agg"
    $env:PYTHONDONTWRITEBYTECODE = "1"

    $VerifyEnv = Join-Path $WorkRoot "verification-venv"
    $Python = Join-Path $VerifyEnv "Scripts\python.exe"
    $GeneratedRoot = Join-Path $WorkRoot "generated"
    $FreshWheel = Join-Path $WorkRoot "dist\$WheelName"
    $PythonSource = Join-Path $WorkRoot "python-source"

    Invoke-CheckedNative $BootstrapPython @("-m", "venv", $VerifyEnv)
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        throw "Virtual-environment Python was not created: $Python"
    }
    Invoke-CheckedNative $Python @(
        "-m", "pip", "install", "--disable-pip-version-check",
        "--requirement", (Join-Path $ReleaseRoot "code\python\requirements.lock")
    )

    Invoke-CheckedNative $Python @(
        (Join-Path $ReleaseRoot "code\python\run_all.py"),
        "--output-root", $GeneratedRoot,
        "--compare-release-root", $ReleaseRoot
    )
    Copy-Item -LiteralPath (Join-Path $ReleaseRoot "code\python") `
        -Destination $PythonSource -Recurse -Force
    Invoke-CheckedNative $Python @(
        "-m", "build", "--wheel", "--no-isolation",
        "--outdir", (Join-Path $WorkRoot "dist"),
        $PythonSource
    )
    if (-not (Test-Path -LiteralPath $FreshWheel -PathType Leaf)) {
        throw "Missing temporary wheel: $FreshWheel"
    }
    Invoke-CheckedNative $Python @(
        "-m", "pip", "install", "--force-reinstall", "--no-deps", $FreshWheel
    )

    Push-Location $WorkRoot
    try {
        Invoke-CheckedNative $Python @(
            "-m", "pytest", "-q", "-W", "error", "-p", "no:cacheprovider",
            "--import-mode=importlib", (Join-Path $ReleaseRoot "code\python\tests")
        )
        Invoke-CheckedNative $Python @("-m", "pip", "check")
        Invoke-CheckedNative $Python @(
            "-c",
            'import seed_refinement; assert seed_refinement.__version__ == "1.2.1"; print("WHEEL_IMPORT_PASS version=1.2.1")'
        )
        Invoke-CheckedNative $Python @(
            "-m", "seed_refinement.release_validation", "compare-wheels",
            $FreshWheel, $FrozenWheel
        )
    }
    finally {
        Pop-Location
    }

    $LeanWork = Join-Path $WorkRoot "lean"
    Copy-Item -LiteralPath (Join-Path $ReleaseRoot "formalization\lean") `
        -Destination $LeanWork -Recurse -Force
    $LeanBuild = Join-Path $LeanWork ".lake\build"
    if (Test-Path -LiteralPath $LeanBuild) {
        Remove-Item -LiteralPath $LeanBuild -Recurse -Force
    }
    Push-Location $LeanWork
    try {
        Invoke-CheckedNative $Lake @("--wfail", "build")
        Invoke-CheckedNative $Python @("scripts\verify_theorem_map.py")
        Invoke-CheckedNative $Lake @(
            "env", "lean", "-E", "warning",
            "KomorebiVerification/PaperII/KernelAudit.lean"
        )
    }
    finally {
        Pop-Location
    }

    $PaperWork = Join-Path $WorkRoot "paper"
    Copy-Item -LiteralPath (Join-Path $ReleaseRoot "paper") `
        -Destination $PaperWork -Recurse -Force
    $PaperFigures = Join-Path $PaperWork "figures"
    Copy-Item -Path (Join-Path $GeneratedRoot "paper\figures\*.png") `
        -Destination $PaperFigures -Force
    Copy-Item -Path (Join-Path $GeneratedRoot "paper\figures\*.pdf") `
        -Destination $PaperFigures -Force
    Push-Location $PaperWork
    try {
        Invoke-CheckedNative $Latexmk @(
            "-C", "Projector_Resolved_Seed_Calculus_II.tex"
        )
        Invoke-CheckedNative $Latexmk @(
            "-pdf", "-interaction=nonstopmode", "-halt-on-error",
            "Projector_Resolved_Seed_Calculus_II.tex"
        )
    }
    finally {
        Pop-Location
    }
    $BuiltPaper = Join-Path $PaperWork "Projector_Resolved_Seed_Calculus_II.pdf"
    if (-not (Test-Path -LiteralPath $BuiltPaper -PathType Leaf)) {
        throw "Temporary LaTeX build did not produce the paper PDF"
    }

    Assert-ReleaseChecksums $ReleaseRoot $ChecksumFile
    $FinalManifestHash = (Get-FileHash -LiteralPath $ChecksumFile -Algorithm SHA256).Hash
    if ($InitialManifestHash -ne $FinalManifestHash) {
        throw "SHA256SUMS.txt changed during verification"
    }

    Write-Host "Paper II verification completed successfully without modifying the frozen release."
}
finally {
    if (Test-Path -LiteralPath $WorkRoot) {
        $ResolvedWorkRoot = [System.IO.Path]::GetFullPath($WorkRoot)
        if (-not $ResolvedWorkRoot.StartsWith($TempBase) -or
            -not ([System.IO.Path]::GetFileName($ResolvedWorkRoot)).StartsWith("projector-seed-II-")) {
            throw "Refusing to remove unexpected temporary path: $ResolvedWorkRoot"
        }
        Remove-Item -LiteralPath $ResolvedWorkRoot -Recurse -Force
    }

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
