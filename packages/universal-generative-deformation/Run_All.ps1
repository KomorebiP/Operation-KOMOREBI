$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
    python -m pip install -e . --no-build-isolation
    python .\run_all.py
    python -m pytest -q
    Push-Location .\paper
    try {
        pdflatex -interaction=nonstopmode -halt-on-error Universal_Generative_Deformation_Calculus.tex
        pdflatex -interaction=nonstopmode -halt-on-error Universal_Generative_Deformation_Calculus.tex
        pdflatex -interaction=nonstopmode -halt-on-error Universal_Generative_Deformation_Calculus.tex
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
