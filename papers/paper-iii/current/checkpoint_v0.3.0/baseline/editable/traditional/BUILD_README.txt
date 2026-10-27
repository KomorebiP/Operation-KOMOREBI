PAPER III: TRADITIONAL MODERN MONOGRAPH

Compile the authored master and chapter inputs:

    python3 build.py

The builder requires Python 3.9 or later, XeLaTeX, and the TeX packages named
in the current preamble. BibTeX is invoked when the auxiliary file declares a
bibliography. All source inputs, bundled fonts, local styles, and PDF/vector
figure assets are copied to an isolated temporary directory. Four XeLaTeX
passes resolve contents, theorem references, and bibliography links. The build
does not regenerate the master, chapters, figures, formal source, or guide data.

Put compiled files elsewhere:

    python3 build.py --output-directory /path/to/output

Compile without changing delivered files:

    python3 build.py --check-only

The compatibility flag --assemble also compiles the authored master. It never
runs historical integration. Reproduce that integration explicitly in a separate
archival directory:

    python3 assemble.py --historical-output source/historical_assembly/replay

Historical integration is restricted to a named directory below
source/historical_assembly/. It cannot overwrite the current edition.

SOURCE_DATE_EPOCH defaults to the edition date and FORCE_SOURCE_DATE is enabled.
Rebuilds on different TeX versions may differ in binary PDF details. From the
package root, use scripts/build_pdfs.py --check-only to compare extracted page
text and page counts against the shipped PDFs. That comparison needs PyMuPDF.
No Lean compiler is invoked by either PDF builder.

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
