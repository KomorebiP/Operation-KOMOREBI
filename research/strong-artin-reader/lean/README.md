# Strong Artin formal source guide

The latest authoritative mathematical checkpoint is the exact v0.38 effective
matrix Hensel archive, SHA-256
`d5f065bcb05ee02465082804dfb14800f82b86f43a8838eded2e3d3519abcb9a`.
Strong Artin is open.

`history/v0.38/src/` contains its seven new mathematical modules. These exact
bytes match the successful September 12, 2026 extracted-archive replay.
`history/v0.38/DECLARATIONS.json` records 60 named declarations: 44 theorems,
15 definitions and one abbreviation. Helpers and controls are included. These
counts are not independent discoveries or progress percentages.

`history/v0.9/` through `history/v0.38/` are selected source, build and boundary
files from the checkpoint's exact nested ancestry. No sibling branch absent
from the original archive has been added. Repeated dependency files have not
been merged into one synthetic Lean namespace. Historical result filenames
such as `verification/fresh/RESULT.json` retain their original meaning: they
describe the run timestamp inside the record, not verification performed for
this publication.

`ANCESTRY_INDEX.json` records each archive identity and its canonical extracted
directory. Thirty byte-distinct archives occur in the retained ancestry, with
repeated edges. `AUTHENTICATION_2026-10-08.json` records fresh CRC, payload-hash
and static-source checks. Authentication is not Lean compilation.

The current publication attempted to recover the matching portable Lean kit.
The seven Library archive parts were found, but downloading their bytes failed
with HTTP 403. No kit was materialized and no fresh compiler invocation ran.
See `CURRENT_REPLAY_STATUS.json` and `../evidence/LEAN_COVERAGE.md`.

## Replay

Use the exact original v0.38 archive included in the handoff and the external
portable kit with these pins:

* Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
* Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
* Combined offline runtime archive SHA-256
  `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`

The isolated wrapper preserves all historical evidence:

```bash
python3 lean/replay_current.py \
  --archive /absolute/path/to/Strong_Artin_Lean_v0.38.0_Effective_Matrix_Hensel_Checked.zip \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --work /absolute/path/to/a/new/replay-directory
```

The original verifier rebuilds every new v0.38 module into a fresh object
directory and audits all 60 named constants. It excludes unrelated project
object paths, authenticates the v0.37 parent and reuses the pinned Mathlib
compiled cache. It does not rebuild the full ancestry, Mathlib or a second
Lean kernel. A `BLOCKED`, `PARTIAL`, `FAIL` or timeout is not a pass.

To reproduce the byte audit, use `authenticate_archives.py` with the original
archive, the retained September 12 replay JSON and a new output path.

## Current module map

| Module | Mathematical task |
| --- | --- |
| `NCPowerEstimates` | Ordered derivative and ultrametric nonlinear remainder estimates |
| `NCPowerLocalImage` | Exact small-ball image and uniqueness from a bounded two-sided inverse |
| `PadicMatrixNorm` | Entrywise matrix norm, completeness, integral embedding and congruence comparison |
| `MatrixInverseCertificate` | Pair-indexed coefficient action and exact inverse identities checked on matrix units |
| `EffectiveMatrixRoot` | Existence and uniqueness of integral matrix powers in a deep congruence fibre |
| `FiniteMatrixCriterion` | Reduction of the target condition to one finite residue-ring calculation |
| `EffectiveMatrixControls` | Singular-residual unipotent example, noncommuting root and rejected target |

The source documentation explains the older obstruction, syzygy, local-gauge,
compactness and scalar-horizon results. The coverage report distinguishes their
proved conditional statements from the arithmetic inputs they require.
