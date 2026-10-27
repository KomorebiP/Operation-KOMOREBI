# Komorebi Euler Lean — v22

Actual nearest-neighbor collision cores and an analytic derivative-jet ceiling.
See **PROOF_AND_STATUS.md** for exact hypotheses, mathematical boundaries,
verification scope, and the distinction between manuscript results and Lean results.

## Main checked addition

For the actual normalized Euler residual G_r, if r>0, the actual terminal index
j_r is at least four, and the carry-defined lower polynomial has only simple
roots in F_2, then G_r and its ordinary derivatives of orders 1,2,3 cannot all
vanish at any dyadic argument. One nearest integer skeleton neighbor forces a
quadratic residue core; two give constant/affine or a cubic after exactly one
additional content division. This does not exclude double or triple roots.

Main source: `Euler/EulerCollisionDegree.lean`.
Actual resonant example: `Euler/EulerCollisionExamples.lean`.
The source project has 794 indexed theorem/lemma declarations in 87 modules.

## Replay

Required external environment (not included):

- Lean 4.34.0-rc2
- mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- matching cached dependencies, or an independently configured checkout
- Python 3.10+ for the standard-library wrappers

With the portable kit:

```sh
python3 scripts/verify_manifest.py
python3 scripts/replay.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /path/to/NEW_replay
python3 scripts/check_nearest_cores.py \
  --max-j 192 --trials 256 --output /path/to/NEW_nearest_audit.json
```

The replay refuses existing output directories and starts with no project
compiled objects. It checks all declarations' transitive axioms. Only
`Classical.choice`, `Quot.sound`, `propext` are permitted. It reuses pinned mathlib
caches; it does not rebuild the Lean compiler or all of mathlib from source.

Without the portable kit, first configure the pinned Lake environment and run
`python3 scripts/replay.py --evidence /path/to/NEW_replay`.

## Evidence

`RELEASE_STATUS.json` contains the final build outcomes and comparisons.
`evidence/replay1` and `evidence/replay2` contain clean compiler logs, source hashes,
and every declaration's axiom report. `evidence/nearest_core_audit.json` contains
finite corroboration; it is not a proof of the universal statements.
`evidence/development` contains rejected development diagnostics separately.

The unchanged incoming v21 ZIP is retained under `history/v21`.
No runtime binaries or generated compiled project objects are distributed.
