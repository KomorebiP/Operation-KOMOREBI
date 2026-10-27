# Complete bundle v1.3.1

This is a packaging correction to the v1.3.1 visual refresh, not a new mathematical
revision. The manuscript text continues to identify as v1.3.0.

- Preserved the delivered 39-page PDF, TeX, ten figure pairs, all local Lean sources,
  Python algorithms and tests.
- Corrected the root release metadata, stale SHA-256 manifest and current output
  inventory. The inherited manifest failed on 22 visually refreshed files.
- Preserved superseded metadata and generation records explicitly as historical.
- Added START_HERE, a continuation capsule, a read-only check wrapper, an external
  dependency inventory and an exact file inventory.
- Reran 33 Python tests and finite examples in a separate working copy.
- Regenerated all ten figure PNGs exactly and rebuilt all 39 PDF pages with matching
  text and rendered pixels at 144 DPI.
- Matched all 20 Lean source hashes to the prior successful audit. Did not rerun Lean.
- Omitted generated Python bytecode, one TeX auxiliary file and one redundant build
  copy of the article PDF; no substantive source, figure, test or review was removed.

Earlier edition notes are retained in `provenance/pre_packaging_records/CHANGELOG.md`.
