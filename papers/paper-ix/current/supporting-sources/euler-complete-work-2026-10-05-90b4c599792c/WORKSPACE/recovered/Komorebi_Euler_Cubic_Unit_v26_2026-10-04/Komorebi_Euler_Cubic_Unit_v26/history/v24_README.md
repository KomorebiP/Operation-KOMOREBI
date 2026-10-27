# Komorebi Euler Critical Value v24

Cumulative Lean project: **878 named theorem/lemma declarations in 96 modules**.
New block: constructed critical points, exact stationary value precision,
quantitative perturbation gaps, and a connection to actual one-neighbor Euler
cores. The universal Euler simplicity question is NOT closed.

Read `PROOF_AND_STATUS.md` for mathematical hypotheses and the exact boundary.
`THEOREM_INDEX.json` enumerates the actual declarations.
`RELEASE_STATUS.json` describes this release; `evidence/v24_*` contains its new
execution evidence. Earlier evidence and archive files retain their own versions.

## Check file integrity

```bash
python scripts/verify_manifest.py
```

## Replay the Lean proofs

Use the pinned compiler and dependency revision:

- Lean 4.34.0-rc2
- mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06

With the separately supplied Komorebi portable Lean kit:

```bash
python scripts/replay.py \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /absolute/path/to/NEW-evidence-directory \
  --build-dir /absolute/path/to/NEW-build-directory \
  --timeout 120
```

Both output directories must be new. The replay refuses to overwrite evidence,
verifies the pins, compiles with one worker and warnings-as-errors, and checks
every declaration's transitive axioms. Only `Classical.choice`, `Quot.sound` and
`propext` are permitted. The full process environment is never logged.

Alternatively configure Lake for this project with its pinned dependencies and
omit `--runtime`. The runtime/compiler/dependency cache are not included here.

## Replay the new finite checks

Python 3.10+ standard library only:

```bash
python checks/check_critical_value.py --output /tmp/v24-generic-NEW.json
python checks/check_critical_value.py --actual --output /tmp/v24-actual-NEW.json
python checks/check_critical_replay.py --output /tmp/v24-independent-NEW.json
```

Outputs must not already exist. The last script compares its fresh higher
precision results against the frozen `evidence/v24_checks_actual.json` record.
It uses a different source construction, factorial decomposition, local
translation method and critical-point solver; its Bernoulli evaluator is shared.

Finite tests are not universal proofs, and finite dyadic residues are not exact
critical points. Two rejected terminal-17 chart selections are retained rather
than counted as successful theorem applications.

## New modules

- `QuadraticCriticalSeries`: restricted quadratic class and unique critical point.
- `QuadraticCriticalValue`: exact motion-corrected value and strict remainder gap.
- `StationaryValuePrecision`: exact squared-distance / half-slope error identity.
- `QuadraticPerturbationGap`: explicit perturbation margin and sharp controls.
- `EulerCriticalValueBridge`: actual one-neighbor coefficient construction and
  conditional nondegeneracy transport to the original Euler residual.

No historical-priority or new terminal-family coverage claim is made.
