# Generic polynomial Taylor remainder development

`PolynomialTaylorRing.lean` proves a polynomial substitution identity over every commutative ring, using the actual partial derivatives. The remainder is chosen before evaluation, works for every input, and has zero constant term. No domain or nonzero scale hypothesis is needed for this statement.

Observed development runs:

1. `attempt_01.log`: FAIL. Simplification changed `eval 0` to `constantCoeff` before the local zero-evaluation hypothesis applied. The evaluation homomorphism lemma needed the primed `eval₂Hom_X'` name. A sequence-focus linter also rejected inherited proof syntax. No mathematical statement was weakened.
2. `attempt_02.log`: FAIL. All mathematical goals closed, but one unnecessary sequence-focus linter error remained.
3. `attempt_03.log`: PASS, process exit code 0, no output under the low-memory runner's warnings-as-errors gate.

Compile command used the pinned Lean 4.34.0-rc2 kit, one thread, 240-second timeout, default heartbeats, `/dev/shm/paper9_weighted_build` imports/output, and the mandated `LD_PRELOAD` and `TMPDIR=/dev/shm` environment.

Frozen source SHA-256: `344502b0ee6d50e602ae1a23a2b6685c3992a08a6366c029b4e64d2c1f9d1c32`.

Declarations: 1 definition (`linearPart`) and 10 theorems. The source does not use `sorry`, `admit`, custom axioms, `unsafe`, or `native_decide`. Final cumulative gate and dependency audit are managed by the parent task.
