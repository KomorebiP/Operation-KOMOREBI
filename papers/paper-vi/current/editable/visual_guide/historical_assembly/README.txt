PAPER VI — FINAL VISUAL GUIDE
Komorebi P. — 5 October 2026

Deliverable
  Paper_VI_Visual_Guide_Final.pdf
  44 physical pages: 2 preliminary pages + V1–V42.
  40 editable vector plates: 26 preserved + 14 new.

Read
  source/pages.tex retains the 28-page September worked atlas. Its mathematical
  formulas and original vector plates are unchanged. Editorial source references
  now identify Traditional Part I; obsolete combined-PDF navigation and historical
  evidence wording have been updated for this standalone final guide.
  source/extensions.tex adds V29–V42, including new worked examples and an evidence
  map. Part II references have an E prefix. The front matter also navigates to the
  complementary Part III and the operator material migrated from Paper IV.

Build
  python3 build.py
  python3 build.py --output-dir /absolute/path/to/output
  python3 build.py --check-only

  Python 3 plus pdflatex and the TeX packages named in the main .tex file are
  required. The build stages sources in a temporary directory, uses three TeX
  passes, and rejects overfull boxes, missing glyphs, and unresolved references.
  It uses the shipped vector geometry; SymPy is not required to build this PDF.
  SOURCE_DATE_EPOCH fixes the edition timestamp. No network calls are made.

Fresh exact examples
  python3 checks/check_extensions.py --output /path/to/EXTENSION_EXACT_CHECKS.json

  Uses only the Python standard library. Current result: 120 exact assertions
  and 8 rejected false controls. The report lists each finite assertion, every
  false alternative, the checker hash, and limits. This does not rerun Lean,
  certify all analytic proofs, or replay the inherited symbolic suite.

  Separate package-level verification records 182 independent rational assertions
  and 4 rejected controls for selected original atlas examples. These counts
  remain separate from the new extension suite and the inherited record.

Inherited evidence
  checks/INHERITED_EXACT_CHECKS.json is the saved September record of 204 exact
  or symbolic assertions and 11 rejected false controls. The unchanged historical
  verifier is retained as checks/inherited_verify_examples.py. It imports the
  preserved source/models.py and requires SymPy and mpmath, unavailable in the
  current environment. It was NOT freshly executed for this final edition.

  With those original dependencies in a separate working copy, one may run:
  python3 checks/inherited_verify_examples.py --output /path/to/replayed.json
  python3 source/generate_graphics.py

  Regenerating original graphics is separate from the portable PDF build. The
  original graphics/PLATE_INDEX.json describes the 26 inherited plates only.
  graphics/EXTENSION_PLATE_INDEX.json describes the 14 new plates. The new plate
  generator source/make_extension_plates.py uses only the standard library.

Review and crosswalk
  python3 review_pdf.py
  python3 make_crosswalk.py --traditional-map /path/to/canonical_label_to_final.json

  review_pdf.py requires PyMuPDF and Pillow. It renders all 44 pages and checks
  geometry, vector-only graphics, destinations, and TeX warnings. PDF_QA.json
  records mechanical checks. VISUAL_REVIEW.txt separately records inspection.
  The crosswalk resolves printed and physical traditional pages after pagination
  is frozen; root assembly refreshes this against the authoritative map.

Scope
  The formal release remains the inherited 33-result contract, with 341 supporting
  declarations in 47 proof modules. No fresh Lean kernel verification is claimed.
  The new visual examples do not expand that contract. The complete recovered
  source snapshots remain separately available in the final edition package.
