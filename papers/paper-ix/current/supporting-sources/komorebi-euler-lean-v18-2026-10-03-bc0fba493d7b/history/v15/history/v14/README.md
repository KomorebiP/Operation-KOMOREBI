# Komorebi Euler Lean v14 — the infinite-series certificate bridge

**3 October 2026.** 143 named theorem/lemma declarations in 14 modules, including
66 new declarations for actual restricted-series evaluation and analytic lifting.

## Result

The full infinite coefficient tail is retained. Lean proves convergence in the
actual dyadic integers, evaluation and Hasse-jet reduction modulo every 2^k,
genuine first and second derivatives over Q_2, and a direct contraction-based
simple-root Hensel theorem for arbitrary restricted series. The one/two-neighbor
coefficient cores now automatically satisfy the required convergence condition.

The exact statement and limitations are in `PROOF_AND_STATUS.md` and
`PROOF_BOUNDARY.json`. The original Euler source/kernel-to-coefficients derivation
and the unresolved critical-scalar arithmetic are NOT completed in this release.
No numerical Euler-family coverage bound is increased.

## Executed replay path

Use the previously recovered Linux portable kit (or the same kit within WSL):

```sh
python3 scripts/verify_manifest.py
python3 scripts/replay.py \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /absolute/path/to/NEW_replay_directory
```

The replay pins Lean 4.34.0-rc2 and mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, builds in a fresh directory, treats
warnings as errors, and rejects any transitive axiom outside
`propext`, `Classical.choice`, and `Quot.sound`. Existing evidence directories
are refused. The full process environment is never saved.

Two final clean replays are retained. They use cached pinned mathlib dependencies,
not a fresh rebuild of mathlib or of the Lean compiler. Runtime binaries and fonts
are not included.

With a standard matching Lean/Lake installation and the pinned dependencies:

```sh
lake update
lake exe cache get
lake build
lake env lean -j1 -DwarningAsError=true Audit.lean
```

The portable Linux route above is the route executed for this handoff. The source
uses the pinned toolchain's `module`/`public import` syntax; older Lean versions
are not supported here.

## Contents

`Euler/*.lean` contains the mathematical proofs. `Audit.lean` and
`THEOREM_INDEX.json` index and audit every named theorem/lemma. Successful logs
are under `evidence/clean_replay_*`; failed development diagnostics are kept
separately under `evidence/v14_dev`. `history/v13` is an unmodified input snapshot.
The manifest checks integrity, not mathematical correctness.
