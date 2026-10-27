KOMOREBI PAPER II
Modern Monograph edition
8 October 2026

READING FILES
  papers/Paper_II_Traditional_Final.pdf       80 pages
  papers/Paper_II_Visual_Guide_Final.pdf      26 pages
  papers/Paper_II_Lean_Guide_Final.pdf        45 pages

Start with the monograph for the definitions and written proofs. All twenty-four
worked visual plates are included after the account of the proof scope. The
standalone visual guide presents the same models on consecutive pages. The
Lean guide explains the preserved formal contract and its exact boundaries.
Traditional locators distinguish printed page numbers from PDF viewer pages.

WHAT CHANGED
The monograph uses the same typography, quiet page furniture, reader boxes,
and teal figures as Paper I. The prose has been proofread for a natural tone,
with brief explanations added where notation or scope needed clarification.
All thirteen main figures were redrawn from their mathematical data. The atlas
has one plate per page, and the multigraph footer is now placed clearly inside
its panel. The Lean guide has a matching cover and Arabic body pagination.

All fifty pre-monograph proof bodies remain byte identical. The sixty-one formal
definitions and results retain their formulas, labels, and order. The small prose
clarifications state the zero convention for negative path-count indices, the
lack of a uniform integrality guarantee for character averages at bad primes,
and the finite-depth truncation of directional Smith weights. Exact reports
record these edits. Earlier mathematical corrections remain in their original
logs and are not presented as new monograph discoveries.

CURRENT VERIFICATION
Forty-eight canonical Python tests and 118 exact visual checks pass. All thirteen
main figure generators pass their data assertions. The twenty-two atlas graphics
regenerate byte for byte from the current model sources, including the repaired
multigraph label. Tested ranges, exact arithmetic, floating residuals, input
hashes, and replay commands are recorded under verification/monograph_2026-10-08.
Every publication page was rendered. The figures, plates, dense tables, code,
page endings, and updated statement locators were reviewed. No missing glyphs,
overfull boxes, unresolved references, or text outside the page remain.

The formal checks are static checks. All twenty-two preserved formal-component
files match the release manifest. The twenty-five contract rows contain 171
occurrences of 160 distinct declaration targets across fifteen Lean files.
The September 3 report remains inherited evidence. This edition makes no claim
of a new Lean compiler run or a new kernel audit.

EDITABLE SOURCES
  editable/traditional/       Modular TeX, figures, fonts, and bibliography.
  editable/visual_guide/      Twenty-four plates, exact models, and TikZ sources.
  editable/lean_guide/        Chapters, exact excerpts, maps, and fonts.
  publication/               Build manifest and shared house style.
  source/canonical_v1.2.1/    Complete unchanged canonical release.
  source/annals_expanded/     Preserved expanded manuscript and earlier audits.
  source/visual_guide_original/ Original visual models and historical sources.
  source/provenance/          The incoming edition and legacy assembly helpers.

BUILDING
Run python scripts/build_pdfs.py from this folder. XeLaTeX and BibTeX build the
reading files. Fonts and licences are bundled. Each editable directory also has
a build.py entry point and its own build readme. Current builders preserve the
authored monograph and plate prose. Legacy assembly writes only into an explicit
historical directory.

Regenerate the thirteen main figures with
  python editable/traditional/figure_sources/rebuild_figures.py
The plotting sources require NumPy and Matplotlib. The exact atlas generator
requires SymPy. Fresh computation replay instructions are included in the
verification folder. The historical sources retain their original wording,
figures, counts, and dated evidence. Read the papers/ files for this edition.

Verify package checksums with python scripts/verify_integrity.py.
