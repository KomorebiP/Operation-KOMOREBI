# Machine-Native Reasoning
## Reviewed and expanded continuation

**Author:** Komorebi P.  
**Series:** Realization Calculus  
**Publication state:** Working monograph, not the completed thirty-chapter book.

Read `Machine_Native_Reasoning_Reviewed_Continuation.pdf`. The current manuscript has **74 pages and fifteen numbered chapters**, together with the realization prologue, glossary, verification guide, result map, and sources. It revises the earlier 57-page, twelve-chapter working edition.

### What changed

The composition chapter now proves preservation of complete state, action, report, and label histories, rather than relying only on terminal-state distributions. The stopping argument now treats deadlock, history-dependent strategies, and the command-observation boundary explicitly. Local clarifications in the original core specify missing domains, finite catalogues, positive-weight divisions, and uniqueness only on enabled actions.

Three substantial chapters have been added: transport of safe continuation through exact and conservative quotients, information-preserving representation migration, and finite proof fields with executable closure certificates. Three new mathematical figures have source-bound data and boxed-label fit checks.

### Verification status

All 27 selected core result identities remain. The archived Lean correspondence covers **23/27**, with Core 8.3, 2.4, 2.5, and 3.2 still pending. No new Lean compilation or kernel replay was performed. The pinned runtime was absent, and retrieval failed with a DNS error. Written proofs and passing finite tests are not relabeled as Lean certification.

The original two exact suites were rerun from a freshly extracted, hash-verified source archive and passed all 205,477 assertions in 27 groups. The new and extended finite suites passed separately. Their units and domains are listed in `PROOFREADING_AND_CONTINUATION_REPORT.md`; do not combine them into a theorem count.

### Reproduction

Run integrity verification before modifying or rebuilding the package:

```text
python scripts/verify_package.py
```

Run the exact computations without changing this directory:

```text
python scripts/reproduce.py --mode exact --output ../machine_reasoning_exact_replay
```

Rebuild the PDF in a temporary tree:

```text
python scripts/reproduce.py --mode pdf --output ../machine_reasoning_pdf_rebuild
```

Output directories must be new or empty and outside this package. Exact checks use Python's standard library. PDF building needs `latexmk`, pdfLaTeX, and the packages named in `book.tex`, including NewTX text and mathematics. Figure regeneration additionally needs Matplotlib. Native Windows execution has not been tested in this continuation. Instructions are portable command forms, not a Windows verification claim.

### Contents

- Root `.tex` files are the editable current manuscript. The original core source remains unchanged under `sources/core/`.
- `formal/` contains the current exact Python reference checks. Its name does not mean these Python files are Lean proofs.
- `figures/` contains the mathematical PDF/PNG assets and generating programs.
- `sources/lean15_current/` contains 255 authenticated files from the last accepted Lean archive, including all 64 production source modules, source-facing checks, configurations and selected receipts. The compiler, external dependencies, and full historical archive are not bundled.
- `sources/proof_path/` contains authenticated source passages and their original formal concordance. They are source evidence, not a fresh verification of the rewritten chapter.
- `sources/archives/` preserves the original reviewed-core package for exact regression replay.
- `sources/history/` preserves the complete prior working-package ZIP byte for byte.
- `verification/current_exact_run/` and `verification/current_pdf_run/` contain the present execution records. Earlier records are retained under explicit predecessor locations.
- `editorial/` contains the thirty-chapter plan, source catalogue, correction register and current admission map.

The source catalogue describes the broader research collection. It does **not** mean all 24 specialist manuscripts or all historical archives are included in this compact delivery. The authoritative originals remain separate source packages.

See `PROGRESS_LEDGER.md` for the restart point and `LICENSE_NOTICE.md` for the original-material licensing policy and retained third-party boundary.
