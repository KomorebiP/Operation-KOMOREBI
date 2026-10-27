$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Output = ".\results\local\invariant_kernel_smoke_$Stamp"
python -E -P -B .\run_invariant_kernel.py --profile smoke --output-dir $Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -E -P -B .\verify_invariant_kernel.py --result-dir $Output
exit $LASTEXITCODE
