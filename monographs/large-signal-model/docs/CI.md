# CI and verification

The delivered Lean release has its own completed source-bound verification. The GitHub workflows supplied here have not yet run on GitHub. Local validation of these new workflow, adapter and draft-release files is recorded separately in `ci/SUPPORT_VALIDATION.json`; it must not be presented as a GitHub CI PASS.

## Quick checks

`quick-checks.yml` runs on pull requests, pushes to `main` or `master`, and manual dispatch. It checks the exact `Lean/MANIFEST.json` baseline and every file named in it, then runs the existing source-index, metadata, lexical-guard and diagnostic-classifier checks. It checks the bytes again afterward. These steps are read-only and do not compile Lean.

The baseline is in `ci/frozen_lean_release.json`. Repository support files, the monograph and the reference laboratory are outside that Lean delivery manifest. Their packaging checks are distinct from the formal companion's checked source and evidence. The outer release inventory, when supplied, covers the complete distribution.

`Lean/** -text` is intentionally the final rule in `.gitattributes`. Git must preserve the checked payload's exact bytes. Generated `.lake/` and `.build/` output is ignored; `Monograph/build/` and the checked `Lean/history/` and `Lean/verification/` files remain trackable.

## Full verification

Run **Actions → Full clean Lean verification → Run workflow** when a new clean execution is wanted. It runs by manual dispatch or as the verification prerequisite of the manually dispatched draft-release workflow. It does not run on every push and never publishes a GitHub release.

It installs the explicitly versioned upstream elan installer, selects the exact `Lean/lean-toolchain`, and checks the compiler commit. Lake consumes the existing `Lean/lake-manifest.json`; the workflow never runs `lake update`. The default dependency mode uses mathlib's official cache. The `source` option builds the pinned mathlib library from its source instead and can take substantially longer.

The adapter verifies each actual dependency checkout against its locked revision, checks that Lake left all pinned project inputs unchanged, and creates symlinks to the real installed toolchain and Lake package directories. This supplies the layout expected by the existing verifier. It does not assume that a private portable runtime or a Library file exists on a GitHub runner.

The unchanged verifier then removes and rebuilds the project's own Lean objects, audits the named declarations, replays each module through the pinned kernel API, runs the exact examples and checks every rejection control. The default per-stage limit is 900 seconds. A failed download, missing compiler component, unavailable cache or time limit produces a failed stage and no successful proof-verification claim.

New logs and receipts go to runner temporary storage and are uploaded under the workflow commit's artifact name. The original checked files under `Lean/verification/` are not overwritten. The bootstrap receipt is an environment record; only a complete fresh verifier PASS is a new mathematical execution receipt.

## Action and bootstrap inputs

All actions use full commit pins with readable major-version comments. Their recorded pins are in `ci/action_pins.json`. Checkout credentials are not persisted. The verification workflows request only `contents: read`. The manually dispatched `draft-release.yml` first calls full verification and then grants `contents: write` only to its separate packaging and draft-creation job. That job validates static version `v1.0.0`, requires the same verified commit, checks asset hashes, and creates a draft without moving an existing tag or overwriting release assets. It never publishes the draft automatically.

The installer uses elan release `v4.2.4` from its official release URL. Before extraction or execution it checks the archive against SHA-256 `42b94d4244e8353142c456ec0e4ca6528fd898a6c604d4059f494e706e431f63`, retrieved from the official upstream release metadata. The selected Lean compiler commit and all dependency Git revisions are checked explicitly afterward. The local support-file validation did not download or install the network bootstrap.

Primary implementation references:

- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub artifact storage](https://docs.github.com/en/actions/tutorials/store-and-share-data)
- [Official elan releases](https://github.com/leanprover/elan/releases)
- [Pinned Lake target syntax](https://github.com/leanprover/lean4/blob/v4.34.0-rc2/src/lake/README.md#specifying-targets)
- [Pinned mathlib cache instructions](https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/README.md)
