PAPER V — LEAN GUIDE
Author: Komorebi P.
Edition: 5 October 2026

Read Paper_V_Lean_Guide_Final.pdf.
Eight tutorial chapters lead from coordinate masks to Hilbert-space maps, FIR transfer,
faithful bank reconstruction, Haar packets, edge perturbations, finite tree selection,
formal cyclic products, and projective Smith actions. The complete twenty-result ledger,
all 225 theorem target names/locations, the 63-record Part II prose inventory, and
source/dependency architecture follow the tutorial.

The sources contain 52 literal declaration excerpts. Raw excerpts preserve the source
text; rendered excerpts escape TeX metacharacters and route rare glyphs to math fonts.
The excerpts depend on their original surrounding Lean context and are not standalone
compilable programs. The unchanged full Lean project is included in the complete package.

PDF build:
  python3 build.py

The build uses XeLaTeX, P052 OpenType fonts, DejaVu fonts, Latin Modern Math, and the
TeX packages listed in preamble.tex. It rebuilds the PDF from supplied catalogs and
excerpts. It does not execute Lean and needs no network access.

Optional catalog regeneration in the final complete package (from this directory):
  python3 build_guide_data.py --source ../../source/complete/original_snapshot --traditional ../traditional

Static data reconciliation verifies pinned source hashes, all 225 target declaration
lines, all 225 audit directives, and all 225 inherited axiom-output records. It does not
perform elaboration or a fresh kernel audit. The guide explicitly separates the
September 2026 Lean build from fresh October exact and numerical checks.

The final traditional manuscript has a broader Part II. Its 63 proof records carry no
additional Lean coverage claim. The formal denominator remains twenty scoped results,
225 supporting targets, and 23 proof modules. The inherited namespace audit reports
827 declarations including definitions and generated declarations.

Generated data:
  generated/result_ledger.json
  generated/targets.json
  generated/excerpts.json
  generated/extension_crosswalk.json
  generated/traditional_crosswalk.json
  generated/imports.json
  generated/dependency_pins.json
  generated/static_reconciliation.json

Quality review and build records appear in qa/ and PROOFREAD_REPORT.txt.
