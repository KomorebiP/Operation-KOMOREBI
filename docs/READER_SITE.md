# Maintain the reader website

The public site is at <https://KomorebiP.github.io/Operation-KOMOREBI/>.
Its source is in this repository. The site combines maintained collection
pages with documentation from two explicitly pinned library revisions.

## Sources

| Content | Source |
|---|---|
| Work titles and source ownership | [Source index](../manifests/source-components.json) and import receipts |
| Completion, Lean coverage, confidence and limits | [Project status](../manifests/project-status.json) |
| Selected reading, proof, Lean and code files | [Browse resources](../manifests/browse-resources.json) |
| Introductory terminology and background advice | [Reader experience](../manifests/reader-experience.json) |
| Hand-worked calculations and exercises | [Example index](HAND_WORKED_EXAMPLES.md), [tutorial pages](examples/) and [exact arithmetic checker](../tools/check_hand_examples.py) |
| Statement locations for all 12 core papers and retained Paper I declaration mappings | [Claim navigation](../manifests/claim-navigation.json), bound to the retained source records |
| Library source revisions | [Website library revisions](../manifests/reader-site-libraries.json) |
| Page structure and browser behavior | [Website assets](../website/assets/) and [site builder](../tools/build_reader_site.py) |
| Local PDF and source reading pages | [Document publisher](../tools/reader_documents.py) and receipt-bound source files |
| Embedded PDF reader | [Pinned PDF.js fetch and verification](../tools/fetch_pdf_runtime.py) |

Reading routes, glossary, download guides and work introductions are generated
with the collection's normal status command. Edit their source records or
templates. Keep each claim's exact recorded scope when changing navigation.

The `learning_topics` records in the reader experience manifest generate the
[topic map](LEARNING_MAP.md), the source routes at the end of each tutorial,
and return links on the related work pages. Edit tutorial explanations above
the `learning-navigation` marker. The status command replaces the section
below that marker. A subject route does not establish a theorem correspondence.

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
python -B tools/build_reader_site.py --math-root ../komorebi-math --polyphase-root ../polyphase-float --mathjax-root ../reader-runtime --pdfjs-root ../pdf-reader-runtime --python-root ../python-reader-runtime --revision FULL_COLLECTION_COMMIT --output ../reader-site
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

[The chapter renderer](../tools/readable_chapters.py) publishes the main chapters
of Papers II and III as readable HTML alongside their original source pages.
Paper II's current verification snapshot has its own reading page. Each paper
has a chapter index and bibliography, with links between chapters and recorded
claim locations. Visual atlases remain available as on-site PDFs.

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
explicit and local to this browser. No account or server execution is involved.

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
