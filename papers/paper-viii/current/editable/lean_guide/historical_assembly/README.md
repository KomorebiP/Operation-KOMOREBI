# Paper VIII Lean Guide — final documentation edition

Author: Komorebi P. Documentation date: 6 October 2026 UTC.

The PDF teaches actual objects, hypotheses and proof steps in the current finite
source. It includes 61 complete contiguous source selections, all 56 manuscript
result correspondences, the four separate classical boundaries, and a complete
catalog of 392 theorem declarations plus 66 construction audits.

`python3 build.py` rebuilds the PDF in an isolated directory with four XeLaTeX
passes and deterministic timestamps. All required guide assets are shipped here;
the build does not require the raw snapshot or a Lean installation. Requirements
are XeLaTeX, P052, DejaVu Sans/Mono, Latin Modern Math, and the loaded TeX packages.

`python3 assemble.py --source /absolute/path/to/original_snapshot` regenerates
source-derived tables and exact excerpt assets. Python, fontTools and fontconfig
are required. The default resolver locates the preserved snapshot in the work
layout or in the edition's `source/` tree. Use an explicit `--source` after moving
this guide elsewhere.

`python3 verify_pdf.py --source /absolute/path/to/original_snapshot` checks every
audited name in extracted text, exact excerpt bytes, source identities, references,
glyphs, page bounds, and direct/named internal links. Requirements are PyMuPDF,
Pillow and `pdffonts`. It creates readable checks and contact sheets under `qa/`.

`generated/documentation_reconciliation.json` distinguishes fresh static checks
from inherited proof evidence. The accepted cumulative run is preserved at
`original_snapshot/verification/sixth_final/`. It completed on 6 September 2026
using Lean 4.34.0-rc2 and Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Lean and Lake are absent from this host;
the documentation edition does not claim a new kernel execution.

Raw UTF-8 selections are `excerpts/*.lean.txt`. Printed assets apply font fallback
only to a missing monospaced glyph; the raw files, line ranges and SHA-256 register
preserve exact source fidelity. Full formal sources are retained in the edition's
source tree, rather than being replaced by these selected excerpts.
