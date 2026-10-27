# Reproducibility

The repository separates four kinds of verification.

## 1. Source provenance

The exact single-file source snapshot is retained under `archive/v1.0.0/`. The canonical repository source is modular for review. `scripts/split_monograph.py --check` verifies that every modular content file matches the corresponding segment of the frozen snapshot.

## 2. Document build

`python scripts/repo.py build` performs a clean `latexmk` build. Strict verification checks page count, log hygiene, font embedding, encryption status, and extracted-text equivalence with the committed PDF.

## 3. Deterministic mathematical regression checks

The scripts under `verification/` reproduce finite-dimensional calculations used in the structural examples, case studies, decomposition analysis, and specification-identification section. Their assertions are theorem-specific and tolerance-aware.

## 4. Scholarly review

Neither successful compilation nor passing numerical checks establishes that every proof is correct, every hypothesis is minimal, or every novelty assessment is complete. The audit files make those claims easier to inspect but do not replace external specialist review.

## One-command audit

```bash
python scripts/repo.py verify --strict
```

The same command is executed by GitHub Actions on pushes and pull requests.
