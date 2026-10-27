# Paper XI Lean Guide

Author: Komorebi P. Final reader edition, 6 October 2026.

The general realization endpoint is Conjecture 66. The retained conditional
comparison is a theorem at its printed arithmetic-realization and factor
characterization interfaces. Original obligation 66 corresponds to printed
Theorem 16.2 and all-records registry row 95. Blocks 166–167 supply ordinary
mathematical constructions at restricted scope, not new Lean-certified local
field/simple-character developments.

The accompanying release includes Markdown (.md) proofs, construction notes,
proof audits, and research records. Historical status and failure records are
preserved; current publication scope supersedes stale endpoint labels.

## Rebuild the PDF

```bash
python3 build.py --output-dir /absolute/path/new-empty-output
```

The builder uses only this folder's LaTeX and displayed excerpt files. XeLaTeX,
its declared packages, and fonts must already be installed. It installs nothing,
uses no network, fixes SOURCE_DATE_EPOCH to 1791244800, and invokes no Lean compiler.

## Reading the source evidence

- `sources/PaperXI`: 423 complete, byte-preserved selected production modules.
- `SOURCE_CATALOG.json`: hashes, source layers, import edges, lexical declarations,
  and layer-specific retained historical verification scope.
- `DECLARATION_CATALOG.json`: 4,342 explicitly named lexical commands. This is not
  a kernel census or a count of distinct mathematical discoveries.
- `SOURCE_VERSIONS.json`: repeated source-layer identities; unchanged copies are
  deduplicated by module identity and byte hash.
- `EXCERPTS.json` and `excerpts`: 40 literal source excerpts, raw bytes, reversible
  display conversions, ambient setup lines, and source hashes.
- `HISTORICAL_CLAIM_CROSSWALK.json`: navigation from the original 66 proof-obligation
  records to relevant source families; historical status is not a current proof
  certificate.
- `FINAL_SUMMARY.json`: final PDF and source correspondence checks.

`write_guide.py` is the original authoring/inventory program. Its source-selection
roots refer to the recovered authoring workspace. It is preserved as provenance,
not the portable PDF rebuild entry point. `build.py` is the portable entry point.
Original compiler receipts and portable-runtime availability are documented in
other release folders. No new Lean/Lake/leanchecker run is claimed by this guide.
