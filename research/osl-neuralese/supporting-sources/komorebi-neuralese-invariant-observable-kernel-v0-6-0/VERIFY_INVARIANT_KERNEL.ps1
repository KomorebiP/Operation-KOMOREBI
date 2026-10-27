$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
python -E -P -B .\verify_invariant_kernel.py @args
exit $LASTEXITCODE
