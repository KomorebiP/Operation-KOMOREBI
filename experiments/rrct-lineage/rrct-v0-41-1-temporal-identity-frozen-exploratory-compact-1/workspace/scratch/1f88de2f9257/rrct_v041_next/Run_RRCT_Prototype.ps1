$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = if ($env:CONDA_PREFIX) { Join-Path $env:CONDA_PREFIX "python.exe" } else { "python" }
& $Python -m pip install -e "${Root}[figures]"
& $Python -m rrct.cli verify
& $Python -m rrct.cli demo --output (Join-Path $Root "results_v0.4") --seed 17 --train-episodes 256 --test-episodes 128
