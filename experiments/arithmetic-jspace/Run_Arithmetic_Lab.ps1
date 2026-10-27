param(
    [ValidateSet("smoke", "balanced", "deep_symbolic", "emergence_longitudinal", "symbolic_only")]
    [string]$Profile = "smoke",
    [string]$Python = "",
    [string]$Output = "",
    [int]$Seed = -1,
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($Python)) {
    $preferred = Join-Path $env:USERPROFILE "miniconda3\envs\komorebi-full\python.exe"
    if (Test-Path -LiteralPath $preferred -PathType Leaf) {
        $Python = $preferred
    } elseif ($env:CONDA_PREFIX) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } else {
        $Python = "python"
    }
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$config = Join-Path $PSScriptRoot ("configs\" + $Profile + ".json")
if (-not (Test-Path -LiteralPath $config -PathType Leaf)) {
    throw "Configuration not found: $config"
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $Output = Join-Path $PSScriptRoot ("generated\" + $Profile + "_" + $stamp)
} else {
    $Output = [System.IO.Path]::GetFullPath($Output)
}

$arguments = @("-m", "arithmetic_space_lab", "generate", "--config", $config, "--output", $Output)
if ($Seed -ge 0) {
    $arguments += @("--seed", $Seed)
}
if ($Overwrite) {
    $arguments += "--overwrite"
}

Push-Location $PSScriptRoot
try {
    & $Python verify_package.py
    if ($LASTEXITCODE -ne 0) {
        throw "Package verification failed with exit code $LASTEXITCODE"
    }
    & $Python -u @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Generation failed with exit code $LASTEXITCODE"
    }
    & $Python -m arithmetic_space_lab audit --data $Output
    if ($LASTEXITCODE -ne 0) {
        throw "Audit failed with exit code $LASTEXITCODE"
    }
    Write-Host "RESULT_PATH=$Output"
} finally {
    Pop-Location
}
