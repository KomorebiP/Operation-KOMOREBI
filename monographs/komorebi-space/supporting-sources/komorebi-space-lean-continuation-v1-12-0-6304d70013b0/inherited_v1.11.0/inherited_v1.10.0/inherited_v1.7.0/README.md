# Komorebi Space — proof-expanded edition 1.7.0

**Coherent realizations, obstructions, and descent**  
Komorebi P. · Operation Komorebi · 12 October 2026

The main monograph is in `publication/Komorebi_Space_Monograph.pdf`. The visual and Lean/evidence companions are in the same directory. This edition expands the arguments already in the book rather than adding another set of research topics.

The main reader has **161 pages**. The visual guide has **43 pages and forty plates**, and the Lean/evidence guide has **36 pages**. The original body typography is retained. Editable LaTeX is under `source/`; figure sources, exact programs, checks and historical evidence are included.

## The proof expansion

**67 existing proof blocks** are expanded: fifty KS results, all sixteen WR theorem groups, and the weak-subsequence lemma. The principal statements and stable identifiers are unchanged. Five classical background lemmas are proved in a new analytic appendix. See `PROOF_EXPANSION_MAP.md` for a result-by-result account.

The additions expose intermediate constructions and choices, noncommutative multiplication order, kernel and range hypotheses, the distinction between weak and strong limits, and the tail estimates behind the infinite budget asymptotic. They are mathematical exposition, not additional Lean execution.

## Evidence

The canonical formal baseline remains v1.2.0. The separate regularization extension remains the accepted v1.6.0 focused closure. All **169 files** in those two source trees are unchanged. **No new Lean compilation or axiom audit was run in v1.7.0.** The retained source catalogue contains **80 KS items and 211 references**. The WR catalogue remains sixteen groups with four complete focused counterparts, two partially formal groups, and ten written-only groups.

Seven exact finite suites were rerun with **197,482 assertions**. These finite tests do not validate arbitrary infinite-dimensional statements or mechanically verify the prose. The proof-edit audit checks statement/label preservation and text hashes. Its scope is explicitly editorial.

Start with `PROGRESS_LEDGER.md`, `REVIEW_NOTES.md`, `BUILD.md`, and `FORMAL_SCOPE_REVIEW.md`. The final publication record is `audit/proof_detail/release.json`; the accepted build is `audit/proof_detail/proof_build02.json`.

## Reproduce

From this directory, run:

```sh
python3 checks/verify_payload.py
bash build.sh
python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
```

Inspect the rendered pages. A rendering exit code is not a visual review. `BUILD.md` describes both historical formal replay procedures. The portable runtime and standalone font files are not distributed in this package.
