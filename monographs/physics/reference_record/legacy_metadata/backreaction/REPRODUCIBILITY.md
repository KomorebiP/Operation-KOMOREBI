# Reproducibility

## Three distinct operations

### 1. Validate the frozen package

```bash
python code/validate_release.py
```

This operation is read-only. It checks metadata agreement, TeX and figure references, Python syntax, registry schemas, frozen check counts, cross-volume lineage records, parent-audit summaries, generated-value declarations, and the stated claim boundaries.

### 2. Build the manuscript

Linux or WSL:

```bash
./build.sh
```

Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Both wrappers build in `build/`. The frozen source tree and data are not overwritten. The final validator checks the PDF metadata, encryption state, page geometry, outline, and LaTeX log.

Required system software:

- Python 3.12
- the packages pinned in `requirements.txt`
- a TeX distribution providing `latexmk`, pdfLaTeX, Latin Modern, `tcolorbox`, `cleveref`, and the standard AMS packages

### 3. Recompute the bridge-specific records

The package bundles this frozen parent input from the Volume I source release:

```text
parent/Scale_Covariant_Dark_Sector_Verification.json
```

Then run into a new destination:

```bash
python code/verify_covariant_backreaction.py \
  --parent-json parent/Scale_Covariant_Dark_Sector_Verification.json \
  --output reproduction/data \
  --figures reproduction/figures
cp data/parent_release_audit.json data/cross_volume_lineage.csv reproduction/data/
python code/generate_latex_values.py \
  --data reproduction/data \
  --output reproduction/generated_values.tex
```

The two copied provenance records are inputs to the LaTeX-macro generator; they are not recomputed by the bridge-specific verifier. Do not direct a reproduction run into the release `data/` or `figures/` directories. Compare the regenerated tables numerically. PNG and PDF byte hashes may vary with font, Matplotlib, and PDF backends even when their scientific contents agree.

## Deterministic controls

The bridge verification uses seed `20260819`. The principal resolved closure uses 20 trials on 128 points with input band 3. Negative controls use an aliased 64-point, band-18 case, centered finite differences, an omitted detail gradient, and an omitted average-field exchange term. The production audit also retains the frozen benchmark energy overdraw as a negative physical result.

## Parent-release audit

The parent audit is run with explicit extracted-release roots:

```bash
python code/audit_parent_releases.py \
  --volume-i /path/to/Volume_I_Source \
  --volume-ii /path/to/Volume_II_Source \
  --supplement-i /path/to/Volume_I_Technical_Supplement_Source \
  --output reproduction/parent_audit
```

The audit verifies the Volume II content manifest, parses frozen verification counts, finds byte-identical cross-volume artifacts, statically parses the archived Python programs, and records missing paths. It does not execute the Volume II cosmology pipeline and does not assess physical correctness.

## Comparison contract

For an independent rerun:

1. record the release version and parent hashes
2. record operating system, Python, package, compiler, BLAS, and TeX versions
3. reproduce the five negative controls before accepting the positive residuals
4. compare exact integer and status fields exactly
5. compare floating-point values using declared absolute or relative tolerances rather than file hashes
6. retain all failures and sign changes
7. state whether code was reused, translated, or independently implemented

## Evidence boundary

A successful build establishes only that the archived manuscript compiles. A passing local verification establishes consistency of this implementation over its declared domain. Hash agreement establishes lineage and integrity. None of these operations supplies external independent reproduction, historical novelty, or empirical confirmation.
