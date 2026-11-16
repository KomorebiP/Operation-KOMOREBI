# Finite sequence-library evidence

Current evidence: `run-014/manifest.json`, status `completed`, with
`run-014/checks.json`. The input contract is `contract.json`. This run replays
the extended finite assertion for the displayed coefficient tables and columns. Earlier runs preserve
the evidence for their recorded source inputs.

The current exact checks cover 2,034 parameter records and all 52,579 stored
terms / index maps. Independent comparisons include 2,880 reciprocal terms,
360 tangent coefficients, 3,328 hypergeometric seed coefficients, 6,336
congruential rational coefficients, 1,920 Appell rational coefficients, 16,032
reduced integer components, 24,024 classical-subsequence terms, and 3,696
subsequence hypergeometric coefficients. These overlapping check counts are not
counts of distinct mathematical results.

The 112 research additions contribute 2,112 ordinary secancy-polynomial
coefficients, 288 theta specializations and 288 theta-polynomial coefficients.
The independent oracle uses powers of 1-D_N and unsigned first-kind Stirling
coefficients for the secancy columns. Theta coefficients use a separate formal
polynomial recurrence for cosh(z)^(-x), followed by signed Euler convolution.
The stored windows retain their original n offsets. The seed hypergeometric
checks extend through n=31 for the new j=0, N=2..12 formulas.

The complete OEIS replay scans 401,422 retained records against all 2,162 local
records. It reproduces 3,658 retained hits and 391,570 observed hit positions,
including repetitive / low-information prefixes. It does not establish
infinite identities, novelty, or pairwise distinctness.

Run `python tools/audit_sequence_library.py --oeis --output RESULT_JSON` to
repeat the checks. The manifest records the bounded-run command, actual input
and result hashes, Python version, dirty source state, resource observations,
and timing. Validate it with the computation-audit skill's
`scripts/validate_manifest.py MANIFEST --root .`.

Frontend evidence is separate: the Node suites test exact query semantics,
palette/state validation and legacy behavior; browser suites exercise the
library and original plotting interfaces at 1440/390/320px, full-snapshot
reference matching and shared-excerpt restoration, scoped saved entries across
collections, four-source exact comparisons, arrow-key navigation, SVG/PNG/CSV
export and sharing, no-JavaScript tables, and enlarged text /
forced colors. These checks are not accessibility certification. The
mathematical proofreading scope is recorded in `PROOFREAD_REVIEW.md`.

The readability browser suite checks green and monochrome schemes, page display
modes, visible text contrast, saved preferences, and record offsets in HTML and
CSV. It also covers printing, no-JavaScript reading, enlarged text, forced colors,
and shared plot colors. All 6,069 existing exact data exports remain unchanged
after the editorial pass. These are local implementation/self-review results;
production delivery checks are separate.

The homepage and navigation open the complete library; the 38 extensible
sequences remain in the curated generator interface. Archive searches share
the same library filters. Search cards retain exact offsets and highlight
matched terms. The site-wide math selector preserves original source text and
synchronizes across pages and tabs. Syntax coverage is recorded in
`math-display-check.json`; integrated responsive behavior is recorded in
`math-display-browser.json`. The checker is repeatable with
`node tools/check_sequence_typesetting.cjs PREVIEW_URL REPORT_JSON` after
building a site and loading its pinned runtime. It tests presentation syntax,
not the truth of formula identities.

The shared math control is constructed once by its module. The 121-chapter
Machine-Native Reasoning reader retains its existing 1,800,000-byte shell
budget; the generated shells occupy 1,751,895 bytes with the shared control.

Study actions use the canonical library and generator routes. The handoff page
retains the original section anchors for saved links and static navigation;
generated-page tests check all links between sequence pages and their targets.

The 139 further records comprise 55 complete coefficient tables (5,083 cells)
and 84 supported Appell columns (2,016 terms). The independent oracle expands
positive block sections and their reciprocal powers over Fraction arithmetic,
compares every coefficient and source map, and checks both products of the
forward/inverse kernels at every stored row/column. The formal-series argument
for inversion is written in docs/SEQUENCE_LIBRARY.md; the finite matrix checks
do not supply that general argument.

The math selector is in the footer. The display pass removes empty-parameter
dash placeholders and uses a hypergeometric argument bar, separates definition
lines, stacks sum constraints, and fixes factorial/power binding. Source text
is retained. Syntax checking compiles 524 representatives of 292 layouts;
6,441 representations are recognized and 60 retain their literal source.
Triangle browser checks cover exact coordinates, restored row windows, row
polynomials, roving keyboard links, coefficient wrapping, no-JavaScript tables,
enlarged text and forced colors. See `triangles-browser.json`.
