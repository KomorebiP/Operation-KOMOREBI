param([switch]$StaticOnly)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if ($StaticOnly) { python verification/verify.py --static-only }
    else { python verification/verify.py }
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $code
