Push-Location $PSScriptRoot
try {
    python .\verify_bundle.py
    $Code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $Code
