# Reproducibility

The release was verified with Python 3.12.13, Lean 4.34.0-rc2, Lake 5.0.0,
Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and `latexmk`/pdfTeX.
Python packages are pinned in `code/python/requirements.lock`; Lean and Mathlib
are pinned by `lean-toolchain` and `lake-manifest.json`.

## One-command verification

Run `./Run_All.sh` on Unix-like systems or `.\Run_All.ps1` in PowerShell.
Both entry points require the v1.2.1 wheel and the v1.1.1 Lean theorem map,
and fail if Python, Lake, theorem-map, kernel-audit, or LaTeX verification
fails. The scripts do not update Lean dependencies.

## Individual checks

From the release root, with the pinned Python environment active:

```sh
python code/python/run_all.py
python -m pytest -q -W error code/python/tests
python -m build --wheel --no-isolation --outdir code/python/dist code/python
python -m pip install --no-deps code/python/dist/projector_seed_refinement-1.2.1-py3-none-any.whl
python -m pip check
```

For Lean:

```sh
cd formalization/lean
lake --wfail build
python scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/PaperII/KernelAudit.lean
```

`lake --wfail build` makes Lake warnings fatal, while the package-level
`moreLeanArgs = ["-E", "warning"]` setting makes Lean elaborator warnings
fatal. The theorem-map checker requires exactly one versioned map (the release
ships `LEAN_THEOREM_MAP_v1.1.1.md`), validates contract rows 1--25, and asks
Lean to resolve every mapped declaration. `KernelAudit.lean` is then executed
as a separate fail-closed check over the compiled `Komorebi` declaration
namespace.

For the paper:

```sh
cd paper
SOURCE_DATE_EPOCH=1788393600 latexmk -C Projector_Resolved_Seed_Calculus_II.tex
SOURCE_DATE_EPOCH=1788393600 latexmk -pdf -interaction=nonstopmode -halt-on-error Projector_Resolved_Seed_Calculus_II.tex
```

The epoch is the release date at 00:00 UTC and matches the default exported by
`Run_All.sh`; using it makes repeated clean builds of the canonical PDF
byte-identical in the documented environment.

The numerical results and all figure pairs are deterministically regenerated
from the included Python source. Floating-point residuals may differ in their
last displayed digits across BLAS/platform combinations, while exact symbolic
and modular certificates must remain unchanged.

Lean kernel acceptance checks the formal declarations and their explicit
assumptions. The Python tests check the executable finite realizations. Neither
check establishes novelty, historical priority, or independent peer review.
