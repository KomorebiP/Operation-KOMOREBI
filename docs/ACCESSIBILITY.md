# Accessibility and reading options

The [Komorebi website](https://KomorebiP.github.io/Operation-KOMOREBI/) brings
the maintained guides and library documentation into one HTML reading space.
You can also use the Markdown pages directly on GitHub.

## Navigate and read

The website provides a skip-to-content link, named navigation regions, visible
keyboard focus, descriptive links, a glossary and search. Work pages keep
completion, Lean coverage and confidence in text. The layout adapts to smaller
screens. Wide tables and code blocks can be scrolled with the keyboard.
In HTML guides, captioned tables use their visible captions as the names of
their scrolling regions, so screen-reader region navigation identifies the table.

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

The HTML chapters of Papers I–V open with repeated source and reference links
hidden from the reading flow. **Show source and reference links** reveals each
passage’s permalink, source line, claim record and related resources. The choice
is remembered in this browser when local storage is available. **Read proof**,
**Back to statement**, contents and section links remain visible in either view.
**Skip contents and start reading** moves directly to the chapter text. Without
JavaScript, all passage links remain visible and usable.

In Paper IV, open **Statements and proofs** within a chapter's contents to find
its numbered definitions, results, remarks and examples. Each entry links to the
record, with **Read proof** beside it when a proof is recorded. The list works
with the keyboard and without JavaScript.

Section controls are ordinary links within the chapter, so they do not add a
repeated navigation landmark for every heading. Chapter contents, neighbouring
chapters and work routes retain their named navigation regions.

In-page links to chapters, statements, proofs and source lines also move keyboard
focus to the destination. Any enclosing contents disclosure opens when needed.
Direct passage links and browser Back/Forward navigation also move focus to the
linked passage. Opening a page preserves focus if you have already moved to a control.

Use Tab and Shift+Tab to move between controls, Enter to follow a link or
activate a button, and Space or Enter to open a contents disclosure. Browser
zoom changes the text size. Reading routes and the work catalogue remain
available when JavaScript is disabled. Search and catalogue filters use
JavaScript and announce their result counts.

## Read side by side

Choose **Read side by side** on a reading page or from **Browse** to open the
[two pane reader](https://KomorebiP.github.io/Operation-KOMOREBI/side-by-side.html).
The page you were reading opens on the left, including its current HTML passage
anchor. Each pane has a document picker with work, type and text filters.
Papers, claims, proof locations, Lean sources, code, notation and examples can
be read together. Each document keeps its existing evidence and scope notes.

**Compare papers and monographs** provides separate **Work on the left** and
**Work on the right** choices. Choose any two works, then select **Open these
works**. Each side opens its available reading edition, PDF or work overview.
The works can be different. Their chapters, proof links and related material
remain independent, and **Copy link to this pair** shares the chosen documents.

### Save and resume a reading session

**Save and resume reading** keeps sessions in this browser and on this device.
With **Remember my last reading session** enabled, a plain visit to the reader
resumes the last pair, reading positions, pane layout and focus view. Shared
links open their requested documents. **Resume last reading session** lets you
return to the pair from before you opened that link.
Refreshing the same pair also restores its saved positions.

Enter a **Session name** and select **Save session** to keep a named bookmark.
Choose it under **Saved sessions**, then select **Open saved session**. Reusing
a name updates that bookmark. Up to 50 named sessions can be kept. **Delete
saved session** removes the selected bookmark. An unavailable edition stays
listed so you can identify and delete its old bookmark.

HTML sessions remember a nearby passage and the position within it. After a
window-size change, the reader uses that passage to approximate the same place.
PDF sessions keep the viewer's page, zoom, position and rotation once it is
loaded. Each pane restores when it becomes visible.

Turning off automatic remembering clears the automatic session and keeps named
bookmarks. Clearing browser site data removes all sessions. If storage is
blocked or full, the reader explains that saving failed. Ordinary reading and
**Copy link to this pair** remain available. Shared links keep document addresses
and HTML anchors. PDF toolbar settings and saved scroll positions remain in the
browser's sessions rather than in shared links.

### Follow references and adjust the view

Open **Related material** above either document to find that work's paper,
claims, written proofs, Lean, code, notation, evidence and available examples.
Choosing a link opens it in the other pane and keeps the current document in
place. On a narrow screen, the other pane becomes visible. For an example or
guide shared by several works, **Work for these links** lets you choose which
work to follow. Links use the same recorded routes as the individual work pages.

**Read statement and proof side by side** opens the recorded passages directly
from the claim index, readable chapters and annotated source files. Formatted
chapters are used where available. Other papers open at the original source
lines. Entries without a recorded proof location do not receive a proof pair.

Where a Lean module is already linked to a claim, **Read statement beside this
module** opens the written statement and that source file. It does not claim
that the module proves the entire statement. The mapping and evidence retain
their recorded scope. These pair links also work inside the reading workspace,
where they replace the two documents without opening another tab.

Each pane scrolls independently. Turn on **Open links from this document in the
other pane** to keep the current document in place while following a reference.
**Swap sides** exchanges the documents. **Open on its own** opens a document in
a new tab. External links and the full PDF viewer also open in a new tab.
Links inside the PDF toolbar keep the PDF viewer's normal behaviour.
**Focus on reading** hides the site header and introduction. **Show site
navigation** restores them.

**Read left pane** and **Read right pane** move keyboard focus into the selected
document. **Return to pane controls** at its beginning and end brings focus back.
The width slider works with the arrow keys. On narrow screens, either pane can
occupy the full width. **Both panes** stacks them vertically.

**Copy link to this pair** records both document addresses and HTML anchors.
If clipboard access is unavailable, a selected text field lets you copy the
link yourself. PDF toolbar page and zoom changes are not captured in pair links.
The browser Back button restores earlier pairs. Without JavaScript, use the
ordinary paper, claim and example links in separate browser tabs.

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
[Paper II](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ii/index.html),
[Paper III](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/index.html),
[Paper IV](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iv/index.html),
and [Paper V](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-v/index.html).
These editions retain the original prose, equations,
figures, tables and code examples. Each paper has chapter contents, previous
and next links, cross references and a bibliography. Paper II also includes its
separate current verification snapshot.

The [Paper IX opening chapters](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-ix/index.html)
provide **Scope and conventions** and **Arithmetic packets and coefficient
transport** in HTML. Their original equations, statements, proofs and Lean
declaration notes are retained. Forward references to later material link to
the exact headings in the selectable manuscript sources. The contents page
links to the complete PDF and source continuations; the rest of Paper IX
has not yet been converted to formatted HTML. This adds no proof review or
Lean execution.

Paper I includes its orientation, foundations, packet and graph results,
transport, worked models, notation ledger, statement concordance and bibliography.
Its ten manuscript figures retain their captions and have short text alternatives
plus a visible **Text description of this figure** link. The
[diagram descriptions](PAPER_I_DIAGRAMS.md) explain all ten figures and all
22 visual-atlas plates, including arrows, axes and matrix entries. These reading
aids can be used on the website or GitHub. Original atlas images remain in the
PDF, with a direct page link beside each description. The two conceptual
diagrams have keyboard-scrollable regions. The build checks all 1,445 mathematical
expressions in the six selected source sections, in their original order.

The chapter figures in Papers II–IV also retain their captions and have short
alternatives plus a visible **Text description of this figure** link. The
guides describe directions, axes, scales and numeric values without relying
on colour:

| Reading guide | Chapter figures | Atlas coverage |
| --- | ---: | --- |
| [Paper I](PAPER_I_DIAGRAMS.md) | 10 | 22 plate descriptions |
| [Paper II](PAPER_II_DIAGRAMS.md) | 13 | 24 page descriptions |
| [Paper III](PAPER_III_DIAGRAMS.md) | 6 | 24 page descriptions |
| [Paper IV](PAPER_IV_DIAGRAMS.md) | 6 | 26 HTML plates with drawing-label transcripts |

Paper II and III's atlas descriptions link to each page's retained explanation
and to the original visual-guide PDF. Their reading aids summarize the diagrams;
the full prose and drawing labels are not transcribed into separate HTML plates
as they are for Paper IV.

Paper IV has 17 main sections, an opening orientation and an atlas introduction.
Its HTML edition retains all 68 proof bodies, 95 numbered records, six manuscript
figures and the formalization ledger. The build checks all 1,041 mathematical
expressions in the main document, in their original order. Chapter links keep
the line numbers from the single TeX manuscript.
The preserved formal release and its stated scope remain unchanged.
Chapter figures and atlas drawings reserve their image dimensions during loading,
helping keep linked passages in place as the diagrams appear.

The [Paper IV formalization ledger](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/formalization-ledger.html#L2988)
has a named table with manuscript records marked as row headers, so assistive
table navigation can keep each compiled-scope entry associated with its records.

The [Paper IV diagram descriptions](PAPER_IV_DIAGRAMS.md) also provide formatted
equations with the site's math-reading controls. Longer formulas have their own
keyboard-scrollable areas, and the coefficient table uses descriptive row names.

The [26 Paper IV atlas plates](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iv/atlas/index.html)
also have HTML pages. They retain the source prose and equations, with 24
drawings rendered from the unchanged TikZ files. Each drawing has a text
description and a complete transcript of its labels. Matrix entries, coefficient
values and root certificates use tables with row and column headers. Wide tables
can be scrolled with the keyboard. Each drawing table's scrolling region is named
by its visible caption. Equations use the same MathJax reading controls
as the manuscript. The route guide (V1), object reference (V2) and evidence
summary (V26) also have descriptive table captions and row headers. Their
original cells, formulas and links are retained. Each plate links to its
manuscript statements and original PDF page, and to the previous and next plates.

Paper IV's reading menu includes **Visual atlas**. Referenced manuscript
sections and statements link back to the relevant plates, using each plate's
number and title. These links remain available when source links are hidden.
Previous and next plate links also name their destinations.

Descriptions and table headings are added reading aids. Mathematical labels are
read directly from the retained drawing sources. The build checks that each
label appears exactly once, verifies image and source checksums, and compares
the displayed mathematical inputs with the original atlas and figure sources.
The source's reports of tests and formal evidence remain historical records;
this conversion does not claim a new run of those mathematical checks.

Paper V's HTML edition includes both manuscript branches, all four appendices,
all 83 proof bodies, 35 manuscript figures, ten tables and the bibliography.
Its 40 reading pages preserve the original source line numbers, the core's
appendix letters and the extended development's E-prefixed section numbers.
The 33 main sections retain their equations and links between statements and
proofs. Figures are rendered from the retained PDFs, keep their captions and
have short text alternatives. Source and image checksums identify the conversion.
Full separate diagram descriptions have not been added for this paper. The
forty worked visual plates remain available in the original PDF.
The reading format preserves the manuscript's historical formalization and
finite experimental scope notes. It adds no proof review or Lean execution.

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
Papers I, II, III, IV and V also have formatted HTML chapters. Paper IV's visual atlas
has HTML plates; all original visual atlases remain available through the on-site PDF reader. Use the PDF for
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
