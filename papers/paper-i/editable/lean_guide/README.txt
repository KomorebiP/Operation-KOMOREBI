Paper I Lean Guide, final companion edition, 5 October 2026

Main files
  Paper_I_Lean_Guide_Final.pdf
  Paper_I_Lean_Guide_Final.tex
  build_guide_data.py
  generated/theorem_map.json
  generated/static_identity_audit.json
  generated/local_imports.json
  generated/excerpts.json

Scope
  Detailed tutorial plus the complete 35-row normative contract of the
  traditional v1.3.1 distribution's formal component v1.0.2.
  20 local source files, 84 mapped targets, 1,126 historical namespace entries.
  Distinguishes this component from the machine paper's attached seven-file
  tranche, eight mapped stable records, and wider 108-record inventory.

Verification in this finalization
  Static source and log identity checks passed. The delivered 20 source files
  match the historical successful run, and all 24 compiler/audit/control logs
  match their recorded hashes. Map targets and historical axiom reports agree.
  No fresh Lean compilation is claimed. See the guide's replay instructions.

Regenerate, from editable/lean_guide/ in the final package
  python3 build_guide_data.py --source ../../source/traditional_v1.3.1
  xelatex -interaction=nonstopmode -halt-on-error Paper_I_Lean_Guide_Final.tex
  xelatex -interaction=nonstopmode -halt-on-error Paper_I_Lean_Guide_Final.tex
  xelatex -interaction=nonstopmode -halt-on-error Paper_I_Lean_Guide_Final.tex

The generator accepts any preserved v1.3.1 distribution with --source and does
not modify it. Default path assumes editable/lean_guide in the final package.
Dependencies: Python 3 standard library for generated data, XeLaTeX with the
packages listed in the preamble, P052, Nimbus Sans, DejaVu Sans Mono, and Latin
Modern Math fonts. No Lean executable is required to regenerate this guide.

Exact .lean.txt excerpts are verbatim source ranges. Parallel .render.txt
files contain TeX font fallback escapes only. The quotient slash is drawn
with a typographic mathematical slash because the installed fonts lack the
Lean U+29F8 glyph; the exact underlying excerpt retains U+29F8. This affects
typesetting only, never the preserved Lean source or declaration map.

Source-to-prose self-review
  Scope: all newly authored guide text and generated contract tables.
  Routine corrections: source excerpt boundaries, glyph fallback, font faces,
  cross-reference passes, and appendix page break.
  Mathematical-token changes to preserved source: none.
  Unresolved mathematical issues: the input boundaries and unmatched expanded
  statements are explicitly documented, not claimed as closed.
  PDF: final log checked for missing glyphs, overfull boxes, font fallback,
  and unresolved references. All pages rendered and inspected as contact
  sheets, with detailed source-listing and map inspection.
