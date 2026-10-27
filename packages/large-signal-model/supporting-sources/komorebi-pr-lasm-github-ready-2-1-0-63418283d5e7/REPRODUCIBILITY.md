# Reproducibility

## Core certificate

```powershell
python -m pip install -e ".[test]"
python -m compileall -q src examples
python -m pytest -q -m "not local_suite"
python examples\exact_reconstruction.py
python examples\adaptive_refinement.py
```

## Controlled benchmark

```powershell
python -m komorebi_pr_lasm benchmark --output results\pr_lasm_benchmark
```

Compare the generated JSON and CSV files with
`benchmarks/reference/v2.0.0/pr_lasm_benchmark/`. The reference ledger is
retained, not silently overwritten.

## Wheel certificate

```powershell
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
python -m pip install --target wheel-test (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
$env:PYTHONPATH = "$PWD\wheel-test"
python -c "import komorebi_pr_lasm as p; print(p.__version__)"
```

## Optional local ARC suite

Extract the separate 25-environment fixture archive into the repository
root. Then run `python -m pytest -q` and `./pr-lasm.ps1 suite-audit`.
Environment execution requires the pinned optional dependencies and is not
part of the clean public CI certificate.
