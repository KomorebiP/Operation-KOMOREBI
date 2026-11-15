# Unified sequence and formula library

`sequence-library.html` searches 2,023 local records: the original 38 KSEQ
entries, 90 recovered KOM records, and 1,895 KFOR parameter records. It indexes
6,095 recorded representations, including term formulas, finite sums,
recurrences, generating functions and hypergeometric coefficient formulas.
These counts describe records and representations, not distinct infinite
sequences or new discoveries.

`tools/sequence_formula_catalogue.py` defines the finite parameter grids. Each
parameter record stores 24 terms at its stated offset and an explicit source-degree map.
The original 1,783 records retain n=0..23; new polynomial columns begin at their
first nonzero n. Congruential and
Appell coefficients can be rational; numerator and denominator records reduce
the coefficient first, retain its original rational value, and plot only the
labelled integer component. Denominators are positive. All new records link to
the published special-function registry or the named classical seed.

Each KFOR page has the shared exact-window plot controls, equivalent
representations, a no-JavaScript exact table, JSON/CSV/indexed-text exports, and
finite OEIS comparisons. The complete static index works without JavaScript.
The generator ZIP reproduces the mathematical records using the Python standard
library. It retains the defining registry source. Legacy KSEQ/KOM exact exports
remain preserved; formula metadata is added separately and in page content.

Search uses AND, quoted phrases, OR via `|`, exclusions, exact integer patterns
and `?`. Fields include `formula:`, `representation:`, `collection:`, `n:`
(spacing N), `j:`, `r:`, and `x:`. All formula variants are indexed. Filters,
pagination and shared links preserve applied state. Result CSVs export the
complete filtered set rather than only the current page.

Saved entries use the existing browser-local saved-list key across all 2,023
records, with a 500-record limit. Scoped writes from the older atlas preserve
records from other collections. The saved filter uses the recipient's own list
when sharing a search. Storage denial leaves the current session usable.

The comparison workbench accepts up to four local records or OEIS excerpts.
It supports raw integers, first differences and prefix sums, linear or signed
logarithmic coordinates, residues, and common stored-position windows. Prefix
sums include earlier stored terms before the visible window. Each source keeps
its original local index convention. Position alignment starts the chosen
windows together; recorded-index alignment is available for local records only
and does not imply equal source degrees. The bulk OEIS files omit mathematical
offsets, so reference excerpts always use export positions.

Comparison links contain source descriptors and display settings. Local records
restore immediately; reference descriptors must match the retained snapshot
hash and require an explicit load action. Opening a link does not download the
bulk data. The finder and restoration reuse the same worker's compressed-file
cache. Exact agreement counts compare displayed integers over the overlap;
modular views label these as residue agreements. SVG/PNG exports include the
series legend and OEIS credit when applicable. CSVs retain exact values, index
conventions, source URLs, reference hashes and reference licensing. Points use
roving keyboard focus, with arrows within/across series and Home/End endpoints;
the HTML table provides the same exact integers.

The 112 research additions come from two explicit families in the authored
special-function registry (sections Transfer-secancy parameter polynomials and
Euler-transfer theta polynomials):

- 88 ordinary coefficient columns [r^k] P_(N,n)(r), N=2..12, k=1..8,
  stored at n=k..k+23. No k! scaling is applied. The k=1 columns link to
  the existing transfer-tangent records with their exact index shift.
- 12 specializations Theta_(2n)(x), x=1..12, stored at n=0..23.
- 12 ordinary coefficient columns [x^k] Theta_(2n)(x), k=1..12,
  stored at n=ceil(k/2)..ceil(k/2)+23. Signs are retained.

The source identifies derived research families and requests literature review
before historical novelty is asserted. An absent finite OEIS match does not
change that status. The new displays include finite composition/Stirling and
Bell-column formulas, signed Euler convolution, and inverse-hypergeometric
coefficient representations. Parameter columns search by `k:`; `n:` still
means spacing N, while the visible local index and source degree are separate.
The research browse button selects `tag:research-derived`.

The OEIS snapshot contains 401,422 records, downloaded from the official
`stripped.gz` and `names.gz` URLs. Precomputed comparisons require eight local
terms at a contiguous export position and extend through every available local
term. They report the uncapped hit count and retain the best 50, ranked by
matched length, A-number and position. The browser reference finder accepts
A-numbers, name words, or patterns of 3..1,000 terms. It reports all matching
record counts and shows at most 50 records. Shorter patterns may have many hits.

The bulk files total 41,692,183 compressed bytes and load on explicit reference
search or explicit shared-excerpt restoration. A worker streams decompression for each scan, retaining compressed
bytes rather than the whole decompressed database. Queries stay in the browser.
Cancellation terminates the worker. Unsupported browser features retain download
links and precomputed record comparisons. OEIS data, extracts and matching are
attributed under CC BY-SA 4.0; full entry details remain on OEIS.

The sequence routes default to clean white pages, near-black text and strong
blue links. The Page appearance control changes every reading surface, control,
code block and table together; light/dark/system choices persist independently
of saved entries. No-JavaScript pages use the light theme even under a dark OS.
Plot presets provide full-opacity blue/orange marks, stronger lines and clear
axis labels. Built-in plot colors are adjusted to at least 4.5:1 against the
chosen plot background at full opacity. Custom colors remain exact and show
contrast feedback. These are measured implementation checks, not certification.

The shared appearance panel includes nine built-in palettes and custom main /
comparison colors, paper/white/night backgrounds, direction, opacity, palette
previews, and contrast feedback for custom colors. Built-in colors adapt to the
background; explicit custom colors remain exact. Saved v1 settings and earlier
view links remain supported. System forced colors take precedence. Appearance
changes never alter integer terms, rational reduction, or modular arithmetic.

Validation commands:

```text
python -m unittest discover -s tools -p test_sequence_library.py
node --test tools/test_sequence_library.mjs tools/test_sequence_workbench.mjs tools/test_sequence_readability.mjs
node tools/test_sequence_library_browser.cjs http://127.0.0.1:8834/ OUTPUT_DIRECTORY
node tools/test_sequence_workbench_browser.cjs http://127.0.0.1:8836/ OUTPUT_DIRECTORY
node tools/test_sequence_readability_browser.cjs http://127.0.0.1:8837/ OUTPUT_DIRECTORY
python tools/audit_sequence_library.py --oeis --output RESULT_JSON
```

The independent audit checks every stored new coefficient/component and index
map, factorial versus hypergeometric coefficients, ordinary versus block
convolutions, classical closed-form / recurrence oracles, and the full retained
OEIS comparison. These are finite implementation checks, not novelty review,
an infinite-identity proof, or accessibility certification.
