Paper II Lean Guide - final companion edition, 5 October 2026

COMPILE THE INCLUDED GUIDE
  python3 build.py

This compiles the supplied TeX, chapter files, generated map/pins/crosswalk,
and exact-source display excerpts. It does not regenerate data, read a
canonical source outside this folder, invoke Lean, or download dependencies.
XeLaTeX and the fonts/packages in the TeX preamble must be installed.

REGENERATE FROM THE PRESERVED CANONICAL RELEASE
From editable/lean_guide in the final package:
  python3 build_guide_data.py
  python3 build.py
Or pass another release explicitly:
  ./build_guide.sh --source /path/to/canonical_v1.2.1
Optional independent byte comparison:
  python3 build_guide_data.py --source /path/to/release --baseline /path/to/baseline

The default source is ../../source/canonical_v1.2.1 relative to this folder.
The traditional_crosswalk.json file is a preserved editorial navigation map.
It is not a declaration of additional Lean coverage.

The data generator uses only Python's standard library. The PDF QA script
uses PyMuPDF and Pillow:
  python3 verify_pdf.py
It renders all pages and makes contact sheets in qa/. Visual inspection must
then be recorded explicitly; the rendering command alone does not inspect.

EVIDENCE
- Current check: all 22 formal-component files match the release SHA256SUMS;
  optional baseline comparison also passed for this edition.
- Current map:25 rows,160 unique mapped targets,171 target occurrences, all
  lexically located in15 Lean files / 5,603 physical lines.
- Inherited report: 2026-09-03 verification report claims successful build,
 160 compiled mapped declarations and 1,034 audited namespace entries.
- No raw Lean compiler transcripts accompany this component.
- No new Lean compiler execution is claimed.
- The source Lean files are unchanged. Display fallback files are not Lean.

See BUILD_README.txt for the transparent guide-draft correction history,
generated/static_identity_audit.json for static evidence, and the PDF for the
complete proof walkthroughs and 25-row scoped map.
