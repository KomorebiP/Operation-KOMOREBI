# Windows counterpart. Inspected, not executed on Windows for this edition.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Force -Path 'build' | Out-Null
    & python code/run_validation.py --out-dir build/validation_rerun
    if ($LASTEXITCODE -ne 0) { throw 'Exact checks, demonstrations, or source audit failed.' }
    & python code/verify_computation.py build/validation_rerun/computation_manifest.json
    if ($LASTEXITCODE -ne 0) { throw 'Computation receipt failed verification.' }
    & latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Machine_Understanding_v1.0.0.tex
    if ($LASTEXITCODE -ne 0) { throw 'LaTeX build failed.' }
    Copy-Item -Force build/Machine_Understanding_v1.0.0.pdf Machine_Understanding_v1.0.0.pdf
} finally { Pop-Location }
