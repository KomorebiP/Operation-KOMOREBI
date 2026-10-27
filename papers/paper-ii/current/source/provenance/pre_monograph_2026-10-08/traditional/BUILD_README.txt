Paper II traditional final edition
Author: Komorebi P.

Build from this directory:
    python3 build.py

Requirements: Python 3 standard library; latexmk, pdfLaTeX, BibTeX, Latin Modern,
and the TeX Live packages named in the preamble. No Lean, network access, or
external Python packages are required to compile the article.

The final .tex is independently editable. All 13 exact PDF figures and the
combined bibliography are local. The source/ directory preserves the two
unaltered source manuscripts and expanded bibliography. To regenerate the
integration deterministically from those originals:
    python3 build.py --assemble
    python3 audit_and_crosswalk.py

SOURCE_DATE_EPOCH is fixed by build.py to 2026-10-05 00:00 UTC. Exact PDF bytes
also depend on the installed TeX engine and package versions. This edition
was built with pdfTeX 3.141592653-2.6-1.40.24 (TeX Live 2022/Debian), latexmk,
and BibTeX 0.99d.

Audit files:
    EDITORIAL_CHANGES.json       exact 18 local mathematical clarifications
    PROOF_PRESERVATION.json      original proof identity and merged-proof scope
    SOURCE_CROSSWALK.json        canonical/expanded labels to final numbering
    canonical_label_to_final.json 26 visual/formal companion anchors
    SOURCE_MANIFEST.json        unchanged source and figure SHA-256 identities
    BIBLIOGRAPHY_CHECK.json      small primary-source bibliographic correction
    VERIFICATION.json           final build, scope, and visual-review result
    PROOFREAD_REPORT.txt        conservative mathematical proofreading report

The source has 50 proof environments and 61 named definitions/results. All 43
expanded proof bodies are byte-identical. Six canonical proof bodies are
byte-identical; the concrete Smith solvability display has one explicitly
recorded existential-quantifier restoration. Eight overlapping canonical proof
bodies are represented by the expanded counterparts, not printed twice. Their
complete original text remains in source/canonical.tex. This is integration,
not a claim that two differently scoped source statements were byte-identical.

There was no fresh Lean build for this traditional edition. The expanded
ordinary proofs do not acquire the canonical 25-row formal coverage by being
included in one PDF. No machine-native companion is included.

Optional layout review reproduction:
    python3 review_pdf.py
This requires PyMuPDF and Pillow. It creates low-resolution contact sheets and
14 detail-page images under qa/, not a high-resolution full-page cache.
