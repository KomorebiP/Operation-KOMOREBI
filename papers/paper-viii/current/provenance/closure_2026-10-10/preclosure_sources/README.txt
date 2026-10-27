KOMOREBI — PAPER VIII MONOGRAPH EDITION
Komorebi P. | 9 October 2026
Packet Operator Algorithms, Exact Compilation, and GPU Realization

READING SET
papers/Paper_VIII_Traditional_Final.pdf — 124 pages
papers/Paper_VIII_Visual_Guide_Final.pdf — 34 pages
papers/Paper_VIII_Lean_Guide_Final.pdf — 94 pages
Total: 252 pages.

All seven mathematical part files are byte-identical to the corrected retrieved
edition. All 85 numbered manuscript records and 56 explicit proof bodies remain,
together with every substantive mathematical body in the six proof supplements.
Their overlapping arguments are not counted as independent new discoveries.
The complete worked visual atlas is integrated into the traditional monograph.
The standalone companions use current actual printed and physical PDF locators.

CURRENT EVIDENCE
Start with verification/MONOGRAPH_VERIFICATION.json and its pinned owner reports.
Fresh bounded computation commands, domains, ranges, hypotheses, seeds,
tolerances, expected outputs, negative controls, and actual logs are under
verification/monograph_checks/. COMPUTATIONAL_REVIEW.json separates successful
executions, unavailable gates, historical records and retained limitations.
Layout and source conservation are separate from proof-validity claims.
Historical summaries are archived under provenance/pre_monograph_metadata/.
BASELINE_METADATA_RECONCILIATION.json explains the retrieved October 8 PDFs and
older October 6 summary values. The retrieved bytes are this edition's baseline.

FORMAL AND DEVICE SCOPE
The inherited finite register has 56 manuscript items under their hypotheses.
It records 392 theorem declarations in 40 active modules, including 19 reused
foundation declarations, and 66 separately audited constructions. Four
classical inputs are tracked separately. General SVD existence, numerical
QR/SVD computation, canonical singular-values API identification and CUDA
kernel verification remain outside this independent formal scope.
No fresh Lean compilation or GPU timing measurement is claimed.
Historical benchmark comparisons retain incomplete source-value and correctness
reference metadata. Labels such as "matched" refer to their recorded descriptive
comparison, not an independently authenticated complete Fair contract.
Three broader targets remain open: unrestricted profitable structure discovery,
compilation with nonlocal overlapping candidate models, and packet-native
communication bounds for a specified architecture.

PACKAGE AND REPLAY
papers/ — three reading PDFs
editable/ — current TeX, fonts, vector figures, source excerpts and builders
source/ and downloads/ — unchanged retrieved raw snapshots and original ZIPs
verification/ — current separately scoped runs, reports, preservation and layout
provenance/ and audit/ — exact baselines and explicitly dated historical records
COMPANION_MAP.json — current result/page/formal navigation
MANIFEST_SHA256.json — every package file except the manifest itself

  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-viii-build.json
Requires Python 3, XeLaTeX, BibTeX and PyMuPDF plus the documented companion
dependencies. Each PDF builds in an isolated directory. Page counts and
extracted text are compared exactly; full PDF byte equality is reported too.
Without --check-only all three PDFs are replaced only after all builds succeed.
  python3 scripts/check_publication_consistency.py
  python3 scripts/verify_integrity.py
Fresh finite replay instructions: verification/monograph_checks/README.md.
Use new output directories; builders install nothing and run no Lean process.
No new license grant is introduced. This edition changes Paper VIII only.
