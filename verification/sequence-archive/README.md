# Recovered archive integration: finite verification

`run-006/manifest.json` is the current source replay receipt. Its run status is
`completed`; the result reports `passed`. Run 005 describes the published import
checkpoint; runs 001-004 are retained development receipts. Plot-window and
appearance evidence is recorded separately in `../sequence-plots/`.

The exact replay compares the entire recovered registry (90 records, 5,487
integer terms) with the preserved generator. All 90 indexed text outputs
reproduce the original b-file SHA-256 checksums. It separately checks 162
historical numeric control terms; the preserved generator's optional sibling
CSV check reports zero because this source subset has a different layout.
The portable source launcher is also executed into a temporary directory;
its generated registry and all 90 b-file hashes must match the archive.

The generator's independent controls cover 84 rational-series values, 28
log-derivative values, 3 binomial round trips, 6 classical anchor families,
3,105 Pascal valuation comparisons, 32 subset enumerations, 102 digit-sum
enumerations, 64 formal ladder recurrence checks, and the 24-state Clifford
action. These are finite implementation checks. They do not establish novelty,
infinite identities, research conjectures, or physical circuit realization.

Local checks passed: 10 Python tests and 37 Node tests. Browser suites cover
the recovered library, existing directory/connections, and existing atlas
flows at 1440, 390, and 320 pixels. They include exact large-integer inspection,
offsets 0/1/2, all five archive views, invalid-input recovery, keyboard point
navigation, exports, shared URLs, clipboard denial, no-JavaScript reading,
forced colors and enlarged text. All 114 existing KSEQ exact exports remain
byte-identical. These automated checks and visual self-review are not an
accessibility certification or screen-reader user study.

Final visual review corrected undersized mobile chart labels, excluded
reading-workspace actions from the new tool pages, and corrected UTF-8 label
encoding. One initial atlas browser run timed out while other browser suites
were running; the unchanged atlas suite passed on a separate retry. No failure
was treated as a passing run.
Testing the actual source download caught the archived generator's Windows
newline assertion failure. The added launcher writes explicit UTF-8/LF output;
the preserved generator bytes were not changed.

Mathematical prose self-review covered the added page templates and documentation.
The source formulas and numerical records retain their recovered bytes. The
new flattened-triangle view uses j for the flat index and (n,k) for row/column;
ordinary records use n. No original mathematical assertion was rewritten.

Browser reports and screenshots are in the task workspace's
`sequence-archive-review/` folder. Deployment and live-revision verification
are separate publication steps.
