# Projector-Resolved Seed Calculus X
## Universal Residual Seeds: Deformation Forests, Transport Categories, and System Completion

**Author:** Komorebi P.

This release contains the tenth paper in the Projector-Resolved Seed Calculus series, together with exact finite models, figures, tests, and machine-readable results.

The paper develops:

- residual fibers and the no-crossing theorem;
- lift forests and inverse-limit reconstruction;
- packet decompositions of tangent and obstruction complexes;
- weighted dyadic visibility and delayed packet separation;
- smooth, weighted, and singular seed-zeta functions;
- directed residual transport and the source-component minimum-seed theorem;
- prime-independent system spines and finite companion forests;
- compatible-carrier summand recovery by finite Frobenius separation;
- exact finite occupancy projectors and trace certificates.

The library supplies finite exact models and reproducibility checks. It is not a general-purpose Galois deformation package and does not claim universal compatible-system or automorphic occupancy.

## PowerShell reproduction

```powershell
$Work = "$HOME\Downloads\Projector_Seed_Calculus_X_Release"
Set-Location $Work
& .\Run_All.ps1 -Work $Work
```

To update installed dependencies deliberately:

```powershell
& .\Run_All.ps1 -Work $Work -Update
```

## Direct commands

```powershell
python -m pytest -q
python .\scripts\generate_all.py
python -m pip wheel . --no-deps --no-build-isolation -w .\dist
latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_X.tex
python .\scripts\scrub_pdf_metadata.py .\Projector_Resolved_Seed_Calculus_X.pdf --title "Projector-Resolved Seed Calculus X" --subject "Universal residual seeds, deformation forests, directed transport, seed zeta functions, companion completion, compatible carriers, and finite occupancy"
```
