$ErrorActionPreference = "Stop"
python -m unittest -v test_probe.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python verify_manifest.py
exit $LASTEXITCODE
