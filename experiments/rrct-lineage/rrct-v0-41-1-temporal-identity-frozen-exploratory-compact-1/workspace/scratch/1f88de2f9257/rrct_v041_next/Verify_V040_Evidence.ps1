param([string]$Python = "$env:CONDA_PREFIX\python.exe")
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
$env:PYTHONPATH = "$PSScriptRoot\src;$PSScriptRoot"
& $Python -m pytest -q tests/test_v036_unified_causal_loop.py tests/test_v037_post_change_closure.py tests/test_v038_access_generalization.py tests/test_v039_autonomous_self_diagnosis.py tests/test_v040_robust_reflexive_diagnosis.py
if ($LASTEXITCODE -ne 0) { throw "Focused v0.36-v0.40 tests failed" }
$campaign = Join-Path $PSScriptRoot "validation\v0.40_robust_reflexive_diagnosis_campaign"
if (Test-Path -LiteralPath $campaign) {
    & $Python (Join-Path $PSScriptRoot "validation\audit_v040_campaign.py") --project-root $PSScriptRoot
    if ($LASTEXITCODE -ne 0) { throw "v0.40 evidence audit failed" }
} else {
    Write-Host "Raw campaign rows are absent. Source tests passed; full evidence audit was skipped."
}
