# Accessibility and reading options

The [Komorebi website](https://KomorebiP.github.io/Operation-KOMOREBI/) brings
the maintained guides and library documentation into one HTML reading space.
You can also use the Markdown pages directly on GitHub.

## Navigate and read

The website provides a skip-to-content link, named navigation regions, visible
keyboard focus, descriptive links, a glossary and search. Work pages keep
completion, Lean coverage and confidence in text. The layout adapts to smaller
screens. Wide tables and code blocks can be scrolled with the keyboard.

The header keeps **Collection**, **About the project** and **Search** visible.
**Browse** opens links grouped
under **Read**, **Look up** and **Use**. The current page is marked in its link.
The expanded navigation stays above the content and does not cover it. Press
Escape while focus is in the navigation to close it and return to Browse.
When JavaScript is unavailable, the grouped links remain visible.

The homepage offers four reading routes with underlined titles and large click
targets. Its collection details and work-in-progress explanation use native
disclosures that also work without JavaScript. The warm paper, sage surfaces
and dark green text carry through to the reading pages, with a visible keyboard
focus outline and layouts that reflow on narrow screens.

Long HTML guides have a collapsed **On this page** list of section headings.
Open it and choose a section to jump there. Keyboard focus follows the jump,
so the next Tab continues from that section. These section links also work
without JavaScript. Work pages keep their existing paper, proof, Lean, code
and example routes. Readable chapters keep their chapter contents.

In-page links to chapters, statements, proofs and source lines also move keyboard
focus to the destination. Any enclosing contents disclosure opens when needed.

Use Tab and Shift+Tab to move between controls, Enter to follow a link or
activate a button, and Space or Enter to open a contents disclosure. Browser
zoom changes the text size. Reading routes and the work catalogue remain
available when JavaScript is disabled. Search and catalogue filters use
JavaScript and announce their result counts.

## Find a statement or term

The [claim index](https://KomorebiP.github.io/Operation-KOMOREBI/claims.html)
contains all 12 core papers. Choose a paper or statement type, or search its
indexed titles, text, source labels and recorded Lean names. Each record has a
permanent link. Paper sections connect to the on-site PDF, examples, Lean guide,
code and evidence. Document pages link back to the paper’s claim index.

[Site search](https://KomorebiP.github.io/Operation-KOMOREBI/search.html) includes
individual claims and glossary entries. Filter by repository or result type.
Spaces and common punctuation are treated alike, so “seed-rank” and “seed rank”
find the same indexed text. The page address preserves your query and filters.
Use **Show more results** to reach matches beyond the first 40. Keyboard focus
moves to the first new result, and the result count is announced.

Use **Search this work** on a paper or source page to limit results to that work.
The **Work** filter keeps its claims, indexed proof locations, reading files,
Lean coverage, code instructions and linked examples together. Result types
include **Written proofs**, **Lean** and **Code**. A proof result identifies a
reading location. It does not add a proof assessment.

Source pages show a **Statement** or **Proof block** link beside each indexed
starting line. Follow the title to return to the exact claim, or use **Go to
proof** and **Go to statement** to move between the recorded locations. The
file’s statement list provides the same routes without searching through code.
Mapped Lean modules list the claims that link to that module. The original
source text and line numbers are preserved.

On original source pages, use **Go to line** to reach a numbered line directly.
Focus moves to that line and the page address records it, so you can copy a
link to the passage. With JavaScript enabled, Tab moves through the reading
controls and claim links without stopping at every line number. **Skip source
text** moves past the listing, and **Back to source controls** returns to its
navigation. Without JavaScript, the skip links and individual line links remain
available. Your browser’s Find command can locate words within the file.

Search covers indexed HTML and source text. Use the PDF reader’s own search for
the full text of a PDF. With JavaScript disabled, all claim records and paper
jump links remain readable. The browser’s Find command is also available.

## Mathematics and figures

The [HTML reading catalogue](https://KomorebiP.github.io/Operation-KOMOREBI/read/index.html)
brings together the main chapters of [Paper I](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-i/index.html),
[Paper II](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ii/index.html)
and [Paper III](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/index.html).
These editions retain the original prose, equations,
figures, tables and code examples. Each paper has chapter contents, previous
and next links, cross references and a bibliography. Paper II also includes its
separate current verification snapshot.

Paper I includes its orientation, foundations, packet and graph results,
transport, worked models, notation ledger, statement concordance and bibliography.
Its ten manuscript figures retain their captions. The two conceptual diagrams
have keyboard-scrollable regions. The separate 22-plate visual atlas is linked
to the PDF and is not converted to HTML. The build checks all 1,445 mathematical
expressions in the six selected source sections, in their original order.

Statements and proofs link to each other, their claim records and the original
source lines. Reading pages connect to the paper's recorded Lean coverage, code
and worked examples. Paper III retains the manuscript's distinctions between
its finite formal contract, inherited results and formalization targets.
These reading editions add no mathematical review or Lean verification.

Search includes passages from these chapters, equation previews and highlighted
matching words. Common Greek symbols can be searched by name or character,
such as **rho** or **ρ**. Mathematical previews retain the source expression.
Wide equations have a separate scroll area that can receive keyboard focus.
Displayed equations and code blocks in HTML guides can also receive keyboard
focus without JavaScript. Use the arrow keys to scroll a wide block.

The HTML guides use a locally served, pinned MathJax runtime. Its menu and
accessibility components are enabled, including assistive MathML and expression
exploration. Open an expression's context menu for the available math options.
Support varies with the browser and assistive technology.

The [glossary](GLOSSARY.md) includes prose explanations of introductory symbols.
The original papers retain their own definitions. Text descriptions and source
files are linked where available. This does not establish that every diagram
or every mathematical expression in the collection has an adequate spoken
description.

## PDFs and downloads

Use **Papers and PDFs** in the website navigation to open papers, visual guides
and formal companions without leaving the site. Each document has an embedded
reader with search, page selection, zoom and printing. **Expand reader** opens
the same document in a larger reading view. **Open PDF directly** and
**Download PDF** remain available if the embedded reader cannot load.

Document pages link back to the work, written proofs, Lean coverage, code and
available worked examples. Edition READMEs are rendered as HTML. Linked
manuscript and program sources have selectable text and line links. TeX source
is shown as source, with links to included manuscript sections where available.
Papers I, II and III also have formatted HTML chapters. Their separate visual
atlases remain available through the on-site PDF reader. Use the PDF for
typeset manuscript sections that have not yet been converted to HTML.

Reading ZIPs include a contents manifest, source revision, checksums and
available license notices. They contain selected reading files, not complete
software or Lean builds. Use [Downloads](DOWNLOADS.md) for that distinction and
the full source instructions.

Some original PDFs may lack semantic tags, a correct reading order or usable
equation descriptions. This website has not converted or certified the entire
PDF collection. Where an accessible format is missing, identify the work and
section when reporting it. HTML library guides, Markdown and TeX sources are
additional reading options, with different limitations.

## Checks and remaining limits

The website build checks local links and fragments, page titles, language,
main headings, skip links, form labels and image text alternatives. It also
verifies every reading ZIP against source receipts. These checks do not
establish WCAG conformance or replace testing with assistive technology.

Keyboard and responsive browser checks cover representative pages. A full
screen-reader review of all pages and source PDFs remains open. Proof review,
Lean replay and software qualification retain their separately recorded scope.

## Report an access problem

Use the [accessibility and reading problem template](https://github.com/KomorebiP/Operation-KOMOREBI/issues/new?template=04-accessibility.md)
or the [contribution guidance](../CONTRIBUTING.md). Include the page URL, the
section or control, what you expected, and what happened. Browser and assistive
technology details are useful when you can provide them.
You do not need to identify a standard, propose a fix, or share a diagnosis.

Math rendering uses [MathJax](https://www.mathjax.org/) under its retained
Apache 2.0 license. The website build records the runtime's source and integrity.
The PDF reader uses [Mozilla PDF.js](https://mozilla.github.io/pdf.js/) with its
retained Apache 2.0 license. The build verifies the pinned viewer and each
published document against its source identity. PDF scripting is disabled.

[Reading routes](READING_ROUTES.md) · [Glossary](GLOSSARY.md) · [Project statement](PROJECT_STATEMENT.md)
