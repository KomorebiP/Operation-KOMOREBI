param(
    [string]$RuntimeRoot = (Join-Path $PSScriptRoot "external_runtime"),
    [string]$Config = (Join-Path $PSScriptRoot "configs\prontoqa_multimode_coconut_gpt2.json"),
    [ValidateSet("cuda", "cpu")][string]$Device = "cuda",
    [switch]$StageOnly,
    [switch]$RunOnly
)

$ErrorActionPreference = "Stop"
if ($StageOnly -and $RunOnly) { throw "StageOnly and RunOnly cannot both be set." }
$PathsFile = Join-Path $RuntimeRoot "runtime_paths.json"
if (-not (Test-Path $PathsFile)) {
    throw "Missing runtime_paths.json. Run Setup_External_PrOntoQA_Coconut.ps1 first."
}
$Paths = Get-Content -Raw $PathsFile | ConvertFrom-Json
$Py = $Paths.python
$Seal = Join-Path $PSScriptRoot "frozen\real_preaudit_seal.json"
$Result = Join-Path $PSScriptRoot "results\real_checkpoint_audit.json"

Push-Location $PSScriptRoot
try {
    if (-not $RunOnly) {
        & $Py -m sric_real_lrm stage-real `
            --config $Config `
            --data $Paths.data `
            --external-repo $Paths.external_repo `
            --checkpoint $Paths.checkpoint `
            --base-model $Paths.base_model `
            --output $Seal
        & $Py -m sric_real_lrm verify-seal $Seal
    }
    if (-not $StageOnly) {
        & $Py -m sric_real_lrm run-real `
            --config $Config `
            --data $Paths.data `
            --external-repo $Paths.external_repo `
            --checkpoint $Paths.checkpoint `
            --base-model $Paths.base_model `
            --seal $Seal `
            --device $Device `
            --output $Result
        & $Py -m sric_real_lrm verify-result $Result
        & $Py .\summarize_result.py --result $Result --output .\results\real_checkpoint_summary.md
    }
} finally {
    Pop-Location
}
