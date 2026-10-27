# Active Paper III formal source

`PaperIIIContinuation.lean` is the release import root. It imports the finite
predecessor, the three Section 16 coordinate modules, and the four Section 17 modules for finite
multilinear reconstruction, bounded ambient jets, and continuous jets on actual
projector ranges, plus the finite partition composition and support laws.

The old `KomorebiPaperIII.lean` root and its 41-row theorem map continue to
identify the finite predecessor. The expanded default Lake target now builds
`PaperIIIContinuation`, so the default build includes all four Section 17 modules.

## Reproducible verification

Install the official Lean version named in `lean-toolchain` (Lean 4.34.0-rc2),
with its sibling `lake` executable, and use Python 3.11 or later and Git. The
release does not include a compiler installation or the upstream dependency
cache. `verification/COMPILER_PROVENANCE.json` records the official Linux asset
digest verified for the accepted run.

From this directory, restore the nine exact revisions in `lake-manifest.json`
and obtain their compiled dependencies:

```bash
python3 scripts/restore_pinned_dependencies.py --lean /absolute/path/to/lean --cache
```

The restore helper discovers `lean` on `PATH` when `--lean` is omitted. It
refuses an existing dependency checkout with a different commit or modified
tracked files. Dependencies are installed beneath this project's `.lake`
directory; no global toolchain or user configuration is changed. Then run the
four verification phases, using an object directory and labels that do not
already exist:

```bash
python3 scripts/run_release_verification.py --lean /absolute/path/to/lean --phase full --label fresh_build --objects build/fresh_objects
python3 scripts/run_release_verification.py --lean /absolute/path/to/lean --phase audit --label fresh_audit --objects build/fresh_objects
python3 scripts/run_release_verification.py --lean /absolute/path/to/lean --phase replay --label fresh_replay --objects build/fresh_objects
python3 scripts/run_release_verification.py --lean /absolute/path/to/lean --phase controls --label fresh_controls --objects build/fresh_objects
```

The build refuses an existing own-project object directory. Audit/replay phases
reuse only that new object directory and the pinned upstream dependencies.
Each command records its source snapshot, source hash, command, result, and log.
A timeout or an import failure never counts as a successful negative control.
The ownership audit scans all declarations owned by the production modules,
including generated/private declarations outside the project namespace.
Fourteen inherited compiler runtime helpers remain separately inventoried and
excluded from logical replay, with checks forbidding logical dependencies on them.

The accepted release receipts are
`verification/final_release_full/report.json`,
`verification/final_release_audit/report.json`,
`verification/final_release_replay/report.json`, and
`verification/final_release_controls/report.json`.
`verification/FINAL_VERIFICATION_SUMMARY.json` binds their results to the current
source hashes, reports the exact declaration inventory, and records the scope
of the mathematical coverage. Paths in these new instructions resolve from the
extracted release and do not require the original scratch directory. The raw
receipts retain the original absolute commands as historical evidence.

The expanded Lean scope includes finite algebraic packet reconstruction, the
continuous ambient projected-jet norm estimate, closed packet ranges, a continuous
linear coordinate equivalence, continuous range jets that forget literally to
the algebraic jets, their sharper inherited-norm bound, and direct reconstruction
of mathlib's chosen iterated Frechet derivative at every order. The last identity
does not assert differentiability of an arbitrary supplied function. The composition module additionally proves the full finite partition formula
for actual range jets under the stated ContDiffAt assumptions, a sufficient
vanishing criterion, and one-way structural support inclusion. The formula uses
canonical ordered finite partitions and retains every original input slot and
intermediate packet label. Projected Taylor formulas remain outside this Lean scope.
The canonical block order in the formal formula is increasing greatest element,
with increasing input positions within each block, as in the pinned mathlib
`OrderedFinpartition` API. The nullary case is included. The support theorem
asserts only existence of nonzero constituent jets and proves no converse.
Touchard/Stirling term counts and the separate restricted product-bound and
Hilbert norm-one corollaries are not separately certified by this closure.
