KOMOREBI — PAPER VII: FINAL PROSE AND PROOFREAD EDITION
Komorebi P. | 18 October 2026
Quantum Seeds and Effective Dynamics
Symmetry, geometric transport, quantum channels, and bounded refinement towers

START HERE
papers/Paper_VII_Traditional_Final.pdf — 159 pages
papers/Paper_VII_Visual_Guide_Final.pdf — 42 pages
papers/Paper_VII_Lean_Guide_Final.pdf — 85 pages
Total: 286 pages. Original project title: Quantum Seed and Packet Calculus.
PROOFREAD_REPORT.md explains the prose, layout, preservation and review decisions.

COMPLETE CONTENTS
papers/ — all three final reading PDFs
editable/ — current TeX, vector plates, figures, exact excerpts and PDF builders
publication/ — synchronized reading PDFs and build configuration
source/ and downloads/ — complete retrieved source snapshots and two recovery ZIPs
verification/final_prose_2026-10-18/ — current source, build and rendered QA evidence
verification/proofread_2026-10-18/ — preceding initial proofreading evidence
verification/monograph_checks/ — earlier dated bounded computational evidence
provenance/ — retrieved baseline and prior sources, PDFs, checkers and metadata
audit/ — retained dated mathematical argument and correction reviews
COMPANION_MAP.json — refreshed result, page and formal navigation
MANIFEST_SHA256.json — size and SHA-256 of every other package file

WHAT WAS COMPLETED
All nine mathematical parts, all 40 worked visual pages and all seven Lean guide
chapters received a complete prose review. Explanations now use connected full
sentences, with unnecessary editorial hyphens and semicolons removed. Required
mathematical, bibliographic and code punctuation remains. Proofs were not
shortened into summaries, and no filler was added to force page density.

All 107 complete proofs remain. Of these, 73 have byte-identical bodies and 34
contain reviewed prose revisions. All 1,795 mathematical spans in the nine
traditional parts are byte-identical to the retrieved source. The ordered
inventory remains 147 statement records, with 142 numbered and five unnumbered.
All six supplements and all three alternative proofs remain. These overlapping
counts do not measure independent discoveries.

The visual guide and integrated atlas retain 40 worked pages and 38 vector plates.
The Lean guide retains 67 exact raw and rendered excerpts. All 121 inherited Lean
files are unchanged. All three PDFs were rebuilt, visually reviewed and given
current printed/physical locators. The nine active PDF copies are synchronized.

CURRENT VALIDATION
Start with verification/final_prose_2026-10-18/RELEASE_VALIDATION.json.
The records distinguish source prose review, independent focused review, closed
preservation comparisons, static reconciliation, checker controls, PDF builds,
manual visual review and isolated packaged build replay. Candidate review reports
retain their original hashes and findings; final reports identify the accepted
PDFs. The preceding initial proofreading record is historical for this edition.

All 784 retrieved source files, both retained recovery ZIPs and thirteen baseline
files match the actual October 11 delivery. That delivery had already removed
standalone font files. Earlier archive hashes remain historical.

FORMAL AND MATHEMATICAL SCOPE
The inherited formal contract has 19 scoped finite items, 323 named theorem
declarations in 25 active modules, six separately audited constructed objects,
and nine dependency pins. These are distinct units. Lean, Lake and Elan are
unavailable here. No fresh Lean compilation or kernel-control run is claimed.
Inherited compiler/axiom records are from the September 6 v0.6.0 release, pinned
to Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Five physical continuum targets remain open: anomaly-free refinement, uniform
Feshbach control for the proposed tower, Lorentzian reconstruction, an Einstein
infrared limit and a positive physical massless spin-two sector. Each bounded,
finite or conditional statement retains its own hypotheses.

Earlier numerical, rational and symbolic reports keep their October 9 date and
scope. They were not rerun in this prose revision. The twelve extended vector
plate sources were regenerated exactly; that is a source reproducibility check,
not a new mathematical experiment. The original 26-plate generator needs SymPy,
which was unavailable, and was not executed. The earlier 16-method verifier
regression run was not repeated. Current closed-preservation controls separately
check positive cases and reject deliberate source or contract corruption.

REBUILD OR VERIFY
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-vii-build.json
  python3 -B scripts/verify_integrity.py
  python3 -B scripts/check_publication_consistency.py
  python3 -B verification/compare_monograph_preservation.py
The last three commands are read-only by default. Optional reports should be
written outside the frozen package to keep the shipped manifest valid.

Requirements: Python 3, XeLaTeX, xdvipdfmx, BibTeX, PyMuPDF, pypdf and the TeX
packages used by the sources. P052 and Nimbus Sans OpenType faces, Latin Modern
text/math fonts and DejaVu Sans Mono must be available through the font/TeX
installation. Relative fonts/ files are accepted if supplied; otherwise the
builders select the explicit installed faces. No standalone font binaries or
new dependencies were added, and no builder invokes Lean.

Each builder stages the complete current authored source tree in isolation,
runs four XeLaTeX passes with BibTeX when needed, and emits the PDF once with
xdvipdfmx. Packaged replay compares exact extracted text and page count, with
PDF byte identity reported separately. After changing text, rebuild the
traditional volume and its page map, refresh visual and Lean navigation, then
rebuild both guides. Renew final reviews, metadata and the integrity manifest
before distributing a new edition. This revision changes Paper VII only.
