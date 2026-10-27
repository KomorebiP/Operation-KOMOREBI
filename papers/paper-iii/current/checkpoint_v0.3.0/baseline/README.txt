KOMOREBI PAPER III | MODERN MONOGRAPH
Komorebi P. | 8 October 2026

READING SET
  papers/Paper_III_Traditional_Final.pdf: 98 pages
  papers/Paper_III_Visual_Guide_Final.pdf: 26 pages
  papers/Paper_III_Lean_Guide_Final.pdf: 49 pages
  Total: 173 pages.

The monograph connects finite typed transfer with the strengthened nonlinear
and analytic development. It preserves all 95 current proof bodies, in order,
and 125 named definitions and results. Six main vector figures and24 visual
plates are integrated into the paper. The visual guide retains the same 24
plates as a separate reader. The Lean guide contains 41 formal contract rows,
143 mapped declaration names and44 exact source excerpts.

CURRENT CHECKS
All95 proofs match the incoming current edition byte for byte. The original
canonical source retains 26/26 identical proofs. The expanded original retains
65/69 identical proofs, with the four earlier repairs still documented.
This monograph pass does not introduce another proof repair.

Fresh offline replay passed the finite release integrity/static checks,
all 11 strengthened finite/numerical check groups,124 exact visual checks,
and the rejection of all 4 deliberately false controls. All 22 current TikZ
sources regenerate exactly. The six main figures pass 20 exact assertions and
all 12 PDF/PNG assets regenerate byte-identically. These are bounded examples,
not universal proofs. Numerical checks retain their specified tolerances.

The formal compiler and kernel evidence is inherited from 3 September 2026.
Current static reconciliation checks 9 Lean files,16 formal component files,
41 map rows,143 targets and44 excerpts. No fresh Lean execution is claimed.
The nonlinear and analytic ordinary proofs retain their own hypotheses and
remain outside the finite formal contract unless their exact statements
are covered by that contract.

EDITABLE CONTENTS
  editable/traditional/: master, four chapters, six figures, integrated atlas
  editable/visual_guide/: 24 plates, 22 TikZ sources, models and checker
  editable/lean_guide/: seven chapters, full map, 44 exact excerpts and pins
  source/: complete finite, expanded, visual and historical source releases
  source/provenance/pre_monograph_2026-10-08/: incoming editable edition
  verification/: current replay, proof preservation, build and page review
  COMPANION_MAP.json and CURRENT_PUBLICATION_LOCATORS.json: current locators
  MANIFEST_SHA256.json: all shipped file hashes except its own

REBUILD
Use XeLaTeX and BibTeX from a TeX distribution. The fonts are bundled.
From any working directory:
  python3 /path/to/package/scripts/build_pdfs.py
For a read-only page/text comparison:
  python3 /path/to/package/scripts/build_pdfs.py --check-only --report REPORT.json
Each guide also has an isolated compile-only build.py. The builders never
regenerate prose, figures, formal sources or historical assembly. Legacy
assemble.py requires an explicit archival output and cannot replace this master.

After a source edit that moves pages, build each editable document, then run:
  python3 scripts/update_locators.py editable --visual-build-directory editable/visual_guide
Sync editable/visual_guide/source/pages_final.tex into traditional/visual_atlas.tex,
regenerate Lean static guide data, and rebuild until locators stabilize. Refresh
metadata and the outer hash manifest before redistributing an edited package.

For integrity only:
  python3 scripts/verify_integrity.py
Computational dependencies and commands are in verification/computational/README.txt.
No builder downloads dependencies. Read the raw *.lean.txt excerpts when copying
Lean source. Their *.render.txt companions only add TeX display escapes.

Original attribution and licensing records remain as supplied. This edition
adds no new license grant. Earlier dates and reports under source/ and dated
verification directories describe preserved snapshots, not current runs.
