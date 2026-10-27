# Machine Societies — v0.5.0
## A Theory of Persistent Plural Computational Organization

**Komorebi P. · 7 October 2026 · Expanded theoretical edition · 64 pages**

This is a self-contained theoretical manuscript. It does not report the author's agent experiments or claim that a machine society has been demonstrated. The eight additions develop membership, institutional language, public knowledge, noncommutative federation, amendment ordering, computability, evolving inquiry agendas, and founding authorization.

## Start here

- `Machine_Societies_v0.5.0.pdf`: the complete reading edition.
- `Machine_Societies_v0.5.0.tex`: editable source, with references included inline.
- `THEOREM_INDEX.md`: all 41 proved statements, 6 definitions, and 11 counterexamples.
- `REVISION_NOTES.md`: substantive changes from the preserved v0.4.0 source.
- `PROOFREADING_REPORT.md`: review scope, corrections, execution results, and remaining limits.
- `validation/`: exact checks, provenance, source diff, reference audit, and release verifier.
- `sources/v0.4.0/`: historical predecessor source and selected records, not new v0.5 evidence.

## Compile the manuscript

Use a TeX Live or MiKTeX installation with `latexmk`, pdfLaTeX, `newtx`, and the other packages declared in the source. The figures are already supplied as PDFs. A separate bibliography processor is not needed.

```sh
bash build.sh
```

On Windows PowerShell:

```powershell
.\build.ps1
```

The result is `build/Machine_Societies_v0.5.0.pdf`. The shipped reading PDF is not overwritten. The Bash build has been executed in this environment. The PowerShell script is supplied and inspected but has not been executed on Windows.

## Verify integrity before modifying or regenerating

```sh
python validation/verify_release.py
```

The verifier checks the release inventory, manuscript/code/result hashes, and the legacy computation-manifest record. This is not a theorem prover.

## Repeat exact finite checks

```sh
python validation/check_finite_models.py
```

The tests need Python 3.10 or later and only the standard library. The recorded execution used Python 3.13.5. They enumerate integer and rational constructions with explicit domains. The release run passed 39 groups and 325,054 assertions. That is finite companion validation, not an empirical agent experiment or an independent replication.

A rerun rewrites the result and manifest with fresh timing. Consequently the original `SHA256SUMS.txt` will no longer match those regenerated records. Verify the original release before rerunning; retain regenerated evidence separately or intentionally create a new inventory. The release verifier supports `--manifest-only` for checking a regenerated computation record without asserting byte identity to this release.

## Optional figure regeneration

Matplotlib is required only to regenerate the diagrams and analytical plots:

```sh
python figures/regenerate_figures.py
python figures/regenerate_analytical_figures.py
python figures/regenerate_v05_figures.py
```

All figures are programmatic vector graphics. None is an AI-generated image. Regeneration may change PDF metadata or font-subset bytes across installations even when the geometry is the same. No font files are distributed.

## Status and attribution

The mathematical foundations include established state aggregation, game theory, epistemic logic, rewriting, synchronization, and computability results. The framework and its institutional applications should not be confused with priority claims for those foundations. The manuscript has not undergone independent peer review, formal-kernel verification, an exhaustive priority search, or venue-specific editorial review. No publication acceptance, empirical society formation, moral status, or legal authority is asserted.
