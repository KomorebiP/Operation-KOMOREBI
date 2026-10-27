# Proof Path Theory — monograph edition 1.6.0

**Komorebi P. · Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

## Read the book

`docs/Proof_Path_Theory.pdf` is the current **62-page monograph**. Its source is
`docs/Proof_Path_Theory.tex`. The edition retains five illustrated part openers,
**22 vector figures**, and four worked visual studies. The eight-page
`docs/Proof_Path_Theory_Visual_Sampler.pdf` is extracted from this same PDF.

This pass applies the refinement recovery condition, fixes the logical context
of endpoint equivalence, and separates serialization loss from hashing. It also
repairs an actual tuple-encoding defect in the provenance helper. The visual
design and all finite diagram data are preserved.

## Versions and evidence

Publication **1.6.0**, Python distribution **1.4.0**, and inherited formal evidence
**1.2.0** are distinct versions. The software minor release changes provenance
digests intentionally. **Read `docs/PROVENANCE_FORMAT.md` before migrating old
digests.** Certificate, realization, and review algorithms are unchanged.

`PROOFREADING_REPORT.md` records corrections and test scope.
`data/publication_verification_1.6.0.json` records the current publication audit.
`evidence/finalization_1.6.0/` contains fresh test, build, installation, and review
records. `PROGRESS_LEDGER_v1.6.0.md` gives the completed work and restart point.
The 33 result-group identifiers are retained. Earlier reports remain historical.

**Lean was not rerun.** The unchanged formal sources retain their historical
checks. This is not a claim that the whole monograph or Python implementation is
formally verified. The social models remain conditional models, not measured
facts about mathematical communities.

## Reproduce

Before changing anything in an extracted release, verify its manifest:

```bash
python scripts/check_manifest.py
```

Install the package and optional publication dependencies while they are
available. The checks themselves need no model API.

```bash
python -m pip install -e ".[release]" --no-build-isolation
python -m pytest -o addopts='' -q
python scripts/deep_validation.py
python scripts/verify_bridge.py
python scripts/verify_publication_edition.py
```

The old `verify_visual_edition.py` and `verify_editorial.py` names delegate to the
current publication audit. They do not substitute for the test commands above.

Figures require the installed Lato font. No font files are distributed. The
manuscript requires pdfLaTeX, NewTX, Source Sans Pro, TikZ, upquote, and the other
packages named in its preamble. Versions used in this run are recorded in
`evidence/finalization_1.6.0/environment.json`.

```bash
python scripts/design_figures.py
cd docs
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
```

Rebuilding a PDF or rewriting a report can change its hash. The shipped manifest
certifies the delivered bytes, not the bytes after a new build. Validate the
manifest before running those commands. Source and figure changes have their own
explicit identity checks.

For PowerShell, use the extraction block in Appendix C, then
`scripts/run_all.ps1` after dependencies are installed. The PowerShell script
was not executed in this Linux environment. Its commands were checked in source
and copied-text form. Python commands were executed here.

## Optional full formal replay

The pinned Lean runtime is not bundled. With it available, use a fresh copy:

```bash
python scripts/verify_lean.py --runtime /path/to/portable-kit
```

`scripts/verify_release.py` additionally performs a full technical replay and
requires the same runtime. It writes new formal evidence and can rebuild the
Python distributions, so do not run it over the only historical copy. A later
formal run changes evidence hashes and needs its own versioned audit. This
edition does not claim that command was executed.

## Rights

The license notice remains unchanged. This edition does not choose a
redistribution license on the author's behalf. Mathematical correctness,
software execution, priority, independent review, and empirical validation
remain separate questions.
