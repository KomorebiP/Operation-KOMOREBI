# Komorebi Special Functions: consolidated working edition 0.1

This package consolidates Projector Generated Special Functions I–VIII into three mathematical strands, with a shared manuscript, selected visual atlas, explicit correction register, and a complete reader preserving all eight papers.

Start with `Komorebi_Special_Functions_Consolidated_Manuscript_v0.1.pdf` (38 pages). The complete reader (469 pages) appends the eight source papers with their page content preserved and has bookmarks for each volume. Internal destinations are namespaced so later papers' contents links remain within their own paper. This is a working consolidation, not a claim of an exhaustive new proof audit or completed Lean formalization.

## Contents

- `manuscript/`: the unified LaTeX manuscript, its selected source figures, and compilation instructions.
- `original_releases/`: eight unchanged source release ZIPs and the earlier special-function registry ZIP.
- `evidence/`: source/archive hashes, all 173 special-function claim records, review notes, fresh pytest evidence, formalization scope, proof audits, and final quality checks.
- `reproduce_tests.py`: a portable runner that extracts the eight releases into a temporary directory and runs their independent test suites.
- `reproduce_reader.py`: combines a built manuscript with the eight archived PDFs and creates source-volume bookmarks.

## Verification

The present rerun passed 148/148 pytest cases across all eight volumes, with no failures, errors, or skips. This includes recomputed assertions and archival-file checks. Archived built-in ledgers record 243/243 checks, but only 64 built-in checks were recomputed through pytest (Papers I and VII). The other built-in totals remain historical evidence.

The retrieved special-function claim ledger contains 125 theorem/proposition/lemma/corollary records among 173 source objects. These are source claims, not 125 distinct results or kernel-checked theorems. One coefficient-refinement theorem is present in the retrieved Lean special-function tranche; full analytic formalization and a successful whole-corpus kernel build were not established by the retrieved evidence.

## Rebuild

Install the dependencies listed in `requirements.txt`. From `manuscript/`, run `pdflatex -interaction=nonstopmode -halt-on-error main.tex` three times. Copy `main.pdf` to the package root under the consolidated manuscript filename. Then run `python reproduce_reader.py` from the package root.

Run `python reproduce_tests.py` from the package root to rerun all eight independent suites. Original release bytes are never modified. Reports are written to a new `rerun_evidence/` directory.

Run `python evidence/exact_correction_witnesses.py` from the package root to repeat the seven bounded exact witnesses. This refreshes their result JSON; the accompanying audit manifest records the consolidation-time run.

The correction register governs the known source issues. In particular, positive spectral weights are not positive complex residues, Gaussian quadrature nodes need not be original spectral atoms, and a telescoping pentagon by itself does not validate the representation or projector. The q-Racah scalar-to-matrix normalization remains a comparison task, not a completed identification in this edition.
