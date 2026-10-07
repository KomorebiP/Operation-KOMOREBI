# Release Manifest

Release root: `Projector_Resolved_Seed_Calculus_II_v1.2.1/`

- `paper/Projector_Resolved_Seed_Calculus_II.pdf` — final paper.
- `paper/Projector_Resolved_Seed_Calculus_II.tex` — complete LaTeX source.
- `paper/figures/` — 13 figures, each supplied as PNG and vector PDF.
- `formalization/lean/` — Lean 4/Mathlib component version 1.1.1 and its
  scope-explicit 25-item theorem map, `LEAN_THEOREM_MAP_v1.1.1.md`.
- `formalization/lean/KomorebiVerification/PaperII/` — eight substantive Paper II
  modules plus the fail-closed Paper II kernel audit.
- `formalization/lean/scripts/verify_theorem_map.py` — executable theorem-map
  consistency check.
- `code/python/seed_refinement/` — Python 1.2.1 implementation.
- `code/python/tests/` — 48-test suite.
- `code/python/dist/projector_seed_refinement-1.2.1-py3-none-any.whl` —
  installable wheel built from the included source.
- `code/python/requirements.in` and `requirements.lock` — direct constraints
  and the exact verification environment.
- `results/numerical_results.json` and `numerical_summary.csv` — generated
  machine-readable certificates.
- `results/` verification logs and `run_record.json` — captured final checks.
- `provenance/` — baseline, contract, claim map, verification, and render records.
- `Run_All.sh` and `Run_All.ps1` — fail-fast reproduction entry points.
- `RELEASE.json`, `CHANGELOG.md`, `REPRODUCIBILITY.md`, `CITATION.cff`,
  `CITATION.bib`, and `LICENSE_STATUS.md` — release metadata.
- `SHA256SUMS.txt` — checksum manifest for every release file except itself,
  regenerated after the final verified build.

Mathlib build products under `.lake/`, Python caches, build staging folders,
and LaTeX auxiliary files are intentionally excluded from the release archive.
