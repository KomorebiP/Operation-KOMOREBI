# Development

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Required checks

```powershell
python -m compileall -q src examples
python -m pytest -q -m "not local_suite"
python examples\exact_reconstruction.py
python examples\adaptive_refinement.py
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

## Optional full local suite

Install the separate fixture archive, then run:

```powershell
python -m pytest -q
.\pr-lasm.ps1 suite-audit
```

## Change discipline

A change to an exact transform must add reconstruction tests. A change to a
program family must add a controlled identification case or state why no
such certificate is possible. A new benchmark number must be written to a
machine-readable result file and must specify the configuration that
produced it.
