# Sequence and Formula Atlas

The [Sequence library](https://komorebip.github.io/Operation-KOMOREBI/sequence-library.html)
is the main search for all 2,292 records and is available from the homepage.
The [curated generators](https://komorebip.github.io/Operation-KOMOREBI/sequence-explorer.html)
provide the extensible plotting interface for 38 of those records. Existing
atlas links retain their search or plot state. The Math display preference is
shared with the rest of the site.

## Recovered research library

The [research sequence library](https://komorebip.github.io/Operation-KOMOREBI/sequence-archive.html)
adds 90 recovered KOM records across 18 families, with 5,487 exact terms.
Its fielded and exact-term search, family and review filters, and shareable
searches use the complete library with the archive filter applied. It retains
offset-aware plots of values, differences, prefix sums, residues,
and consecutive residue pairs. Every record has a static definition, complete
indexed data, CSV, indexed text, JSON with integer strings, and source downloads.
The coefficient triangle KOM084 shows its flat index alongside its row and column.

KOM IDs are archive labels. The 62 exploratory records make no novelty claim.
Stored ranges vary by record; plots never extrapolate. A partial sum begins at
that record's first stored index, and the first difference is undefined there.
Links to the curated KSEQ atlas report finite, same-index data overlap only.
The existing 38 KSEQ entries and their exact exports retain their identifiers
and values. All collections can be searched together in the main library.

Source bytes and archive SHA-256 are recorded in
`research/sequence-archive/README.md`. Reproduce the finite audit with:

```text
python -B tools/audit_sequence_archive.py --output archive-audit.json
node --test tools/test_sequence_archive.mjs
```

The audit compares every regenerated record, all 90 b-file hashes, the historical
numeric controls, and the generator's independent finite checks. It establishes
bounded implementation agreement, not originality, infinite sequence identity,
or any of the research program's global conjectures. The archive's annotations
of OEIS references are retained as source annotations, not fresh corpus checks.

[Open the curated generators](https://komorebip.github.io/Operation-KOMOREBI/sequence-explorer.html) · [Sequence derivations](demonstrations/SEQUENCE_SHAPES.md)

The atlas organizes source-linked integer sequences and formulas, with exact
term tables and an interactive plot explorer. Its catalogue contains
the 21 published reciprocal families for N=2,…,8 and r=1,…,3, together with
Bell numbers, Fubini numbers, factorials, Fibonacci numbers, and signed even
Euler numbers. Twelve further references add nonnegative integers, odd numbers, triangular numbers, squares, cubes, powers of two and three, Catalan numbers, central binomial coefficients, integer partitions, Lucas numbers, and Pell numbers. The 38 identifiers KSEQ-000001 through KSEQ-000038 are stable.
New entries must be appended, preserving existing identifiers.

These are existing published families and classical reference sequences.
No entry or formula is claimed new. The atlas adds no Lean execution,
independent mathematical review, or change to the linked works’ proof status.

## Explore a sequence

Use sequence values, values modulo m, residue grids, residue frequencies,
successive-term pairs, or successive-residue plots. First and second differences, partial sums, successive ratios, and
running averages are available as transforms. Alternating signs, absolute values, binomial, and inverse binomial transforms are also available. Sums and averages start at
index zero, even when the displayed window starts later. Undefined ratios
and initial differences are omitted. The second difference at n is
a(n) - 2a(n-1) + a(n-2), defined from n=2 onward. Modular views require integer-valued
transforms. Residues use the least nonnegative representative, including for
negative terms. The modulus ranges from 2 to 128.

Choose a comparison sequence to overlay it at the same compressed indices.
Reciprocal entries use degree Nn; comparing equal n at different N therefore
compares different ordinary degrees. Parameter controls select N and r.
The first-index and term-count controls move and zoom the sample window.
Previous/next-window and fewer/more-term buttons provide the same operations
without typing. Guided investigations load Fibonacci residues, signed Euler
growth, reciprocal-power comparisons, and ordered/unordered partitions.
Family-specific term limits are shown below the graph.

Plots use approximate coordinates. Integers and fractions remain exact in
the table and CSV. Log10 omits nonpositive values; signed log uses
sign(x) log10(1+|x|). Residue colors cycle through eight colors, with exact
residue labels available on points. Focus or select a mark to inspect it.
The table provides an alternative to the graph. The graph has one Tab stop:
arrow keys move between marks, Home/End jump to the first/last, and Enter
or Space announces the selected value. Previous/next-mark buttons provide
touch targets for the same inspection. Point inspection pauses animation.
Spoken labels abbreviate very long values and give their digit counts;
the inspector, exact table, and exports preserve every digit. Search inputs
use short instructions rather than reading the entire help panel on focus.
Modulus animation starts only on request, cycles from 2 through 128, stops
when the page is hidden, and has a stop button. Status announcements are
quiet during animation. Invalid fields are associated with an error and
the last valid plot remains available. Invalid link options fall back to defaults.

Copy view link retains the controls and any pasted terms in the URL. Pasted
terms are browser-local unless the user shares that link; they are labelled
unreviewed. Downloads include exact CSV, view JSON, and standalone SVG or
PNG plots. Search displayed integers looks up a contiguous block of up to
eight integer-valued transformed samples. The OEIS link is an explicit
external lookup and uses OEIS's `signed:` prefix to preserve the signs;
the atlas makes no background OEIS search requests.

Individual entry pages include previous/next navigation, related entries,
copyable starting terms, indexed text in b-file style, exact CSV, and JSON
with reference attribution. Stored exports contain only n=0,…,63. Save
entry keeps identifiers in this browser, with a current-page fallback when
storage is unavailable. Saved lists are never included in copied links;
a saved-filter link uses the recipient's own browser-local saved list.

## Catalogue search and OEIS comparisons

Catalogue search covers names, formulas, identifiers, recorded OEIS matches,
and contiguous terms among the first 64 stored terms per entry. It is not a
search across the complete OEIS. A candidate period requires at least three
repetitions in the selected finite window and is not a global-period proof.

Words combine with AND, quotes retain phrases, `|` joins alternatives, and
a leading minus excludes a word or field. Supported fields are `id:`,
`name:`, `formula:`, `tag:`, `kind:`, `oeis:`, `n:`, `r:`, `status:`, and
`terms:`. This subset is inspired by the [OEIS search hints](https://oeis.org/hints.html).
Examples include `n:4 r:2`, `name:"ordered bell"`, and
`tag:partitions -name:fubini`. Local IDs accept forms such as `KSEQ7`.

Term patterns allow `?` for one unknown integer; for example, `1, ?, 69`.
Results report and highlight the matched indices. Matching can start at
index zero or anywhere in the recorded terms. All numeric comparisons use
exact integer strings, with at most 2,000 digits per search term and
20,000 characters per query. Text suggestions address spelling only and
never change numeric matching. Topic/type/saved filters and result sorting
compose with the query. Copy search link preserves those controls. Press
`Ctrl+/` (`Command+/` on Mac) outside an input to focus search; Arrow Down reaches the result links. Plain character keys do not move focus.

The separate OEIS comparison tool reads official bulk exports locally. It
scans every exported position for six starting terms and extends each hit
through at most twelve terms. Shorter exported excerpts are outside this
comparison. Excerpt positions count from zero and do not supply mathematical
offsets. A match does not prove identity; no match does not establish novelty.

The retained comparison report records retrieval time, export headers,
compressed-file SHA-256 hashes, catalogue-term hash, and all finite matches.
The same retained bulk dumps were compared again for the expanded catalogue; their original retrieval time is preserved separately from comparison time. The bulk dumps are kept outside the public site. Only the comparison
report and attribution are published. Refresh explicitly with:

```text
python -B tools/update_sequence_atlas_oeis.py --stripped PATH/stripped.gz --names PATH/names.gz
```

Download the files from the [official download page](https://oeis.org/wiki/Download).
OEIS data and imported names are credited to The Online Encyclopedia of
Integer Sequences and the OEIS Foundation under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Finite matching and presentation are adaptations. Preserve source links,
attribution, license notices, and modification descriptions when reusing the
comparison report. The atlas is an independent Komorebi project.

## Definitions, maintenance, and reproduction

The source of truth is `tools/sequence_atlas.py`. Entry pages, term CSV files,
and `assets/sequence-atlas-data.json` are generated by the existing reader
build. The browser engine is `website/assets/sequence-atlas-core.mjs`.
Field parsing and ranking live in `website/assets/sequence-atlas-search.mjs`,
and browser-local saved-entry handling in `sequence-atlas-saved.mjs`.
Its BigInt implementation is compared with the independently generated
Python terms. Reciprocal coefficients are also checked against ordinary
rational power-series inversion, and partition sequences against binomial
recurrences. These are bounded implementation checks.

Reproduce the recorded terms for a selected entry:

```text
python -B tools/sequence_atlas.py --id KSEQ-000004
python -B -m unittest discover -s tools -p test_sequence_atlas.py -v
node --test tools/test_sequence_atlas.mjs tools/test_sequence_atlas_search.mjs tools/test_sequence_atlas_discovery.mjs tools/test_sequence_atlas_interface.mjs tools/test_sequence_atlas_study.mjs tools/test_sequence_atlas_directory.mjs
```

Each future entry needs a definition, indexing convention, source, exact
generator, finite test range, and separate formula/sequence originality
assessment. Add conjectural entries with an explicit conjecture label;
never infer novelty or proof from a matching result or a plot.

## Discover connections

The discovery form accepts 6–64 exact integers. It tests the original input,
first and second differences, partial sums, alternating signs, absolute values,
binomial and inverse binomial transforms, and omission of the first one or two
input terms. Each usable probe must retain at least six terms. A candidate
must match every available transformed input term consecutively in a catalogue
entry's first 64 recorded terms; no floating-point rounding or fuzzy integer
matching is used.

The optional catalogue-transform comparison additionally tests its original
terms, differences, sums, and sign transforms. Binomial transforms are applied
to input only in discovery. Initial undefined differences are skipped and the
source and target indices are reported. Binomial transforms use
b(n)=sum_{k=0}^n binom(n,k)a(k); the inverse includes (-1)^(n-k).
All sums start at zero. Omitting terms changes only the input start position.

Results rank longer matches first and prefer simpler operations; samples with
fewer than three distinct transformed values are ranked later and labelled.
Repeated target positions are grouped in a single suggestion, with all starting indices in the JSON. Redundant shortened-input results are omitted when the full input already matches that target transform. Up to 24 suggestions are displayed. Buttons plot the transformed input or the
catalogue transform at the reported target indices. Pasted transformed input
is reindexed from zero and remains labelled unreviewed. A transform too large
for the existing plot paste limits is retained in the discovery JSON instead.
The JSON records matched values, operations, and index ranges. This is a bounded
local discovery tool, not a full OEIS search or an identity/novelty test.

Copy discovery link deliberately includes the entered terms and comparison
option; no background queries are sent to OEIS. The explicit external link uses
signed term search. The local example follows squares to odd first differences.
Topic links offer a compact browse index, and Random entry opens a local record.

Entry pages now have permanent section anchors for definitions/indexing,
formulas/recurrences, worked examples, programs, computed connections, exact
data, and references. The program block is a named keyboard-focusable scroll region, including without JavaScript. Copyable self-contained Python programs reproduce the
first sixteen terms with the standard library. Four exact transforms are
checked over twelve terms to suggest cross-references; each is labelled with
both index origins and finite scope. Similar-topic navigation is separate.
The full snapshot comparison remains in catalogue JSON; pages show at most
twelve hits per entry, with its declared OEIS reference first when present.

## Reading interface and index conventions

The atlas uses linked Browse, Discover, Plot, All entries, and About workspaces.
JavaScript shows one workspace at a time; native fragment links and the full
catalogue remain available without JavaScript. Browser Back/Forward restores
workspace selection. Search, discovery, and plot controls retain their values
when switching. Opening a search/discovery match selects Plot, while searching
displayed values selects Browse. Ctrl+/ (Command+/ on Mac) outside a form field opens Browse and
focuses search. Leaving Plot pauses modulus animation. All entries always
shows the entire catalogue independently of the current search query.

Entry pages place the identifier, status, primary actions, and first eight
values at the top. A contents sidebar becomes a horizontal section menu on
phones. Search from an entry submits a normal catalogue URL. Formula rendering
uses the existing accessible MathJax runtime, with an open plain-text formula
when JavaScript or the math runtime is unavailable. Formula copying always
uses the unchanged plain-text definition, independent of the rendered SVG.

Each record includes a specific definition, the meaning and domain of n,
local offset, value convention, and an exact six-row index map. Reciprocal
entries distinguish compressed index n from ordinary degree Nn, and show the
ordinary coefficient a(n)/(Nn)! beside the stored factorial-weighted integer.
Signed Euler entries distinguish n from Euler index 2n without extra factorial
scaling. Direct reference sequences use their stated n with no shift.

The entry term inspector reads the 64 stored values, reports the source index
and exact normalization, and can copy a value or link to its data-table row.
Term links use #n-0 through #n-63 and do not change the indexing convention.
The mathematical domain n>=0 and the finite stored range 0..63 are stated
separately. Snapshot positions remain zero-based excerpt positions; OEIS
mathematical offsets are not inferred from them. The explanatory model draws
on the [OEIS offset guidance](https://oeis.org/wiki/Offsets).

Reading metadata is maintained in tools/sequence_atlas_reading.py. It does not
change sequence generators or any of the 2,432 stored values. The metadata is
included in entry JSON under reading; existing formula and term fields are
preserved. Index-map fractions are computed with Python Fraction and the
browser inspector uses exact BigInt arithmetic. Browser checks cover all 38
formula renderings and representative reciprocal, Euler, and direct-index
records at desktop, phone, and 320px widths, including plain-text fallbacks.

## Study exact values

Each entry has a Study section, also reachable directly from search results.
Eleven views show original terms, first/second differences, partial sums,
successive ratios, running averages, alternating signs, absolute values,
binomial/inverse binomial transforms, and residues modulo 2 through 128.
The window covers 2–32 index positions among the 64 stored terms. Moving it
does not reindex values: sums, averages, and binomial transforms still start
at zero, and sign alternation uses the original n. Ratios use reduced exact
fractions; division by zero and initial differences retain undefined positions.

Sample statistics count signs, integer parity, and defined values. The GCD
is reported only for a nonempty integer-valued sample; all-zero samples have
GCD zero. A separate table shows backward differences of orders 0–4 of the
original stored integers, before the chosen transform, across up to eight
indices. Constant-row observations use the whole selected window and require
at least four defined values. They are finite observations, never polynomial
proofs or inferred infinite identities.

Search and discovery actions use only an initial consecutive run of defined
integers, without crossing missing or fractional values. Search sends up to
eight integers within its 2,000-digit limit; discovery requires at least six
with at most 300 digits each. The action note reports how many are used and
that discovery reindexes its input from zero. Other values remain available
in indexed copies and exact CSV/JSON downloads. CSV retains every n and a
defined flag; JSON retains undefined positions as null and records the
transform, window, modulus, conventions, and finite observations.
Plot links select signed-log scale when a defined value or the full signed
range exceeds linear floating-point coordinates; modular plots stay linear.
The link names the signed-log choice, while the study table remains exact.

Copy study link preserves the applied state, and browser Back/Forward restores
it. Invalid links display a message and the first twelve original terms;
invalid form edits retain the last valid results. Prefix operations, exports
and difference tables use exact arithmetic throughout. The initial original
terms, sample statistics, and expandable difference table are generated in
Python and remain readable without JavaScript. Controls are an enhancement.

The independent Fraction-based Python study oracle lives in
`tools/sequence_atlas_study.py`; the browser engine and interface are
`website/assets/sequence-atlas-study.mjs` and `sequence-atlas-study.js`.
The Node study test compares rows, statistics, and difference ladders in
1,482 windows across all 38 entries, eleven transforms, moduli 2, 7, and 128,
and three index windows. The separate Edge study suite covers responsive
controls, exact exports, linked search/plot, history, copy fallback,
no-JavaScript reading and 200% text with forced colors.

## Directory and connection evidence

All entries opens a compact alphabetical directory. Letter links work without
JavaScript; the enhanced form adds the existing exact query syntax, topic
filters, identifier ordering, and a filter for entries with incoming or
outgoing computed connections. These settings are independent of Browse.
Copy directory link retains the applied settings; Back/Forward restores them,
including a return from identifier order to a letter anchor. Invalid links
show the full alphabetical index with an explanation, while invalid form
edits retain the previous results. The current workspace stays visible in
the horizontal mode menu on narrow screens.
Copied directory links include only directory settings. Local history retains
the existing Browse/Plot context, while copied directory links omit unrelated
queries, pasted plot terms, and discovery input.

Each row links to the entry, its Study section, and any connections. The
reciprocal family index provides all 21 N/r pairs, with N mapping compressed
n to ordinary degree Nn and r fixed. Expanded catalogue cards remain in a
separate disclosure. The full index CSV contains all 38 entries regardless
of the active filter, with metadata, public URLs, and incoming/outgoing counts.

Connection sections now list both outgoing and incoming evidence. They
preserve the seven existing directed checks; no new transforms or matches
are inferred. Each disclosure shows twelve exact comparisons with the
original source index, source integer, transformed value, target index, and
target integer. The 84 distinct comparisons appear in 14 disclosures across
the six participating entries. For example, partial sums of odd numbers at
source n=0..11 match squares at target n=1..12. The reverse listing retains
this direction and does not infer an inverse transform or an infinite identity.
Study links load the source transform or untransformed target at its recorded
indices. Evidence tables remain available without JavaScript, with focusable
scroll regions and a fixed source-index column.

`assets/sequence-atlas-connections.json` retains the seven directed edges,
their exact rows, operations, index ranges, scope, and a SHA-256 signature of
all catalogue identifiers and stored terms. The graph and full index CSV are
generated by `tools/sequence_atlas_index.py`. Original entry JSON, generators,
formula strings, term arrays, and retained OEIS comparisons are preserved.
`website/assets/sequence-atlas-directory.mjs` reuses the search parser for
index filtering and supplies namespaced URL state. The directory/evidence
browser suite checks filtering, independent Browse state, copied links,
history, all 21 family cells, downloads, incoming/outgoing offsets,
source-to-Study actions, no-JavaScript keyboard scrolling, narrow layouts,
200% text with forced colors, and clipboard denial.

## Plot appearance, preferences, and research-record windows

Both plot interfaces have **Customize appearance and layout** controls for
palettes, a custom main color, point size, line weight, chart height, grid lines,
value-axis fitting, and endpoint or sparse index labels. Coincident labels are
combined instead of being printed over one another. Comparison marks retain
their separate shapes and line patterns. Modular plots and bars/stems retain
their zero baseline; other value plots can fit their observed range.

**Remember palette and layout** stores presentation preferences in this browser.
Copied view links contain the complete appearance and override the recipient's
saved settings. Denied or corrupt storage falls back to a usable default; it
does not prevent plotting. These preferences do not change terms or indexing.

Growth, residue, and difference presets provide starting views while retaining
the current sequence and index window. Research records also have valuation or
arithmetic-profile presets where appropriate, points/connected points/stems,
and coloring by the displayed value or original index modulo m. Lines connect
discrete samples; they do not add interpolated sequence data.

The research-record viewer adds window navigation, zoom in/out, and **Fit stored
data**. Every window stays within the record's original offset and stored range.
KOM084 additionally selects complete polynomial rows while retaining its flat
index j=n(n+1)/2+k. It never presents a flat index as the polynomial row number.

SVG exports include their styling and point titles; PNG exports use twice the
SVG canvas dimensions. Exact CSV exports remain available, and
all 384 existing KSEQ/KOM exact exports retain their data. Source definitions
and exact modular arithmetic are independent of the appearance choices.

Presentation preferences and image export live in
`website/assets/sequence-plot-options.mjs`; research-record rendering lives in
`sequence-archive-plot.mjs`. The pure window model remains in
`sequence-archive-core.mjs`. The plot browser suite covers three viewport widths,
preferences, shared links, exports, triangle rows, storage denial, forced colors,
and enlarged text. The finite checks are software checks, not accessibility
certification or new mathematical review.
