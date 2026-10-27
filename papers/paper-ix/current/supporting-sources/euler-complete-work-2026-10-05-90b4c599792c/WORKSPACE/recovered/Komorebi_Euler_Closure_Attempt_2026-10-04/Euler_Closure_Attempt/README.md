# Euler closure attempt

Read `ATTEMPT_AND_BOUNDARY.md` for the mathematical derivations, exact hypotheses,
corrections, and the remaining universal-simplicity boundary.

This is not a Lean release. No new Lean compilation or axiom audit was performed.

Fast reproducibility (Python 3.10+, standard library only):

```sh
python verify_results.py
python continuity_checks.py
```

Fresh source reconstruction, typically tens of seconds per small batch:

```sh
python fresh_euler_tests.py 0,1,2,3 256 replay_256_head.json
python fresh_euler_tests.py 4,5,6 256 replay_256_tail.json
python fresh_euler_tests.py 0,718787533 272 replay_272.json
python fresh_cubic.py
```

`prepare_probe.py` also runs 260 planted-factor tests and reproduces the saved
62-bit prepared cubic. `fresh_cubic.py` recomputes its 110-bit version.

The original v26 Bernoulli/source computation code is supplied under its original
relative path. It is unchanged. Finite coefficient records need the inherited
whole-tail error bound to describe infinite Euler functions. The new preparation
algorithm proves/verifies factorization of complete coefficient residues, not
identity inferred from point samples.

`MANIFEST.json` records input archive hash, included file hashes, and exact scope.
No claim of universal simplicity or all-parameter analytic continuation is made.
