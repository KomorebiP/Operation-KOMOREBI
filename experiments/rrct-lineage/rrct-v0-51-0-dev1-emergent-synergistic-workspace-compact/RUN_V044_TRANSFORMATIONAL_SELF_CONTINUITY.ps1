param([switch]$FullReplay)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { Join-Path $env:CONDA_PREFIX "python.exe" } else { "python" }
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = Join-Path $Root "src"
Push-Location $Root
try {
    & $Python -c "import rrct; assert rrct.__version__ == '0.44.0.dev1'; print('RRCT', rrct.__version__)"
    if ($LASTEXITCODE -ne 0) { throw "RRCT v0.44 import/version check failed" }
    & $Python -m pytest -q -p no:cacheprovider tests/test_v044_transformational_self_continuity.py
    if ($LASTEXITCODE -ne 0) { throw "RRCT v0.44 focused tests failed" }
    $Temp = Join-Path ([System.IO.Path]::GetTempPath()) ("rrct_v044_verify_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $Temp -Force | Out-Null
    try {
        $VerifyArgs = @("validation/verify_v044_release.py", "--output", (Join-Path $Temp "V0_44_RELEASE_VERIFICATION.json"))
        if (-not $FullReplay) { $VerifyArgs += "--skip-replay" }
        & $Python @VerifyArgs
        if ($LASTEXITCODE -ne 0) { throw "RRCT v0.44 release verification failed" }
        & $Python validation/verify_v044_build_manifest.py
        if ($LASTEXITCODE -ne 0) { throw "RRCT v0.44 build-manifest verification failed" }
    }
    finally {
        Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($FullReplay) { Write-Host "V044_RELEASE_VERIFIED_WITH_FRESH_REPLAY" } else { Write-Host "V044_RELEASE_VERIFIED" }
}
finally {
    Pop-Location
}
