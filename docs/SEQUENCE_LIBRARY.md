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

Search results show the review status, collection, exact term preview at
its recorded offset, highlighted term matches, and a compact source-formula
excerpt. The complete defining expression remains in an expandable disclosure,
with exact source text preserved. Opening a result with multiple recorded formulas
reveals one native representation selector. The selected variant displays its
recorded formula type, exact expression, explanatory note when supplied, and
linked derivation source. Selecting another variant changes only the visible
formula, not the stored terms, definition, indexes, or CSV/JSON exports.
The main defining formula stays in the selector even if a source lists only
alternative representations. Variant controls mount only when the definition
is opened, and closed definitions are not typeset by MathJax, avoiding work
on off-screen formulas.

Inside an expanded formula, the optional **Inspect exact values** panel shows
eight stored values at a time. Previous, Next and Go navigate the original
stored index, not an inferred source Taylor degree. Formula records also display
an explicit source-degree column calculated with the same existing index map
used on their full record pages. This distinction matters for multisections,
polynomial columns and flattened triangles. Collections without a verified
source-degree map do not display one. Complete coefficient triangles identify
the flat index j, row n and column k separately. For rational-derived numerator
or denominator records, the reduced component and original rational coefficient
appear in separate columns. The **Export window CSV** control downloads precisely
the visible eight-value window, with record ID, stored index, source degree where
available, triangle coordinates where applicable, and exact value strings.
The CSV does not imply that an ordinary index equals a Taylor degree.
Long integers remain exact strings and scroll inside the table without any
floating-point conversion. On wide compact rows, the indexed table can appear
beside the selected formula. Phone layouts stack them without page-wide overflow.
**View original formula text** provides a wrapped, selectable copy of the exact
formula source and a copy control. It changes when the selected representation
changes, without changing the mathematical data, source definitions or exports.
The inspector table is built only when opened. The **Copy inspection link**
control creates a focused, self-contained Search URL with the record ID,
selected representation, and first stored index of the current eight-value
window. On opening that URL, the intended formula and indexed table expand
automatically. The URL carries no coefficients or private browser storage.
Invalid, duplicate, stale, or out-of-range view parameters are ignored rather
than selecting a different formula or a fabricated window. A selectable link
is shown when clipboard access is unavailable. The separate **Copy search
link** control continues to share filters and pagination, not the inspection
state. Shared views preserve local indices and do not imply a source-degree
identity or mathematical novelty.

For integer records, Plot, Save, and Compare remain visible. A More actions
disclosure holds the defining-formula page, transfer action where applicable,
and recorded finite OEIS comparisons. It stays closed on broad searches and
opens automatically when three or fewer records match. Generalized family
results retain their definition and source navigation. Collection and review
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

Comparison links contain source descriptors and display settings. New links
also bind each local sequence to a SHA-256 receipt of its complete indexed
integer data: record ID, collection, stored index convention and offset, exact
term strings, and source degrees where available. A recipient's current
catalogue must match those receipts, offsets and stored lengths before a pinned
comparison is shown. A mismatch stops restoration with a visible error instead
of silently substituting revised coefficients. The source receipts are available
under **Source identity and comparison receipts** on the Compare page. That
panel distinguishes exact local data from parameter-generated families, pasted
integer data, and retained OEIS reference snapshots. These receipts check data
identity, not the truth of an infinite identity or historical priority.

Earlier comparison URLs still open through the original schema. They carry
record identifiers but cannot attest to the original exact local coefficients;
the Compare page explicitly labels such links as legacy. Pinned links remain
reproducible only while the corresponding exact records are present in the
published catalogue. Use the complete notebook or source exports for durable
offline records. The Copy comparison link action is available beside the
selected sources as well as below the chart.

Local records restore immediately; reference descriptors must match the retained
snapshot hash and require an explicit load action. Opening a link does not
download the bulk data. The finder and restoration reuse the same worker's
compressed-file cache. Exact agreement counts compare displayed integers over the overlap.

The Compare page now also exports an **Exact comparison certificate (JSON)**.
Unlike the displayed-row CSV, this self-contained finite record retains the
entire stored integer prefixes for each selected source, including earlier
values required for partial sums and first differences. It also records original
offsets and index conventions, source URLs, generated-family parameters or
retained OEIS snapshot labels when present, a SHA-256 data fingerprint for each
input, the existing local-catalogue receipt where available, all exact window
rows, transformed values, finite comparison counts, first mismatches,
plot settings, and a SHA-256 digest of the canonical certificate body (excluding the digest field itself, independent of JSON whitespace). Up to four sources
are supported. It includes no private browser storage or external requests.
An embedded source digest detects accidental changes within the certificate,
but does not independently establish the authority of an external source.

The certificate generator invokes a separate BigInt verifier before download.
The verifier **recomputes every row and finite agreement from the embedded
integer strings**, independent of the workbench's transform and plotting code.
For local records, it also checks the complete indexed source data against
the pre-published catalogue receipt, including degree maps where recorded.
No decimal plot position is used to establish an equality. The certificate
documents that OEIS export positions do not supply mathematical offsets.
The verification result is limited to the selected finite calculation; it is
not a proof of infinite sequence equality, novelty, provenance history or
physical realization.

The Compare page also includes **Verify a saved comparison certificate**
in a collapsed disclosure. Select the downloaded JSON file and choose
**Verify exact certificate**. Verification runs entirely inside the reader's
browser. The file is never uploaded or sent to a server. It is not necessary
to load the original comparison first. The verifier recomputes every finite
value and agreement, checks the embedded SHA-256 digests, and then reports a
separate check of pinned local-record receipts against the current site's
published catalogue. It displays source-by-source matches, changes, missing
records, or missing receipts. An old certificate may still have valid finite
arithmetic even when one of its local sources no longer matches the current
catalogue. Generated, pasted and OEIS inputs are checked against their
embedded exact data but are not independently authenticated against external
repositories.

After a successful verification, **Inspect verified exact rows and finite
differences** provides a second, collapsed section. It displays twelve exact
rows at a time with source identity, window position, stored-prefix position,
recorded index or OEIS export position, separately recorded source degree where available, original
integer, exact displayed integer and comparison status. Readers can page
through the full verified finite window, filter to one source, or show only
genuine differences from the first source. The on-screen table also shows the
alignment key and the exact displayed integer from the first source when an
overlap exists. Undefined transformed values and positions without an
overlapping baseline are labelled separately and are not counted as
disagreements. The first mismatch and finite agreement counts
are displayed from the independently checked certificate.

**Export filtered exact CSV** downloads all rows matching the currently
selected source and differences-only filter, not just the twelve rows on the
visible page. Each exported line includes the source identity, both stored
and recorded index conventions, optional source degree, alignment key,
original and displayed exact integers, baseline displayed integer,
comparison status, the original local-source receipt when available, and
the verified certificate SHA-256 digest. The `source_number` column identifies
each source by its one-based position in the certificate, with source 1 as
the baseline. The inspector table and source selector show the same numbers,
which remain unchanged when filters select fewer sources. The source verification
list and finite comparison summaries use the same numbering, including the
baseline. This distinguishes sources that share a display identifier, such as two pasted inputs or two
parameter choices from one family. The `source_data_sha256` column records
the verified digest of that source's embedded finite data. Distinct parameter
choices can have the same finite prefix and digest. The certificate digest
together with `source_number` identifies the source entry. The data digest does
not establish external provenance. This CSV is a convenient tabular
extract, not a substitute for independently replaying the complete JSON
certificate. The decimal integer strings remain exact in the file, but
spreadsheet programs may round large integers during automatic import;
select text columns rather than numeric conversion. An empty differences-only
filter disables its CSV export instead of producing a misleading empty report. This view works
without reconstructing the current comparison or loading OEIS data. It never
interprets the recorded index as a Taylor degree.

Invalid JSON, altered calculations, digest mismatches, or files exceeding the
16 MiB browser import limit produce a visible verification failure. Selecting
a new file or encountering any verification failure also clears the preceding
verified table, so old successful values cannot be mistaken for the new file.
The import does not modify the currently selected comparison, chart settings,
or saved entries.

Reverify a downloaded certificate offline using a checkout of the repository
and Node.js 24:

```bash
node tools/verify_sequence_comparison_certificate.mjs komorebi-sequence-comparison-certificate.json
```

The command prints verified source, row and overlap counts and returns a
nonzero exit status for an altered input, incorrect computation, mismatched
receipt, unsupported format or malformed file. For very large comparisons,
the tool refuses certificate exports beyond its explicit size limit rather
than rounding or truncating integers. The existing exact CSV is still
available for those cases.
Modular views label residue agreements separately. SVG/PNG exports include the
series legend and OEIS credit when applicable. CSVs retain exact values, index
conventions, source URLs, reference hashes, and reference licensing. Points use
roving keyboard focus, with arrows within/across series and Home/End endpoints;
the HTML table provides the same exact integers.

The Compare page has an optional **Customize chart title, legend and axes**
panel. Readers can change the chart title, horizontal and vertical axis titles,
legend visibility, placement above or below the plot, and up to four series
names. Legend presentation includes compact names, IDs only, or full IDs and
names. The chart title and each axis title can be shown or hidden independently.
The chart title has automatic sizing or 14, 18, 22 and 26 pixel choices, with
left, center or right alignment. Each axis title has its own automatic sizing
or 12, 14, 16 and 18 pixel choices. Longer titles wrap in full, and the chart
reserves space for them and its legend while retaining room for the plotted
values. Empty titles retain suitable defaults that name the selected
sequence or sequences and the plotted transformation. The selected transformation
remains visible in the automatic title. Hiding a visible chart title retains
the SVG's accessible title. Custom text, visibility, sizes and alignment are
included in SVG/PNG exports, copied comparison links, and research workspace
snapshots. Restore chart labels returns these choices to their defaults.
These settings are presentation metadata in exact comparison certificates.
They do not change selected sources, stored integers or finite arithmetic
checks. Previously exported certificates remain verifiable with their original
presentation fields and SHA-256 digests.

The curated Sequence Explorer and individual Research archive and formula
record plots offer the same type of controls in a separate **Chart titles,
legends and axis labels** disclosure. A single record may hide the redundant
legend, or display its short name or ID. Chart text travels in its plot link
with the same title visibility, size and alignment controls, without altering
source terms or index windows. The original no-JavaScript
record pages, exact-value tables and downloads remain available.

For signed-logarithmic plots, the vertical coordinates are
`sgn(v) log10(1+|v|)`. The default axis labels apply the inverse transform
and show **approximate original-value magnitudes** such as `≈41`, `≈1.7K`,
and `≈3M` rather than unexplained log coordinates. The reader may instead
choose scientific notation such as `≈4.1×10^1`, or the numerical signed-log
coordinate. Positive logarithmic plots offer corresponding approximate values,
scientific labels and raw log coordinates. All three modes preserve the
underlying non-linear spacing and the exact integers. Residue plots retain
exact integer tick labels, and transformed pairs label the relevant axes.
Linear plots can round their tick labels while retaining exact indexed integers
in point details, tables, and CSV. A short note under each chart states the
scale convention. Decimal or scientific axis annotations are not the exact
stored sequence values.

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
The dedicated Research page shows its four family groups and all nine type links
without an initial disclosure click. The search and reference workbenches remain
on their own pages. The research browse button selects `tag:research-derived`.

The OEIS snapshot contains 401,422 records, downloaded from the official
`stripped.gz` and `names.gz` URLs. Precomputed comparisons require eight local
terms at a contiguous export position and extend through every available local
term. They report the uncapped hit count and retain the best 50, ranked by
matched length, A-number, and position. The browser reference finder accepts
A-numbers, name words, or patterns of 3..1,000 terms. It reports all matching
record counts and shows at most 50 records. Shorter patterns may have many hits.

The standalone OEIS page first reads a small snapshot identifier instead of
loading the full integer and generalized family catalogues. The bulk files
total 41,692,183 compressed bytes and load on explicit reference search or
explicit shared excerpt restoration. A worker streams decompression for each scan, retaining compressed
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

## Compact result rows and accessible layout choice

Sequence search results default to compact rows, rather than the earlier
two-column card layout. Each result keeps its recorded identifier, title,
source and review metadata, exact term sample, and actions. The left side
shows the record; the right side shows its exact term excerpt on wide screens.
The two regions stack on narrow screens, with no horizontal page overflow.
Defining formulas remain optional in broad searches and open automatically
when a search yields no more than three matches.

The "Results view" control offers both **Compact rows** and **Cards**.
It uses native buttons with explicit pressed states and supports keyboard
activation. The chosen layout is stored in the browser when storage is
available, otherwise it applies for the current page. The choice changes
presentation only: result count, ordering, exact data, export and navigation
are unaffected. It is hidden without JavaScript; static definitions remain
accessible in the complete index.

The browser regression checks default density, both layout choices, keyboard
activation, persistence across reloads, formula disclosures, no-JavaScript
fallback, and mobile widths 390 and 320, in addition to the existing
source-data and search-function checks.

## Layout density and whitespace refinement

The Sequence Library keeps its three primary tasks together in the rendered
page. Search is followed by Transfer and Compare, while the research-family
cards, generalized-family explorers, graph, identification, and notebooks
share one secondary disclosure. Deep links still open the relevant panel.
The complete static index, source records, sequence formulas, and exports
remain unchanged.

The results grid no longer stretches shorter cards to the height of the
tallest adjacent card. Result card spacing and action rows have been
reconciled to reduce unused interior space without reducing the minimum
44-pixel control targets. Single-result searches retain their expanded
formula view. Sequence tables continue to scroll internally instead of
expanding the page width.

The transfer workbench has a shorter vertical rhythm, including more compact
verification summaries and coefficient previews. The original index
alignment formula is now behind a labelled native disclosure, with the
source and target anchor indices still visible in the summary above.
Opening the disclosure triggers MathJax enhancement when available.

This is an interface improvement, not a change to the mathematical
certificates, source-index conventions, record count, or finite-scope claims.
Targeted browser checks verify search-card spacing, main-task order,
expandable index alignment, and no horizontal overflow across mobile and
desktop widths.

## Compact research workbench rendering

The dedicated Connections page shows the exact relationship descriptions and
their derivation links first. Its neighborhood diagram starts closed and is
drawn only when the reader opens **View relationship diagram**. The SVG scales
to a shorter 280, 350 or 440-unit canvas according to the number of
neighbors in the displayed connection page. Closing the diagram discards
its SVG nodes, and opening it again uses the current relation filters.
The recorded edges, proofs, directed-path logic and exports are unchanged.

The Modular dynamics page now displays the certificate summary and a bounded
plot of at most 128 retained residue samples at a time. If more are retained,
an indexed plot-window control and Previous/Next buttons allow viewing later
samples without rendering all plotted points at once. Plot labels show their
original positions, and the current SVG export reflects the selected window.

The recurrence engine can inspect up to 20,000 complete states, but a
certificate currently retains at most 256 initial residue samples and
64 initial complete-state snapshots. Three labelled disclosures contain
a frequency chart for those retained samples, their exact indexed table
and the initial state snapshots. The contents are created on first opening
and remain scrollable within their own regions. Exports retain the same
bounded samples and the exact recurrence, scanned-state count, transient
and certified period as before. They do not purport to include every state
examined during a longer search.

The responsive browser checks open and close the graph visualization,
verify its compact viewport, check the optional modular panels are initially
unpopulated, and then inspect their full exact values at 1440, 390 and
320 pixels. No-JavaScript explanations and the existing Research directory
remain available. These are presentation and DOM-performance changes,
not new mathematical results.

## Focused pages and existing links

The main Sequence Library now serves search and exact record discovery rather
than mounting every workbench on one page. These sections have dedicated
reader pages:

- Search: sequence-library.html
- Transfer: sequence-transfers.html
- Comparison: sequence-compare.html
- Research family directory: sequence-research.html
- Connection graph and directed paths: sequence-connections.html
- Sequence identification: sequence-identify.html
- Modular recurrence dynamics: sequence-modular.html
- OEIS lookup: sequence-oeis.html
- Combined notebooks and multiple-tool restoration: sequence-workspace.html

The five primary navigation choices remain Search, Transfer, Compare,
Research and OEIS. Research is a directory with direct links to three
individual workbench pages. These dedicated pages load only their relevant
tools rather than initializing graphs, searches and modular calculations
together. Each has a return link to Research and to the combined workspace.
The Search page does not mount those research tools. Their headers,
controls and formulas have been proofread and spaced for narrow screens.
Long mathematical displays and exact tables have their own horizontal
scrolling regions. Source data, finite arithmetic certificates, and
exports remain unchanged.

Older links to sequence-library.html#transfers, #comparison, #oeis,
#research-families, #research-graph and the other research anchors
redirect to the matching focused pages when JavaScript is available.
The earlier sequence-research.html#research-graph, #identify and
#modular-dynamics links also redirect to their individual workbench pages.
The landing page retains targeted static gateways for those hashes
when JavaScript is disabled. Search URLs, collection and family filters,
saved records and original record links stay on the Search page.

The Search result action "Build a transfer" opens the dedicated Transfer
page with that source record selected. The "Add to comparison" action
opens the dedicated Compare page with that source already loaded.
Compare also has its own sequence picker, so it can be used without
returning to Search. OEIS comparisons can be transferred in the same
way without downloading references automatically.

The optional sequence-workspace.html is a combined compatibility
workspace for notebooks and links involving multiple tools at once.
It is not the default landing page. Research-only notebooks continue
to work in the focused Research page. For saved notebooks containing
search, comparison and transfer state together, use the combined
workspace to restore every component.

Dedicated browser tests cover cross-page selections, old hash links,
the standalone record picker, graph, identification and modular workbench
mounting, responsive MathJax displays, exact tables, and static fallback
content on desktop and 390/320-pixel screens.
Passing these tests is not an independent WCAG conformance certification.

## Search help and full research-family navigation

The Sequence Library's expanded search guide now separates basic examples,
combination operators and field meanings. Clickable examples demonstrate
search by name, exact record ID and integer terms. The guide states the
logical behavior of AND, OR, exclusion, exact phrases and the unknown
integer placeholder. It groups search fields into record details,
mathematical parameters and relationship or source fields. In particular,
the n: field refers to spacing N, k: to a polynomial column and order:
to recurrence order. These are not interchangeable with a sequence's
stored index.

The Research Families section is now a directory rather than a small
selection of examples. Four named areas link to complete kind-filtered
search results:

- Secancy polynomials: 88 parameter columns and 11 coefficient triangles.
- Euler-transfer theta: 12 integer specializations, 12 polynomial columns
  and one complete coefficient triangle.
- Block-Appell: 21 coefficient triangles and 84 supported columns.
- Linear recurrences: 120 weighted k-step records and 10 standard
  zero-seeded k-bonacci records.

The nine full-category links cover all 359 currently tagged
research-derived records. Counts are computed from the active catalogue
when the page is generated, rather than copied into the displayed markup.
An overall browse-all link uses the research-derived tag. Each area keeps
a specific worked record for orientation. If future research kinds are added
to the catalogue, they appear in an additional indexed-families group.

Links use the existing exact search parser and retain the normal result
filters, pagination, mathematical typesetting, source links and review
statuses. Native disclosures and direct example-record links remain usable without
JavaScript. The full category filtering itself requires JavaScript. A
complete static sequence index is linked as the no-JavaScript alternative.
Browser regression checks verify category counts, filtered navigation,
search examples, mobile layouts and the static fallback. These records are indexed research constructions,
not claims of historical novelty or pairwise distinctness.

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

