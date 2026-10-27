# Grounded Abstraction
## Identifiability, Representation Change, and the Limits of Learning

**Komorebi P. · Operation Komorebi · Expanded theoretical edition v0.5.0 · 9 October 2026**

A 33-page, five-part theoretical manuscript. The principal product is its sixteen self-contained statement/proof pairs. Small exact constructions support the exposition; there is no training campaign or broad agent implementation.

The central extension distinguishes full-state calibration, identifiable observable behavior under a fixed unknown model, a common quotient valid across models, and a predictor that can actually be initialized from available evidence. A second extension supplies an exact probability memory for repeated noisy correction and a criterion for migrating that memory when the evidence language changes.

## Reading map

`Grounded_Abstraction_v0.5.0.pdf` is the reading manuscript and the matching `.tex` file is canonical editable source. `STATEMENT_INDEX.json` maps all sixteen formal statements to their current numbers and source lines. `ASSUMPTION_REVIEW.md` records essential premises. `SOURCE_MAP.md` states actual reference-review depth. `REVIEW_NOTES.md` distinguishes proofs, finite checks, preservation, and remaining limits. `FIRST_EDITION_PLAN.md` defines a bounded route to a first-edition freeze.

The ten predecessor statement/proof pairs and two original reference programs are unchanged. Selected predecessor files and records are retained under `history/v0.1.0/`; that folder is a provenance extract, not the complete old release. The original v0.1 PDF and ZIP remain separate unchanged deliverables. The historical checksum file is contextual evidence for that old release, not a claim that its whole payload is copied into this folder.

## Reproduction

Check the frozen snapshot before replacing timed receipts:

```text
python code/verify_release.py
```

The two exact suites use only Python's standard library:

```text
python code/run_checks.py
python code/verify_release.py --receipt-only
```

They run 17 bounded groups and 42,311 assertions in integers, exact fractions, finite sets, and F2. Each actual child process has a twenty-second wall limit. Counts do not replace the manuscript's general proofs.

To regenerate the seven analytical figures:

```text
python code/make_figures.py
python code/make_observable_figures.py
```

Install `requirements-figures.txt` first. Supplied vector figures suffice for a text rebuild, so regeneration is optional. No generative pictorial images or font files are distributed.

With a suitable TeX installation:

```text
bash build.sh
python code/audit_manuscript.py
python code/pdf_preflight.py
```

The preflight additionally uses PyMuPDF and the Poppler `pdffonts` command. `build.ps1` is provided but has not been executed on Windows. A complete same-environment clean rebuild check is available as:

```text
python code/check_fresh_rebuild.py
```

A rerun replaces timed validation files, intentionally making the original frozen snapshot inventory stale. A matching checksum establishes byte integrity relative to that inventory, not independent provenance or mathematical truth.

## Worked distinctions

A three-coordinate hidden system has a shared two-coordinate exact predictor when its uncertainty remains in an invariant invisible direction. An initially invisible difference can instead return to the output after one further step. Two fixed models can agree on a restricted family of initial conditions while alternating between them produces a different output: fixed uncertainty is not arbitrary switching.

For a noisy eight-world sensor, four joint target/likelihood-profile masses preserve all specified future evidence probabilities and target corrections. Two priors with the same target and sensor marginals give posterior probabilities 3/4 and 1/4 after the same report. These are probabilities, not four bits of physical memory.

## Status

The edition is internally reviewed theoretical work. It is not independently peer reviewed, Lean verified, a universal identification algorithm, or an empirical claim that a model learned its semantics. All candidate systems and likelihoods in the new exact constructions are supplied. Approximate common quotients, economical noisy memory, restricted experiment languages, and model admission remain separate theoretical extensions.
