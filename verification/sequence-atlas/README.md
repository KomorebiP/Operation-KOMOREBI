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
