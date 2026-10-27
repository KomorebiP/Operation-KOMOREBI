# Paper X: build, verify, restore

## 1. Check the delivery without installing anything

Extract the complete ZIP into a short writable path, for example `C:\K\` on
Windows. The archive has a single `Paper_X` root. In that root run:

```powershell
python verify_release.py
```

The verifier checks every manifest-listed regular file by size and SHA-256.
It reports additional local files separately and never treats hash checking as a
proof replay. Read `MANIFEST.json` for the exact files covered. Do this before
rebuilding, since a rebuild may change generated PDF identifiers or build logs.
The reader-only ZIP is intentionally not a source or formal restoration package.

## 2. Reproduce finite examples and publication checks

The tested Python package versions are in `requirements-review.txt`. Install
deliberately into a separate environment. The launchers do not install packages,
contact external services, or invoke a Lean compiler.

```powershell
python publication/validate_publication.py
python verification/run_checks.py --output ../paper_x_replay
```

The validator checks page counts, internal and companion destinations, all
twenty statement routes, and the thirty duplicated atlas pages. The test runner disables Python bytecode writes, selects the headless Agg plotting backend, and
uses temporary copies for inherited programs and runs seven gates. Its residue
check verifies 255 saved source/object hash pairs. That is not compilation.
The default replay destination is within this archive. Supply `--output` as
shown to preserve frozen verification logs.

## 3. Rebuild all three readers

The build needs a working TeX Live installation providing pdfLaTeX, XeLaTeX,
Latin Modern, the required URW/DejaVu system fonts, and the TeX packages used by
the source preambles. Font binaries are not included. `ENVIRONMENT.json` records
the actual local tool and package versions. No network installation occurs.

```powershell
python publication/build_publication.py --build-directory ../paper_x_build --output-directory ../paper_x_rebuilt
python publication/validate_publication.py --pdf-directory ../paper_x_rebuilt
```

The builder creates fresh per-document output directories, removes a stale target
PDF before a new attempt, builds the visual guide first, then the traditional
text plus atlas, then the formal guide. It returns nonzero when a document fails.
Its evidence includes explicit source and build paths from the execution host.
Those paths are provenance, not portable dependencies.

The isolated rebuild passed all three documents with no warnings. The delivered
and rebuilt PDFs are identical except for trailer identifiers. All 158 page texts
and 86.4-dpi rendered images match. Strict byte-identical PDF reproduction is not
claimed. `REBUILD_COMPARISON.json` records both hashes for every document.

## 4. Restore the formal source content

```powershell
python formal_preservation/restore.py --verify
python formal_preservation/restore.py --root conditional_checked --output ../paper_x_restored
```

The output must be new or empty. The map covers 3,079 unique payloads at 13,730
mapped leaf occurrences. Nested ZIPs are reconstructed as directories ending in
`.zip.contents`. Source leaf bytes are restored, not the original compressed
archive streams. The preserved README explains the other available roots.

The terminal production file is printed unchanged in the formal guide along
with its three direct dependency modules. Four listings are not a standalone
Lean project. Full transitive sources and dated metadata are in the preserved
archives. The original Lean verifier has workspace paths and frozen-cache
assumptions that need deliberate restoration. The recorded Lean toolchain is
4.34.0-rc2 and the Mathlib revision is
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

No `lean` or `lake` executable was available on PATH during this publication
pass. A fresh full kernel replay therefore remains distinct from the successful
reader build, exact finite tests, saved-object hash checks, and delivery audit.
