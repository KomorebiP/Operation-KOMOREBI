# Finite sequence-library evidence

Current evidence: `run-019/manifest.json` and `run-021/manifest.json`, both
completed. The first uses `contract.json` and checks all parameter families and
OEIS replay. The second uses `connections-contract.json` and checks record
definitions, archive source replay and exact JavaScript transfers. Each run
retains its result in `checks.json`. Earlier runs preserve evidence for their
recorded inputs; runs 017/018 preceded final accessibility and source-label edits. Run 020
used the unchanged browser core with Windows CRLF bytes; run 021 replays it with
the committed LF bytes so that the current receipt matches Git exactly.

The current exact checks cover 2,164 parameter records and all 55,939 stored
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

The complete OEIS replay scans 401,422 retained records against all 2,292 local
records. It reproduces 4,841 retained hits and 1,275,413 observed hit positions,
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
6,441 complete representations are recognized. Mixed definitions separate prose
from independently recognized equations; 11 such equation parts also compiled.
Unrecognized notation and the original Plain text remain available.
Triangle browser checks cover exact coordinates, restored row windows, row
polynomials, roving keyboard links, coefficient wrapping, no-JavaScript tables,
enlarged text and forced colors. See `triangles-browser.json`.

The coefficient explorer partitions all 5,083 cells of the 55 tables by rows,
columns and right-edge diagonals. Independent coordinate loops check all three
partitions (15,249 cell visits) and exact signed residues. Its tests also cover
source-degree maps, large-integer CSV/copy/search, shared options, invalid input,
all-zero plots and UTF-8 punctuation. The 70 Node tests and 15 Python tests pass.
The explorer browser report is `table-browser.json`; it checks 1440/390/320px,
PNG/SVG/CSV downloads, keyboard navigation, no-JavaScript reading, enlarged text,
forced colors and unavailable storage. All 6,486 current exact data exports
remain byte-identical. These are implementation checks, not a novelty review or
accessibility certification.

Run-015 is retained as the intermediate display-source capture. Run-016 pins
the corrected UTF-8 source and is the current arithmetic evidence. The new
selection plots also retain black text on white when printing a dark page.

The recurrence expansion adds 130 records and 3,360 stored values. Its 120
weighted k-step families are checked at n=0..95 against integer convolution
powers, finite binomial sums and exact finite hypergeometric sums (11,520
coefficients for each comparison). The pinned maintained k-bonacci source
is replayed for 1,440 order/index pairs. Hypergeometric endpoint controls reject
parameter cancellation that would change the explicitly truncated definition.

The connection audit covers 2,292 definitions and 63,858 stored integers. It
replays all 90 archive records (5,487 values), checks 1,224 typed relations and
10,571 available overlap values, and compares 2,236 scalar transfers (26,820
coefficients) to a separate Fraction geometric-reciprocal oracle. The 56
coefficient tables are explicitly excluded from scalar convolution. All scalar
windows in this snapshot have usable nonzero anchors; zero-window rejection is
covered separately by the Node boundary tests. Transfer coefficients, shifts,
inverse recovery, integrality flags and kernel products are exact. These are
finite implementation checks, not predictions or universal recurrence claims.

The focused mathematical self-review and full family derivations are in
research/sequence-connections/AUDIT.md and IDENTITIES.md. Historical novelty
and whole-manuscript independent review remain outside the completed scope.

The expansion passes 75 Node tests and 15 Python tests. Browser reports
connections-browser.json, connections-unified-browser.json and
connections-readability-browser.json cover 1440/390/320px, exact transfer and
inverse, late zero seeds, matrix headers, invalid-input recovery, share and CSV,
citations, explicit finite formula notes, unchanged global display controls,
no-JavaScript reading, forced colors, 200% text, print and clipboard fallback.
They are local implementation checks, not accessibility certification.
All 6,486 pre-expansion exact CSV/JSON/TXT exports are byte-identical.

## Generalized-family studio

The current receipt for the generalized engines and source index is run-024,
under families-contract.json. Its hashes validate against the current inputs.
Runs 022 and 023 retain intermediate source/wording snapshots and are historical;
earlier baseline receipts also retain their original inputs rather than claiming
to cover subsequently changed library builders.

Run-024 compares 1,486 exact family cases and 31,876 values with independent
rational-series, convolution, Bell-column and classical constructions. It also
checks 19,200 finite hypergeometric values, 802 worked alternatives, 274 modular
searches (22,127 states and 218 certificates), and 216 scalar transfer
compositions (2,592 coefficients) against an independent Fraction quotient
oracle. Four identification cases each scan all 2,236 local scalar records.
The 22 definitions, 11 source bindings and 1,231 typed relations are checked.
The source-defined analytic families are outside the numerical engine audit.

Local checks pass 85 Node tests and 17 targeted Python tests; the separate
pinned-library Python integration suite requires the library installed by CI.
The downloadable source ZIP reproduces all 2,164 parameter records, their 55,939
stored integers and 6,838 formula representations. All 6,876 pre-existing
per-record CSV/JSON/TXT exports remain byte-identical.

The research-browser report covers 1440/390/320px family/paper search, exact
controls and worked examples, keyboard plot inspection, invalid-input recovery,
directed paths and composition exports, local transformed identification,
modular cycles and capped searches, notebook validation/import/export/sharing,
explicit reference loading, no-JavaScript definitions, denied storage/clipboard,
forced colors, enlarged text and print. It includes a full 401,422-record OEIS
identification run. Existing unified-search, readability and transfer browser
suites also pass. These are automated implementation checks, not certification
or physical-device user testing.
