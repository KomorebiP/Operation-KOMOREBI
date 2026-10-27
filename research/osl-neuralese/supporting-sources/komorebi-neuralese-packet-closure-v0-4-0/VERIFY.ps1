$ErrorActionPreference="Stop"; $Root=Split-Path -Parent $MyInvocation.MyCommand.Path; Set-Location $Root; python -E -P -B .\verify_package.py; exit $LASTEXITCODE
