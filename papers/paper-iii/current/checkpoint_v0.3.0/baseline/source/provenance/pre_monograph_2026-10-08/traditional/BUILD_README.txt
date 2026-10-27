PAPER III: TRADITIONAL FINAL EDITION

Build the final manuscript with:

    python3 build.py

This portable build uses only local assets and requires pdflatex, bibtex,
and the standard TeX packages named in the preamble. No Lean compiler is
invoked. The final source includes all authorized local mathematical repairs.

To reproduce the integration from the unmodified source copies and the
explicit edit instructions:

    python3 build.py --assemble

The build script runs pdflatex, bibtex, and two final pdflatex passes.
SOURCE_DATE_EPOCH is fixed for the edition date. Rebuilds on different TeX
versions may differ in binary PDF details; compare page text and source hashes
when assessing a portable rebuild.

OPTIONAL EDITORIAL CHECKS

    python3 audit_and_crosswalk.py
    python3 review_pdf.py

The crosswalk and render checks need PyMuPDF; contact sheets also need Pillow.
review_pdf.py deliberately resets the manual review field to pending: a fresh
render needs a fresh visual inspection before it can be marked reviewed.

CONTENTS

Paper_III_Traditional_Final.tex is the editable final manuscript.
references.bib contains the combined 19-entry source bibliography.
source/ preserves the finite and strengthened source manuscripts unchanged.
figures/ contains the three original mathematically generated figures.
EDITORIAL_CHANGES.json records every applied textual or mathematical repair.
PROOF_PRESERVATION.json records all 95 source proof environments.
canonical_label_to_final.json and expanded_label_to_final.json preserve every
original label and record its final printed number and page, together with the
1-based physical PDF page. The unnumbered cover precedes printed page 1.
SOURCE_CROSSWALK.json additionally records all 167 statement environments.
SOURCE_MANIFEST.json pins the preserved source files and figure assets.
VERIFICATION.json and qa/PDF_LAYOUT_CHECK.json describe this editorial build.

SCOPE

Part I retains the finite v1.0.1 formal contract. Part II contains the ordinary
proof development of the strengthened nonlinear manuscript. The finite
41-row formal map does not certify every result in Part II. This edition
does not claim a new Lean execution. No machine-native companion is included.
