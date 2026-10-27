KOMOREBI — PAPER IV MONOGRAPH EDITION
Komorebi P. | 8 October 2026
Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

READING SET
papers/Paper_IV_Traditional_Final.pdf — 77 pages
papers/Paper_IV_Visual_Guide_Final.pdf — 28 pages
papers/Paper_IV_Lean_Guide_Final.pdf — 140 pages
Total: 245 pages.

The traditional volume uses the monograph design established for Paper III.
All 95 canonical numbered statement environments and 68 proof bodies remain
byte identical to the selected proofread source. Six Python exact-model
figures, a worked coefficient example and a complete 26-plate visual atlas
support the mathematical development. The standalone visual guide retains
all 26 worked pages and 24 vector figures. The Lean guide preserves all
151 map rows, 1164 declaration targets, 68 coverage entries and 49 excerpts.
Current printed-page references connect the three volumes.

CURRENT EVIDENCE
All three PDFs compiled using isolated four-pass XeLaTeX builders and bundled
fonts. All 245 pages were rendered and reviewed. The canonical source,
mathematical environments, original Lean source and recovered archives were
preserved. Current reports live in verification/MONOGRAPH_VERIFICATION.json
and the monograph_* reports. Earlier reports retain their dated scope.

Fresh bounded replay passed 1008 exact rational algebra assertions, 981 CSV
rows, 647 original-paper checks, 1246 strengthened checks, 147 visual checks,
five deliberately invalid controls, and four rational cubic brackets. The
historical-source regression checks inspect unchanged historical snapshots.
All 24 current vector figures regenerated exactly. Finite checks support
only their stated ranges and are not a universal proof or theorem count.

FORMAL EVIDENCE
The September 5 v1.0.0 formal release records 68 scoped manuscript results,
953 mapped theorem declarations and 211 constructions. Its raw transcripts,
119 Lean source files and pinned dependency versions are included unchanged.
Current checks reconcile the source, map, contract, transcripts and excerpts
statically. lean, lake and elan are absent, so no new Lean execution occurred.
The saved namespace audit reports 2234 entries, including 1999 theoremInfo
declarations. Those inherited counts were not regenerated in this edition.
Imported standard fact 11.1 and explicit open questions remain outside the
68-result contract. No new external literature or novelty audit was run.

PACKAGE CONTENTS
editable/ — current TeX, bundled fonts, figure generators and portable builders
papers/ — three final reading PDFs
publication/ — synchronized PDF copies and delegated builder
source/ and downloads/ — unchanged recovered sources and original archives
verification/ — current bounded checks, raw logs and current edition reports
audit/ — retained dated argument review and bounded algebra evidence
provenance/ — source selection, original hashes and pre-monograph metadata
COMPANION_MAP.json — current statement/page/formal associations
MANIFEST_SHA256.json — hashes of all shipped files except this manifest

REBUILD OR VERIFY
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-iv-build.json
Requires Python 3, XeLaTeX, BibTeX, the packages in each preamble and PyMuPDF.
Each editable companion contains a compile-only build.py. All builders copy
the full portable source tree into isolated staging directories. Without
--check-only the series builder updates papers/ and publication/pdfs/.
Refresh metadata and hashes after source edits. No builder installs packages.

Integrity only:
  python3 scripts/verify_integrity.py

Source preservation and cross-reference check:
  python3 verification/monograph_checks/compare_preservation.py

The bounded suite replay requires SymPy and mpmath. New Python figures require
NumPy and Matplotlib. Commands, exact ranges and limitations are in the
verification reports and editable companion instructions. Lean replay uses
the original pinned toolchain and procedures. No new license grant is made.
