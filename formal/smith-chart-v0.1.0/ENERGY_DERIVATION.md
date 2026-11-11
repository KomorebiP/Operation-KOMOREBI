# Angular packet energy

This is a self-reviewed mathematical derivation for the angular energy shown
in the Smith chart. Separate Lean proofs establish the squared-coefficient
sums, finite phase-orbit Parseval identity, and finite-radius angular means.
The written derivation below uses a different route.

Fix `N ≥ 1` and `0 ≤ r < 1`. For `1 ≤ j < N`, the impedance packet on the
radius-`r` circle is

```
P[N,j]z(r exp(iθ)) = 2 Σ(m≥0) r^(j+mN) exp(i(j+mN)θ).
```

The series converges uniformly and absolutely in `θ`: its term magnitudes
are bounded by the summable geometric sequence `2 r^(j+mN)`. Its squared
modulus is therefore represented by an absolutely and uniformly convergent
double series, so integration and summation can be interchanged. The average
of `exp(i(m-n)Nθ)` over one full turn is one when `m=n` and zero otherwise.
Consequently,

```
(1/2π) ∫[0,2π] |P[N,j]z(r exp(iθ))|² dθ
    = 4 Σ(m≥0) r^(2(j+mN))
    = 4 r^(2j)/(1-r^(2N)),                    1 ≤ j < N.
```

For the zero lane, the constant coefficient is one and all other surviving
coefficients are two. The same argument gives

```
(1/2π) ∫[0,2π] |P[N,0]z(r exp(iθ))|² dθ
    = 1 + 4 Σ(m≥1) r^(2mN)
    = 1 + 4 r^(2N)/(1-r^(2N)).
```

These formulas include `r=0` and `N=1`. They describe finite-radius angular
means; they do not assert a finite Hardy-space norm for the impedance
function up to the unit circle. Indeed, the zero-lane mean and every existing
nonzero-lane mean diverge as `r` approaches one from below. The chart's
finite-radius readout must not be confused with a finite boundary H² norm.

`SmithEnergy.lean` proves the convergent real coefficient sums, while
`SmithParseval.lean` proves the separate finite phase-orbit identity.
`SmithEnergyIntegral.lean` proves the finite-radius angular identities by
using the Poisson kernel and connects them to the actual packet series and
coefficient sums. The uniform-convergence argument above remains self-reviewed
prose; it is not the route used in the Lean proof.
