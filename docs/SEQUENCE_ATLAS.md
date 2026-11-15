# Sequence and Formula Atlas

[Open the atlas](https://komorebip.github.io/Operation-KOMOREBI/sequences.html) · [Sequence derivations](demonstrations/SEQUENCE_SHAPES.md)

The atlas organizes source-linked integer sequences and formulas, with exact
term tables and an interactive plot explorer. Its initial catalogue contains
the 21 published reciprocal families for N=2,…,8 and r=1,…,3, together with
Bell numbers, Fubini numbers, factorials, Fibonacci numbers, and signed even
Euler numbers. The identifiers KSEQ-000001 through KSEQ-000026 are stable.
New entries must be appended, preserving existing identifiers.

These are existing published families and classical reference sequences.
No entry or formula is claimed new. The atlas adds no Lean execution,
independent mathematical review, or change to the linked works’ proof status.

## Explore a sequence

Use sequence values, values modulo m, residue grids, residue frequencies,
successive-term pairs, or successive-residue plots. First and second differences, partial sums, successive ratios, and
running averages are available as transforms. Sums and averages start at
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
The bulk dumps are kept outside the public site. Only the small comparison
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
node --test tools/test_sequence_atlas.mjs tools/test_sequence_atlas_search.mjs
```

Each future entry needs a definition, indexing convention, source, exact
generator, finite test range, and separate formula/sequence originality
assessment. Add conjectural entries with an explicit conjecture label;
never infer novelty or proof from a matching result or a plot.
