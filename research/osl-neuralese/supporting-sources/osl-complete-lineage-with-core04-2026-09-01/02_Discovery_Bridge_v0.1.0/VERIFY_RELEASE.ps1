param([string]$OslCore = "")
$Arguments = @("verify_release.py")
if ($OslCore) { $Arguments += @("--osl-core", $OslCore) }
Push-Location $PSScriptRoot
try {
    python @Arguments
    $Code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $Code
