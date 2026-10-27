param(
    [string]$Python = $(if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" } else { "python" })
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
    $env:PYTHONPATH = Join-Path $Root "src"
    & $Python -m pytest -q tests/test_v029_agent_boundary_integration.py tests/test_v036_unified_causal_loop.py tests/test_v036_development_protocol_spec.py tests/test_v037_post_change_closure.py tests/test_v038_access_generalization.py
    if ($LASTEXITCODE -ne 0) { throw "Focused validation failed" }
    & $Python -m rrct.access_generalization_experiment verify-freeze
    if ($LASTEXITCODE -ne 0) { throw "Pre-outcome freeze verification failed" }
    $Code = @'
import json
from rrct.access_generalization_experiment import aggregate_v038_campaign
summary = aggregate_v038_campaign()
print(json.dumps(summary, indent=2, sort_keys=True))
raise SystemExit(0 if summary["cohort_target_met"] else 2)
'@
    & $Python -c $Code
    if ($LASTEXITCODE -ne 0) { throw "Cohort evidence verification failed" }
}
finally {
    Pop-Location
}
