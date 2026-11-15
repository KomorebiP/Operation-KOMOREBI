# Sequence atlas finite validation

The contract separates the finite implementation assertions from sequence
novelty, global identities, periodicity, and the linked manuscripts’ proof
status. `run-002` is the completed bounded arithmetic run. Its manifest
records exact working-tree input bytes, software versions, command, limits,
and result hashes. Git line-ending conversion on another platform can
change byte hashes without changing the source text; regenerate a run for
the local checkout rather than silently rewriting a retained manifest.

`run-001` records a failed audit wrapper: Python’s legacy Windows output
encoding could not print the Unicode Node test reporter. The Python checks
had passed, but that run produced no result file and supplies no completed
audit evidence. The wrapper now explicitly writes UTF-8.

The independent reciprocal oracle uses rational ordinary power-series
inversion through 16 compressed terms for N=2,…,8 and r=1,…,3 (336
coefficients). Bell and Fubini terms are checked against binomial
recurrences through index 31. JavaScript BigInt generation is compared
with all 64 stored terms of each of the 26 entries (1,664 terms).
Fixtures cover negative and large residues, exact fractions and undefined
ratios, contiguous matching, snapshot positions, and bounded period suggestions.

The browser checks are separate from these mathematical assertions:

```text
node tools/test_sequence_atlas_browser.cjs BASE_URL OUTPUT_DIRECTORY
```

They require Playwright and installed Microsoft Edge, and exercise desktop,
390px and 320px layouts, the five plot views, parameter changes, comparison,
search, custom exact integers, keyboard point inspection, animation, actual
CSV/SVG/PNG downloads, copied-link restoration, entry pages, and no-JavaScript
reading. The screenshots and browser report are retained with the task’s
local review artifacts. These checks are not user testing or accessibility
certification.

Self-review covered the added atlas definitions, indexing, recurrence labels,
source routes, and scope language. No predecessor mathematical text was changed.

## Refinement run 003

`refinement-contract.json` and `run-003` record the completed refinement
checks: five Python tests and fifteen Node tests. They retain the original
26 identifiers and all 1,664 stored integer terms. The existing dated OEIS
comparison is reused only after its catalogue-term signature is checked;
this refinement does not claim a fresh corpus scan or a novelty result.

The new finite fixtures cover second differences of squares through index
63, a signed second-difference example, and successive modular coordinates
containing a negative integer and an integer above 2^53. Search checks cover
field combinations, phrases, exclusions, alternatives, wildcard boundaries,
match offsets, identifier normalization, sorting, search links, and saved-list
validation. The declared atlas source surface is hashed before and after;
shared reader modules are pinned by the recorded repository commit rather
than exhaustively included in the hash list.

The separate updated Edge suite exercises six plot views at 1440px, 390px,
and 320px; one-stop graph keyboard navigation, touch-sized inspection
buttons, window controls, saved-entry persistence, query error recovery,
short spoken labels with complete exact data retained, copied search/view
links, and CSV/SVG/PNG/view-JSON downloads. It also checks indexed-text and
entry-JSON files, related-entry navigation, no-JavaScript reading, 200% text
at 320px with system high-contrast colors and reduced motion, and browser
storage denial. These are implementation and browser checks, without
screen-reader user testing or accessibility certification.

`run-004` repeats the same finite contract after changing the global search
shortcut to Ctrl+/ (Command+/ on Mac). The separate Edge regression verifies
that plain / leaves a result link focused and can be typed normally in search,
while Ctrl+/ focuses search outside an input. This avoids a bare character
shortcut; see the W3C explanation of
[character key shortcuts](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html).

## Discovery run 005

`discovery-contract.json` and `run-005` record eight Python tests and
twenty-two Node tests for 38 catalogue entries. A fixed signature preserves
the original 26 identifiers and 1,664 terms. Twelve classical entries are
appended. Each added declared OEIS reference matches twelve starting terms
in the retained export. The same two export files were compared again over
the expanded catalogue (401,397 records; 6,470 finite hit positions). The
original retrieval time and file hashes are preserved; comparison time is
separate. This is not a fresh bulk download or an identity/novelty result.

Self-contained Python entry programs reproduce sixteen terms for all 38
entries. New controls compare Catalan convolution with its closed form,
central binomial coefficients with Vandermonde sums, and partition coin-change
with the browser pentagonal recurrence. The binomial transform and inverse
round-trip 64 signed integers containing 81-digit magnitudes. Discovery tests
check full usable-input matching, sign preservation, both index origins,
omitted initial terms, grouped repeated positions and redundant-result removal.
Computed cross-references are explicitly twelve-term checks, not proofs.

The separate Edge suite covers discovery-to-plot actions, copied/restored
discovery links, JSON download, random entry navigation, formula/program
copying, and previous atlas functions at 1440px, 390px and 320px. It also checks
the discovery layout with 200% text, forced colors and reduced motion, plus
clipboard and storage denial fallbacks. These are implementation checks,
without screen-reader user testing or accessibility certification. Self-review
covered the added definitions, displayed recurrences, worked examples,
compressed indices, transform signs and finite-scope wording.
