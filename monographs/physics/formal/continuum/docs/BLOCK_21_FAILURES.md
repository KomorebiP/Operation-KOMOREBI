# Block 21 failure and repair record

This record separates checked results from unsuccessful development attempts.

1. A first direct compile of the new anisotropy theorem failed because a rewrite tried to find the coefficient difference inside an already distributed expression. The proof was repaired by an explicit algebraic `calc` step separating the frequency difference from the correction-coefficient difference.
2. The first sixth-order shell proof oriented the quartic coefficient identity in the wrong direction. Reorienting the exact identity closed the Taylor polynomial normalization without changing the theorem.
3. Early group-velocity proofs left function-level multiplication implicit, so Lean could not identify the intended pointwise derivative expression. Explicit function equalities were inserted before derivative transport.
4. One velocity draft contained a tactic after the goal had already closed. It was removed so the module compiles cleanly under warnings-as-errors.
5. A direct build of a new module initially failed because the required local `DiracWalk3D.olean` had not been produced in that build tree. Building through Lake resolved the dependency order; this was an environment/build-order failure, not a mathematical counterexample.
6. Two aggregate parallel `lake build` invocations exceeded their external command windows near the end of the cumulative graph. They are not counted as completed verification. The three remaining modules were then compiled explicitly and sequentially with the pinned toolchain.
7. Two attempts to run the portable kit's broad self-test exceeded external command limits while loading the complete Mathlib environment. The preexisting kit report remains historical evidence only; project-specific compilation and the release verifier are the relevant current checks.
8. The observer-shell formula was audited before formalization. A naive fixed-momentum substitution was rejected because the boosted momentum itself changes by order `Δ²`; the missing moving-argument remainder is now recorded explicitly as the next proof obligation.

No failed compile, timeout, cached object, or partial run is counted as a checked theorem. No admission, custom axiom, or weakened mathematical statement was introduced to repair these failures.
