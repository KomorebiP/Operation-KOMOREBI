# Paper IX: Euler Congruences

## Monograph reading edition, 10 October 2026

**Euler Congruences: Completion, Factorial Strengthening, and Sharp Dyadic Geometry**  
Komorebi P. / Operation Komorebi / Core series IX

This is the coordinated reading set: the traditional monograph, the visual guide,
and the Lean and evidence companion. The current PDFs are in `publication/pdfs/`,
with byte-identical convenience copies in `output/pdf/`.

| Reader | PDF file | Pages |
|---|---|---:|
| Traditional monograph | `Paper_IX_Euler_Main_Final.pdf` | 232 |
| Visual guide | `Paper_IX_Euler_Visual_Guide_Final.pdf` | 25 |
| Lean and evidence guide | `Paper_IX_Euler_Lean_Guide_Final.pdf` | 139 |

The combined PDF count is 396 pages. Eight worked atlas pages are intentionally
shared between the main paper and the visual companion.

## What changed

The strengthened Euler manuscript is retained, not replaced by a shortened
summary. This edition adds eight exact worked examples connecting reciprocal
coefficients, normalization, the odd-prime sign, Newton truncation, smooth and
obstructed lifting, shared corrections, and derivative-weighted precision.

The reconstructed historical chapter formerly contained fourteen blank figure
panels because its original artwork was absent. It now contains fourteen clearly
labeled **new reconstructions**. These are schematics and exact finite examples,
not a claim to have recovered the original figure files. Its older mathematical
corrections and proof-status notices remain visible.

The Lean companion's navigation now points to the current monograph, including
62 inherited statement entries, 202 retained source links, and the newer written
proof and worked-example routes. The visual contents now fit on one page.

The stale release verifier, outdated packaging entry point, font lookup, and build
failure reporting were repaired. Builds now begin with clean generated-output
directories so that interrupted TeX auxiliary files cannot corrupt a retry.

## Mathematical and formal boundaries

The inherited record includes the full stated external Nishibuchi congruence
capstone and the individually identified arithmetic, dyadic and lifting results.
The source/log reconciliation was rerun. **No Lean or Lake compiler was available
for a fresh theorem build in this release pass.**

The newer factorial, mixed-step, all-rank and Taylor-radius results remain written
proofs with their retained internal audits and bounded computational checks.
This reading edition does not silently promote them to compiled Lean endpoints.
The general ordinary Euler-tail simplicity problem, remaining exact
higher-difference classifications, and the broad Native13.2/13.3 programs retain
their stated open boundaries.

The recovered historical chapter has a narrower provenance status. Its original
bibliography was not recovered. Unresolved historical citation keys are explicitly
preserved as such, not replaced with guessed references. That chapter is not
blanket-certified by its inclusion in this publication.

## Verification and reproduction

From the extracted directory, run the standard-library-only integrity check:

```text
python verify_release.py
```

With PyMuPDF installed, check PDF identities, mirrors, page bounds and navigation:

```text
python preflight_pdfs.py
```

Run the bounded arithmetic and source/log gates without changing the frozen
archive. Choose an empty output directory outside this release:

```text
python replay_checks.py --output ../paper_ix_replay --jobs 1
```

The full dyadic check uses row bound 512, 4,096-bit modular precision and difference
order bound 128. This is exact finite modular arithmetic, not a universal proof.
The nine gates overlap and their counts must not be added as independent evidence.
NumPy and matplotlib are needed for the inherited visual-data replay. No command
installs software, downloads a toolchain, or launches Lean.

The two new example programs can also run on their own:

```text
python tools/worked_examples.py --output ../worked_examples.json
python tools/reconstructed_figures.py --output ../reconstructed_figures.json
```

An optional `--figures DIRECTORY` argument regenerates each program's figures.
Do not write regenerated figures into this frozen release unless intentionally
creating a new edition and retaining the old manifest.

For the typeset readers, use an installed TeX environment with pdfLaTeX, XeLaTeX,
Latin Modern, TeX Gyre fonts, DejaVu Sans Mono and PyMuPDF:

```text
python rebuild_pdfs.py --work-dir ../paper_ix_pdf_rebuild
```

The rebuild copies the source and figures into an empty external directory. The
frozen release remains unchanged. The clean reproduction matched every PDF byte
except the generated trailer identifiers. That is explicitly **not** a claim of
unqualified byte-for-byte identity. The frozen PDFs' hashes, rather than those of
the regenerated copies, are the identities used by the released navigation map.
No font files are bundled.

To package the already verified, unchanged edition:

```text
python package_release.py --output ../paper_ix_release_copy.zip
```

This command verifies the frozen manifest first. It does not renew the mathematical
review or generate a new proof certificate.

## Evidence map

`Paper_IX_Final_Review_2026-10-10.md` is the release-specific review. The current
metadata is `RELEASE.json`, and `MANIFEST_SHA256.json` covers the frozen files other
than itself. The manifest is an integrity record, not a digital authenticity
signature.

`verification/2026-10-10/` contains the executed checks, source preservation
comparison, publication tests, rendering records, clean rebuild comparison, and
records of failed or interrupted attempts. `CURRENT_GATE_REGISTER.json` selects
successful receipts whose script hashes match this release, without treating
interrupted reruns as passes.

`preserved/` retains the earlier mathematical sources, Lean files, archives, and
logs with their original scope. `audits/` and `evidence/` are inherited records.
Their earlier dates and hashes are historical and must not be read as a new
compiler run. Previous root metadata is retained under
`verification/2026-10-10/predecessor_files/`.

Source and log integrity, internal editorial review, exact finite checks, and
formal kernel acceptance are distinct types of evidence. This package also makes
no claim of external peer review, journal acceptance, or global historical priority.
