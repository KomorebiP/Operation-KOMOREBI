param(
    [ValidateSet("wiring", "smoke", "pilot")]
    [string]$Profile = "smoke",
    [string]$Model = "",
    [string]$Output = "",
    [string]$Python = "",
    [int]$Seed = 0,
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Seed -lt 0) {
    throw "Seed must be zero (profile default) or a positive registered seed."
}

if (-not $Python) {
    $RawPythonCandidates = @(
        "$env:USERPROFILE\miniconda3\envs\komorebi-full\python.exe",
        "$env:USERPROFILE\anaconda3\envs\komorebi-full\python.exe",
        "$env:LOCALAPPDATA\miniconda3\envs\komorebi-full\python.exe"
    )
    $PythonCandidates = @($RawPythonCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Sort-Object -Unique)
    if ($PythonCandidates.Count -ne 1) {
        throw "Could not identify exactly one komorebi-full Python. Pass -Python explicitly."
    }
    $Python = $PythonCandidates[0]
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}

if (-not $Model) {
    $KnownModel = "$env:USERPROFILE\Downloads\RRCT_v060_MODELS\Qwen2.5-0.5B-Instruct"
    if (Test-Path -LiteralPath "$KnownModel\config.json" -PathType Leaf) {
        $Model = $KnownModel
    }
    else {
        $ModelCandidates = @(Get-ChildItem -LiteralPath "$env:USERPROFILE\Downloads" -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "Qwen2.5-0.5B-Instruct" -and (Test-Path -LiteralPath (Join-Path $_.FullName "config.json") -PathType Leaf) } | Select-Object -ExpandProperty FullName -Unique)
        if ($ModelCandidates.Count -ne 1) {
            throw "Could not identify exactly one Qwen2.5-0.5B-Instruct directory. Pass -Model explicitly."
        }
        $Model = $ModelCandidates[0]
    }
}

if (-not $Output) {
    $RunName = if ($Seed -gt 0) { "$Profile-$Seed" } else { $Profile }
    $Output = "$env:USERPROFILE\Downloads\Neuralese_G1_Runs\$RunName"
}

$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:TOKENIZERS_PARALLELISM = "false"
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$Root;$env:PYTHONPATH" } else { $Root }

& $Python "$Root\verify_package.py" --quick
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$RunArguments = @(
    "$Root\run_experiment.py",
    "--profile", $Profile,
    "--model", $Model,
    "--output", $Output,
    "--device", $Device
)
if ($Seed -gt 0) {
    $RunArguments += @("--seed", "$Seed")
}
& $Python @RunArguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python "$Root\verify_results.py" --run $Output
exit $LASTEXITCODE
