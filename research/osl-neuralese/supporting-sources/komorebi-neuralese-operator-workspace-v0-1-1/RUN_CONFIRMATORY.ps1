$ErrorActionPreference="Stop"; $Root=Split-Path -Parent $MyInvocation.MyCommand.Path; Set-Location $Root; python .\run_experiment.py --profile confirmatory --output-dir .\results\confirmatory
