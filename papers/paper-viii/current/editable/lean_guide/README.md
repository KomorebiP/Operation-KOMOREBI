# 10 October 2026 release addendum

This companion retains all mathematical text from the 9 October edition.
The current build resolves installed fonts into a disposable build directory.
It does not download or install dependencies, and no standalone font binaries
are distributed. See `FONT_DEPENDENCIES.json` and the release root
`BUILD_AND_REPLAY.md`. The older build records below remain historical.

The release rechecks the exact source excerpts and body-content sequence.
Pagination within the Lean guide has small line-break changes compared with
the predecessor, while its 94-page count and content are preserved. Current
output hashes belong to `EDITION.json` and `verification/RELEASE_CLOSURE.json`.

---

# Paper VIII Lean guide, monograph edition

Author: Komorebi P. Documentation date: 9 October 2026.

The PDF teaches actual objects, hypotheses and proof steps in the current finite
source. It includes 61 complete contiguous source selections, all 56 manuscript
result correspondences, the four separate classical boundaries, and a complete
catalog of 392 theorem declarations plus 66 construction audits.

`python3 build.py` rebuilds the PDF in an isolated directory with four XeLaTeX
passes and deterministic timestamps. All required guide assets are shipped here;
the build does not require the raw snapshot or a Lean installation. Requirements
are XeLaTeX and the loaded TeX packages. P052, Nimbus Sans, DejaVu Sans Mono
and Latin Modern Math fonts are bundled in `fonts/`.
Use `--check-only` to compile without replacing outputs, or
`--output-directory /path/to/rebuilt` to create an independent output set.

`python3 assemble.py --source /absolute/path/to/original_snapshot` regenerates
source-derived tables and exact excerpt assets. Python and fontTools
are required. The default resolver locates the preserved snapshot in the work
layout or in the edition's `source/` tree. Use an explicit `--source` after moving
this guide elsewhere.

The complete regeneration order is:

```bash
python3 assemble.py --source /absolute/path/to/original_snapshot
python3 refresh_evidence.py --source /absolute/path/to/original_snapshot
python3 navigation.py --traditional ../traditional
python3 build.py
python3 verify_pdf.py --source /absolute/path/to/original_snapshot
```

The evidence refresh updates this edition's static metadata. The inherited
coverage ledger retains its historical page fields explicitly. Current page
locators are resolved by `navigation.py` into `generated/traditional_crosswalk.json`
from the traditional volume's actual final source map and PDF page labels.
These scripts never invoke Lean or change the formal source.

`python3 verify_pdf.py --source /absolute/path/to/original_snapshot` checks every
audited name in extracted text, exact excerpt bytes, source identities, references,
glyphs, page bounds, and direct/named internal links. Requirements are PyMuPDF,
Pillow and `pdffonts`. It creates readable checks and contact sheets under `qa/`.

`generated/documentation_reconciliation.json` distinguishes fresh static checks
from inherited proof evidence. The accepted cumulative run is preserved at
`original_snapshot/verification/sixth_final/`. It completed on 6 September 2026
using Lean 4.34.0-rc2 and Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Lean and Lake are absent from this host;
the monograph edition does not claim a new kernel execution. No GPU benchmark
was rerun. Three broader research targets remain open.

The original generated documentation metadata is retained under
`historical_assembly/generated/`. Its page numbers and dates belong to the
earlier documentation edition. The current provenance file is
`generated/evidence_provenance.json`.

Raw UTF-8 selections are `excerpts/*.lean.txt`. Printed assets apply font fallback
only to a missing monospaced glyph; the raw files, line ranges and SHA-256 register
preserve exact source fidelity. Full formal sources are retained in the edition's
source tree, rather than being replaced by these selected excerpts.
