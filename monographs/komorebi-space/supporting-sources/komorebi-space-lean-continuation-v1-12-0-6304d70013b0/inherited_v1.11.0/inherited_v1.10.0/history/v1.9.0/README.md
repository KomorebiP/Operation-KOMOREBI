# Komorebi Space — revised full monograph v1.9.0

This edition updates the complete monograph with the accepted v1.8.0 formal coverage and a full mathematical proofreading pass. It preserves the expanded written proofs and records every mathematical wording or hypothesis correction separately from copyediting.

## Read and review

- `publication/Komorebi_Space_Monograph_v1.9.0.pdf`: the current full monograph.
- `reviews/PROOFREADING_REPORT.md`: scope, significant corrections, validation, and limitations.
- `source/`: current monograph LaTeX, diagrams, and plot assets.
- `reviews/` and `audit/`: chapter reviews, draft findings, build logs, final review coverage, source hashes, and exact accepted publication identity.
- `PROGRESS_LEDGER.md` and `.json`: completed work and the next restart point.
- `formal/`: the unchanged accepted v1.8.0 combined formal source snapshot.
- `continuation/`: unchanged v1.8.0 compiler/audit evidence and continuation guide.
- `inherited_v1.7.0/`: unchanged historical reader set, source, examples, and evidence. Its 43-page visual guide and 36-page Lean guide are retained as historical companions; they have not been updated or proofread as new v1.9.0 editions.
- `examples/`: unchanged example scripts, copied for the paths cited in the current monograph.
- `history/v1.8.0/`: the predecessor release ledger and verification summary.

Six WR groups have complete formal counterparts, eight remain written-only, and two have partial formal coverage with written limiting conclusions. This revision does not add a Lean compilation or rerun the historical finite suites. Proofreading and focused correction of identified issues do not constitute a new global referee audit of every proof.

## Rebuild the monograph

Install a LaTeX distribution with pdfLaTeX and the packages named in `source/preamble.tex`; Python 3 is required for the orchestration scripts. From this package root:

```sh
python3 scripts/check_manuscript.py
python3 scripts/build_monograph.py local_rebuild
```

Use a fresh build label each time. The build makes three passes, records source hashes, and rejects unresolved references, overfull boxes, missing glyphs, and designated font/package warnings. Underfull-line warnings require visual review. The rebuilt file is `publication/Komorebi_Space_Monograph.pdf`. TeX PDF metadata can vary, so bitwise identity with the delivered PDF is not promised by a rebuild.

All mathematical figures are TikZ diagrams or plots of explicit formulas. The changed budget plot can be rebuilt with `python3 scripts/build_budget_figure.py` (NumPy and Matplotlib required); the other historical plotting sources are preserved in `inherited_v1.7.0/checks/`. For optional page rendering, `scripts/render_review.py` uses PyMuPDF and `pdffonts`.

## Formal evidence and trust boundary

The accepted predecessor compiled a clean 144-target baseline and then an incremental four-target enlargement, producing 144 production modules plus three roots and auditing 4,872 declarations. Its twenty control files met their intended outcomes. See `continuation/FORMAL_COVERAGE.json`, `continuation/VERIFICATION_SUMMARY.json`, and the accepted run receipts for precise clauses and source identities.

Replay instructions remain in `history/v1.8.0/README.md`. The portable Lean runtime is supplied separately and is not embedded here. Lean's compiler/kernel, standard axioms, and pinned external dependency cache remain trusted. No independent kernel check, full dependency-source rebuild, native Windows validation, universal Python refinement proof, or automatic certification of all prose is claimed.

`SHA256SUMS.txt` hashes every package payload file except itself. The historical trees are copied byte for byte. Draft reports retain their draft-specific findings and are superseded, for final pagination only, by the final visual review record.
