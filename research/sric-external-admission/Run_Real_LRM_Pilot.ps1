param(
    [string]$RuntimeRoot = (Join-Path $PSScriptRoot "external_runtime"),
    [ValidateSet("smoke", "primary", "full")][string]$Profile = "primary",
    [ValidateSet("cuda", "cpu")][string]$Device = "cuda",
    [switch]$StageOnly,
    [switch]$RunOnly
)

$ErrorActionPreference = "Stop"
if ($StageOnly -and $RunOnly) { throw "StageOnly and RunOnly cannot both be set." }

function Invoke-PythonChecked {
    param(
        [Parameter(Mandatory=$true)][string]$Python,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE: $Python $($Arguments -join ' ')"
    }
}

$PathsFile = Join-Path $RuntimeRoot "runtime_paths.json"
if (-not (Test-Path $PathsFile)) {
    throw "Missing runtime_paths.json. Run Setup_External_PrOntoQA_Coconut.ps1 first."
}
$Paths = Get-Content -Raw $PathsFile | ConvertFrom-Json
$Py = $Paths.python
if (-not (Test-Path $Py)) { throw "Pinned external Python is missing: $Py" }
if ($Device -eq "cuda") {
    $CudaVisible = (& $Py -c "import torch; print(int(torch.cuda.is_available()))").Trim()
    if ($LASTEXITCODE -ne 0 -or $CudaVisible -ne "1") {
        throw "CUDA profile requested, but CUDA is not available in the pinned external runtime."
    }
}

$ConfigMap = @{
    smoke = (Join-Path $PSScriptRoot "configs\prontoqa_smoke.json")
    primary = (Join-Path $PSScriptRoot "configs\prontoqa_multimode_coconut_gpt2.json")
    full = (Join-Path $PSScriptRoot "configs\prontoqa_full.json")
}
$Config = $ConfigMap[$Profile]
$Seal = Join-Path $PSScriptRoot "frozen\real_${Profile}_preaudit_seal.json"
$Result = Join-Path $PSScriptRoot "results\real_${Profile}_block24.json"
$Summary = Join-Path $PSScriptRoot "results\real_${Profile}_summary.md"

Push-Location $PSScriptRoot
try {
    Invoke-PythonChecked -Python $Py -Arguments @("-m", "sric_real_lrm", "preflight", "--external-repo", $Paths.external_repo, "--checkpoint", $Paths.checkpoint, "--data", $Paths.data)
    Invoke-PythonChecked -Python $Py -Arguments @("-m", "sric_real_lrm", "verify-source", "--external-repo", $Paths.external_repo, "--dataset-key", "prontoqa_test")

    if (-not $RunOnly) {
        $StageArgs = @(
            "-m", "sric_real_lrm", "stage-real",
            "--config", $Config,
            "--data", $Paths.data,
            "--external-repo", $Paths.external_repo,
            "--checkpoint", $Paths.checkpoint,
            "--base-model", $Paths.base_model,
            "--checkpoint-revision", $Paths.checkpoint_revision,
            "--base-model-revision", $Paths.base_model_revision,
            "--output", $Seal
        )
        Invoke-PythonChecked -Python $Py -Arguments $StageArgs
        Invoke-PythonChecked -Python $Py -Arguments @("-m", "sric_real_lrm", "verify-seal", $Seal)
    }

    if (-not $StageOnly) {
        if (-not (Test-Path $Seal)) { throw "RunOnly requires an existing verified seal: $Seal" }
        Invoke-PythonChecked -Python $Py -Arguments @("-m", "sric_real_lrm", "verify-seal", $Seal)
        $RunArgs = @(
            "-m", "sric_real_lrm", "run-real",
            "--config", $Config,
            "--data", $Paths.data,
            "--external-repo", $Paths.external_repo,
            "--checkpoint", $Paths.checkpoint,
            "--base-model", $Paths.base_model,
            "--checkpoint-revision", $Paths.checkpoint_revision,
            "--base-model-revision", $Paths.base_model_revision,
            "--seal", $Seal,
            "--device", $Device,
            "--output", $Result
        )
        Invoke-PythonChecked -Python $Py -Arguments $RunArgs
        Invoke-PythonChecked -Python $Py -Arguments @("-m", "sric_real_lrm", "verify-result", $Result)
        Invoke-PythonChecked -Python $Py -Arguments @(".\summarize_result.py", "--result", $Result, "--output", $Summary)
    }
} finally {
    Pop-Location
}
