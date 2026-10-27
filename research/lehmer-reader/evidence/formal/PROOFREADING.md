# Mathematical proofreading record

Release review: 9 October 2026. Mode: source review with coordinated minimal
corrections as new files appeared, plus author self-review of the new operator
appendix. Substantive mathematical repairs were not attempted.

Status: complete source proofreading of all nineteen authoring TeX inputs,
with final source hashes frozen in `source_review_final.json`. The integrated
visual inspection below is limited to the assigned pages and specified PDF
hash, with final physical pages 39--58 individually reinspected by this reviewer.

## Current coverage

- `paper/main.tex`
- `paper/opening.tex`
- `paper/chapters01_03.tex`
- `paper/chapters04_05.tex`
- `paper/chapters06_07.tex`
- `paper/chapters08_10.tex`
- `paper/chapters11_12.tex`
- `paper/chapters13_14.tex`
- `paper/chapters15_16.tex`
- `paper/chapters17_18.tex`
- `paper/chapters19_21.tex`
- `paper/chapter22.tex`
- `paper/appendices.tex`
- `paper/appendix_operator.tex`
- `paper/appendix_workbook.tex`
- `paper/bibliography.tex`
- `visual/main.tex`
- `shared/preamble.tex`
- `shared/guide_preamble.tex`

All nineteen authoring TeX inputs were read in full. The seven earlier chapter
files changed by figure and notation additions were reread in full at the
final source pass. The review checked prose integration, notation,
domains and boundary cases, displayed equations, theorem-to-proof consistency,
local labels and macro meanings. In the current scope the coefficient engines,
parity derivation, p^6 criterion, prime reduction, differential-ring extraction
and Catalan moment rows are consistent. Review also covers the theta descent,
null and sign certificates, threshold and content proofs, refinement exact
sequence, primitive arithmetic, nonhomogeneous conservation, interpolation,
actual joint-image congruences, filtered module, synthetic countermodel and
closeout implications. The whole guide source was read, then its final
clarifications were reread in context.

Routine edits: restored twelve omitted backslashes in `quad`/`qquad` spacing
commands in `paper/chapters08_10.tex`, at the valence coefficient range, first
shell power sums, correction-degree counts and positive-dual equations. The
intended spacing was uniquely forced. No equation, operator or proof was
otherwise changed. A phrase in Chapter 12 was changed from “corrected orbit
total” to “weighted correction sum”, accurately describing the existing
formula involving Q rather than the full correction F.

Mathematical-token changes performed by the proofreader: added the uniquely
required range `m >= 1` to Chapter 21's formula
`R_f(q^(2m)) = (-1)^m q^(11m-1)(q+1)`, and stated `R_f(1)=1` separately. At
`m=0` the displayed formula would be false. The source model proof supplies
exactly this range. In the new operator appendix's self-review, the radial
Laplacian display was explicitly restricted to `j >= 1`, with `j=0` separately
zero, avoiding an undefined negative radial power at the origin.

An author-coordinated hypothesis clarification in the visual guide adds the
existing valuation check's candidate domain, `p != ell` and `ell | (p+1)`, to
its first-failure statement. Without that domain the claimed first failures
would be false. The guide author also changed a synthetic-model strapline to
“No actual tau zero established”, avoiding an unsupported assertion that
the original tau coefficient is nonzero. The guide's exact q congruences
were restored through the computation review. The workbook now explicitly
defines `s_f` as its sixteen-entry original fine-mass vector. Chapter 22 now
requires a proved comparison identifying the normalized local Frobenius trace
with `tau(p)` before claiming that an actual global identification would give
a zero. This states the exact intended extra premise rather than silently
using an unramified arithmetic-Frobenius formula at the auxiliary prime p.

The final owner-coordinated boundary correction in Chapter 16 now states
`m >= 1` for the zero-parameter even block, `m >= 0` for the odd block, and
`R(1)=1` separately. Chapter 9's operator formula now explicitly states
`m >= 2`. The appendix recurrence states `r >= 2`, and its trace-normalization
contract explicitly names the `t=0` half-weight. The visual-review wording
now says individual review records, avoiding a false human-review claim.
These final changes were reread in context. The changed Theorem 3.1 display,
shortened Chapter 5 tail, bounded irreducibility paragraph relocation,
low-degree section relocation, Chapter 22 table/tail and bibliography
spacing were also checked. No unresolved objective proofreading issue
remains. External
source authentication is owned by the literature audit and is not claimed by
this proofreading pass.

Root's final integrated build produced 103 physical paper pages and 32 guide
pages. The proofreader read and scanned both compiler logs. They show no
overfull, undefined-reference, missing-character, PDF-string or rerun warning.
`build_log_review.json` pins these logs and PDFs. The final paper hash is
`67489fe4cba46d9a1f09010576b2dba182a29c1a8b44803f60e98068af6241de`.
The unchanged guide hash is
`d6e185b0e83e3390cc8627e44ec9a330781dfd9b285b873f04db19bee1ffb165`.
Final paper pages 39--58 were individually reinspected on this exact snapshot.
The final record replaces the preliminary 108-page snapshot inspection, which
is retained separately as `preliminary_paper_formal.json`. The six-page operator appendix compiled separately and every page
was inspected at 150 dpi. Its final range clarification changed only page 4,
which was reinspected. Full RGB comparison confirmed that pages 1,2,3,5,6
were unchanged. Standalone external chapter references are intentionally
unavailable and must resolve in the integrated book.

`python3 evidence/formal/scan_tex.py` checks current authoring inputs for
unexpected control bytes and likely omitted backslashes in quad/qquad
spacing commands. The nineteen-file scan result is PASS, with no such issue.
`proofreading_progress.json` records the reviewed source hashes. Later edits
or added files require further review.

## Integrated page inspection

The proofreader individually viewed every physical page 39 through 58 of
the final immutable 103-page paper snapshot at original resolution, using
`view_image` on the 150 dpi PNGs made by system Poppler. The final PDF hash is
`67489fe4cba46d9a1f09010576b2dba182a29c1a8b44803f60e98068af6241de`.
The record is `evidence/layout/manual_paper_formal.json`. This is a fresh
final-snapshot inspection. No clipping, overlaps, broken symbols, illegible
table entries or misplaced equation numbers were found. Equations, tables
and captions agreed with the reviewed source. Chapter-ending physical
pages 41, 49 and 53 retain considerable whitespace at conventional chapter
boundaries. This remains a nonblocking density observation, with no source
alteration requested.

The inspection was performed by an agent, not a human referee. It claims
only those twenty pages. The prior six-page standalone operator inspection
is a separate author self-review and is not promoted to a complete integrated
book inspection.

## Validation commands and limits

Commands actually used in this proofreading work include:

- `python3 evidence/formal/scan_tex.py` from the project root, producing the
  nineteen-input `tex_token_scan.json`.
- `pdflatex -interaction=nonstopmode -halt-on-error operator_check.tex` in
  the temporary standalone operator validation folder, followed by system
  Poppler rendering at 150 dpi.
- `/usr/bin/pdftoppm -r 150 -png operator_check.pdf page` for that temporary
  six-page check, followed by individual page views.
- Hash comparisons against `proofreading_progress.json` to find changed
  source inputs. Every changed input was reread before its new hash was
  recorded.
- `rg` scans and full reads of the integrated compiler log and displayed
  formulas, including valuation domains and scalar/operator notation.

The final build entry point is `python3 build.py --figures`. Root owns that
integrated execution and its release checks. The source byte/token scan does
not parse TeX or prove mathematical statements. The mathematical source pass
is a conservative proofreading pass, accompanied by the separately recorded
local derivation reconstruction and definition audit. The literature audit,
critical proof audit and computation audit remain distinct evidence.

Final nineteen-source combined pin: `942865f36fa0c40c09654e7b36385714f58db92eeb43dd5528f5d7264dcd3202`. This pin is defined by the
ordered path, NUL separator, individual SHA-256 and newline for every input.

The final five redundant adverb deletions were reread in context. They changed
no mathematical premise, equation, proof or conclusion. The source and compiler
log pins above now match the frozen final 103-page paper.
