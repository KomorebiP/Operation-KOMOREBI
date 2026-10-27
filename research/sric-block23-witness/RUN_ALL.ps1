$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$env:PYTHONHASHSEED='0'
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
python .\run_all.py
python .\stage_external_fixture.py
python .\make_figures.py
python .\generate_release_docs.py
python -m pytest -q
python .\independent_verify.py
python .\build_manifest.py
python .\verify_package.py
