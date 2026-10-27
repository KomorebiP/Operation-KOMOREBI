param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $Work
$env:PYTHONPATH = Join-Path $Work "src"
& $Python -m komorebi_arc3_offline.lasm_cli smoke --output (Join-Path $Work "results\pr_lasm_smoke") --max-actions 90 --initial-probes 16 --recurring-probes 8
