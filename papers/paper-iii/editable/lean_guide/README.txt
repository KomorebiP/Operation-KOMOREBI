PAPER III: THE LEAN GUIDE
Komorebi P. | Final companion edition | 5 October 2026

Read Paper_III_Lean_Guide_Final.pdf. The source is split into seven tutorial
chapters, the complete 41-row formal map, and navigation/provenance appendices.
It contains 44 source-exact excerpts and all 143 fully qualified mapped names.

Compile only, from any working directory:
  python3 /path/to/editable/lean_guide/build.py

The builder runs four XeLaTeX passes. It does not invoke Lean and does not
regenerate generated data. It needs the LaTeX packages in preamble.tex and
P052, DejaVu Sans, DejaVu Sans Mono, and Latin Modern Math fonts.

Regenerate static guide data from the delivered package:
  python3 build_guide_data.py

The default source is ../../source/finite and the default traditional directory
is ../traditional, both relative to this guide directory. Override with:
  python3 build_guide_data.py --source /path/to/finite --traditional /path/to/traditional

This regeneration checks preserved formal source checksums, lexical declaration
locations, the map, the saved kernel transcript, and inherited report hashes.
It generates exact source excerpts, dependency/import tables, and editorial
traditional-paper locators. It never edits the preserved source release.

Evidence distinction:
- The formal build and namespace audit are inherited from 3 September 2026.
- The original release includes its kernel-audit transcript.
- Current source/map/transcript reconciliation is static; no new Lean run occurred.
- Expanded ordinary proofs are outside the finite v1.0.1 denominator unless a
  particular exact statement is covered by the existing 41-row map.

Read BUILD_NOTES.txt for failed authoring attempts and repairs.
Read PROOFREAD_REPORT.txt for the final self-review scope.
Read generated/static_audit.json and qa/pdf_verification.json for actual checks.
The original source release, report, transcript, and original replay tools are
preserved in source/finite. Keep exact *.lean.txt excerpts for copying; the
*.render.txt files contain TeX display escapes only.
