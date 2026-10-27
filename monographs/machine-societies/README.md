# Machine Societies

**A Theory of Persistent Plural Computational Organization**  
Komorebi P. · Operation Komorebi  
Text edition 1.0.0, 8 October 2026  
**Final monograph edition, 15 October 2026**

Open `Machine_Societies_v1.0.0.pdf` for the final 118-page reading edition.
It follows Paper I's typography and layout, with muted plum (`#6B3C63`) for
the machine-theory series. Appendix D contains a clickable index of all 62
theorem and proposition statements. Appendix E states the verification scope.

## What passed

- All 62 statement-and-proof pairs are byte-identical to the original source.
- A targeted self-review covered 15 central results and supporting lemmas.
  No failed implication was identified under their written hypotheses.
- A fresh exact run passed 75 groups and 922,032 assertions.
- The 60 PDF bookmarks and 186 theorem-index links reach the checked targets.
- All 118 pages were rendered. New and changed pages were inspected, and
  unchanged pages were matched to the previously reviewed edition.

`MATHEMATICAL_REVIEW.md` contains the claim cards and dependency review.
`LITERATURE_REVIEW.md` records primary-source checks and retrieval limits.
`RELEASE_LEDGER.json` records the release history and current evidence boundary.
`verification/` contains production, preservation, visual, and computation records.

The other 47 retained proofs were not newly audited in this targeted pass.
Finite checks do not replace general proofs. This edition makes no claim of
independent peer review, proof-assistant verification, an agent deployment,
or closure of the research questions in Section 45.

## Rebuild the PDF

Install Python 3 and XeLaTeX with the packages listed in
`publication/BUILD_README.txt`. From this package directory, run:

```bash
python3 publication/build.py
```

On Windows PowerShell, run `python publication/build.py`.

The editable manuscript and series style are in `publication/`. The new
appendices are `statement_index.tex` and `release_review.tex`. Local fonts,
licenses, vector figures, and original figure generators are included. The
build updates the root PDF, compiler logs, and compiled cross-reference record.
The delivered build ran on Linux. Windows execution was not tested.

## Reproduce the exact reference checks

Python 3.10 or later is sufficient. These commands use the standard library:

```bash
python3 code/demo_commons.py
python3 code/demo_accountability.py
python3 validation/check_finite_models.py
```

Each group in `validation/finite_checks.json` declares its input range.
The quotient experiment covers two specified refinement families, not all
possible refinements. The five-unit and eight-unit examples use different
declared observation and resource contracts.

The delivered replay is separately preserved in `verification/final_computation/`.
Its version 2 manifest pins execution inputs, records actual commands,
resource limits and result hashes, and can be checked with:

```bash
python3 verification/tools/validate_manifest.py verification/final_computation/manifest.json --root .
```

For PDF and source-preservation checks, install PyMuPDF and run:

```bash
python3 verification/verify_monograph.py
```

## Provenance

`source_release/` preserves the complete original first edition, including
its original PDF, code, historical sources, and evidence. Its records describe
their own dates and inputs. Active reference code is copied into `code/`;
the active tests in `validation/` point to the current manuscript and correct
one overly broad coverage description. Mathematical program logic is unchanged.

`SHA256SUMS.txt` inventories the delivered package. Running commands that
regenerate outputs changes those outputs, so a later snapshot mismatch is
expected. The final release has no outstanding editorial or production blocker.
Theoretical and external-model limitations remain as stated in the manuscript.
