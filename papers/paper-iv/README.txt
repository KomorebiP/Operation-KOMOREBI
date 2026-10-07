KOMOREBI — PAPER IV FINAL COMPANION EDITION
Komorebi P. | 5 October 2026 (America/Chicago)
Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

READING SET
papers/Paper_IV_Traditional_Final.pdf — 44 pages
papers/Paper_IV_Visual_Guide_Final.pdf — 28 pages
papers/Paper_IV_Lean_Guide_Final.pdf — 136 pages
Total: 208 pages. No machine-native companion.

The traditional edition preserves the full selected proofread manuscript:
95 numbered statements, 68 proofs and one imported standard fact. It retains the
nine prior correction groups. The visual guide has 26 worked pages and 24 exact
vector plates. The Lean guide explains the actual source architecture, all
151 formal-map rows, all 1,164 mapped names, the 68-result completion ledger and
the nine final closure modules. Printed-page/statement references connect
the three companions.

FORMAL EVIDENCE
The original v1.0.0 release reports full scoped coverage of all 68 theorem-like
manuscript results, 953 mapped theorem declarations and 211 constructions.
Its raw kernel transcript, 119 Lean source files, exact toolchain pins and
original replay procedures are included. The saved namespace audit records
2,234 entries, including 1,999 theoremInfo declarations. These are distinct counts.
Current source/map/transcript checks are static. No new Lean compiler or
kernel audit was run. This is a new editorial companion edition, not a new
formal release or a broader theorem contract.

Imported standard fact 11.1 and the paper's explicit open questions remain
outside the 68-result contract. Fixed logarithms, normalized germs, positive
integral reciprocal orders, simple-nearest-zero hypotheses, multiplicities,
exceptional zeros and the specialized diagonal determinant remain explicit.

CURRENT CHECKS
All 291 preserved source files and both recovered archives match their original
bytes. Original manifest checks and 95-record regeneration passed. Exact
integer/rational comparisons passed for 818 numeric CSV rows. All four stored
cubic brackets were rechecked using rational Taylor remainder and derivative
enclosures. The separate algebra audit passed 1,008 bounded exact assertions.
These finite results are not added together as a universal theorem count.

The original 147-check visual suite, 5 false controls, 24-plate regeneration and
original strengthened regression scripts were not rerun: SymPy and mpmath
are unavailable. No dependency installation was attempted in this Paper IV
run. Historical results remain explicitly historical. Lean/lake are also
unavailable. See verification/README.txt for exact ranges and all boundaries.

The bounded mathematical review found no new repair necessary. It reviewed
manuscript argument chains and selected actual formal interfaces, not every
transitive dependency of all 1,164 targets. The original Hadamard full-text
retrieval timed out; the citation and local specialization are distinguished
in audit/SCOPED_MATHEMATICAL_AUDIT.txt. No novelty or priority judgment is made.

PACKAGE CONTENTS
editable/ — final TeX, guide excerpts, figures, crosswalks and portable builders
source/complete/ — original complete formal, proofread and visual release
source/strengthened/ — unchanged earlier strengthened edition
downloads/ — both original ZIPs, required by the exact archive-replay checker
audit/ — bounded argument review, source pins and independent algebra checks
verification/ — current bounded run, raw logs, PDF build/layout evidence
provenance/ — current source selection and complete recovered-source hashes
COMPANION_MAP.json — all current statement/page/formal-result connections
CORRECTIONS_AND_MIGRATION.txt — retained repairs and deliberate scope migration
SERIES_STATUS.json — only IV advanced; I–III closed and V–XII frozen
MANIFEST_SHA256.json — hashes of all shipped files except the manifest itself

REBUILD OR VERIFY
PDF compilation from packaged sources in temporary directories:
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-iv-build.json
Requires TeX Live with pdflatex, bibtex, xelatex, the packages in each preamble,
and PyMuPDF for comparison. The Lean guide uses P052, DejaVu Sans, DejaVu Sans
Mono and Latin Modern Math. This rebuild invokes no mathematics or Lean.
Without --check-only, the builder replaces PDFs; refresh metadata after edits.
Each editable companion has its own compile-only build.py.

Integrity only, using Python standard library:
  python3 scripts/verify_integrity.py
Fresh exact/static replay from this package root, using standard Python:
  python3 -B verification/scripts/verify_available.py --source source \
    --downloads downloads --out verification/reproduced
Use a new output directory. See verification/README.txt for the full contract.
The independent algebra runner and its finite ranges are under audit/.
Lean replay instructions and pinned versions are in the guide and original
formal release. No supplied builder automatically installs dependencies.

Final PDFs live under papers/. Companion READMEs also use the basename of
their locally rebuilt PDF. Original source/status/reports describe their
historical snapshots. Keep them intact. No new license grant is introduced.
