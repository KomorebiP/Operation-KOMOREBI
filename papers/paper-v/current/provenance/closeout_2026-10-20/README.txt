KOMOREBI — PAPER V MONOGRAPH EDITION
Komorebi P. | 9 October 2026
Multiresolution Signal Calculus
Exact coordinates, singular packets, and stable reconstruction

READING SET
papers/Paper_V_Traditional_Final.pdf — 129 pages
papers/Paper_V_Visual_Guide_Final.pdf — 43 pages
papers/Paper_V_Lean_Guide_Final.pdf — 64 pages
Total: 236 pages.

The traditional volume preserves both currently corrected mathematical
branches: the 20-result formal core and 63 broader proof records. All 119
numbered environments and 83 proof bodies remain byte identical to the
recovered current edition. Counts are proof records, with mathematical
overlap, not a sum of independent or newly formalized results. The monograph
adds reading notes, three exact-model Python diagrams and all 40 worked
visual plates. All 32 original figures remain. Four heatmaps have presentation
repairs for contrast, label size and title clearance, with unchanged data.

The standalone visual guide preserves 40 worked pages and 37 figures. All 71
displays and 464 inline formulas retain their mathematics, with one documented
LaTeX grouping correction required by Unicode math. All 73 traditional page
locators are current. The Lean guide retains 20 result rows, 225 theorem targets,
52 exact excerpts, 63 broader proof locators and nine dependency pins.

CURRENT EVIDENCE
All three PDF source trees use portable four-pass XeLaTeX builders and bundled
relative fonts. All 236 pages were rendered and visually inspected. Current
reports start at verification/MONOGRAPH_VERIFICATION.json. The full packaged
replay report is verification/MONOGRAPH_PACKAGED_BUILD.json.

Six bounded v2 computation manifests record current execution and hashes.
The 20 exact-model tests passed 305,933 counted exact assertions. The 16 verifier
control methods, 33 current pytest and 27 overlapping historical pytest passed.
The Annals suite passed 11,052 mixed exact/numerical checks in 13 groups. All 52
floating metrics and 18 discrete metric leaves reproduced stored values.
Eighteen numerical companion figure pairs and all 37 visual figures regenerated.
The symbolic visual suite passed 181 checks and rejected 7 false controls. The
rational extension suite passed 38 checks and rejected 4 false controls. These
counts are not added into a universal proof or theorem total. Numerical
residuals are floating evidence, not interval certificates. All 598 recovered
historical source snapshot files remain byte identical, including original
formal sources and evidence.

FORMAL SCOPE
September 6 v1.1.0 evidence records 20 scoped manuscript results, 225 theorem
targets, 23 proof modules and 827 namespace declarations. These are distinct
counts. The current static source/map/contract/transcript reconciliation does
not replace Lean elaboration or kernel validation. lean, lake and elan are
absent, so no fresh Lean execution occurred. The 63 extended proof records do
not add formal coverage. Two broad edge recovery conjectures remain open.
The separated-jump results retain their fixed model, explicit signal/noise
gaps and admissible grids. No unrestricted edge recovery or new external
literature or novelty audit is claimed.

HISTORICAL RECOVERY GAP
An earlier truncated archive left 17 October 5 verification artifacts missing:
the old available-checks runner, raw results/logs and nine verification figure
PDFs. Their original expected paths, sizes and hashes are listed in
provenance/HISTORICAL_RECOVERY_GAPS.json. Current manuscripts, mathematical
figures and the original September formal project are intact. Fresh tests
are recorded separately as new evidence. They do not authenticate the missing
historical runner or reproduce the old combined available-checks gate.

PACKAGE CONTENTS
papers/ — three final reading PDFs
editable/ — current TeX, relative fonts, exact excerpts, figures and builders
publication/ — synchronized PDF copies and delegated builder
source/ and downloads/ — unchanged original mathematical/formal snapshots
verification/ — current bounded runs, raw records, source comparison and QA
provenance/ — source selection, earlier metadata and exact recovery inventory
audit/ — retained dated argument review and historical correction validation
COMPANION_MAP.json — current statement/page/formal navigation
MANIFEST_SHA256.json — all shipped file hashes except this manifest

REBUILD OR VERIFY
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-v-build.json
Requires Python 3, XeLaTeX, BibTeX, packages in the preambles and PyMuPDF.
Without --check-only, PDFs in papers/ and publication/pdfs/ are replaced after
all three builds pass. Each editable companion has its own isolated builder.
No supplied builder installs dependencies or executes Lean or mathematics.

Integrity only:
  python3 scripts/verify_integrity.py
Canonical source preservation:
  python3 -B verification/monograph_checks/compare_preservation.py
Fresh finite replay commands, exact ranges and dependencies:
  verification/monograph_checks/README.txt
Use new output directories as documented. Figure generators require the
listed Python plotting dependencies. After edits, rebuild, inspect pages,
refresh guide locators, metadata and the manifest. Original Lean replay uses
the preserved pinned toolchain and procedures. No new license grant is made.
