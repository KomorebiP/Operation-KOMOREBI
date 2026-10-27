$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$env:PYTHONHASHSEED='0'
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
python .\verify_package.py
python -m pytest -q
python .\independent_verify.py
