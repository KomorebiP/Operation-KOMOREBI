# Maintain the reader website

The public site is at <https://KomorebiP.github.io/Operation-KOMOREBI/>.
Its source is in this repository. The site combines maintained collection
pages with documentation from two explicitly pinned library revisions.

All twelve core papers have formatted HTML reading editions. Each retains its
recorded mathematical scope; companion guides and atlas coverage are described
on the individual reading pages.

## Core visual-guide coverage

The **Browse → Core visual guides** directory at `read/visual-guides.html`
links every core paper's visual material, manuscript and evidence overview.
HTML status follows the maintained reading configuration; PDF destinations
and hashes come from the existing source receipts. Paper I's visual atlas is
inside its main monograph. The other eleven have separate visual-guide PDFs.

The [current inventory](../verification/reader-visual-guides/2026-11-02-final.json)
checks the committed visual sources against their receipts and identifies the
complete ports. Counts below describe source units, which vary by guide;
they are not counts of theorems or PDF pages. The
[initial inventory](../verification/reader-visual-guides/2026-11-02.json) retains
the earlier four-atlas snapshot.

| Paper | Retained visual source | HTML visual coverage |
|---|---|---|
| I | 22 plates | Complete |
| II | 24 plates | Complete |
| III | 24 plates | Complete |
| IV | 26 plates | Complete |
| V | 40 plates | Complete |
| VI | 42 plates | Complete |
| VII | 40 plates | Complete |
| VIII | 32 plates across two inputs | Complete |
| IX | 23 sections across two inputs, plus a generated coefficient input | Complete |
| X | 30 plates, two opening scope sections and their diagram | Complete |
| XI | 47 lessons, opening orientation and two reader-route sections | Complete |
| XII | 27 plates, including final claim and evidence records | Complete |

All twelve core papers now have complete HTML visual guides. Paper XI retains
all 47 lessons, 23 original vector figures, three source tables, six recorded-data
tables, the opening orientation and both reader-route sections. Its conversion
preserves 436 mathematical expressions and 66 manuscript return links. The
historical theorem number, open Conjecture 66 and same-candidate H5 comparison
remain distinct. Placeholder companion aliases resolve to the actual reader PDFs.

Paper XII retains all 27 plates, 23 drawings (including two embedded directly in
the page source), 335 selectable labels and 15 source tables. Its conversion
preserves 752 mathematical expressions and 53 manuscript return links. The
revised contract, historical original wording and evidence kinds retain their
source distinctions. The unused `support_rotated` drawing stays in the archive.

`render_paper_xi_atlas.py` checks all 47 lesson titles and three opening pages in
the retained 53-page PDF, then renders its original single-page vector figures.
`render_paper_xii_atlas.py` checks all 27 titles in the retained 28-page PDF and
renders the original drawing regions. These conversions do not rebuild TeX,
run mathematical generators or examples, audit proofs, or replay Lean. The new
atlas tests run alongside the existing source and website checks in CI.

Source-page line wrappers use compact HTML attribute syntax. The generated
class names and fragment links are safe ASCII tokens; optional quotes
are omitted to save six bytes per source line. Original source bytes,
whitespace, accessible line labels and browser DOM values remain unchanged.

Run `python -B tools/audit_core_visual_guides.py` to inspect the current coverage.
The report identifies the committed source revision and states that HTML
configuration is read from the working tree. `test_core_visual_guides.py`
checks the twelve destinations and distinct integrated/separate PDF routes.

Paper I's complete atlas is at `read/paper-i/atlas/`. Its 22 plates preserve
20 original monograph drawings, 435 selectable labels, and 699 mathematical
expressions, including formulas in the plate headings. Native source theorem
references resolve to manuscript passages with return links. The path, cycle,
coordinate-ring and evidence plates also link their explicitly selected source
sections. Three source tables and the matrix-label transcripts have semantic
headers. The first source table has no printed headings; its reading-aid
headings retain all three original data rows.

`tools/paper_i_atlas.py` records the source, macro and figure identities in
`documents/paper-i-atlas.json`. PDF routes keep the integrated monograph's
physical pages 83–104. To regenerate only those original drawing views, use
`python -B tools/render_paper_i_atlas.py` with pypdfium2 available. Normal
builds need no PDF renderer or TeX engine. Run
`python -B -m unittest discover -s tools -p 'test_paper_i_atlas.py' -v`.
This conversion adds no proof audit, mathematical example run or Lean replay.

Papers II and III each have a complete atlas at `read/paper-ii/atlas/` and
`read/paper-iii/atlas/`. Each retains 24 plates and 22 original PDF drawings.
Paper II preserves 754 selectable labels, 1,043 mathematical expressions, and
40 manuscript routes; Paper III preserves 488 labels, 747 expressions, and
44 routes. Each manuscript destination has a return link. Four source tables
and the gridded matrix-label transcripts retain semantic headers. Both PDFs
have two front-matter pages, so V1–V24 open physical pages 3–26.

`tools/worked_visual_atlas.py` implements these two source-bound conversions;
`tools/core_worked_atlases.py` declares the source table schemas. Figure sources,
PDF hashes, physical pages and crop bounds are recorded in
`tools/worked_atlas_sources.py` and the per-paper figure receipts. Render the
unchanged drawings with `python -B tools/render_worked_atlases.py`; ordinary
website builds use the committed images and need no PDF renderer or TeX engine.
Paper II's multiline drawing label retains both formulas, and V24 includes its
separate current-scope source verbatim with a source link. Its recorded counts
are inherited evidence statements, not a new replay. The verifier reconstructs
the numbered manuscript destinations from the published source chapters and
rejects reachable-but-wrong destinations. Run
`python -B -m unittest discover -s tools -p 'test_core_worked_atlases.py' -v`.
The mathematical proofreading self-review covers the new presentation wrappers,
labels, descriptions, source references and tables. No mathematical tokens or
imported manuscript bytes are changed; no new proof audit, exact example run or
Lean replay is claimed.

Paper VIII's complete standalone guide is at `read/paper-viii/atlas/`: 32
plates, 30 original PDF drawings, 711 selectable drawing labels, 830 mathematical
expressions, three source tables, and 84 manuscript routes with return links.
Both standalone source inputs retain their own source-line links. Four literal
TikZ loops in the extension drawings are expanded with their original node lines
and explicit bindings; unreviewed values or loops stop conversion.

The audit found that the inherited reference crosswalk records PDF checksum
`63d0a88a9f5e055c9ddb4e862cb8ee7549342c8bb890c2f15c1c035423097801`, while both
retained visual PDF copies have checksum
`a78f1c18c7c36cecbaf9484bc6dc643300c3b5054df338f48be6390af5e520c7`.
The selected PDF is retained. All 32 titles, printed locators and page labels
were independently checked against its physical pages 3–34. The crosswalk's
stable labels, statement numbers, kinds and titles are rechecked against the
current manuscript source. The one declared kind translation is `fact:cg`:
the guide's “Classical input 7.5” is the current manuscript's “Standard fact 7.5”.
The original source, crosswalk and PDF bytes are unchanged. The conversion record
and provenance details disclose the stale checksum rather than treating it as a
current PDF identity certificate.

`tools/paper_viii_atlas.py` uses the shared worked-atlas renderer and emits
`documents/paper-viii-atlas.json`. `tools/paper_viii_atlas_sources.py` records the
two source inputs, exact crosswalk identity, current PDF and reviewed crop bounds.
`python -B tools/render_paper_viii_atlas.py` rechecks all PDF pages and regenerates
the drawing views with pypdfium2; normal website builds need no PDF renderer.
For V15, the recipe renders its 48 original resized drawing objects alone to
exclude adjacent page prose from the crop. The PDF file and drawing objects are
unchanged; no PDF is saved and no TeX is rebuilt.
Run `python -B -m unittest discover -s tools -p 'test_paper_viii_atlas.py' -v`.
The mathematical proofreading self-review covers the presentation wrappers,
labels, descriptions, references and tables. Mathematical tokens are preserved;
this conversion adds no proof audit, mathematical example run or Lean replay.

The **Komorebi Methodology** also has a complete HTML edition at
`read/komorebi-methodology/`: preface, nine essay chapters, closing reflection,
verification notes, and references. Its 12 text pages preserve 164 mathematical
expressions, three numbered equations, nine references, and the three original
diagrams. [The proofreading and conversion record](reviews/KOMOREBI_METHODOLOGY_2026-11-02.md)
states the review scope and validation. The source package and PDF are unchanged.
`tools/methodology_sections.json` binds the exact source ranges and identities;
`tools/methodology_reading.py` translates only the reviewed print wrappers.
Run `python -B -m unittest discover -s tools -p 'test_methodology_reading.py' -v`
to check the complete edition, source drift, numbering, equations, figures, and
chapter/citation links. This conversion adds no proof audit or Lean coverage.

Komorebi Space and Realization Boundaries also have complete HTML editions at
`read/komorebi-space/` and `read/realization-boundaries/`. Their 52 source sections
retain 137 proof blocks, 46 original figures and 4,828 mathematical expressions.
`tools/foundational_reading.py` translates declared print wrappers;
`tools/foundational_sections.json` fixes the source ranges, input order, source
identities and accessible table headers. A changed source requires a reviewed
selection. Equation and theorem numbers follow each book's printed counters.
The statement finder links adjacent written proofs without adding formal claims.

Figure receipts in `website/assets/figures/komorebi-space/` and
`website/assets/figures/realization-boundaries/` identify the retained source and
browser image. Space's TikZ diagrams are rendered from the retained book PDF;
the receipt records the PDF identity, page and crop. Standalone plots and
Boundaries diagrams use their retained figure assets. Captions remain selectable
HTML. This presentation adds no mathematical review or Lean execution.
`tools/render_foundational_figures.py` reproduces the images from those receipts
with pypdfium2; it is separate from the normal website build.

Run `python -B -m unittest discover -s tools -p 'test_foundational_reading.py' -v`
to check both complete editions, source changes, formula preservation and HTML
structure. The normal site checker also checks their navigation and source links.

Quantum and Circuits has a complete HTML reading edition at
`read/monographs-quantum-and-circuits/`: chapters 1–21, appendices A–F and back matter in 206 topic pages,
with 233 numbered statements, 120 written proofs, 82 original scientific figures
in 85 manuscript appearances, 61 accessible tables, and 4,200 mathematical
expressions. The contents page groups the main chapters, appendices, glossary and sources,
with a preface and volume guide retaining the part introductions and general glossary. `tools/quantum_reading.py` translates the retained print wrappers;
`tools/quantum_sections.json` binds complete source ranges, original identities,
chapter groups and table headers. Authored QA labels and source-line links stay
intact. `tools/quantum_symmetry.py` retains the symmetry treatment's chapter-wide
statement, equation and figure numbering, its scope panels, and all twelve open
questions. The 21 numbered equations remain part of the complete mathematical
sequence; identical longtable continuation headers appear once in HTML.
`tools/quantum_catalytic.py` adds the complete catalytic treatment: 28 topic
pages, 134 numbered statements, 51 proofs, 32 figures in 34 appearances,
15 tables, six literal listings, and 1,906 mathematical expressions. The six
numbered gates in the linear atom appear as separate displays, retaining their
original equation numbers and source lines. The eight explicitly named proofs
have links from their earlier statements and return links across chapter pages.
`tools/quantum_circuits.py` adds chapters 13–20 in 23 topics and the complete
25-topic circuit visual study: 30 numbered results with written proofs, 12
original figures, ten tables, two literal reproduction listings, and 775
mathematical expressions. It preserves C01–C08 claim labels, five named scope
panels, and six printed equation numbers. The binary-field main treatment and
general-field visual scope retain their separate macro contexts. The Appendix E.4 citation now opens the HTML evidence ledger. All 54
collected references retain their original numbering.
`tools/quantum_companions.py` completes the reading edition with 58 pages:
the volume orientation, appendices A–F, glossary and source notes. The new
pages add 314 mathematical expressions, 30 accessible tables, and 157 literal
code extracts. All 115 circuit declaration types retain their full Unicode
text, source locators, block labels and axiom sets. The arithmetic guide keeps
its 96-theorem inventory and its distinct inherited checkpoints. Visible scope
notes distinguish retained verification statements from this HTML conversion.
The 30-entry circuit result index keeps its printed page column, linking the
original PDF at the corresponding physical page; its source digest and page
map are in `tools/quantum_sections.json`. Recheck the PDF map with `python -B tools/check_quantum_pdf_pages.py`
(using the same PDFium dependency as the figure helpers). The volume guide routes all 21
chapters and six appendices to their first HTML topics. Literal code bodies
are protected before any print-wrapper translation, and source lines remain
unchanged. The complete sequence has 207 pages including references. The former
`#source-continuations` bookmark remains an alias for the complete contents.
The shared statement finder links all written proofs without adding Lean
correspondences. This presentation adds no mathematical review or Lean replay.

The arithmetic figure receipts and browser images are in
`website/assets/figures/quantum-arithmetic/`; symmetry figures and receipts are in
`website/assets/figures/quantum-symmetry/`; catalytic figures are in
`website/assets/figures/quantum-catalytic/`; circuit figures are in
`website/assets/figures/quantum-circuits/`. Reproduce them from the original
single-page PDFs with `python -B tools/render_quantum_figures.py` and
`python -B tools/render_symmetry_figures.py`, plus
`python -B tools/render_catalytic_figures.py` and
`python -B tools/render_circuit_figures.py`. Normal site builds check their
source identities and publish the retained PNGs. Figure receipts default to one
use; the symmetry compiler diagram and catalytic Pareto and packet diagrams
explicitly record their two appearances. Run
`python -B -m unittest discover -s tools -p 'test_quantum_reading.py' -v` for the
complete edition, formula sequence, proof routes, tables and source anchors.

Reading editions keep one complete, native chapter menu in the top navigation.
Quantum and Circuits also provides `read/monographs-quantum-and-circuits/start.html`:
three editorial reading paths with prerequisites, chapter links, and checkpoints.
The visual tour, four-treatment study route, and formal companion link into the
retained edition. Its contents, reading-library card, work overview, and search
entry expose the guide without changing the chapter sequence.

Footers keep previous/next links and a direct Full contents link, avoiding the
quadratic storage cost of repeating a second full menu on every topic page.
Atlas-specific menus retain their existing behavior. The site-size guard
continues to enforce the 1 GiB GitHub Pages ceiling.

The twelve core editions share collection switching, chapter filtering,
persistent text size and font choices, and sidebar chapter shortcuts. The
[control renderer](../tools/reader_usability.py) runs after chapter layout and
preserves manuscript text and mathematics. [Reading tools](../website/assets/reading-tools.js)
enhance native links and disclosures; full chapter lists and paper switching
remain usable without JavaScript. Text preferences tolerate unavailable or
invalid browser storage. Keep these controls in the shared renderer rather than
adding separate versions to individual papers. Run
`python -B -m unittest discover -s tools -p 'test_reader_usability.py' -v` along
with the reading-navigation and source-preservation checks when changing them.

Inline formulas retain their source and full rendering scale while scrolling
within the available text width on narrow screens and with enlarged text.
The shared reader adds a named keyboard scroll stop only when a formula
overflows, and rechecks after typesetting, resizing, text preferences and live
search results. Existing accessible names and author-supplied focus settings
are retained. CSS provides touch scrolling without JavaScript; print layout
removes the scrolling treatment. Run `node tools/test_math_overflow.cjs` for
the adaptive keyboard behavior and check a real rendered chapter at narrow
phone widths with extra-large text.

Direct passage links and in-page navigation correct their scroll position once
MathJax and web fonts have finished loading. This correction retains the target
and existing browser history. Pointer, touch, wheel and keyboard input cancel
the pending correction, as do a newer destination, changed focus or a removed
passage. Readers who have already interacted before page load keep their place.
Run `node tools/test_reader_navigation.cjs` for delayed layout, cancellation,
safe hashes, disclosure opening and browser-history behavior.

[Citation and figure navigation](../tools/reading_links.py) adds native links
to the existing figure assets and return links from bibliography entries to
their citing HTML passages. Return routes are derived from the rendered
canonical chapters after each book is built. They retain the nearest source
passage anchor and deduplicate repeated citations within one passage. The site
verifier recomputes those routes and checks their placement and targets. Run
`test_reading_links.py` when changing this code. Bibliography search enhances the
original entries in the browser; direct links and Back/Forward reveal an entry
that a search has hidden. Print styles restore the complete bibliography.

All core chapter statement indexes are rendered from the existing statement
nodes and proof routes. [Statement matching](../website/assets/statement-search.js)
supports printed numbers, types, source labels and Greek names. Keep proof-link
filtering tied to actual rendered links. The [statement-index verifier](../tools/statement_navigation.py)
checks complete coverage, source labels, order and agreement with the proof
links in each passage. Run `test_statement_navigation.py` and
`node --test tools/test_statement_search.cjs` when changing these controls.

Each core paper also has `read/<paper>/statements.html`, linked as **Find
statements** from its shared reading controls. The directory uses the same
statement-entry renderer and recorded proof routes, grouped in chapter order.
Search hides empty chapter groups; the native full list remains usable without
JavaScript, and print styles restore all groups. Switching papers from a finder
opens the other paper's finder. The verifier checks every directory entry,
chapter context, title and destination against the canonical chapter indexes.
Finder filters use `q` and `proof=1` query parameters, updated with replaceState.
Page restoration and Back/Forward apply the URL filters after native form-state
restoration. Preserve unrelated query parameters and anchors when updating them.

[Reference previews](../tools/reference_previews.py) audit marked reference and
citation links after the canonical chapters and bibliography are rendered.
Each paper's lazy-loaded JSON contains inert text/element trees from those
destinations. Equation labels are retained as metadata before their print-only
TeX commands are removed, so formulas sharing a passage can be selected exactly.
Excerpts end at whole blocks and formulas; section excerpts and omitted content
are identified in the dialog. The site verifier regenerates every entry and
checks it against the published JSON. Do not substitute generated summaries.
The browser creates an allowlisted DOM, keeps original hyperlinks, respects
text preferences, and guards against stale loads and wrong-paper data. Run
`test_reference_previews.py` and `node tools/test_reference_previews.cjs` when
changing this behavior, then check keyboard, phone, math and passage navigation
in real rendered chapters.
For same-document Back navigation, previews mark the restored control with
`data-reading-history-focus` containing the current URL. The generic hash
handler consumes that marker once, preserving the explicit focus return while
continuing to handle ordinary or unrelated fragment navigation.

## Inspect Lean

**Inspect Lean** opens a source directory for the works that already have HTML
reading editions and selected Lean resources. It is linked from their reading
controls, work overviews, claim routes and the Browse menu. File filtering
matches paths and lexical declaration names; `q` in the address retains the
filter. The complete native file list works without JavaScript.

The inspector groups core papers and books separately. File lists show the
filename and module folder, with their shared source root under **Source
locations and editions**. Full retained paths remain searchable. Source pages
use filename headings and a compact row of reading, download and comparison
actions. Coverage labels stay visible; their descriptions and evidence routes
use a native disclosure. The original source bytes and line anchors are retained.

Lean source views color comments, strings, keywords, tactics, and numbers while
retaining the original text and line anchors. On wide screens a declaration
outline stays beside the code; phones and comparison panes use a native
disclosure. Its optional name/kind filter changes the outline only. The source
verifier extracts rendered code text and compares every line with the original
download, independently of its token spans. Colors and declaration names are
navigation aids, not a Lean compiler result.

The inspector expands only receipt-owned `.lean` files within the existing
Lean resource selections. It excludes package caches, build directories and
`lakefile.lean`. Original source readers retain exact downloads, linked line
numbers, existing claim correspondence and SHA-256 provenance. Declaration
locations ignore nested comments and strings, and provide navigation only;
anonymous, generated or unusually formatted declarations may be omitted.
Coverage labels and evidence links retain the current recorded assessment.
The viewer does not execute Lean or add claim mappings.

Implementation lives in `tools/lean_reader.py` and `lean-reader.js`/`.css`.
The website workflow runs `test_lean_reader.py` and `test_lean_reader.cjs`;
the full site verifier checks published source identities and declaration
locations against `lean/index.json`.

## Sources

| Content | Source |
|---|---|
| Work titles and source ownership | [Source index](../manifests/source-components.json) and import receipts |
| Completion, Lean coverage, confidence and limits | [Project status](../manifests/project-status.json) |
| Selected reading, proof, Lean and code files | [Browse resources](../manifests/browse-resources.json) |
| Introductory terminology and background advice | [Reader experience](../manifests/reader-experience.json) |
| Core-paper questions, scope and first reading paths | [Paper introductions](../manifests/paper-introductions.json) and [guidance renderer](../tools/reader_guidance.py) |
| Hand-worked calculations and exercises | [Example index](HAND_WORKED_EXAMPLES.md), [tutorial pages](examples/) and [exact arithmetic checker](../tools/check_hand_examples.py) |
| Statement locations for all 12 core papers and retained Paper I declaration mappings | [Claim navigation](../manifests/claim-navigation.json), bound to the retained source records |
| Library source revisions | [Website library revisions](../manifests/reader-site-libraries.json) |
| Page structure and browser behavior | [Website assets](../website/assets/) and [site builder](../tools/build_reader_site.py) |
| Local PDF and source reading pages | [Document publisher](../tools/reader_documents.py) and receipt-bound source files |
| Embedded PDF reader | [Pinned PDF.js fetch and verification](../tools/fetch_pdf_runtime.py) |

Reading routes, glossary, download guides and work introductions are generated
with the collection's normal status command. Edit their source records or
templates. Keep each claim's exact recorded scope when changing navigation.

The homepage keeps its five research previews in one manually selected panel,
with named topic tabs, previous/next buttons, touch swipes, and standard tab-list
keyboard controls (Left/Right, Home/End). It never advances automatically. All
five sections and their reading links remain visible without JavaScript. The
four reading routes and a short tools row stay outside the slides. Homepage
content lives in `tools/home_page.py`; its styles and behavior load only on the
homepage from `website/assets/home.css` and `home-slides.js`.

The collection keeps title search and discipline selection visible. Completion,
Lean coverage, evidence, publication type and page size live under **Advanced
filters**. Shared filter URLs reopen that panel when an advanced selection is
active. Work overviews use one reading toolbar, with specialist links under
**More resources**; existing section and return anchors remain available.

HTML chapters use compact previous/next controls and a section contents panel.
On wide screens the panel stays beside the text and marks the current section.
In narrow windows, including comparison panes, it becomes a sticky **Contents**
disclosure that closes after a section is selected. Contents and resource links
remain native disclosures without JavaScript. These controls rearrange the
reading interface without changing the manuscript article or its passage IDs.

The section panel keeps **Work overview** and **Full contents** links available
while reading a chapter, so a link into a definition still has a visible route
back to the introduction. They share one compact row with Previous and Next;
the core-paper enhancements reuse this row. On narrow screens, anchor spacing follows the actual
height of these controls, including wrapped text. The links work without scripting;
the site checker verifies that they return to the matching work and reading index.

The twelve core-paper overviews introduce the central question, contribution,
assumptions and limits, followed by an example → setup/definition → result →
proof route. Edit the paper-introduction manifest for that editorial copy.
Each example must already belong to the paper's learning topics. Setup lines
are checked against receipt-bound source text; result and proof links use the
existing claim index. Where an HTML chapter is available the links open that
passage, otherwise they use the on-site source reader.

**Notation help** opens a chapter-local search dialog and downloads only the
current work's compact index when opened. It reuses the notation search's
case-sensitive symbol ranking and source contexts. A notation-table result
keeps the whole row's subject and meaning together; an occurrence inside a
definition is shown as a passage, rather than treated as a definition of every
symbol it contains. Closing the dialog returns keyboard focus to its control.
Without scripting or dialog support, the ordinary notation-index link remains.

The `learning_topics` records in the reader experience manifest generate the
[topic map](LEARNING_MAP.md), the source routes at the end of each tutorial,
and return links on the related work pages. Edit tutorial explanations above
the `learning-navigation` marker. The status command replaces the section
below that marker. A subject route does not establish a theorem correspondence.

## Saved reading

**Browse → Saved reading** opens a personal list of pages and passages stored in
this browser. Reading pages offer **Save page**, and section headings have a
bookmark control that retains the exact fragment. The list supports title,
paper and section search, individual removal, and updates across open tabs.
It records explicit saves only. Storage failures leave save controls unchanged
and explain how to use browser bookmarks instead. Without JavaScript, the
ordinary reading links and browser bookmarks remain available.

The page and controls are built by `tools/reading_list.py`; browser behavior and
styles live in `website/assets/reading-list.js` and `reading-list.css`. URL and
storage guards keep saved links inside this site's reading pages. The site
workflow runs the rendering and browser-state regressions alongside reader tests.

## Paper V HTML reading edition

[Paper V](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-v/index.html)
has 40 reading pages plus contents and bibliography. Its contiguous source ranges
retain both manuscript branches, four appendices, 1,219 mathematical expressions,
83 proof bodies, 35 manuscript figures and ten tables. Chapter navigation uses
the shared reading controls. All forty visual-atlas plates also have HTML pages
at `read/paper-v/atlas/`, retaining 37 drawings, 550 selectable TikZ labels,
962 mathematical expressions, six semantic tables, original source-line links
and 73 manuscript links with return routes.
The reused Gibbs plot has a separate text description; its labels remain in
the original image and PDF. Historical computation totals retain their
source-edition scope and do not describe a new execution during conversion.

`tools/paper_v_atlas.py` checks plate numbering, source and image identities,
the complete equation sequence and both directions of manuscript links.
`documents/paper-v-atlas.json` records those checks. Regenerate the reviewed
PDF crops with `python -B tools/render_paper_v_atlas.py` (pypdfium2 required).
Normal builds verify committed images without a PDF renderer or TeX compiler.
Run `python -B -m unittest discover -s tools -p 'test_paper_v_atlas.py' -v`.

The [chapter configuration](../tools/paper_v_chapters.py) records the original
line ranges and E-prefixed numbering. The [figure publisher](../tools/reader_figure_assets.py)
checks the retained PDF sources and their rendered PNG hashes. Normal builds
verify those images; the [figure renderer](../tools/build_paper_v_figures.py)
is needed only to regenerate them. Run
`python -B -m unittest discover -s tools -p 'test_paper_v_reading.py'`
to check the complete equation sequence, statement/proof routes, numbering,
tables and figure identities. The wavelet walkthrough and Haar lab link directly
to the related HTML chapters. Historical formal and experimental scope remains
attached to the edition; this conversion adds no proof review or Lean replay.

## Paper VI worked visual atlas

[All 42 Paper VI atlas plates](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vi/atlas/index.html)
have HTML pages. The conversion retains 40 original drawings, 588 selectable
drawing labels and 931 expressions, with 76 manuscript passage links and
return links. The two evidence-guide plates retain their original wording
and link to the work's evidence record. Existing plate URLs and index anchors
remain available; the five previously published drawing images are unchanged.

The [atlas renderer](../tools/paper_vi_atlas.py) verifies source correspondence,
figure identities, table cells and both directions of the manuscript links.
The [shared transcript parser](../tools/reader_drawing_transcripts.py) also
serves Paper VII without changing its retained mathematics. Conversion records
are published in `documents/paper-vi-atlas.json`. To regenerate only the
frozen-PDF crops, run `python tools/render_paper_vi_atlas.py --pdftoppm PATH`.
The website build checks the assets and requires no TeX compiler. This
conversion adds no mathematical example execution, proof audit or Lean replay.

## Paper VIII HTML reading edition

[Paper VIII](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-viii/index.html)
has 23 reading pages, contents and a bibliography: the opening orientation,
three exact models, 15 manuscript sections and Appendices A–F. The conversion
retains 1,192 mathematical expressions, 56 proof bodies, 25 figures and 12
tables. Numbering is checked against the retained compiled labels. The worked
visual atlas remains in the original PDF.

The [chapter configuration](../tools/paper_viii_reading.py) fixes source ranges,
appendix transitions and table reading aids. Tables with grouped columns retain
their column groups; tables printed in parallel retain both row-header columns.
The shared figure publisher checks the original PDF and rendered PNG digests.
Use [the figure renderer](../tools/build_paper_viii_figures.py) with `--pdftoppm`
only when regenerating those assets. Normal builds need no PDF renderer.

Run `python -B -m unittest discover -s tools -p 'test_paper_viii_reading.py'`
to check complete source coverage, equation order, printed numbering,
statement/proof routes, figure identity, tables and internal links. The website
workflow runs these checks before publication. This reading conversion adds no
proof assessment, Lean replay or new hardware measurement.

## Paper IX HTML reading edition

[Paper IX](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ix/index.html)
has 56 reading pages and a bibliography. The route covers all 13 main sections,
the edition summary and all five mathematical appendices. It retains 5,252
mathematical expressions, 153 proof environments, 14 manuscript figures,
33 tables and all 27 bibliography entries. Historical headings and checkpoint
notices keep their source scope.

The [complete visual guide](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ix/atlas/index.html)
has 23 HTML sections, 20 original figures, 278 mathematical expressions, six
source tables and 35 manuscript routes with return links. The entrypoint
`sources/visual.tex` includes both `visual_body.tex` and `worked_atlas.tex`;
the latter includes the generated Newton coefficients. The older retained
`visual_README.md` still describes 15 sections and 12 figures. The audit follows
the actual input graph and checks the retained 25-page PDF instead of using that
stale inventory. All imported source bytes remain unchanged.

`tools/paper_ix_atlas.py` preserves source wording, captions, mathematical
sequences and line anchors. Figure math labels are read from the retained
generator's Python AST without executing it. Other native figure labels are
selectable PDF text, with descriptions and semantic data tables for reading
order. Tables project the retained exact records, including every residue in
the four displayed periods. The 5,490 illustration assertions and 463 worked
example checks are inherited records, not executions performed by this port.
Manuscript targets are reconstructed using the manuscript reader's own
normalization and printed-label map. `documents/paper-ix-atlas.json` records
these bindings and the stale README count.

Run `python -B tools/render_paper_ix_atlas.py` with pypdfium2 to check all 23
PDF section titles and render the 20 retained vector figures. Normal builds
use frozen images and extraction receipts without PDF or TeX dependencies.
Run `python -B -m unittest discover -s tools -p 'test_paper_ix_atlas.py' -v`
for source coverage, formula preservation, transcripts, data tables and
two-way manuscript links. The mathematical proofreading self-review covers the
presentation, captions and labels; this port adds no mathematical proof audit,
new example execution or Lean replay.

The [chapter map](../tools/paper_ix_sections.json) fixes the reading ranges;
the [conversion module](../tools/paper_ix_reading.py) checks the complete input
graph and preserves original line anchors through Pandoc and print wrappers.
The [table aids](../tools/paper_ix_tables.json) bind reviewed headers and captions
to the retained source. Tables inside proofs remain inside their proof blocks.
The bibliography has a separate source-bound mathematical conversion record.

Run `python -B -m unittest discover -s tools -p 'test_paper_ix_reading.py'`
to check input coverage, printed numbering, equation order, tables, figures,
bibliography and reading links. No proof assessment or Lean replay is added.

## Paper X HTML reading edition

The [complete Paper X visual guide](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-x/atlas/index.html)
has 30 numbered HTML plates and retains both opening scope sections on its
contents page. Its 29 drawings include the opening diagram that distinguishes
the transported target family from the independently recovered carrier summand.
The guide retains 754 selectable labels, 969 mathematical expressions, two
source tables and 50 manuscript routes with return links.

The audit follows `visual_appendix/appendix.tex`, including its opening contract
and `source/pages.tex`. Physical PDF pages 2–3 hold the opening scopes; V1–V30
are pages 4–33. The historical 17/20, checked conditional 20/20 and later
unpromoted 19/20 records retain their different input contracts. Conversion
checks reconstruct all authored prose and table cells as well as the equations,
so changes to conditional scope wording fail verification.

`tools/paper_x_atlas.py` uses the shared worked-atlas renderer and emits
`documents/paper-x-atlas.json`. The source and crop bindings are in
`tools/paper_x_atlas_sources.json`. Three crops touch adjacent page prose:
V11, V19 and V22 render only the original drawing objects at scale 1.18541,
with independently checked counts of 104, 83 and 135 objects. No PDF is saved
or rebuilt. `python -B tools/render_paper_x_atlas.py` checks all 32 source
section titles and regenerates the 29 drawing views with pypdfium2.
Run `python -B -m unittest discover -s tools -p 'test_paper_x_atlas.py' -v`.
Descriptions were checked against the rendered figures. This presentation
conversion adds no proof audit, mathematical example execution or Lean replay.

Generated metadata JSON uses compact syntax to keep the reader within the
1 GiB publication limit. Parsing preserves every data value and all whitespace
inside source strings. Receipt-bound files under `documents/files/` and frozen
asset receipts retain their exact bytes. The site-size guard remains active.

[Paper X](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-x/index.html)
has 30 reading pages and a bibliography. It covers all 15 main sections,
the algorithms and reproducibility appendices, the dated Block 27 discussion,
the residue-counting continuation and the final conditional completion.
The conversion retains 1,080 mathematical expressions, all 16 main proof
bodies, 16 original figures, three tables and all 23 bibliography entries.
The complete visual guide is linked above; its retained PDF also remains available.

The [chapter map](../tools/paper_x_sections.json) fixes contiguous source
ranges. The [conversion module](../tools/paper_x_reading.py) checks every
authored input, preserves source-line anchors and expands the continuation's
literal notation macros. Headings within proofs remain inside their proof
blocks. Equation references retain the published numbering. The bibliography
has its own source-bound equation and reference record.

Run `python -B -m unittest discover -s tools -p 'test_paper_x_reading.py'`
to check coverage, numbering, statement/proof routes, figures, tables,
bibliography and mathematical order. Historical totals and the independent
outputs of the conditional endpoint retain their source qualifications.
This conversion adds no proof assessment or Lean execution.

## Paper XI HTML reading edition

[Paper XI](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-xi/index.html)
has 38 reading pages and a bibliography. All 19 main sections, 68 main proof
environments and fifteen construction appendices are retained. The conversion
preserves 1,030 typeset mathematical expressions, 275 literal derivation blocks,
16 original figures, five semantic tables and all 29 bibliography entries.
The visual, Lean and research companions remain available as PDFs.

The [chapter map](../tools/paper_xi_sections.json) fixes contiguous ranges and
authored input order. The [converter](../tools/paper_xi_reading.py) preserves
literal derivations, source-line anchors, published numbering and Conjecture 66's
open status. Internal companion route keys resolve through the retained reading
concordance to actual PDF pages. The bibliography follows the published order
and citation numbers, checked against the compiled labels.

The [figure renderer](../tools/build_paper_xi_figures.py) produces browser PNGs
from receipt-bound single-page PDFs. The shared publisher verifies the original
PDF and rendered PNG hashes; normal builds need no PDF renderer.

Run `python -B -m unittest discover -s tools -p 'test_paper_xi_reading.py'`
to check input coverage, numbering, literal and mathematical order, figures,
tables, companion routes and bibliography. The HTML conversion adds no proof
assessment, arithmetic realization result or Lean execution.

## Paper XII HTML reading edition

[Paper XII](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-xii/index.html)
has 16 reading pages and a bibliography, covering all 13 main sections, the
reading map and the full verification/revision record. The conversion retains
873 mathematical expressions, 52 proof bodies, all 82 statement environments,
18 original figures, two semantic tables and all 27 bibliography entries.
The visual and Lean/evidence companions remain available as PDFs.

The [chapter map](../tools/paper_xii_sections.json) fixes contiguous source
ranges. The [converter](../tools/paper_xii_reading.py) checks authored inputs,
equation order and source anchors. Companion route keys resolve through the
retained reading concordance to actual PDF pages. The ring-isomorphism heading
keeps its mathematics in the text and uses its plain PDF label in navigation.

The [figure renderer](../tools/build_paper_xii_figures.py) produces browser PNGs
from receipt-bound single-page PDFs. Normal builds verify the original PDF and
PNG hashes without requiring a renderer.

Run `python -B -m unittest discover -s tools -p 'test_paper_xii_reading.py'`
to check source coverage, numbering, mathematical order, proof links, figures,
tables, companion routes and bibliography. The conditional arithmetic inputs
and separate original/revised claim records retain their source scope.
This conversion adds no proof assessment or Lean execution.

## Special Functions hub and coupled-function lab

The [Special Functions hub](SPECIAL_FUNCTIONS.md) connects the current HTML
monograph, its five subject families, the five selected reading PDFs, and the
coupled recurrence's formal report and claim map. Its chapter links follow the
source-bound HTML edition. The preserved scientific figure retains its caption,
alternative text and intrinsic dimensions in the shared Markdown renderer.

The `special-functions-coupled` playground preset uses exact rational
coefficients, exports both coefficient lists as CSV, and distinguishes its local
series-tail envelope from floating-point plot evaluation. Run
`python -B -m unittest discover -s tools -p 'test_special_function_python.py'`
for its independent polynomial, closed-form, export and input controls. The
reader tests also check the hub's chapter and selected-source links. This
integration adds no formal replay or mathematical completion claim.

## Extended factorial-lanes example

The [factorial-lanes derivation](demonstrations/FACTORIAL_LANES.md) has an
independent exact program in [examples/factorial_lanes.py](../examples/factorial_lanes.py).
The [factorial publisher](../tools/factorial_case.py) provides a checked on-site
source reader and source-bound downloads. Its finite output snapshots live in
[verification/factorial-lanes/](../verification/factorial-lanes/). The site
checker validates their byte identities, while the workflow re-runs the
arithmetic and compares freshly emitted tables against the committed copies.

## Extended wavelet and polyphase transfer example

The [wavelet-polyphase walkthrough](demonstrations/WAVELET_POLYPHASE.md) extends
the existing four-level Haar lab with exact lifting, weighted detail selection,
a circular FIR filter, a complete four-level operator conjugacy, sharp finite
stability, operation-order counterexample and boundary correction. The
[exact program](../examples/wavelet_polyphase.py) uses rational arithmetic
for its mathematical checks. Six CSV tables, a JSON certificate, and two
Python-generated SVG figures are stored under
[verification/wavelet-polyphase/](../verification/wavelet-polyphase/).
The [publication bridge](../tools/wavelet_case.py) verifies source-bound
downloads and archives without running the program at build time. GitHub
Actions separately checks the program, exact output identity and site links.

## Extended Stirling, Bell and Fubini example

The [partition-transform derivation](demonstrations/STIRLING_BELL_FUBINI.md)
starts with exact Stirling numbers of the second kind, gives Bell and
factorial-weighted Fubini numbers and reverses the triangular transform
using signed Stirling numbers of the first kind. It then derives Touchard
polynomial evaluation, scaled exponential moments and the
Fubini reciprocal EGF, a general reversible Stirling substitution,
coupled residue transfers and a precise boundary between recoverable
polynomial data and noninjective row summaries.
The [standard-library checker](../examples/stirling_bell_fubini.py)
independently enumerates small partitions, verifies surjection counts,
triangular inverse matrices and formal series coefficients, and generates
seven CSV tables, a Python SVG figure and JSON checks.
The [publication bridge](../tools/stirling_case.py) rebuilds every record
from the retained program, binds the source identities and checksums,
and publishes a reproducible reader and download archive.

## Extended roots-of-unity and falling-factorial example

The [roots-of-unity / Newton walkthrough](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
takes the ordinary power x^5 through a primitive-cubic-residue projector,
the Stirling/Newton coordinate isomorphism, finite-difference transfer,
refinement and an induced multiplication law. It distinguishes transported
projectors from raw ordinary-degree filters using a concrete failed control.
The [standalone exact checker](../examples/roots_unity_falling_factorial.py)
uses standard-library rational arithmetic, an exact cyclic permutation trace
for root-of-unity orthogonality, direct enumeration of function images,
rational spectral polynomials in the backward-difference number operator,
filtered formal generating functions, general cross-packet translation
blocks, and independent matrix coefficients. The degree-operator spectral
formula's characteristic-three failure is an explicit control rather than
a theorem inferred beyond its rational coefficient scope.
The [publication bridge](../tools/roots_newton_case.py) regenerates eleven
CSV tables, three accessible Python SVGs, JSON checks, and a deterministic
source-and-results archive. Tests include reproducible bytes and
deliberately corrupted downloads.

The [quantum phase and measurement derivation](demonstrations/QUANTUM_PHASE_MEASUREMENT.md)
adds exact Gaussian-rational matrix calculations, three-setting tomography,
partial dephasing, coherent records, and packet refinement. Its
[standalone program](../examples/quantum_phase_measurement.py) generates two
CSV tables, a labelled SVG, and a JSON case summary. The
[publication bridge](../tools/quantum_case.py) binds the source, walkthrough,
and records to their SHA-256 identities in a deterministic ZIP. Pages CI
checks the arithmetic, expected output, reproducible bytes, and corruption
detection. The `physics-dephasing` playground preset exports editable exact
data. These finite teaching checks do not replay Lean.
The collection extension adds amplitude damping, a rational modulus-12
Ramanujan projector and phase family, and three-qubit bit-flip recovery.
Three additional CSVs and the `physics-arithmetic-phase` preset expose
the exact data. The expanded program checks 1,917 finite cases, including
the difference between syndrome measurement and full address measurement.

## Build locally

Use a complete collection checkout and separate checkouts of the two libraries
at the revisions in `manifests/reader-site-libraries.json`. Python 3.13 is used
by the website workflow. Choose fresh output directories for each build.

```text
python -m pip install -r website/requirements.txt
python -B tools/claim_navigation.py --check
python -B tools/update_completion_status.py --check
python -B tools/fetch_reader_runtime.py --output ../reader-runtime
python -B tools/fetch_pdf_runtime.py --output ../pdf-reader-runtime
python -B tools/fetch_python_runtime.py --output ../python-reader-runtime
git clone https://github.com/live-codes/browser-lean.git ../browser-lean
git -C ../browser-lean checkout a8aed095534e67061e2626b94e8e69193099091d
python -B tools/prepare_lean_wasm.py --source ../browser-lean --output ../lean-browser-runtime
python -B tools/build_reader_site.py --math-root ../komorebi-math --polyphase-root ../polyphase-float --mathjax-root ../reader-runtime --pdfjs-root ../pdf-reader-runtime --python-root ../python-reader-runtime --lean-wasm-root ../lean-browser-runtime --revision FULL_COLLECTION_COMMIT --output ../reader-site
python -B tools/check_reader_site.py --site ../reader-site
python -m http.server 8765 --directory ../reader-site
```

Replace `FULL_COLLECTION_COMMIT` with the output of `git rev-parse HEAD`.
The runtime fetches verify pinned digests before installing MathJax, PDF.js and Python.
The finished site serves both runtimes and its selected documents locally.
Source receipt mismatches or
missing reading files fail the build. The ZIPs identify their selected files
and do not claim to be standalone build environments.

The PDF catalogue includes the main papers, visual guides and formal companions
listed in the browse resources. The document publisher also renders edition
Markdown, shows source files with line links, and follows explicit local TeX
inputs. It never executes the manuscripts or programs. PDF page bookmarks and
Markdown line references retain their destinations. Documents without a PDF
keep their available source formats.

The build writes `documents/index.json` with the published file paths and source
identities. The site checker verifies those copies, embedded reader targets,
linked images and runtime integrity, in addition to HTML links and reading ZIPs.

## Readable chapters

Paper VII has 25 reading pages: the opening orientation, three exact finite
models, fifteen focused Part I topics, and all eight later source parts.
Measurements, Kraus channels and error correction have separate reading pages.
The chapters preserve the I, II and III numbering, original counter resets,
107 proof environments, and the same 1,820 mathematical expressions in order.
The complete Part I page retains its earlier URL and passage anchors.
All 38 original manuscript figures appear as inline PNGs with source captions,
reviewed text descriptions, full-size links and the original PDFs. The asset
record binds every PNG to its retained PDF with SHA-256 hashes and intrinsic
dimensions. All 40 worked visual-atlas plates also have HTML pages, with 38
original drawings, 547 selectable drawing labels, and 945 source expressions.
Each plate links to the manuscript passages it illustrates; those passages
link back to the plates. The atlas retains its wording and evidence limits.
This presentation adds no proof assessment or Lean execution.

The [atlas renderer](../tools/paper_vii_atlas.py) checks the prose and drawing
math sequences, finite label loops, source hashes, image sizes, and both
directions of the manuscript links. `documents/paper-vii-atlas.json` records
the conversion. Drawings are reviewed crops of the frozen monograph PDF;
rebuild them with `python tools/render_paper_vii_atlas.py --pdftoppm PATH`.
The web build verifies the checked-in assets and requires no TeX compiler.

[The chapter renderer](../tools/readable_chapters.py) publishes the main chapters
of Papers I, II, III, IV and VII as readable HTML alongside their original source pages.
Paper II's current verification snapshot has its own reading page. Each paper
has a chapter index and bibliography, with links between chapters and recorded
claim locations. Paper IV's atlas also has HTML plates; the original visual
atlases remain available as on-site PDFs.

Paper IV's single source is divided into contiguous, checked line ranges for
17 main sections, the opening orientation and the atlas introduction. These
ranges preserve original source lines and resolve claim links to the correct
chapter. The 68 proof bodies, 95 numbered records and all 1,041 mathematical
expressions in the main document are retained. Six receipt-bound figures are
included. Source changes that shift
section boundaries require a review of the chapter configuration.

[The atlas renderer](../tools/reader_atlas.py) publishes all 26 Paper IV plates,
including their retained prose and tables, 24 drawings, text descriptions and
structured label transcripts. Integer references in the
[reading aids](../tools/paper_iv_atlas_descriptions.py) select original TikZ
labels; mathematical values are not retyped. Each label must appear exactly once.
The reader validates references to manuscript sections and statements, preserves
original source-line links, and records the atlas and drawing mathematical input
sequences in `documents/paper-iv-atlas.json`. The site checker re-derives those
sequences from the published source files and verifies the rendered HTML.

Atlas manuscript references also generate return links at their exact section
or statement. These links stay visible with proof navigation when optional
source links are hidden. No relation is inferred from matching keywords.
`manuscript_backlinks` in the conversion record stores the source-derived
connections; the site checker verifies both directions for every plate.

Drawing PNGs and their source/image receipts are committed under
`website/assets/atlas/paper-iv/`. To rebuild only these images, use
`python tools/build_atlas_figures.py --tectonic PATH_TO_TECTONIC --pdftoppm PATH_TO_PDFTOPPM --stage EMPTY_DIRECTORY`.
This compiles the unchanged TikZ in an isolated directory and renders 24 cropped
pages. It does not execute the mathematical model generator or checker. The
ordinary website build verifies the committed assets without requiring TeX.
Evidence notes are explicitly attributed to the retained source edition; new
reading descriptions do not extend its proof or formal-verification scope.

The renderer handles the selected manuscripts' prose, statement environments,
references, equations, tables, code listings and receipt-bound figures. Its book
configuration is explicit. The build checks chapter order against the main TeX
file. Unsupported prose commands and unresolved references stop the build.
It does not execute TeX. Mathematical macros and formal scope labels come from
the retained main manuscript, with the first definition preserved for
`providecommand`. Bibliography links use citation keys from each current BibTeX
source so that they do not depend on a historical compiled bibliography.

The build compares the full sequence of mathematical expressions with the source
and writes `documents/readable-chapters.json` with source identities, locations,
macro definitions and conversion counts. The site checker also compares every
rendered math input with its source expansion. The original pilot's
`documents/readable-paper-ii.json` remains available. Original line URLs and claim
records are preserved. Search includes chapter passages and equation excerpts.
Extend the selected books only after checking syntax, source fidelity, figures,
navigation and rendered mathematics. Passing these checks does not establish
mathematical correctness or new Lean coverage.

The diagram guides cover all chapter figures in
[Paper I](PAPER_I_DIAGRAMS.md), [Paper II](PAPER_II_DIAGRAMS.md),
[Paper III](PAPER_III_DIAGRAMS.md) and [Paper IV](PAPER_IV_DIAGRAMS.md):
10, 13, 6 and 6 figures respectively. Each book's
`website/paper-*-figure-descriptions.json` supplies concise image alternatives
and guide anchors. Each description is bound to the reviewed PNG checksum;
changed, missing or unused figures stop the build for review. Original captions
remain unchanged, and description links stay visible in the quieter reading view.
The first three guides also describe their 22, 24 and 24 atlas pages. Paper IV's
guide links to the existing 26 HTML plates and their complete label transcripts.

## Proof Path Theory reading edition

The [Proof Path Theory HTML edition](https://KomorebiP.github.io/Operation-KOMOREBI/read/proof-path-theory/index.html) follows the retained manuscript from the preface through five parts, its theorem ledger, source-bound tables, and the final reproducible example. Chapter navigation, original TeX line links, selectable mathematics, original figures, PDF and visual sampler links, and routes to Lean, code and evidence are retained. Source expressions are checked against the unchanged TeX. The reading presentation adds no proof or formal verification assessments.

The converter also reads the five part-opening figures and four explanatory
paragraphs from the manuscript's preamble macro. All 25 figure numbers follow
the printed sequence. Captions, including their nine mathematical expressions,
are included in the source and HTML checks. Plain references retain their
authored numbers, the tagged condition links as `(SC)`, and the nine bibliography
entries retain their numeric citation order. The complete HTML edition contains
1,051 mathematical expressions and 51 proof environments.

Run `python -B -m unittest discover -s tools -p 'test_proof_path_reading.py' -v` to check manuscript boundaries, formula preservation, readable syntax and source illustrations. The normal website checker verifies published equations, chapter links and all reading ZIPs.

## Publication

The [reader website workflow](../.github/workflows/reader-site.yml) builds and
checks the site on pushes and pull requests. Only a successful build on `main`
can deploy it through GitHub Pages. Pull requests receive build checks without
publication. Library revisions are pinned so a rebuild cannot silently adopt
unreviewed changes from another repository.

Update library pins deliberately after reviewing their changes and checks.
Record qualifications in the existing publication metadata only after those
runs finish successfully. A website build confirms its own navigation and
packaging scope, not new mathematical or formal verification.

The workflow also runs the documented introductory Python and C examples.
It checks the 26 hand-worked examples with exact rational, modular and finite-set calculations.
The library workflows retain their broader platform and release checks.

[Accessibility and known limits](ACCESSIBILITY.md) · [Repository maintenance](MAINTENANCE.md)

## Claim indexing and search

The [project overview](START_HERE.md), [project map](PROJECT_MAP.md) and
[three demonstrations](DEMONSTRATIONS.md) introduce the collection as a whole.
The map labels reading suggestions separately from documented source uses.
It does not generate or certify a theorem dependency graph.

The website publishes `examples/komorebi_demonstrations.py` as a readable source
page and an identical download. Its source record includes the collection
revision and SHA-256. The site checker compares the download and displayed
source. `python -B tools/check_demonstrations.py` runs each demonstration and
compares its output with the corresponding guide. The website workflow runs
this check alongside the existing hand-worked example checks. Demonstration
pages also participate in the related work's search filter.

Run `python -B tools/claim_navigation.py` to regenerate the manuscript index, then
run the normal status command to refresh the claim guide. `--check` compares the
index with the receipt-bound source texts. Paper I keeps its existing correspondence
records. The other core papers use literal statement environments and TeX inputs.
The extractor does not expand macros, index historical environments or infer Lean
coverage. Proof links identify immediately following proof blocks. A missing link
does not assert that a proof is absent elsewhere.

Site search includes individual claim and glossary links, with filters for result
type and repository. Search addresses preserve filters. Results load in groups of
40, and the next group remains reachable through the Show more results button.
The claim index has separate paper and statement-type filters. Direct claim links
reveal their paper even when an earlier filter would otherwise hide it.

## Links within a work

The document publisher supplies the same reading routes on work pages and
source readers. Indexed statement and proof lines have return links to the
exact claim. Lean module return links use only the declaration paths already
recorded in the claim index. These are navigation overlays. Downloaded source
files remain byte for byte identical to their import receipts.

Search entries carry explicit `work_ids`. Reading files use their receipt owner,
claims and proof locations use their recorded paper, and examples use the
learning topic relationships. Glossary entries inherit the works linked by
those topics. General guides and library pages stay outside a work filter
unless a relationship is recorded. Work section results provide routes to
proofs, Lean coverage and code instructions even where no individual source
file has been selected for on-site reading.

The site checker validates search work identifiers and every result’s local
page and fragment. Claim types and existing evidence assessments are unchanged.

## Browser Python

The [Python playground](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html)
runs the three teaching demonstrations and the pinned Komorebi Math introductory
example. A labelled preset dropdown loads the selected editor, source routes and
expected output. Choices retain their page fragments, and switching presets keeps
edits in the current page. The original example links remain available without
JavaScript. Python starts on demand in a disposable module worker. Stop terminates
the worker, including an infinite loop. Reset also restores the selected source.
Each run uses a fresh namespace. A two minute timeout and an output limit keep
ordinary mistakes manageable. The plain text editors support keyboard navigation.

`website/python-runtime.json` pins Pyodide, Python and the NumPy wheel with byte
counts and SHA-256 checksums. `tools/fetch_python_runtime.py` verifies those files
before the build copies them to the site. Pass their directory as `--python-root`
to the site builder. Runtime files load from the same site. The reader does not
upload editor contents or selected data files. Save draft explicitly stores code
in this browser. Restore draft and Delete saved draft control that stored copy. Edited Python can
still use browser networking, so this is not an isolated service for untrusted code.

`tools/browser_python.py` extracts the teaching functions without rewriting their
bodies. It checks every library file against the pinned Git tree and produces a
deterministic ZIP containing the package and its license. The worker verifies the
ZIP checksum before loading it. `downloads/python-playground.json` records the
sources, expected output and library revision. The static checker validates this
record, the runtime and all source links. The workflow checks the extracted
examples against their published output.

The tested browser library scope includes packet reconstruction, exact rational
coordinate changes, and the finite reciprocal and Fubini sequence experiments
described in [Komorebi sequence shapes](demonstrations/SEQUENCE_SHAPES.md). NumPy is included. Optional packages, native backends and the
rest of the library have not been qualified in the browser. A passing example
does not establish a general theorem, execute Lean or change any proof status.

## Plotting and data in the playground

The preset menu includes interactive 2D signals, a 3D surface, a 3D helix, a
Matplotlib figure, symbolic SymPy calculations, SciPy integration and CSV/JSON
data plotting. These are software tutorials, not new proof or novelty claims.
NumPy, Matplotlib, SymPy and SciPy load on demand from the pinned runtime files.
Direct imports of those packages also trigger loading. Dynamic imports may need
an explicit import first. Interactive 3D uses WebGL through the pinned Plotly.js
runtime. It includes front, top and default view buttons, image downloads, CSV
and JSON downloads, and a table of the first 100 plotted samples.

`website/python/komorebi_browser.py` supplies the browser display bridge.
`show_plot(data, layout, description=...)` accepts Plotly-style dictionaries for
scatter, bar, heatmap, surface and scatter3d traces. `show_matplotlib` and ordinary
`plt.show()` produce PNGs. `export_file` offers CSV, JSON or text downloads. The
helper is separate from the Komorebi Math package and is included in the site
source record with a checksum. Downloaded browser plotting scripts can be opened
again through the playground's Python file control.

Upload controls read up to five UTF-8 CSV/JSON files locally, at most 2 MB each
and 4 MB in total. The run receives a snapshot in `uploaded_files`. A run report
records the executed code, output, package and collection revisions, figures, and
input-file checksums. It omits the uploaded file contents. Edited code, printed
output and individual results have separate download controls. Draft saving is
explicit and local to this browser. Code runs locally.

The helper limits interactive figures to 50,000 samples, messages to 2 MB and
combined figures and exports to 8 MB per run. Unsupported graphics or unavailable
WebGL leave a visible error and downloadable data. Source-linked mathematical
examples retain their existing evidence labels. The broader Komorebi Math
library remains outside the tested scope except for the documented introductory
operations and sequence experiments.

## Komorebi sequence experiments

The playground opens with the source-linked sequence research group. It includes
reciprocal coefficient growth, labelled 2D and 3D comparisons after factorial normalization,
and the factorial-weighted Stirling rows from the Special Functions sequence
atlas. General plotting tutorials remain available further down the menu.

`tools/sequence_presets.py` defines the programs, parameter bounds, expected
output, related works and reading links. Reciprocal presets call the pinned
library's `reciprocal_coefficients`. The factorial preset checks its row sums
against `fubini_sequence`. Exact exports use integer and rational text to avoid
losing large integer digits through JavaScript numbers. Charts use ordinary
counts or floating-point logarithms as labelled. The 3D sequence views preserve the discrete
parameter domains. They do not interpolate a continuous family.

Plot titles wrap above the chart. Larger labels, point shapes, patterned bars
and keyboard-accessible series checkboxes help distinguish the data. The
Enlarge plot control gives figures more height. PNG downloads retain titles
and legends. The factorial weights preset includes a 2D map before its 3D view.

`tools/test_sequence_python.py` compares 448 reciprocal coefficients with
independent ordinary rational-series inversion and 190 weighted Stirling entries
with inclusion-exclusion. It also checks preset outputs and exact export
normalization. The existing website workflow discovers these tests. Source
records and proof assessments retain their previous scope.

## Notation reference

The [notation index](NOTATION_INDEX.md) provides symbol search and a source inventory for every work. Entries link to exact source lines and retain the paper’s own context. Its JSON downloads record every detected occurrence in the selected TeX, Markdown and text sources. PDF and image notation remain explicit coverage limits.

`tools/notation_index.py` builds the reference. `manifests/notation-sources.json` declares additional manuscript entrypoints. The reader follows their literal includes and checks source receipts before indexing. Parser regression tests and the site checker validate extraction, source positions, counts and links.

Search excerpts omit recognized layout commands and source bookkeeping such as
`Needspace` and `RecordID`. Balanced arguments keep nested metadata out of the
preview while preserving section titles, literal set braces and escaped text
characters. These previews remain reading aids: the downloadable occurrence
records and linked source passages retain the exact original text and positions.

Word searches can use the source's explicit definition title as the result
heading, with a direct link to its reading passage. Names follow the enclosing
definition scope, including long definitions; unnamed definitions keep a generic
label. Symbol searches keep the matched symbol visible and identify its source
definition separately. Matching symbol spellings remain available in a disclosure.
The build checks title metadata against the source; comments and code examples
cannot supply a definition name.

## Source-bound proofreading notes

The [1 November 2026 proofreading record](../manifests/reader-proofreading-2026-11-01.json)
covers the main online chapter text of Papers I and II. Two labelled editorial
reading notes clarify Paper II's abbreviated Fourier hypotheses and the two
uses of `t` in its walk-series subsection. The retained manuscripts, mathematical
expressions, statement numbering and proof bodies are unchanged.

`tools/reader_proofreading.py` binds the review to 17 source-file hashes and
exact source passages. Notes link to the existing HTML definitions and publish
their record at `documents/reader-proofreading.json`. The build rejects stale
source bindings, moved reference targets, missing notes and duplicate placements.
This is a proofreading record, with no new proof audit, Lean replay or external
citation verification. Visual atlases and PDF layout are outside its coverage.

The [Papers III and IV proofreading record](../manifests/reader-proofreading-papers-iii-iv-2026-11-01.json)
covers Paper III's four main chapters and Paper IV's eighteen non-atlas reading
sections, plus their abstracts, notation, preambles and bibliography syntax.
No objective routine correction was identified in that scope. The record binds
eight retained source files and reports the scoped syntax checks. The same
exclusions apply; the manuscripts and mathematical statements are unchanged.

The [Papers V and VI proofreading record](../manifests/reader-proofreading-papers-v-vi-2026-11-01.json)
covers 88 non-atlas reading sections, their abstracts, notation, preambles and
bibliography syntax. It recommends two wording corrections for a later edition:
“minimum cost among all admissible prunings” in
[Paper V's best-basis theorem](https://komorebip.github.io/Operation-KOMOREBI/read/paper-v/admissible-packet-trees.html#L2436),
and “potential weight” in
[Paper VI's alternating-product theorem](https://komorebip.github.io/Operation-KOMOREBI/read/paper-vi/extended-finite-state-feynman-kac-transfer.html#L4417).
Both adjacent interpretations already explain the intended meaning. The record
binds four source files and reports the syntax checks. The retained text and
mathematics are unchanged; the same review exclusions apply.

The [Paper VII proofreading record](../manifests/reader-proofreading-paper-vii-2026-11-01.json)
covers its 25 main reading sections, front matter, notation, cross-references,
figure captions, preamble and bibliography syntax. The finite core,
strengthened development, six supplements and three retained alternative
derivations were reviewed. No objective routine correction was identified in
that scope. The record binds twelve source files and reports the syntax checks.
The retained text and mathematics are unchanged; the same review exclusions apply.

The [Paper VIII proofreading record](../manifests/reader-proofreading-paper-viii-2026-11-01.json)
covers its 23 main reading sections: the orientation and abstract, three exact
models, fifteen manuscript sections and Appendices A–F, together with notation,
cross-references, captions, preamble and bibliography syntax. No objective
routine correction was identified in that scope. The record binds ten source
files and reports the syntax checks. The retained text and mathematics are
unchanged; the same review exclusions apply.

The [Paper IX proofreading record](../manifests/reader-proofreading-paper-ix-2026-11-01.json)
covers its 56 main reading sections, front matter, notation, cross-references,
captions, preamble and bibliography syntax. The five mathematical appendices,
continuation notes, checkpoint supplements and recovered historical text were
included. One grammar correction is recommended for a later edition: the
singular subject in “The full exact classification … are” requires “is.”
The record binds 39 source files and gives the exact source and reading passage.
The retained text and mathematical tokens are unchanged; the same review
exclusions apply.

The [Paper X proofreading record](../manifests/reader-proofreading-paper-x-2026-11-01.json)
covers its 30 main reading sections, front matter, notation, cross-references,
captions, preamble and bibliography syntax. The algorithms and reproducibility
appendices, retained checkpoints, residue-counting continuation, final conditional
completion and atlas introduction were included. One punctuation correction is
recommended for a later edition: the smooth-chart digit-stream display ends its
sentence with a comma and should end with a period. The record binds six source
files and gives the exact source and reading passage. The retained text and
mathematical tokens are unchanged; the same review exclusions apply.

The [Paper XI proofreading record](../manifests/reader-proofreading-paper-xi-2026-11-01.json)
covers all 38 main reading sections, the fifteen construction appendices,
literal derivation blocks, front matter, notation, references, captions, tables,
preamble and both bibliography files. Two corrections are recommended for a
later edition: clarify the tensor example's carrier-dimension wording and protect
German title capitalization in the generated bibliography. The record binds
19 source files and gives the exact source and reading passages. The retained
text and mathematical tokens are unchanged; the same review exclusions apply.

The [Paper XII proofreading record](../manifests/reader-proofreading-paper-xii-2026-11-01.json)
covers all 16 main reading sections, including the reading map, abstract,
publication scope, thirteen manuscript sections and complete verification/revision
record, plus notation, references, captions, tables, preamble and both bibliography
files. One bibliography typography correction is recommended for a later edition:
use “pp.” before the Mazur entry's page range. The record binds four source files
and gives the exact source and reading passage. The retained text and mathematical
tokens are unchanged; the same review exclusions apply.

## Recovery Laboratory

`recovery-lab.html` extends the introductory shared-summary diagram to exact
linear measurements on 2–4 real input coordinates. Readers edit up to four
measurement rows and three question rows, using integers from −99 to 99 or
fractions whose numerator is in that range and whose denominator is 1–99.
Checkboxes select the available measurement rows. Six starters distinguish
recoverability, partial loss, redundancy, fractional rules, and full recovery.

`tools/recovery_lab.py` publishes the page and search entry. Its model,
`website/assets/recovery-lab-core.mjs`, uses reduced BigInt fractions throughout
row reduction, kernel construction, recovery weights, and rank-based repair.
The model and controller imports use content versions. A successful question
shows weights giving its row exactly; an unsuccessful one shows a vector w
with Rw = 0 and Fw ≠ 0. The input and summary plots approximate the exact values
in the adjacent table. A zero motion parameter makes the displayed points
coincide without changing the global obstruction certificate.

The repair retains an independent subset of enabled measurement rows, removes
redundant and disabled rows, and adds independent question rows until every
question is recoverable. The additional row count is rank([R; F]) − rank(R).
Undo restores the original settings. Versioned share links retain all matrices,
selections, base inputs, and inspection settings; malformed links are rejected.
JSON downloads contain settings and recomputed exact certificates. Invalid
matrix edits keep the last valid result visible and disable sharing and repair
until the entries are complete.

Run `node --test tools/test_recovery_lab.cjs` and
`python -B -m unittest discover -s tools -p 'test_recovery_lab.py' -v`.
`tools/audit_recovery_lab.py` independently checks 1,604 cases with Python
Fraction arithmetic and ranks from determinants of minors. These comprise
1,354 exhaustive two-coordinate cases and 250 seeded rational cases, including
coefficients at the supported bounds. The checks verify recovery products,
kernel bases, obstruction witnesses, row-operation matrices, collisions, and
minimal sufficient repairs. The page explains the general linear-algebra
argument separately; finite software checks add no manuscript proof review or
Lean coverage.
The [bounded run manifest](../verification/recovery-lab/run-2026-11-03/manifest.json)
binds the audited model and oracle bytes; its
[result](../verification/recovery-lab/run-2026-11-03/result.json) records the
tested case and certificate counts.
Recovery-specific line-ending rules live in `tools/.gitattributes`,
`website/assets/.gitattributes`, and `verification/recovery-lab/.gitattributes`.
The root attributes file is retained byte for byte because the Euler
publication record binds it. The recovery tests check both that binding and
the scoped attributes.

## Signal Laboratory

`signal-lab.html` is a larger known-reference signal experiment with 16–256
samples. Its maintained interface is in `tools/signal_lab.py`; the model and
browser controller are `website/assets/signal-lab-core.mjs` and
`website/assets/signal-lab.js`. The shared site builder publishes it and adds
its search entry. Both the page script and model import use content versions.

`signal-lab-workspace.mjs` supplies bounded sample strokes, a 32-edit history,
and validated notebook serialization. Its import and the model import both use
content versions, including nested module references. Drawing fills crossed
sample addresses and commits a stroke on release; cancellation restores the
previous reference. The precise sample editor provides keyboard access.

The notebook keeps at most 12 labeled settings records in local browser storage
and falls back to the current tab if storage is unavailable. JSON imports append
atomically within that limit. All metrics are recomputed from settings; stored
result fields are ignored. Saved reconstructions are overlaid only when both
reference and observed arrays match exactly. Resetting the active lab retains
the notebook. Its JSON and results CSV are separate from the active experiment's
exports and share link. `node --test tools/test_signal_lab_workspace.cjs` checks
stroke/history behavior, import boundaries and comparison eligibility.

The four starter experiments append two compatible runs and open their
comparison. They preserve existing notebook entries and require two free slots.
The comparison inspector switches among reconstructions, signed errors
(reconstruction minus reference), and differences (B minus A). Its pointer and
keyboard sample selection is independent of the active experiment's inspector.
The largest-difference action chooses the first address attaining the maximum
absolute separation. A numeric comparison CSV and sample table retain both
reconstructions and all signed values. Mismatched data disables these views and
exports. The workspace tests cover starters and an exact zero-versus-full
sample-coordinate fixture for the comparison values and CSV signs.

Comparison links use a bounded, versioned UTF-8 payload in the `#compare=`
fragment. The payload contains exactly two validated named settings records,
one of the three plot views, and an in-range comparison address. Results are
recomputed and the data-compatibility guard is checked on restoration. The
preview is separate from notebook storage and works even when the notebook is
full. Saving both runs is an explicit append action and requires two free slots.
Closing a preview restores notebook selection; ordinary experiment links omit
the comparison fragment. Malformed comparison links preserve the current valid
experiment and notebook. Clipboard failure exposes a selectable link field.

The comparison region inspector accepts inclusive integer addresses, including
a single sample. `compareRegion` derives local RMS error, mean signed error,
maximum absolute error and its first address from the existing full-signal
reconstructions. The chart rescales both axes, while sample selection, the
largest-difference action, sample table and CSV stay within that region and
retain original addresses. Maximum-error buttons inspect each run's worst
local sample. Invalid edits keep the last applied region. Selecting another
pair or a starter resets the region to the full signal.

Version-1 comparison links optionally include `region: [start, end]`; links
without it retain the full-signal behavior. A linked selected address must be
inside the region. Opening a preview leaves notebook storage unchanged; saving
its runs keeps the current region in the open comparison. Notebook JSON stores
run settings, so use a comparison link to preserve the selected region. Exact
sample-coordinate fixtures check regional metrics, CSV boundaries, single
samples, and ties; regional partitions recover whole-signal squared errors
across all supported sizes and bases.

The quality-target finder uses the active experiment's existing error curves.
It scans every budget in order, including zero, for either observed-energy
retention (0–100%) or reference RMS error (0–64). Reference error need not be
monotone; no qualifying budget is reported when the entire curve misses the
target. Threshold checks allow `1e-10 * max(1, relevant signal energy)` in
squared-error units. Zero observed energy satisfies retention targets at zero
budget. Applying a result changes the active basis and budget. Saving qualifying
runs appends the reachable settings as one group within notebook capacity; it
does not replace saved entries. The finder controls are an analysis aid; saved
experiments and links retain the resulting applied basis and budget.

The lab compares averaging-normalized Haar wavelets with their support
weights, an orthonormal DCT-II, and sample coordinates. Seeded bounded integer
noise, equal coefficient budgets, three selection policies, full budget/error
curves, component inspection, CSV/JSON import/export, and shareable settings
are supported. Imported samples become the known reference before simulated
noise is added. The minimum-budget action uses this reference and a stated
numerical tolerance. It is not an estimator for an unknown clean signal.

The website workflow runs `node --test tools/test_signal_lab.cjs` and
`python -B -m unittest discover -s tools -p 'test_signal_lab.py' -v`.
The model tests include every mask of one 16-sample benchmark in each basis.
For an independent bounded numerical check, run
`python -B tools/audit_signal_lab.py --node node --output signal-lab-report.json`
with NumPy installed and a fresh report filename. This checks 180 explicitly
specified configurations and 54,108 budget cases using NumPy FFT/IFFT and
explicit Haar support vectors. Its report records the tested range and
numerical errors; it does not change manuscript or proof status.

## Interactive Lean pilot

The collection-wide native runner at `lean/run.html` extends execution beyond
the single-file pilot. Every displayed Lean source links to its selected
workspace and command. See [Running the retained Lean sources](LEAN_EXECUTION.md)
for the source bundle, manual GitHub workflow, retained/reconstructed
environments, compiler receipts and dedicated-server export path.

`lean/playground.html` embeds the official `live.lean-lang.org` editor only
after a visitor presses **Load Lean editor**. A normal external link works
without site JavaScript and is also the fallback for blocked frames or failed
connections. The editor runs Lean on that external service; it is not a local
WebAssembly compiler. Code entered in the editor is sent to that service.

The single starting example is Paper XII's complete retained
`PaperXII/LocalIdempotents.lean` (Proposition 3.4). `tools/browser_lean.py` takes
its bytes through the reader's receipt checks and appends only a labelled
`#check` command. `lean/playground.json` records the source identity, appended
command, service and project. Downloads and scientific sources remain unchanged.
Links appear in Inspect Lean, the Paper XII source directory and the selected
file; other modules do not acquire an unsupported run button.

The `MathlibDemo` service project tracks its own Lean/Mathlib environment.
Its displayed version is authoritative for that session; the example is not
a replay of the paper's lockfile or the entire project. The parent page never
converts an iframe load into a proof-success indicator. Lean's own diagnostics,
including unfinished-proof warnings, remain inside the editor. Restoring or
closing the frame discards edits and releases the session. No new verification
status is assigned by the site build. To change the pilot source, update its
explicit selection and recheck both the valid proof and a deliberately broken
proof against the live service in the embedded frame.

CI runs `test_browser_lean.py` and `test_browser_lean.cjs`. The site verifier
checks the exact source checksum, the complete encoded editor input and the
absence of an automatically loaded external frame.

## Paper navigation

Paper, source and PDF pages keep the overview, chapter contents, visual atlas
and main reading format together. Supporting destinations are grouped under
More resources. Overview pages also expose the visual atlas directly when a
work has one. Existing URLs and source passage anchors are retained.

Chapter and atlas reading bars share previous/next controls, position markers,
an overview link and a complete jump menu. Paper VI's contents and chapter menu
group the reading sequence by its four parts and references. The current part
opens in the chapter menu. Contents groups, plate pickers and resource menus use
native disclosures, so they remain usable without JavaScript. Both complete
visual atlases use the chapter sidebar for their on-page contents and keep PDF
and source options in a separate disclosure. Paper IV's visual atlas uses the
same controls and sidebar.

