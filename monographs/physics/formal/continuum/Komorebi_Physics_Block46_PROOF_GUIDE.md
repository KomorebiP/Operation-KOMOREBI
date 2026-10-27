# Block 46 proof guide

## 1. Complete coefficient Hilbert space

`CoeffL2` is `ℓ²(Mode, HilbertSpinor)`, with `Mode = Fin 3 → ℤ` and `HilbertSpinor = ℂ⁴`.

`modewiseMap` applies a norm-preserving mode operator coordinatewise. `modewiseIsometry` proves that this action preserves the complete `ℓ²` norm exactly.

## 2. Full propagators

`continuumCoeffPropagator` and `centralCoeffPropagator` apply the checked unitary mode propagators to every Fourier coefficient. Their exact norm preservation follows coordinatewise.

The opposite-time mode identities prove surjectivity. This promotes both propagators to linear isometric equivalences:

- `continuumCoeffUnitary`
- `centralCoeffUnitary`

The time-group law is proved on the full coefficient space.

## 3. Finite truncation

`coeffTruncation S f` retains only coefficients in the finite set `S`. The canonical series of singleton coefficients sums to `f`, so every `f` admits a finite truncation with arbitrarily small `ℓ²` tail.

## 4. Finite-core compact-time estimate

`coeffPacketResidual` is the finite-truncation propagator residual. Its squared norm is exactly the finite sum of the mode residual energies. The result is identified with the torus finite-packet residual from Blocks 42–45, so it inherits the checked compact-time quadratic bound.

## 5. Cutoff removal

For `g = coeffTruncation S f`, exact norm preservation gives

\[
\|U_h(t)f-U(t)f\|
\le 2\|f-g\|+\|U_h(t)g-U(t)g\|.
\]

Choose the tail below `ε/4`; then choose sufficiently small `h` so the finite-core error is below `ε/2`, uniformly for `|t| ≤ T`. This proves `eventually_fullCoeffResidual_lt` and `fullCoeffPropagator_compactTime_converges`.

## 6. Rate boundary

For fixed finite support, the error remains `O(h²)`. For arbitrary `ℓ²` data, only convergence is asserted. A uniform global rate would require additional Fourier-tail regularity.
