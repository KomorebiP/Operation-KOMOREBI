# Unified sequence and formula library

`sequence-library.html` searches 2,292 local records: the original 38 KSEQ
entries, 90 recovered KOM records, and 2,164 KFOR parameter records. It indexes
7,033 recorded representations, including term formulas, finite sums,
recurrences, generating functions, and hypergeometric coefficient formulas.
These counts describe records and representations, not distinct infinite
sequences or new discoveries.

The homepage search and main navigation open this complete library. Collection
buttons show the scope and count before filtering. The 38 curated generators
are a subset that can compute additional terms; they are not the size of the
library. Their plotting interface is `sequence-explorer.html`. Existing
`sequences.html` search links open the library, while saved plot links retain
their settings in the generator interface. Research-archive searches also use
the library, with the archive collection filter applied.

Results show the defining formula, review status, collection, exact term preview
at its recorded offset, and highlighted term matches. Collection and review
filters share the same URL state as the query. Removable filter buttons make
the current scope explicit; copying a link leaves the result count visible.

The Math display selector at the bottom of each page offers Typeset math and Plain text. Its
preference persists across pages and tabs where browser storage is available.
Readers retain their original TeX; sequence formulas retain their original
plain-text source. A bounded notation parser supplies a display transcription,
without changing exact data, program code or formula exports. Unsupported
source notation remains literal. Typeset formulas can scroll within their
panels and remain keyboard accessible. Without JavaScript the original source
and complete static index remain available.

`tools/sequence_formula_catalogue.py` defines the finite parameter grids. Scalar
parameter records store 24 terms at their stated offsets and an explicit source-degree map. Coefficient triangles store all complete rows n=0..12.
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

Saved entries use the existing browser-local saved-list key across all 2,292
records, with a 500-record limit. Scoped writes from the older atlas preserve
records from other collections. The saved filter uses the recipient's own list
when sharing a search. Storage denial leaves the current session usable.

The comparison workbench accepts up to four local records or OEIS excerpts.
It supports raw integers, first differences, and prefix sums, linear or signed
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
conventions, source URLs, reference hashes, and reference licensing. Points use
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
matched length, A-number, and position. The browser reference finder accepts
A-numbers, name words, or patterns of 3..1,000 terms. It reports all matching
record counts and shows at most 50 records. Shorter patterns may have many hits.

The bulk files total 41,692,183 compressed bytes and load on explicit reference
search or explicit shared-excerpt restoration. A worker streams decompression for each scan, retaining compressed
bytes rather than the whole decompressed database. Queries stay in the browser.
Cancellation terminates the worker. Unsupported browser features retain download
links and precomputed record comparisons. OEIS data, extracts, and matching are
attributed under CC BY-SA 4.0; full entry details remain on OEIS.

Reader-facing names are Sequence library, Curated sequences, Formula families,
and Research archive. Headings and controls describe what readers can do;
release numbers, development milestones, and source archive filenames belong
in reproducibility records rather than the browsing interface. Record IDs,
original source notes, exact exports, reference dates, and attribution remain
available for citation and reproduction.

The sequence routes use the site's green tones by default. The visible Color
scheme buttons switch between Site green and Black & white; Light/Dark/System
is a separate display control. Choices persist across sequence routes. Switching
a page scheme also applies it to the current plots, including when an older
saved plot preference used color. Black & white uses neutral gray text, panels,
controls, plot backgrounds, and marks. Shapes and line patterns distinguish
series without requiring hue. Print output uses black text on white paper.

Plots default to Match page scheme. Green-only and monochrome palettes are
listed first; the remaining multicolor and custom palettes are grouped as
Optional colors. A user can choose these independently after switching page
schemes. Readable light/dark plot presets preserve the chosen page scheme.
Copied plot links resolve Match page scheme to an explicit palette so recipients
see the same plotted colors. Exact arithmetic and source data are independent
of appearance settings.

The shared appearance panel also supports custom colors, backgrounds, direction,
opacity, point size, line weight, chart height, grid, baseline, and labels.
Built-in mark colors meet 4.5:1 against the chosen background at full opacity;
custom colors remain exact with contrast feedback. Saved v1 preferences and
older explicit view links remain supported. System forced colors take precedence.
These are measured implementation checks, not accessibility certification.

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

## Complete coefficient tables and supported columns

The library exposes 55 additional coefficient tables from the registry: 11
secancy parameter triangles (N=2..12), the Euler-transfer theta table, 21
j=0 block-Appell triangles (N=2..8, r=1..3), and 22 forward/inverse
block-binomial kernels (N=2..12). The kernels are classical block constructions
used in the project; their inclusion is not a claim of historical priority.
The polynomial families retain the registry's unassessed novelty status.

All tables store complete rows n=0..12. Ordinary triangles flatten with
j=n(n+1)/2+k; the theta table has degree 2n and uses j=n^2+k. Zero coefficients
are retained. HTML and CSV show flat j, row n, column k, source degree, and the
exact coefficient. The plot selector displays the row polynomial and selects
its exact contiguous flat-index window. Shared row windows restore that row.

Another 84 records expose the supported columns of the j=0 Appell tables,
with N=2..8, r=1..3, and k=1..4. Local index n selects polynomial row Nn+k.
Their formulas are obtained directly from the registry's Appell generator:
the coefficient equals binom(Nn+k,k) times the normalized coefficient of the
inverse block section. The displayed reciprocal-power form keeps its
alternating sign. These are further indexed instances of existing published
families, not 139 assertions of distinct or historically new infinite sequences.

The notation pass separates defining equations, stacks constraints beneath
sums, leaves empty hypergeometric parameter rows blank, and uses a vertical
bar before the hypergeometric argument. Factorial powers retain their binding.
Original formula strings, programs, and exact exports remain available. The
shared selector sits in the footer and keeps the same saved preference.


For the inverse block kernel, fix an integer \(N\ge2\), work in the formal series ring \(\mathbb Q[[z]]\), and set
\[
H_N(z)=\sum_{m\ge0}\frac{z^{Nm}}{(Nm)!},\qquad
C_N(z)=H_N(z)^{-1}=\sum_{m\ge0}c_m\frac{z^{Nm}}{(Nm)!}.
\]
For integers \(n\ge k\ge0\), the product of the forward and inverse matrices is
\[
(KL)_{n,k}=\binom{Nn}{Nk}
\sum_{h=0}^{n-k}\binom{N(n-k)}{Nh}c_h
=\binom{Nn}{Nk}(N(n-k))![z^{N(n-k)}]H_N(z)C_N(z)
=\delta_{n,k}.
\]
The reversed product has the same convolution in the opposite order. Thus the
inverse statement follows from the formal reciprocal identity; it is not
inferred from the finite matrix tests. The tables use N=2..12.

## Exploring a coefficient table

The 55 complete coefficient tables support selections by row, column, or
right-edge diagonal. A row fixes n and varies k. A column fixes k and varies n.
The right-edge distance d selects k = row length - 1 - d in each stored row;
this is k=n-d for ordinary triangles and k=2n-d for the theta table. Rows
without that column are omitted, rather than filled with invented zeros.

Exact coefficients are the default. The modular view computes nonnegative
residues with BigInt for moduli 2 through 1,000,000, including negative and very
large original coefficients. Optional outlines distinguish zeros without
requiring color. The complete source integers and their flat j, row n, column k,
and source degree remain in the selection table and CSV. Copy and library
search actions use the original coefficients, even when residues are displayed.

The selection plot uses k on its horizontal axis for rows and n for columns or
diagonals. Signed logarithmic and linear scales are available for exact values;
modular plots use a linear residue axis. Arrow keys navigate plotted points;
Enter opens the corresponding indexed coefficient. SVG and PNG exports retain
the plotted selection, while CSV retains exact integers. Shared table links
restore the selection, modulus, scale, and zero emphasis. Invalid options retain
the previous view or restore the default row on initial load.

Indexing help and secondary display options are expandable. Without JavaScript,
the complete coefficient and exact-index tables remain available. The explorer
does not extend a stored window or infer an infinite sequence from a selection.

## Recurrence families and transfer maps

The ordinary k-step expansion adds 120 weighted reciprocal-power records
(order 2..16, power 1..4, weight 1..2) and ten standard zero-seeded k-bonacci
records (orders 7..16). The latter store 48 terms; the other scalar parameter
records store 24. Existing orders 3..6 receive alternate finite binomial and
hypergeometric representations while their original exports remain unchanged.
The generalized hypergeometric expression uses an explicit finite cutoff:
parameters may not be cancelled before that cutoff. Full derivations and domain
conditions are in research/sequence-connections/IDENTITIES.md; the maintained
k-bonacci source is pinned alongside it. These extensions do not establish
historical novelty.

Search fields `order:`, `weight:`, and `parent:` find recurrence order, step
weight and source subsequence respectively. `k:` retains its polynomial-column
meaning. Every record has finite-window sign, support, and GCD details, source
normalization, typed research connections, and a copyable citation.

The transfer tool computes H=B/A and K=A/B exactly over Q for nonzero stored
tails, preserving original indices, leading-zero prefixes, and both shifts.
Different zero-prefix lengths require a bijection between the prescribed-prefix
classes, not an automorphism of all Q[[z]]. Certificates contain forward values,
recovered values, residuals, and convolution matrices. CSV and share links retain
the input conventions. These finite transfers do not predict unrecorded terms.
The Euler/Fibonacci example links the infinite source derivation and explains
F(n+1) and the transported shift's boundary term.

The typed relation download distinguishes subsequences, seed shifts, polynomial
coefficient extraction, evaluation, inverse matrices, and ordinary convolution.
A false reversibility flag means that no inverse is asserted. The available
stored overlaps are checked without extending their original data windows.
The focused self-audit is in research/sequence-connections/AUDIT.md.
