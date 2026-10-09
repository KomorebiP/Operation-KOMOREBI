# Repository audit

## Preserved source

- The complete recovered final source archive is preserved under `research/original`.
- The original checksum ledger contains 291 entries.
- All 291 entries pass `sha256sum -c SHA256SUMS.txt`.
- No file inside the preserved snapshot was intentionally rewritten.
- `.gitattributes` disables end-of-line conversion for the snapshot.

## Historical verification

The preserved programs pass:

- 16 core packet-atlas groups
- 8 Singular Packet Decomposition groups
- 15 intermediate AM-SPD groups
- 11 final groups
- 12,154 final scenarios
- zero final failures

## Version 0.3.0 package

- The installable source contains 22 Python modules and approximately 9,198 lines.
- The test tree contains 12 files, 44 explicit test functions, and 45 collected tests.
- All 45 collected tests pass.
- `python -m compileall -q src` passes.
- `python -m am_spd verify --full` passes all 20 package integration checks.
- Dense and sparse `.amspd` model round trips recover the normalized input to floating-point roundoff.
- Schema-2 checkpoint continuation matches the uninterrupted tested reconstruction exactly.
- `.amspdt` tiled archives round trip, preserve exact global accounting, and support continued tile searches.
- Modified or inconsistent model payloads and aggregate totals are rejected.
- The finite pixel-coordinate closure is exact at zero residual threshold.
- Automatic finite-grid tuning and hash-aware batch processing pass end-to-end tests.

## Distribution artifacts

- The intended wheel is universal `py3-none-any`.
- Package data includes the compact packet histories and reference ledgers required for exact paper replay.
- The clean repository archive excludes caches, local environments, build directories, generated models, and runtime validation outputs.
- The source distribution retains documentation, examples, scripts, monorepo workflow templates, and the focused manuscript source.

## Exact paper replay

All four cases reproduce the required final reference invariants. The replay ledger continues to expose archived intermediate Lagrange-proxy diagnostic differences rather than silently changing them. Final reconstructions, budgets, and required benchmark invariants match.

## Repository limits

- No intended repository file approaches GitHub’s 100 MB single-file limit.
- Generated caches, local environments, build directories, models, and runtime benchmark directories are excluded by `.gitignore` and release staging.
- Large replay models are validation artifacts and are not included in the source archive.

## Manuscript integration

- The focused manuscript remains a 78-page edition with 85 Python-generated vector figures.
- The clean source package remains under `docs/paper/final`.
- The original 147-page archival manuscript remains under `research/original`.
- Version 0.3.0 changes software functionality and does not alter the finalized manuscript claims.

## Remaining publication decisions

- Public-use license or continued restricted distribution
- Whether the private Operation-KOMOREBI repository should become public
- Whether to publish the complete historical source and manuscript assets without restriction
- Whether to publish wheels through GitHub Releases only or also through a package index
