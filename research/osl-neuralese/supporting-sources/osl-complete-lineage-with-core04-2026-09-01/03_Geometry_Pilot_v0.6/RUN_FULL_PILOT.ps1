param([string]$Python = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($Python)) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) { $Python = Join-Path $env:CONDA_PREFIX "python.exe" }
    else { $Python = "python" }
}
$env:PYTHONPATH = Join-Path $Root "experiment"
$env:PYTHONDONTWRITEBYTECODE = "1"
& $Python "$Root\experiment\osl_emergence_pilot.py" verify --root $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Remove-Item "$Root\checkpoints\*.pt" -Force -ErrorAction SilentlyContinue
& $Python "$Root\experiment\osl_emergence_pilot.py" run --root $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python "$Root\experiment\osl_emergence_pilot.py" recheck --root $Root
& $Python "$Root\experiment\postoutcome_controls.py"
& $Python "$Root\experiment\postoutcome_geometry_audit.py"
& $Python "$Root\experiment\postoutcome_intervention_sweep.py"
& $Python "$Root\experiment\build_release.py"
& $Python -m pytest -q -p no:cacheprovider "$Root\tests"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python "$Root\experiment\build_manifest.py"
exit $LASTEXITCODE
