param([string]$Python = "$env:CONDA_PREFIX\python.exe")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
& $Python -c "import numpy, pytest; print('numpy=' + numpy.__version__); print('pytest=' + pytest.__version__)"
if ($LASTEXITCODE -ne 0) { throw "The selected Python needs numpy and pytest" }
& $Python -m pip install --disable-pip-version-check --no-deps --no-build-isolation -e $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python "$Root\validation\run_v042_causal_necessity_analysis.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest -q "$Root\tests\test_v042_causal_self_model_necessity.py"
exit $LASTEXITCODE
