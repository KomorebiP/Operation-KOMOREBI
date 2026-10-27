KOMOREBI — PAPER VII: COMPLETE PROOFREAD EDITION
Komorebi P. | 18 October 2026
Quantum Seeds and Effective Dynamics
Symmetry, geometric transport, quantum channels, and bounded refinement towers

START HERE
papers/Paper_VII_Traditional_Final.pdf — 154 pages
papers/Paper_VII_Visual_Guide_Final.pdf — 42 pages
papers/Paper_VII_Lean_Guide_Final.pdf — 84 pages
Total: 280 pages. The original project title is Quantum Seed and Packet Calculus.
PROOFREAD_REPORT.md explains the completed corrections, review and evidence scope.
It also records three minor, nonblocking pagination observations in the traditional PDF.

COMPLETE CONTENTS
papers/ — three final reading PDFs
editable/ — current TeX, vector plates, figure assets, excerpts and PDF builders
publication/ — synchronized PDFs and build configuration
source/ and downloads/ — all retrieved source snapshots and two recovery ZIPs
verification/proofread_2026-10-18/ — current proofreading, build and QA evidence
verification/monograph_checks/ — retained, dated earlier bounded computations
provenance/ — retrieved comparison baseline, prior sources, PDFs and metadata
audit/ — retained dated mathematical argument and correction reviews
COMPANION_MAP.json — refreshed result, page and formal navigation
MANIFEST_SHA256.json — size and SHA-256 of every other package file

WHAT WAS COMPLETED
All nine mathematical parts were proofread. Six local meaning/assumption
clarifications were made without changing any of the 107 complete proof bodies
or their extracted mathematical expressions. The 147 statement-like records
(142 numbered plus five unnumbered) and all six supplements remain. Counts
from overlapping source branches do not count independent discoveries.

The Lean guide's six prose corrections preserve its 67 exact source excerpts
and all active formal sources. All 40 worked visual pages match the integrated
atlas, all 38 vector plates remain, and diagram/prose corrections are reflected
in the duplicate sources and supplied generators. Bibliography capitalization,
font selection and a theorem-interrupting float were repaired. The full reading
set was rebuilt, visually checked, and given current printed/physical locators.

CURRENT VALIDATION
Start with verification/proofread_2026-10-18/RELEASE_VALIDATION.json.
The records distinguish source proofreading, the focused mathematical wording
review, static/source reconciliation, verifier-software tests, PDF compilation,
manual visual review and packaged build replay. Earlier reports retain their
original dates and do not claim a fresh run on the October 18 sources.
All 784 retrieved source files, both retained recovery ZIPs and thirteen
comparison-baseline files match the actual October 11 delivery. That delivery
had already removed standalone font files; earlier archive hashes are historical.

FORMAL AND MATHEMATICAL SCOPE
The inherited formal contract has 19 scoped finite items, 323 named theorem
declarations in 25 active modules, six separately audited constructed objects,
and nine dependency pins. Lean, Lake and Elan are unavailable here; no fresh
Lean compilation or kernel-control execution is claimed. The inherited
compiler/axiom records are from the September 6 v0.6.0 release, pinned to Lean
4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Five physical continuum targets remain open: anomaly-free refinement, uniform
Feshbach control for the proposed tower, Lorentzian reconstruction, an Einstein
infrared limit and a positive physical massless spin-two sector. Each finite,
bounded or conditional analytic statement retains its own hypotheses. This
proofreading adds neither a new continuum theorem nor an external literature audit.

REBUILD OR VERIFY
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-vii-build.json
  python3 scripts/verify_integrity.py
  python3 -B scripts/check_publication_consistency.py
  python3 -B verification/compare_monograph_preservation.py
The last three commands are read-only by default. Optional report paths should
be outside this frozen package if the shipped integrity manifest is to remain valid.

Requirements: Python 3, XeLaTeX, xdvipdfmx, BibTeX, PyMuPDF and the TeX packages
used by the sources. Install P052 and Nimbus Sans OpenType faces, Latin Modern
text/math fonts and DejaVu Sans Mono through your normal font/TeX distribution.
The sources first accept relative fonts/ files if present and otherwise use the
explicit installed faces. Standalone font binaries are not supplied; the retained
license notices remain. No builder installs dependencies or invokes Lean.

Each companion stages its complete current source tree in isolation, runs four
XeLaTeX passes (BibTeX after the first when needed), and emits the PDF once with
xdvipdfmx. Packaged replay compares exact extracted text and page count; PDF
byte identity is reported separately. To edit navigation, rebuild the traditional
volume, run map_pages.py, refresh visual and Lean navigation, then rebuild both
guides; see their READMEs. This edition changes Paper VII only.
