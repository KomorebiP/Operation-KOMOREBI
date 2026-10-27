# Diagonal inexact-rate formal connection

Base checkpoint: `v115-start-from-73e9c5c`.

The public theorem is `KomorebiSpace.DiagonalRegularization.diagonal_inexact_rounded_rate` in `publication/lean/KomorebiSpace/DiagonalInexactRate.lean`.

It works on the actual infinite diagonal Hilbert model. The schedule is the literal natural-number ceiling of the real power δ^(-2/3), with the existing inverse-square `alpha` definition. The normal residual is stated in the displayed form T*(T a − s) + α a and evaluated at measured datum s. The noise hypothesis is ‖s − b‖ ≤ δ. The conclusion is the printed norm rate (√2 + 1 + κ)δ^(1/3), with 0 < δ ≤ 1 and κ ≥ 0 retained.

The proof first identifies the displayed normal residual with the existing gradient definition. Schedule positivity makes α positive, so the residual error bound yields ‖a − correction(s)‖ ≤ κδ^(1/3). The actual-model rounded noisy-rate theorem bounds ‖correction(s) − w‖. The triangle inequality and scalar rearrangement give the conclusion. There is no remaining exact-data bias assumption, no abstract replacement of the operator, and no missing attainment premise: the imported diagonal model has already identified w as the minimum-norm preimage.

The first candidate failed because scalar automation did not unfold the local abbreviation m when comparing α(m) with α(ceil(...)). The second candidate makes that definitional equality explicit and compiled with warningAsError and autoImplicit=false. Both candidate sources and actual compiler outputs are retained under `logs/inexact_attempts`. The separate imported-theorem audit printed its type, proof, and axiom dependencies. Its only axioms are propext, Classical.choice, and Quot.sound.

This is an author self-review. Independent review and the full integrated replay belong to the parent task and are not claimed here.
