$ErrorActionPreference="Stop"; $Root=Split-Path -Parent $MyInvocation.MyCommand.Path; Set-Location $Root; python .\verify_package.py
