param(
    [string]$Model = "",
    [string]$Run = "",
    [string]$Output = "",
    [string]$Python = "",
    [switch]$StaticOnly
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $Python) {
    $ActiveCondaPython = if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" } else { "" }
    if ($ActiveCondaPython -and (Test-Path -LiteralPath $ActiveCondaPython -PathType Leaf)) {
        $Python = $ActiveCondaPython
    }
    $RawPythonCandidates = @(
        "$env:USERPROFILE\miniconda3\envs\komorebi-full\python.exe",
        "$env:USERPROFILE\anaconda3\envs\komorebi-full\python.exe",
        "$env:LOCALAPPDATA\miniconda3\envs\komorebi-full\python.exe"
    )
    if (-not $Python) {
        $PythonCandidates = @($RawPythonCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Sort-Object -Unique)
        if ($PythonCandidates.Count -eq 0) {
            throw "Could not find komorebi-full Python. Activate that environment or pass -Python explicitly."
        }
        $Python = $PythonCandidates[0]
    }
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}

if (-not $Run) {
    $Run = "$Root\input_run\pilot-711001"
}

if (-not $Output) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Output = "$env:USERPROFILE\Downloads\Neuralese_G1D_Runs\pilot-711001-$Stamp"
}

if (-not $StaticOnly -and -not $Model) {
    $KnownModel = "$env:USERPROFILE\Downloads\RRCT_v060_MODELS\Qwen2.5-0.5B-Instruct"
    if (Test-Path -LiteralPath "$KnownModel\config.json" -PathType Leaf) {
        $Model = $KnownModel
    }
    else {
        throw "The registered local Qwen model was not found. Pass -Model explicitly."
    }
}

$EnvironmentNames = @(
    "HF_HUB_OFFLINE",
    "TRANSFORMERS_OFFLINE",
    "TOKENIZERS_PARALLELISM",
    "CUBLAS_WORKSPACE_CONFIG",
    "PYTHONPATH"
)
$SavedEnvironment = @{}
foreach ($Name in $EnvironmentNames) {
    $SavedEnvironment[$Name] = [Environment]::GetEnvironmentVariable($Name, "Process")
}

try {
    $env:HF_HUB_OFFLINE = "1"
    $env:TRANSFORMERS_OFFLINE = "1"
    $env:TOKENIZERS_PARALLELISM = "false"
    $env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
    $env:PYTHONPATH = if ($env:PYTHONPATH) { "$Root;$Root\vendor\g1_v0_1_1;$env:PYTHONPATH" } else { "$Root;$Root\vendor\g1_v0_1_1" }

    & $Python "$Root\verify_package.py" --quick
    if ($LASTEXITCODE -ne 0) { throw "Package verification failed with exit code $LASTEXITCODE" }

    $Arguments = @(
        "$Root\run_diagnostics.py",
        "--run", $Run,
        "--output", $Output
    )
    if ($StaticOnly) {
        $Arguments += "--static-only"
    }
    else {
        $Arguments += @("--model", $Model)
    }
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Diagnostic run failed with exit code $LASTEXITCODE" }

    & $Python "$Root\verify_diagnostics.py" --output $Output
    if ($LASTEXITCODE -ne 0) { throw "Diagnostic verification failed with exit code $LASTEXITCODE" }
    $ResultZip = "$Output-results.zip"
    Compress-Archive -LiteralPath $Output -DestinationPath $ResultZip -CompressionLevel Optimal
    $Scope = if ($StaticOnly) { "STATIC_ONLY" } else { "FULL_DIAGNOSTIC" }
    Write-Output "G1D_STATUS=$($Scope)_COMPLETE"
    Write-Output "OUTPUT=$Output"
    Write-Output "RESULT_ZIP=$ResultZip"
}
finally {
    foreach ($Name in $EnvironmentNames) {
        [Environment]::SetEnvironmentVariable($Name, $SavedEnvironment[$Name], "Process")
    }
}
