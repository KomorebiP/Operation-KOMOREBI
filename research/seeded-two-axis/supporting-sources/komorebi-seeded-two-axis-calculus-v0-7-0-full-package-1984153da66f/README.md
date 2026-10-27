# Komorebi Seeded Two-Axis Calculus v0.7.0

**Working mathematical manuscript, 60 pages. Author: Komorebi P.**

This release continues the supplied v0.6.0. It contains written proofs and authoring-session self-review, plus exact finite regression checks. It does not contain Lean certificates or an independent referee report.

## Read first

- `Komorebi_Seeded_Two_Axis_Calculus_v0.7.0.pdf`: the complete running manuscript.
- `Komorebi_Seeded_Two_Axis_Calculus_v0.7.0.tex`: standalone source, with its bibliography embedded.
- `STATUS.md`: current outcomes, restrictions, and next mathematical obligations.
- `audit/AUDIT.md`: claim dependencies, checks, scope, counterexamples, and review boundary.
- `proofs/`: the two new proof blocks, also embedded in the standalone manuscript.
- `checks/`: executable exact regression and recorded results.
- `previous/`: the preceding PDF, source, and complete v0.6.0 ZIP, preserved unchanged.

## Main additions

K32 constructs coherent event diagrams from strict chain-natural exchange data. K33–K35 define interaction residuals, characterize context-independent event increments, and reconstruct reduced excisive ideal diagrams from principal ideals. K36 constructs the universal constructor-compatible excisive quotient. K37–K41 give tensor-cube and integer models, a gcd calculation, the prime-overlap kernel, a finite-signature certificate for all finite diagrams in the stated scalar grammar, and a matrix free-part collapse criterion.

The historical claim of ordered filtration independence remains refuted. Excision gives context independence of labelled increments, not an identification of differently ordered filtrations. Event-diagram reconstruction is not arithmetic globalization.

## Reproduce the checks

The check scripts use the Python standard library only. They were run with Python 3.13.5. From this directory:

```bash
python checks/check_models.py --max-length 10 --output checks/base_regression_results.json
python checks/check_interactions.py --output checks/interaction_results.json
```

The second script imports `check_models.py` from its own directory. All bounds, coefficient conventions, the explicit matrix family, and nonclaims are recorded in the result JSON. Reruns update runtimes and command paths and therefore change JSON hashes. No floating tolerance or random sampling is used. Tests support implementation checks, not universal category-theoretic certification.

## Build the manuscript

A LaTeX installation with the packages named in the source and `latexmk` is required. The release was built using pdfTeX 1.40.26 (TeX Live 2025/dev/Debian).

```bash
mkdir -p build
latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.7.0.tex
```

To regenerate the standalone source from the preserved base and new proof blocks:

```bash
python audit/integrate_v070.py
```

This regeneration overwrites the current standalone source. Its byte-for-byte idempotence was checked before packaging. Local edits to the source should first be saved or migrated to the integration script/proof fragments.

## Provenance and limits

See `audit/manifest.json`, `audit/source_checks.md`, `audit/v0.6.0_to_v0.7.0.diff`, and `SHA256SUMS.txt`. Public source documents are cited, not bundled. No font files are distributed. The complete v0.6.0 ZIP is retained as a historical input, not reissued as independently verified evidence.

No new foundational axiom, historical novelty, unrestricted arithmetic existence, or Langlands reciprocity is claimed. In the scalar example, coarsening functors are identity functors between labelled resolutions. Actual arithmetic coarsening is a next obligation.
