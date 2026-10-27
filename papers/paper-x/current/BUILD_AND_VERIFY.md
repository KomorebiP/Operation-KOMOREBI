# Paper X — build and verification

Run commands from the extracted release root. Use external output directories to preserve the frozen archive. No launcher installs software or downloads dependencies.

## Frozen file integrity

```bash
python3 -B verify_release.py --strict
python3 -B scripts/test_integrity.py --evidence ../paper_x_integrity_controls.json
```

The strict verifier checks exact regular-file membership, schema, sizes and SHA-256. It rejects malformed/duplicate manifest data, unsafe paths, symlinks, special files and unknown flags. Integrity is not compiler or mathematical proof replay. The 21 isolated verifier controls have a separate scope.

## Finite scientific replay

Use the dependencies in `requirements-review.txt` in a deliberately prepared environment.

```bash
python3 -B verification/run_checks.py --output ../paper_x_finite_replay
python3 -B verification/finite_tools/validate_manifest.py verification/2026-10-20/current_finite/run/manifest.json --root .
```

The first command runs seven documented gates in temporary copies. It disables bytecode writes and selects the headless plotting backend. It does not invoke Lean. The current bounded v2 manifest pins the actually consumed scientific/provenance closure, including the current main source; active PDF/build metadata are not its inputs. Six independent Block 27 suites have their own contracts under `verification/2026-10-20/finite/`. The old selected-October-10 primary record remains baseline evidence; do not validate it as if every later reader/metadata file were unchanged. The fresh current record is separate.

## Readers and references

```bash
python3 -B scripts/build_bibliography.py
python3 -B publication/build_publication.py --build-directory ../paper_x_build --output-directory ../paper_x_rebuilt
python3 -B publication/validate_publication.py --pdf-directory ../paper_x_rebuilt --report ../paper_x_publication_validation.json
```

The source needs the TeX engines/packages/fonts described by `ENVIRONMENT.json` and the preambles. The builder creates isolated per-document output trees, builds the visual guide before appending its thirty atlas pages, fails nonzero on a document failure, and removes stale target PDFs. BibTeX plain regenerates the exact restored 23-entry reference list. Font binaries are external reproduction dependencies.

The current validator checks actual declared page counts, every internal/companion destination, all twenty statement routes, thirty atlas page pairs, and text spans against page bounds. The atlas offset is derived from the actual monograph length so reference restoration does not break it. Fresh PDF binary comparison is reported separately; PDF trailer identifiers can vary.

## Fresh production and declaration audit

Read `production_replay/README.md`. The portable driver accepts the extracted pinned offline runtime:

```bash
python3 -B production_replay/rebuild_production.py --help
```

The exact runtime version is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Runtime/dependency pin checks and its included executable-path adapter are documented with their hashes. The 2.9 GB runtime/cache is not bundled here. Two fresh project builds, 392-artifact identity and source lineage are independently recorded.

Read `production_audit/README.md` for the portable full owner/target replay. The successful unchanged checker used a 6 GB Lean memory cap on an 8 GB host and loaded private/generated payloads. Its earlier 4 GB failures and interrupted partial run are retained, not counted as accepted censuses. Every selected source and all 392 generated artifact hashes were bound before/after the successful audit. No compiler fixture directory entered its production search path.

## Restore older source histories

```bash
python3 -B formal_preservation/restore.py --verify
python3 -B formal_preservation/restore.py --root conditional_checked --output ../paper_x_restored
```

Use a new or empty destination. This restores the 3,079 exact payloads at 13,730 leaf occurrences as directory content; `.zip.contents` does not claim original compressed ZIP bytes. Earlier absolute host paths in as-executed reports are provenance. Current portable drivers resolve their delivered sources relative to the release.
