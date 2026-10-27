param([string]$Python = "$env:CONDA_PREFIX\python.exe")
$ErrorActionPreference="Stop"; $Root=Split-Path -Parent $MyInvocation.MyCommand.Path
if(-not(Test-Path -LiteralPath $Python)){$Python="python"}
& $Python "$Root\validation\verify_freeze.py"; if($LASTEXITCODE-ne 0){exit $LASTEXITCODE}
$env:PYTHONPATH="$Root\src"; & $Python -m pytest -q -p no:cacheprovider "$Root\tests\test_v056.py"; exit $LASTEXITCODE
