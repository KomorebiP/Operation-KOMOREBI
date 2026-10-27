# Verification Notes — Paper I v1.2.1

Author: **Komorebi P.**  
Verification date: **2026-09-03**

## Outcome

The v1.2.1 manuscript, Python v1.1.1 companion, Lean v1.0.1 component,
machine-readable results, and release records passed the internal verification
described below. The certificate-explicit Lean completion contract is covered
35/35 by declarations classified `Exact` or `Stronger`. This is an internal
technical audit, not independent peer review or a historical-priority
determination.

## Manuscript build

- Final PDF: 40 letter-size pages, 628,692 bytes.
- Engine: latexmk 4.83 with pdfTeX 1.40.25 (TeX Live 2023).
- Reproducible epoch: `SOURCE_DATE_EPOCH=1788393600` (2026-09-03
  00:00:00 UTC). Two independent clean builds were byte-identical.
- PDF SHA-256:
  `437f7acc3f1a26592020dae1cbe050f521e0ce4f92a24f41ef666dcb9eb45b5c`.
- TeX SHA-256:
  `17f3601b5f33a8c6cf2d5efeb99e97c5be32c4b33f85b7b44121921c9ed66023`.
- Metadata reports title version 1.2.1 and author `Komorebi P.`.
- The fixed-point LaTeX log has no undefined citation/reference, overfull box,
  underfull box, or package warning.
- All fonts are embedded; no Type 3 font is present.
- Ghostscript 10.02.1 parsed the PDF successfully. pypdf reports 40 pages,
  no encryption, one uniform 612 by 792 point page box, and extractable
  nonempty text on every page.

The final PDF was also checked with `pdfinfo`, `pdffonts`, `pdftotext`, and a
full Poppler rasterization.

## Visual inspection

Every final page was rasterized at 1,063 by 1,375 pixels (125 DPI) and
inspected in order. The repaired production-grammar diagram on page 5 and
theorem-dependency diagram on page 32 were additionally inspected at full
page resolution, as was the final references page. Connectors are behind the
nodes and clear of every label. No clipped text, overlap, missing image, black
glyph box, blank page, malformed table continuation, or sparse spill page was
found.

`provenance/Verification_Render.png` is the ordered five-by-eight contact
sheet of all 40 final pages. Its dimensions are 1,180 by 2,408 pixels and its
SHA-256 is
`9a9f4bca2f8ac9b9655faa6f656148f163044f281090f6f59118596afc1d3cdf`.

## Python verification

- The Python companion is v1.1.1; the version change records the two corrected
  diagrams and the manuscript-versus-companion provenance split.
- `python -m pytest -q -W error -p no:cacheprovider
  --import-mode=importlib` reports 18/18 tests passed against the installed
  wheel with no warning, and `python -m pip check` reports no broken
  requirement.
- `results/numerical_results.json` and `results/run_record.json` separately
  record manuscript release 1.2.1 and Python companion/package 1.1.1.
- Repeated runs under the fixed epoch produced byte-identical JSON, CSV, PDF,
  and PNG outputs.
- Two clean wheel builds were byte-identical. The wheel installed and imported
  successfully as v1.1.1; its SHA-256 is
  `e03ecd9185b20227dd96eb9ab0cd3f7215b89663a4eaec17dff45c25ca3fcce1`.

## Lean verification

- Lean 4.34.0-rc2, Lake 5.0.0, Mathlib revision
  `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- A clean warning-fatal `lake --wfail build` completed exactly 8,883 jobs.
- The executable theorem-map checker passed all 35 contiguous contract rows,
  84 unique compiled declarations, and 84 matching direct axiom reports in
  `formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md`.
- Of the 35 rows, 29 are classified `Exact` and six `Stronger`.
- The separate fail-closed kernel audit traversed all 1,126 compiled
  `Komorebi.*` and `KomorebiVerification.*` declarations.
- A source scan found no actual `sorry`, `admit`, or `sorryAx` term and no
  project-specific `axiom`, explicit `opaque`, or `unsafe` declaration.
- The direct and namespace audits report only `propext`, `Classical.choice`,
  and `Quot.sound`, as applicable.

Rows 10, 13, 14, 32, and 35 consume explicit classification, primary,
polynomial, spectral, or exact-computation certificates. Lean checks the
stated implications and canonical `k[T]` bridge; it does not construct Jordan
or Wedderburn decompositions, an eigensolver, extracted executable code, or
certificate machinery. Exact declarations and exclusions are recorded in
`formalization/lean/VERIFICATION_REPORT.md` and the theorem map.

## Release and privacy checks

- JSON release/result files parse successfully; `CITATION.cff` parses as YAML.
- The canonical package excludes caches, LaTeX intermediates, repository
  metadata, and Lean build caches.
- Packaged text and extracted PDF text were scanned for private workspace
  paths, unresolved placeholders, and development-only proof markers.
- The historical `Paper_I_Audit_Ledger_v0.1.0.md` remains an unchanged record
  of v1.0.0.
- No repository URL, commit, DOI, or license was invented.
  `LICENSE_STATUS.md` records that no license has been selected.

## Remaining external work

Before scholarly submission, the paper still warrants independent proof
review, a broader literature/priority search, and venue-specific formatting.
