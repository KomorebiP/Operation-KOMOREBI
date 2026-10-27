# Block 17 development failures and repairs

Only completed kernel checks count as proof. The following failures occurred during development and are retained here so the successful state is not confused with the failed attempts.

1. **Baseline run exceeded the outer command window.** An initial foreground cumulative verification was interrupted by the execution wrapper. It was not counted as evidence. The identical Block 16 baseline was rerun as an independent process and completed successfully before any inherited mathematical source was changed.

2. **One direct Lean invocation used the wrong working directory.** `DiracWalk1D.lean` initially reported `unknown module prefix 'KomorebiPhysics'` because the command was launched outside the project root. Re-running from the attached project root fixed the environment failure. It was not a mathematical failure.

3. **`DiracWalk1D` contained an unreachable tactic and an invalid trace `change`.** The explicit matrix multiplication had already closed its goals before `all_goals ring`, which warnings-as-errors correctly rejected. The redundant tactic was removed. The trace proof was repaired by invoking `Matrix.trace_fin_two` explicitly before rewriting the diagonal entries.

4. **The first dispersion draft used `λ` as an identifier.** Lean parses `λ` as syntax, so the declarations did not parse. The polynomial variable was renamed `z`.

5. **The first 2 by 2 characteristic-polynomial proof left `det A` opaque.** The determinant theorem had only expanded the left determinant. The proof was repaired by explicitly expanding the second determinant before the ring normalization.

6. **The first half-turn witness failed to rewrite an exponential.** The target still contained `1 * (π/2)` while the rewrite theorem expected `π/2`. A targeted `simp only [one_mul]` normalized the angle before applying the proved Euler identities.

None of these failed attempts is counted as a passed proof. The final source modules compile with `-DwarningAsError=true` and are included in the cumulative audit.
