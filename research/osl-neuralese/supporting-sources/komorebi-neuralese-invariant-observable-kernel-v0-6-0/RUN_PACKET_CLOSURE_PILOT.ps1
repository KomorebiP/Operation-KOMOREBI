$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
python -E -P -B .\run_packet_closure.py --profile pilot --output-dir .\results\packet_closure_pilot
exit $LASTEXITCODE
