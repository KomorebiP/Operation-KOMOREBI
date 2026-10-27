$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$Root;$env:PYTHONPATH" } else { $Root }
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python run_all.py
python -m pytest -q
if (Get-Command latexmk -ErrorAction SilentlyContinue) {
    latexmk -pdf -interaction=nonstopmode -halt-on-error Seven_Area_Worked_Proof_Atlas.tex
} else {
    Write-Host "latexmk not found; symbolic generation and tests completed."
}
