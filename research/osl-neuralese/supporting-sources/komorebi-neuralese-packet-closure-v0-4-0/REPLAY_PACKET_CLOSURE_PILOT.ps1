$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
python -E -P -B .\run_packet_closure.py --profile pilot --replay --output-dir ".\results\local\packet_closure_pilot_$Stamp"
exit $LASTEXITCODE
