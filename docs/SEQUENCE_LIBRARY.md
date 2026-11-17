# Unified sequence and formula library

`sequence-library.html` searches 2,292 local records: the original 38 KSEQ
entries, 90 recovered KOM records, and 2,164 KFOR parameter records. It indexes
7,033 recorded representations, including term formulas, finite sums,
recurrences, generating functions, and hypergeometric coefficient formulas.
These counts describe records and representations, not distinct infinite
sequences or new discoveries.

The homepage search and main navigation both lead to the complete library. Collection
buttons show the scope and count before filtering. The 38 curated generators
are a subset that can compute additional terms; they are not the size of the
library. Plotting and term generation are available in `sequence-explorer.html`. Existing
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
without changing exact data, program code, or formula exports. Unsupported
source notation remains literal. Typeset formulas can scroll within their
panels and remain keyboard accessible. Without JavaScript, the original source
and complete static index remain available.

`tools/sequence_formula_catalogue.py` defines the finite parameter grids. Scalar
parameter records store 24 terms at their stated offsets and an explicit source-degree map. Coefficient triangles store all complete rows n=0..12.
The original 1,783 records retain n=0..23. New polynomial columns begin at their
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
when sharing a search. If browser storage is unavailable, the current session still works.

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
cache. Exact agreement counts compare displayed integers over the overlap.
Modular views label residue agreements separately. SVG/PNG exports include the
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

The registry classifies these as derived research families. Historical novelty
remains subject to literature review. An absent finite OEIS match does not
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
OEIS comparison. These finite implementation checks do not constitute a novelty
review, a proof of an infinite identity, or accessibility certification.

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
weight, and source subsequence, respectively. `k:` retains its polynomial-column
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

## Transfer workbench and exact certificates

The sequence library includes a transfer workbench for stored scalar records.
Each comparison removes the stored leading zeros from both input windows and
forms anchored ordinary power series A and B with nonzero constant terms.
For a selected length L, it computes H=B/A and K=A/B over the rational
numbers, truncated modulo z^L. The calculator checks H A=B, K B=A, and
H K=1 for every displayed coefficient. Both the offset in the stored array
and the original sequence index are retained.

A worked Euler and Fibonacci example shows the finite quotient
H=(1, 2, -1, 53) and inverse K=(1, -2, 5, -65) over four terms.
The first Fibonacci zero is skipped, but its original index is preserved.
This sample illustrates a finite coefficient identity, not a claim that
arbitrary sequences have equivalent recurrences.

The workbench now provides a source identity check, window-length and
nonzero-anchor guidance, three explicit certificate conditions, both kernel
previews, a worked coefficient convolution, exact CSV and JSON exports,
and links that restore a selected finite comparison. The exported JSON records
the source and target anchors, both index shifts, coefficient domain, exact
rows, and the verification outcome. Rational values remain exact strings.

The construction does not predict additional terms or establish a common
homogeneous recurrence. Infinite relations require a separate derivation.
Scalar columns must be selected before a coefficient triangle can be used.
The finite engine is checked in `tools/test_sequence_transfer.mjs`.

## Generalized families and research tools

The homepage links to both integer records and a separate generalized-family
search. The family index contains 36 definitions bound to 12 maintained source
documents, including Special Functions I–VIII and the generalized closed-form
material in Paper IV. Use `family:` to find a construction or its integer
instances, and `paper:SF-VI` (or a quoted paper title) to search by source.
Roman-number matches respect paper boundaries. Family searches offer
construction-type and source filters; integer-only controls are hidden in this
view. Clear removes the query and filters while keeping the selected scope.
Family result CSVs contain the definition, parameter domain, notes, defining
source and member count for every filtered result. The static family index
offers the same definition CSV for all constructions. Each family page also
offers its definition and source bindings as JSON and an indexed-member CSV
with original offsets, review status and entry links. Families without indexed
integer examples retain a header-only member CSV and say so explicitly.
The source coverage page lists
311 source headings and exact source hashes. It is an index, not a claim that
every formula in every paper has been reviewed or converted into a record.

Ten families have exact parameter controls: weighted k-step reciprocal powers,
standard k-bonacci seeds, alternating reciprocal blocks, positive congruential
inverses, block-Appell polynomials, secancy columns, theta specializations and
columns, transfer tangents, and classical multisections. The explorer retains
source degrees, local offsets, reduced rational values and component choices.
The twelve analytic families retain their domains and defining passages without
implying a numerical analytic-continuation implementation. Complex-order source
definitions remain visible even when exact controls use bounded integer values.

The Appell explorer distinguishes values at an integer x from ordinary
coefficient columns in x. Column k uses local index n, polynomial row Nn+k,
and binom(Nn+k,k) times the reduced positive-block inverse coefficient.
All 84 stored Appell column records use this readout. Their
source rows, exact rational values and selected integer components survive
CSV export, comparison and shared links. The point-value controls keep
x=-8..8; Appell columns use k=0..8. Theta specializations allow x=-12..12,
and theta columns allow k=1..12, including all existing stored theta records.

Only parameters active for the selected construction are validated. Inactive
fields cannot block a different family. Invalid shared settings show an error
and do not start a substitute calculation; readers can review the displayed
settings and explicitly calculate. Calculator links preserve the library's
search scope, query and filters. On a family detail page, selecting another
construction opens its matching definition page, and older mismatched links
resolve to the selected family's page before calculation.

Thirteen source-defined discrete constructions and one explicitly labeled
classical reference collection cover the remaining archived material: weighted
block logarithmic derivatives, binomial and Stirling transforms, Hankel
determinants, prime-adic valuations, digit and subset residue counts, Pascal
valuation distributions, totient prefix statistics, prime-power support,
pointwise odd Collatz readouts, formal Smith transfer polynomials, Clifford
identity words, and cyclic subgroup-coset masks. They have source definitions,
representative exact terms, original offsets, full archived member links and
reproduction access. Their finite readouts are reproduced by the archived Python generator.

All 90 recovered KOM records now have a family or reference home. Nineteen
reciprocal-block records link to the existing exact reciprocal explorer with
their actual N and r; four k-bonacci records retain their original order and
zero-prefix convention. The seven archived logarithmic records retain
L_N(0)=0 and L_N(n)=Nn T_N(n-1) for n>=1, rather than silently substituting
the differently indexed tangent readout. The original 90 records, their terms,
classifications, b-files and offsets are preserved.

The three additional curated seeds for natural numbers, odd numbers and
partition numbers belong to the universal coefficient-section definition.
They link to that definition because those parents are not offered by the
browser's exact multisection controls. All 2,292 indexed integer records now
have a family or reference assignment without extending the supported engines.

The new source binding pins the archived generator to commit
`96ef8755314fe6bfa3c5ca76b1d61e20f3c1e510` with its normalized SHA-256. The
classical reference collection is a navigational grouping, not a new
parameter family. Source indexing adds no historical-novelty claim.

The family explorer provides exact tables, worked values, independently checked
alternatives where available, value/residue plots, keyboard point inspection,
CSV, SVG/PNG, comparison and parameter links. Arbitrary k initial values use the
order-k recurrence with its finite numerator; nonzero-tail reciprocal powers
use the order-kr denominator. Derivations and conventions are in
`research/sequence-families/DERIVATIONS.md`.

The connection explorer preserves direction and evidence type across 1,231
relations, including seven explicitly finite transform comparisons. It supports
directed paths and exact scalar transfer composition with both position and
original-index shifts. Finite evidence remains finite after composition.

Identification scans all 2,236 local scalar records, or the retained 401,422
OEIS reference records. It tries bounded exact transformations and reports the
matched operation and positions. Optional target transformations apply locally;
OEIS identification transforms the input against raw exported targets. Tables
are excluded from scalar matching. Export positions are not mathematical
offsets, and finite matches do not establish infinite identity or novelty.

Modular dynamics checks complete recurrence states, including the order-kr
recurrence for powers. A repeat certifies the period and possible preperiod;
reaching the state cap reports no certificate. JSON retains the recurrence,
initial state, repeated state and finite search bound. Displayed frequencies
describe the displayed finite window.

Named notebooks capture searches, generated and pasted comparisons, transfers,
graph selections, modular parameters, display choices and notes. They support
JSON import/export and bounded share links. All tool settings are validated
before restoration. Shared notebooks require an explicit load action; OEIS
excerpts require a separate explicit download. Unavailable or unreadable browser
storage is preserved, with session-only saving and JSON export available.

Notebook links keep their payload in the URL fragment, which is not sent in
the page request. Earlier query-based notebook links remain readable. Comparison
and identification links that exceed the host-safe bound direct the reader to
notebook JSON export; full JSON workspaces retain their larger data limit.


### Three-sequence formal transfer composition

The Transfer Between Sequences workbench can now route an exact scalar transfer
from A to C through an independently selected scalar record B. With nonzero
anchored constant coefficients and a common finite window of length L, the
exact rational transfer quotients satisfy

    H_AB = B/A,  H_BC = C/B,  H_AC = C/A (mod z^L)
    H_AC = H_BC * H_AB (mod z^L)
    L(H_AC) = L(H_BC) * L(H_AB).

The interface displays the two-step kernel and the independently constructed
direct quotient side by side. It transcribes one coefficient witness, the
original A, B, and C index maps, and the equality of accumulated original
index shifts. A JSON export keeps the exact coefficients and the finite
verification result. Invalid or unavailable intermediate records are rejected
without preserving a stale certificate.

This composition identity follows algebraically from the formal units of the
anchored tails. It is **not** evidence of a new shared recurrence, a global
sequence identity, or a discovery of a historically new sequence relation.
The no-JavaScript reading includes the definition and scope, but cannot compute
new three-sequence certificates.

## Sequence Library interface and accessibility

The landing page now prioritizes three tasks: search, transfer, and compare.
The primary navigation stays short. Secondary sections, reference matching,
and the research tools open through labelled native HTML details, so their
content remains keyboard accessible and can be read without JavaScript.
Direct links to OEIS, research families, connections, generalized families,
and the other advanced tools open the relevant panel on a JavaScript-enabled
page without changing the original URL or exact data.

The search results retain their identifiers, exact term excerpts, review
status, and all existing actions. Long defining formulas are initially
collapsed for a broad search; for three or fewer matches, the formula
opens by default to aid focused inspection. The formula display selector
still switches between exact source notation and MathJax typesetting.
The advanced search syntax guide is optional and the original search
filters, saved entries, CSV export, and OEIS comparisons are retained.

In the transfer workbench the input form precedes the methodology.
The coefficient calculation, exact indexed data, matrices, and
three-sequence composition can be reached from a short result navigation.
The heavy matrix panel starts collapsed, while the exact data table
is height-limited and scrollable. Method descriptions, full Euler/Fibonacci
example, sources, and static composition explanation remain in labelled
disclosures. The static reading example and complete index remain
available when JavaScript is disabled.

The layout uses visible focus indicators, native summary controls, labelled
form fields, responsive touch targets, and internal horizontal scrolling
for long equations and exact tables. This is a usability improvement and a
bounded browser regression, not an independent WCAG conformance certification.
The production checks cover widths of 1440, 390, and 320 pixels, hash
navigation into collapsed panels, focused single-result formulas, keyboard
access to disclosures, and no-JavaScript reading.

## Typeset mathematical reading

The sequence reading pages use the shared MathJax display with a site-wide
Typeset math / Plain text selector. The source notation and exact data are
unchanged by display transcription. The sequence library now presents the
anchored transfer equations, quotient and inverse kernels, finite
Euler/Fibonacci witness, and verification identities as display mathematics.
The dynamic certificate uses coefficients from the exact rational transfer,
not rounded plot values. The transfer workbench displays the lower-triangular
convolution operators L(H) and L(K) as MathJax matrices. Readers can choose a
leading principal block of order 1 through 8, with order 4 displayed initially.
The existing exact HTML matrices retain their first eight rows and columns,
or fewer when the selected coefficient window is shorter.
The workbench also displays exact matrix actions on the anchored source and
target vectors. For a selected leading block of order m it shows both
L_m(H) a = b and L_m(K) b = a using original stored integers. The local
matrix position j=0 is labelled with both original source and target indices.
The matrix panel's copy action includes the two action equations as LaTeX.

The matrix panel additionally checks any displayed entry of
`L(H)L(K)` or `L(K)L(H)`, using the exact rational product
`sum_(ell=j)^i h_(i-ell) k_(ell-j)` when `i>=j` and zero above the diagonal.
It displays the individual product terms and compares their exact sum to
the Kronecker delta. A failed entry is not presented as an established
identity. The reader may select rows and columns within the 1 to 8
dimensional displayed block. The LaTeX copy action includes the selected
matrix-product witness. The static Euler/Fibonacci example also includes
the exact lower-left cancellation `53*1 + (-1)*(-2) + 2*5 + 1*(-65) = 0`.

The original index map is typeset separately from the convolution
operator: local position `j` corresponds to source index `alpha+j`
and target index `beta+j`, with original shift `beta-alpha`.
This coordinate pairing does not assert termwise equality or
recurrence equivalence. As before, every matrix assertion is restricted
to the selected finite coefficient window.

The coefficient witness now supports every stored local tail position, not
only the initial example. Readers can choose forward convolution or inverse
recovery and inspect the precise finite sum, original indices, and stored
coefficient. The witness transcribes exact fractions and signs without
rounding and does not assert values beyond the selected coefficient window. The controls can
copy the selected matrix pair and inverse identity as exact LaTeX. The
Euler/Fibonacci worked example includes fixed four-by-four matrices and a
plain-text fallback even when JavaScript is disabled.

Matrix rows and columns refer to anchored tail positions, not the original
source and target index conventions. The finite identities
L(H)L(K)=L(K)L(H)=I hold for the displayed leading block because the
kernel product is 1 modulo z^L. Neither the matrix display nor its LaTeX
export changes the underlying rational transfer certificate.

The connection graph and each record's research-connection panel display an
equation for supported relation types. These include subsequences, seed shifts,
polynomial coefficient extraction, evaluation, inverse block matrices, and
the Euler/Fibonacci ordinary convolution. The accompanying prose retains
direction, indexing conditions, and evidence scope. Finite transform matches
without an established identity remain prose rather than being promoted to
an equation.

Each complete coefficient triangle displays its flat-index map.
Ordinary triangular rows use $j=n(n+1)/2+k$. The theta polynomial
rows use $j=n^2+k$. The interactive row selector computes its displayed
polynomial directly from the exact stored integers. For block matrix tables,
$R_n(x)$ is labelled as a row encoding only. It is not asserted to be a
generating function. The indexed coefficient table retains all zero entries
even when a polynomial omits zero terms.

Generated displays preserve the old plain-source fallback without
JavaScript. Formula exports, comparison and transfer certificates, and
stored sequence offsets remain independent of presentation. Complex
expressions scroll inside their own panels on narrow screens. The targeted
browser regression runs at 1440, 390, and 320 pixels and checks MathJax
errors, plain-source switching, exact row transcription, index maps,
and the no-JavaScript triangle.

Run the focused checks with:

```text
node --test tools/test_sequence_math.mjs tools/test_sequence_transfer.mjs tools/test_sequence_research.mjs
python -m unittest discover -s tools -p test_sequence_library.py
node tools/test_sequence_math_browser.cjs http://127.0.0.1:8846/ OUTPUT_DIRECTORY
```

