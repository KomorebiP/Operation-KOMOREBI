param([string]$Python = "")
$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $Python = Join-Path $env:CONDA_PREFIX "python.exe"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = (Get-Command py).Source
    } else {
        throw "Python was not found"
    }
}
$SourcePath = Join-Path $Root "src"
if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $env:PYTHONPATH = $SourcePath
} else {
    $env:PYTHONPATH = "$SourcePath;$env:PYTHONPATH"
}
& $Python -c "import rrct; assert rrct.__version__ == '0.43.0.dev1'; print('RRCT', rrct.__version__)"
if ($LASTEXITCODE -ne 0) { throw "Version verification failed" }
& $Python -m pytest -q -p no:cacheprovider tests/test_v043_whole_loop_causal_closure.py
if ($LASTEXITCODE -ne 0) { throw "Focused v0.43 tests failed" }
$VerifyOut = Join-Path ([System.IO.Path]::GetTempPath()) ("rrct_v043_release_verification_" + [guid]::NewGuid().ToString("N") + ".json")
& $Python validation/verify_v043_release.py --output $VerifyOut
if ($LASTEXITCODE -ne 0) { throw "v0.43 release verification failed" }
& $Python validation/verify_v043_build_manifest.py
if ($LASTEXITCODE -ne 0) { throw "v0.43 build-manifest verification failed" }
Remove-Item -LiteralPath $VerifyOut -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath ($VerifyOut + ".sha256") -Force -ErrorAction SilentlyContinue
Write-Host "V043_WHOLE_LOOP_CAUSAL_CLOSURE_VERIFIED"
Write-Host (Join-Path $Root "V0_43_BLOCK_SUMMARY.md")
