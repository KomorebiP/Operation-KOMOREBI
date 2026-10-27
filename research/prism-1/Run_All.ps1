$ErrorActionPreference = "Stop"
python prism_chip_model.py --root .
$env:PYTHONPATH = "."
python -m pytest -q
latexmk -pdf -interaction=nonstopmode -halt-on-error Komorebi_PRISM_1_Final_Updated.tex
