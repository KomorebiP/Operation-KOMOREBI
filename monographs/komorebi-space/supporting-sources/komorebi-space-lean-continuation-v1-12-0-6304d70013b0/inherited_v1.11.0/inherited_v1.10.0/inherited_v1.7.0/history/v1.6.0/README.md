# Komorebi Space — 1.6.0

Coherent realizations, obstructions, and descent.

## Reader set

- `publication/Komorebi_Space_Monograph.pdf` — 133 pages.
- `publication/Komorebi_Space_Visual_Guide.pdf` — 43 pages, forty plates.
- `publication/Komorebi_Space_Lean_Guide.pdf` — 36 pages.

Editable LaTeX is in `source/`. Exact examples are in `examples/`. Begin with `PROGRESS_LEDGER.md` and verify the payload before modifying it.

This edition adds two chapters, four mathematical plots, an exact inexact-correction certificate verifier, and three newly verified Lean modules. The canonical `formal/` tree remains unchanged. The focused `extension/` has its own clean seven-target replay and axiom audit. Four WR groups have complete focused counterparts, two have partial pointwise coverage, and ten remain written-only. Read the per-result scope labels instead of treating the publication version as a global verification claim.

```sh
python3 checks/verify_payload.py
bash build.sh
python3 examples/inexact_repair_certificate.py
```

The build requires the existing LaTeX packages and Python dependencies described in `BUILD.md`. It verifies the accepted evidence but does not silently run Lean. Runtime files and disposable build objects are not included. New formal runs use `extension/scripts/verify.py` for the focused closure or `formal/scripts/verify.py` for the unchanged canonical project; each has its own scope and nonoverwriting labels.

The monograph includes complete printed proofs and source correspondences, not a universal theorem that every intended semantic space is realized. The official Lean kernel/compiler and pinned imported caches remain trusted. Neither universal Python refinement nor a new full cumulative Lean replay is claimed.
