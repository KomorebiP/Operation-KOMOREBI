$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$Rehearsal = Join-Path $Root "results\invariant_kernel_seed887_final_rehearsal\REHEARSAL_SUMMARY.json"
if (Test-Path -LiteralPath $Rehearsal) {
    $Receipt = Get-Content -LiteralPath $Rehearsal -Raw | ConvertFrom-Json
    if ($Receipt.decision -eq "CALIBRATION_FAILURE_STOP_BEFORE_SCREEN") {
        Write-Error "The frozen seed-887 calibration failed. Protocol requires seed 947 to remain untouched; screen launch refused."
        exit 3
    }
}
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Output = ".\results\local\invariant_kernel_screen_$Stamp"
python -E -P -B .\run_invariant_kernel.py --profile screen --output-dir $Output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -E -P -B .\verify_invariant_kernel.py --result-dir $Output
exit $LASTEXITCODE
