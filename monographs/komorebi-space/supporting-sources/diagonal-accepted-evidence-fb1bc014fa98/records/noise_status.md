# Current status: Corollary 30.3 kernel checked

The full `DiagonalNoisyRate.lean` module compiled with `-DwarningAsError=true` on its first full-module attempt. The concrete theorem `corollary_30_3` proves both printed inequalities for the actual infinite Hilbert model, with the literal ceiling and no bias hypothesis. All twelve public definitions/theorems and seven model identification dependencies were checked by the imported audit; their only axioms are `propext`, `Classical.choice`, and `Quot.sound`. Exact evidence is in `records/noise_completion.json`, `logs/noise_full_attempt_001.log`, and `logs/noise_axioms_001.log`. There were no failed noise-route compiler attempts.

The earlier entries below are retained as the chronological development record.

# Corollary 30.3 noise-rate route

The scalar schedule is the literal `Nat.ceil (δ ^ (-(2 : ℝ) / 3))`, with natural-to-real cast explicit in every estimate. The desired range is `0 < δ ≤ 1`. The arithmetic proof separately controls the square-root bias term and the noise term, retaining the ceiling factor of two.

Current source is provisional and uncompiled while the pinned toolchain is provisioned. No theorem-completion claim is made. The actual Hilbert-space corollary remains dependent on the diagonal `H`, `T`, `b`, `c`, `w`, `alpha`, exact correction identity, bias norm, and series upper bound. No conditional arithmetic result substitutes for that application.

A concrete provisional theorem `corollary_30_3` has now been added, using `InfiniteDiagonalModel` and the promised series `B_upper`. It exposes the literal ceiling in a `let m`, quantifies arbitrary Hilbert noise, and states both printed inequalities. `diagonal_bias_bound` supplies its concrete bias premise from the actual correction identity and infinite squared norm. All three concrete declarations remain uncompiled; this is implementation progress, not kernel-checked completion.

## Probe validation completed

The scalar prefix compiled on the pinned Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 environment with `-DwarningAsError=true`, first attempt, exit 0 (`logs/noise_scalar_attempt_001.log`). The generic transfer prefix also compiled on its first attempt after concatenation with the unchanged baseline `RegularizedHilbertRepair.lean` source (`logs/noise_transfer_attempt_001.log`). Exact source snapshots were retained in `records/noise_scalar_attempt_001.lean` and `records/noise_transfer_attempt_001.lean`.

An axiom audit of all eight public scalar/generic theorems in that source-prefix probe reported only `propext`, `Classical.choice`, and `Quot.sound` (`logs/noise_transfer_axioms_001.log`). These probe results validate the scalar and generic proof bodies; they do not establish compilation of the concrete imported diagonal module. The full module is waiting for clean compiled series and Hilbert dependencies.
