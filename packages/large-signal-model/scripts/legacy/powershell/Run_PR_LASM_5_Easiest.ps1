param([string]$EnvName = "arc3-offline")
$ErrorActionPreference = "Stop"
$Work = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $Work
$call = "conda run -n $EnvName python -m komorebi_arc3_offline.lasm_cli suite-run --environments-dir `"$Work\environment_files`" --output `"$Work\results\pr_lasm_5_easiest`" --order easy --limit 5 --max-actions 1800 --initial-probes 16 --recurring-probes 8"
Invoke-Expression $call
