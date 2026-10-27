param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $Work
$env:PYTHONPATH = Join-Path $Work "src"
& $Python -m komorebi_arc3_offline.lasm_cli benchmark --output (Join-Path $Work "results\pr_lasm_benchmark")
