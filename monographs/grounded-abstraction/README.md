# Grounded Abstraction
## Identifiability, Representation Change, and the Limits of Learning

**Komorebi P. · Operation Komorebi · First consolidated edition v1.0.0 · 9 October 2026**

A 43-page, six-part theoretical manuscript with twenty self-contained formal statements and prose proofs. Small exact constructions support the exposition. There is no agent-training campaign or large-scale implementation in this release.

The connected question is what evidence can justify when a complete underlying system remains unknown. The exact theory treats accessible evidence, future correction memory, partially calibrated operators, common observable behavior, and initialization of a minimum linear predictor. The quantitative extension adds finite retained probability fields, repeated noisy correction, hidden-to-visible leakage, and one posterior decision certificate that uses both error bounds.

## Reading map

- `Grounded_Abstraction_v1.0.0.pdf`: canonical reading manuscript.
- `Grounded_Abstraction_v1.0.0.tex`: editable source.
- `STATEMENT_INDEX.json`: all twenty statement numbers and source locations.
- `ASSUMPTION_REVIEW.md`: internal review of assumptions, proofs and limits.
- `CLAIM_DEPENDENCIES.json`: an authored dependency guide, not an automatically proved dependency extractor.
- `SOURCE_MAP.md`: reference-by-reference review depth and access failures.
- `REVIEW_NOTES.md`: exact verification and publication boundary.
- `FIRST_EDITION_PLAN.md`: completed closeout scope, with deferred work explicitly separated.
- `NEXT_THEORY.md`: bounded theoretical extensions rather than a broad implementation roadmap.

All sixteen v0.5 formal statement/proof pairs are preserved verbatim. Four inherited reference and figure programs are byte-identical. The original v0.5 source ZIP is retained intact in `history/`, and a selected provenance extract is under `history/v0.5.0/`. Selected v0.1 history is also retained. Historical receipts remain historical, not fresh evidence for changed source. Verify a historical release inside its intact archive rather than treating a selected history directory as its complete payload.

## Reproduction

Verify the frozen snapshot **before** replacing timed records:

```text
python code/verify_release.py
```

The three exact suites use only Python's standard library:

```text
python code/run_checks.py
python code/verify_release.py --receipt-only
```

They execute 28 groups and 70,241 assertions using integers, finite sets, exact rational arithmetic and small F2 vector spaces. Each suite and the preservation audit has a twenty-second subprocess wall limit. The manifest pins source, programs, nine vector figure PDFs and the intact predecessor archive before and after the run. This is a project-local execution record, not a proof kernel or authenticated external attestation.

With a suitable TeX installation, rebuild the reading document and audit it:

```text
bash build.sh
python code/audit_manuscript.py
python code/pdf_preflight.py
```

The preflight requires PyMuPDF and Poppler's `pdffonts`. `build.ps1` is supplied but was not run on Windows. The working environment used pdfLaTeX and the shipped vector figures. To perform the full same-environment clean-copy comparison:

```text
python code/check_fresh_rebuild.py
```

The clean check deletes the copied PDF/build directory, rebuilds, reruns all mathematical checks, audits the source and PDF, and verifies the newly generated local receipt. It compares every page's extracted text and ten scientific/index files, ignoring only the three explicitly named suite runtime fields. It does not require binary PDF identity or claim cross-platform reproduction.

## Figure regeneration

The nine analytical figures are supplied as PDF, SVG and PNG. The first seven are unchanged assets generated in the predecessor work. The two first-edition charts were generated from the new exact illustration data using Python/Matplotlib.

```text
python -m pip install -r requirements-figures.txt
python code/run_checks.py
python code/make_figures.py
python code/make_observable_figures.py
python code/make_quantitative_figures.py
```

Regenerating figures changes pinned inputs, so rerun `python code/run_checks.py` afterward before checking the local receipt. Rebuild the PDF to use changed figure assets. No generated pictorial imagery, standalone font files, third-party full papers or private conversation transcripts are distributed.

## Worked quantitative example

Three noisy sensor-reference reports update an eight-world model while an irrelevant-to-the-reports bit remains unidentified. Four count fields with denominator 65,536 use 68 literal retained bits; this does not count program/model storage or temporary arithmetic. The same model's later response has a separately bounded hidden-return error. Combining the two proved allowances yields a certified posterior-risk upper bound of 12793/262144 (about 0.04880), below the stated threshold 3/50. The actual selected decision is checked to be the unique posterior minimizer in that finite example. This is a conditional mathematical result, not a real-world safety or confidence claim.

## Status

Version 1.0 freezes a theoretical and editorial scope. It is internally reviewed work, not independent peer review, a universal grounding test, Lean verification, or journal acceptance. Supplied likelihoods, candidate systems, arithmetic and model-accuracy assumptions remain inputs. Finite checks illustrate the implemented domains and do not prove every quantified theorem. Rerunning programs intentionally replaces timed receipts and makes the original frozen snapshot inventory stale.
