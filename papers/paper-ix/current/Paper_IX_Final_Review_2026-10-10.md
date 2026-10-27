# Paper IX: final reading-edition review

**Date:** 10 October 2026  
**Title:** Euler Congruences: Completion, Factorial Strengthening, and Sharp Dyadic Geometry  
**Author:** Komorebi P.  
**Disposition:** Coordinated reader release, with the formal and historical boundaries below.

## 1. Delivered reading set

| Volume | Pages | Purpose |
|---|---:|---|
| Traditional monograph | 232 | The complete strengthened arithmetic manuscript, lifting and regularity development, qualified historical chapter, checkpoint supplements, and worked atlas. |
| Visual guide | 25 | The original exact arithmetic and theorem-derived visual route, expanded by eight worked examples. |
| Lean and evidence guide | 139 | Teaching chapters, formal-source excerpts, current manuscript navigation, retained dependency and declaration catalogues. |

The total is **396 PDF pages**. The eight worked atlas pages intentionally occur in
the monograph and the visual guide. They are not sixteen independent additions.
Canonical PDFs are in `publication/pdfs/`. Identical reader mirrors are in
`output/pdf/`. `RELEASE.json` gives their exact current sizes and hashes.

## 2. Source lineage and preservation

The predecessor was recovered from the Library as
`Komorebi_Euler_Final_Paper_Traditional_Visual_Lean_2026-10-06.zip`, containing the
8 October standardized reader update. The filename date alone was not used to
choose an older mathematical checkpoint. Its input ZIP hash is in `RELEASE.json`.

The predecessor's newer publication manifest matched all **2,896 recorded
members**. Its root legacy verifier was still checking pre-formatting metadata.
The predecessor contained 220-, 17-, and 138-page current reader PDFs; older root
release metadata describing different page counts was not treated as current.

The byte-preservation comparison retained **2,334 files in `preserved/` unchanged**,
including **633 Lean source files** across the inherited versions. These are file
counts, not distinct theorem counts. The strengthening source and ordinary-tail
scope source also remain byte-for-byte unchanged.

All **289 literal proof-environment spans** in the inherited active TeX sources
were compared and retained byte-for-byte. This comparison includes historical
proof spans and is a preservation test, not a fresh proof of their correctness.
The reconstructed chapter was edited outside those proof bodies: its provenance
paragraph, figure inclusions and captions were updated. The inherited numerical,
normalization, integrality and range corrections remain visible.

See `verification/2026-10-10/SOURCE_PRESERVATION.json`. Previous versions of modified
release and presentation files are retained under `predecessor_files/`.

## 3. Substantive reader improvements

The new eight-page atlas develops exact examples of the reciprocal coefficient
recurrence, the genuine factorial-normalization loss, the required odd-prime sign
twist, a finite Newton computation modulo 256, a compatible 3-adic root tower, a
singular non-lifting class and a positive singular control, incompatible projected
corrections, and loss of one root-precision digit under a weighted derivative.
The underlying values are computed with rational and integer arithmetic. The
atlas distinguishes the universal theorem used for truncation from its finite
illustration checks. It adds no Lean endpoint.

The historical chapter had fourteen original figure inclusions whose source files
were absent. All fourteen blank panels now have explicitly labeled **new
reconstructions**, including subgroup selectors, compressed inverse periods,
finite-field Fourier transfer, standard-window reduction, kernel valuations,
Mahler sparsification, Fibonacci refinement, cokernel obstruction, recurrence
packets and Chinese remainder reconstruction. The original artwork was **not**
recovered. The modulo-seven inverse plot uses the already-corrected tail
6, 5, 2, 6, 5, 2, rather than repeating the erroneous historical line.

The new diagrams comprise explanatory schematics and exact finite examples. Their
presence does not upgrade the historical chapter's theorem or formalization
status. The diagram program and exact data are included.

The Lean companion now resolves its **62 inherited statement entries** against
the current 232-page monograph, retaining **202 source links**. The old historical
crosswalk is kept separately. A further navigation table covers fifteen newer
written-proof statements and the eight worked examples. The current paper label
map resolves **445 labels** against named PDF destinations. The visual contents
were tightened to a single readable page, and the root-tower figure's final column
label was shortened to avoid crowding.

## 4. Executed arithmetic and metadata checks

`CURRENT_GATE_REGISTER.json` identifies nine successful executed gates and verifies
that their script hashes match this release. Some gates were completed again in a
later interrupted repeat; that repeat itself is not marked passed. Earlier
successful receipts for unchanged scripts remain valid and are identified as
such. No incomplete execution is relabeled as successful.

| Gate | Executed scope |
|---|---|
| Delta/boundary checks | 2,251 family cases, three definition checks, and a cancellation control. |
| Metric tables | 47 exact Newton valuations and six upper-half boundary cases. |
| Formal-source reconciliation | Reconstructed the inherited declaration/evidence index and statement-source links, reconciled recorded hashes/logs, and reran the parser regression. No Lean execution. |
| Dyadic regression | Row bound 512, 4,096-bit modular precision, order bound 128 and rational comparison through row 16. |
| Factorial extension | Row bound 96 and 1,024-bit precision, including homogeneous sharpness and the stronger address-two floor. |
| Factorial frontier | Row bound 96, 1,024-bit precision and mixed orders through five, retaining strict-surplus examples rather than claiming universal equality. |
| Original visual-data replay | 5,490 finite assertions; the regenerated exact-data JSON agrees with the inherited JSON. |
| New worked atlas | 463 exact checks, including independent coefficient constructions and positive/negative lifting controls. |
| New reconstructed diagrams | 802 exact finite checks, including independent affine-kernel constructions and the corrected compressed inverse. |

The dyadic regression records **68 rational comparisons, 525,312 first-shift
checks, 1,141,424 higher-difference lower-bound cases, 139,000 mixed cases, and
2,048 Newton-coefficient checks**. These and the other gate counts overlap. They
are not added into a synthetic total and are not substitutes for universal proofs.
A bounded candidate classification encountered by a check remains bounded data,
not a new theorem for every order.

The release-side source reconciliation is distinct from replaying historical
compiler controls. The twelve inherited negative-control logs are source/log
evidence, not twelve fresh compiler rejections. The four historical affine logs
with missing original digest records retain that limitation.

## 5. Publication checks and reproduction

All three current readers compiled successfully. The selected clean builds report
no unresolved build warnings, overfull-box diagnostics, missing-glyph diagnostics,
or unresolved-reference diagnostics. The metadata check verifies all six reader
copies, the current page counts, the 445-label map and the retained source links.
It also resolves **592 internal PDF links** across the three readers. External
URLs were not newly checked in this pass.

Every final page was rendered for contact-sheet review. Twelve selected dense,
changed or representative pages were additionally rendered with `pdftoppm` at
150 dpi for closer inspection. The automated preflight found no out-of-page words,
empty-text pages, or invalid internal page destinations. These checks and visual
inspection are not a claim that software can prove the absence of every possible
layout defect.

An isolated copied-source rebuild reproduced **every PDF byte except the generated
trailer identifiers**. The frozen released PDF hashes are preserved in
`RELEASE.json`. Strict binary identity failed and is not claimed. The rebuild
script documents precisely which metadata is excluded from its comparison.
`FROZEN_REBUILD_REPORT.json` records the successful final comparison.

## 6. Failures and corrections retained in the package

The legacy root verification failed against stale pre-formatting hashes. The
newer predecessor manifest was checked separately and matched. The current
verifier checks the current frozen edition without pretending that the old audit
hashes certify edited presentation files.

The first Lean-guide PDF rebuild failed because XeLaTeX could not resolve the
installed Latin Modern Math font by its family name. The source now requests its
installed filename. No font files are bundled, and this was a typesetting failure,
not a Lean theorem failure.

One reconstruction render failed because matplotlib MathText does not support the
TeX command used in a title. The renderer-compatible notation was corrected; the
exact arithmetic checks were unchanged. A long displayed path and a crowded table
heading were also corrected during the layout pass.

A copied-source build was interrupted by the outer command timeout. Its partial
auxiliary file caused the next naive retry to fail with a runaway TeX argument.
The interrupted log and auxiliary file were retained. The build driver was then
changed to start each selected generated-output directory cleanly. The clean
retry and the final isolated replay passed. A later combined repeat was also
interrupted before all its arithmetic/figure jobs completed. Its incomplete jobs
were not counted as passes; successful current-script receipts are selected
explicitly in the gate register.

The initial exact-byte rebuild comparison failed solely because of PDF trailer
identifiers. This is a documented reproducibility boundary rather than an altered
mathematical statement or unexplained text reflow.

## 7. What this release does not claim

The inherited record identifies a Lean-checked external Nishibuchi capstone and
specific arithmetic, dyadic, lifting and regularity endpoints. There was **no fresh
Lean/Lake compilation** in this publication pass. The newer mixed-step, factorial,
all-rank and radius developments remain written proofs with their preserved
internal audits and exact finite checks. The 289 unchanged proof spans are not
289 freshly re-proved theorems.

The full ordinary Euler-tail simplicity problem, remaining higher-difference exact
classifications and broader Native13.2/13.3 programs remain open in the stated
scopes. The historical chapter is not blanket-certified. Its original bibliography
was not recovered, and its unresolved historical citation keys are expressly
marked rather than guessed. Original historical figure bytes also remain absent,
although all fourteen reader panels now have new reconstructions.

This is an internal publication and consistency review. It is not external peer
review, journal acceptance, a claim of historical priority, or a declaration that
every broad research target in Paper IX has been closed.

## 8. Frozen package and use

The editable TeX, Python figure and check programs, inherited Lean sources and
archives, source maps, actual logs, failed-attempt records, and reading PDFs are
included. `README.md` gives commands for integrity checks, bounded arithmetic
replay and isolated PDF rebuilding. The archive carries no fonts and performs no
automatic downloads.

The final root manifest covers frozen files other than itself. Packaging verifies
that manifest first and checks ZIP CRC. Delivery validation additionally extracts
the ZIP and reruns the standard integrity and publication checks on the extracted
copy. The delivery-level receipt is supplied alongside the ZIP to avoid a
self-referential hash claim inside the archive.
