# Euler cancellation and stationary points, studied together

Checkpoint: `Euler-coupled-stationarity-20261005`.
Parent: `Euler-regular-address-critical-phases-20261005`, archive SHA256
`ea627109549edd95eaf764800135de0f9bf92b2cb6b1dc7b4662117ef6df8766`.

The new work determines the coupled local geometry, quantifies how moving a
stationary point changes cancellation, and identifies the leading actual
source cancellations. Universal Euler simplicity remains open. No new Lean
compilation or exact singular ordinary Euler index is claimed.

## Actual Euler family and the exact square coordinate

The new results concern the certified terminal-161 progression

    B=17659+2^18 T, r=B*2^640-161,
    x=10202+2^15 Z, K_T(Z)=2^-178 G_r(x).

B is a positive ordinary odd integer and the true terminal must be161.
All three computed inputs have their true terminal checked from the global
carry cutoff. The full underlying definitions remain in `sources/euler_v4.md`.

For every actual index satisfying these conditions there is a unique
stationary point c_T and an exact bijective analytic isometry w_T, with
w_T(c_T)=0, such that

    K_T(Z)=Phi_T+w_T(Z)^2,  Phi_T=K_T(c_T).

This gives a single description of stationarity and value cancellation.
It follows from the uniform complete coefficient class

    K_T(Z)=213+167T+88Z+81Z^2 (mod256),

and a convergent square-root construction. Thus c_T=20 modulo128 and
Phi_T=69+167T modulo256, while the square-coordinate identity itself is exact.
Read `coupled/morse/ACTUAL_MORSE.md`.

## Motion changes the observed cancellation

Let e=v2(T-S). The inherited coefficient precision gives actual-pair laws

    e<443 implies v2(c_T-c_S)=e+7,
    e<451 implies v2(Phi_T-Phi_S)=e,
    e<443 implies v2(K_T(c_S)-Phi_T)=2e+14.

The last equality measures the error caused by freezing the old stationary
point. It is an exact consequence of the square coordinate and center-distance
law, not a numerical approximation. These are finite-separation theorems for
actual integer pairs, not an all-precision analytic interpolation in T.

Read `coupled/parameter_geometry/COUPLED_GEOMETRY.md`. Its chosen finite affine
model also has an exact analytic quadratic fold and a unit Jacobian for the
coupled system `(value, half derivative)`. The proof carefully separates this
model from the actual undepleted integer-index functions.

Fresh actual Euler calculations at320 global coefficient bits give:

| Input T | Critical-value valuation | Curvature valuation |
| --- | ---: | ---: |
| 0 | 0 | 1 |
| 718787533 | 30 | 1 |
| 437396180251114280047565 | 80 | 1 |

| Change | Center displacement valuation | Frozen-point value valuation | Moving critical-value valuation |
| --- | ---: | ---: | ---: |
| first to second | 7 | 14 | 30 |
| second to third | 37 | 74 | 80 |

In the second change, the lower and upper group displacement corrections each
have valuation27, cancel to valuation74, and their total then cancels the
frozen value through valuation80. The packet ledger records every retained
contribution, both as a dyadic rational residue and by its valuation layer.
The third input was selected from an existing necessary parameter residue.
It does not extend the previous multiplier precision or provide a new range
exclusion. Read `coupled/packet_balance/README.md`.

## Exact source cancellation and independent deformation dynamics

For each fixed r, keep the undepletion parameter independent and put
epsilon=2^24 eta. The source and first-packet derivative contributions obey

    W'_x=50+94=16 (mod128).

This determines the exact critical-point motion

    v2(c(eta)-c(theta))=18+v2(eta-theta).

The critical value Phi(eta)=K(c(eta),eta) satisfies

    Phi''=K_etaeta-K_Zeta^2/K_ZZ.

The two terms have exact valuations27 and37. Hence the stationary-motion
correction cannot cancel the leading direct curvature. The stronger exact
chord law is

    Phi(theta+h)=Phi(theta)+h Phi'(theta)+2^26 h^2 V_theta(h),
    Phi'(theta)=17 (mod32), V_theta(h)=1 (mod8).

The companion stationary-point law and explicit leading units are proved in
`coupled/critical_dynamics/COUPLED_CANCELLATION_DYNAMICS.md`.

If E=2r-25, actual singularity would require

    0=Phi(0)+2^E Phi'(0)+2^(2E+26) V_0(2^E).

In particular it requires v2(Phi(0))=E, normalized unit15 modulo32, and then
a further precisely prescribed cancellation of depth E+26. These are stronger
necessary conditions, not a proof that an actual index fails them.

## Remaining obstruction and preserved scope

At the actual stationary point, the lower and upper packet slopes cancel.
Their values must additionally cancel for a multiple root. The joint analysis
now accounts for the point's motion and the nonlinear correction exactly,
but does not prove that the remaining value-unit equality is impossible for
every ordinary r. The enlarged independent family contains one singular
member. The actual Euler parameter still must be shown to avoid it.

The earlier terminal-129/161 range exclusions, regular-address band, and first
irregular-address reduction are retained in the parent checkpoint. Their full
archive is preserved under `history/`. This continuation does not replace the
global simplicity target with the solved local geometry.

## Reproduce

Python3.10 or newer and the standard library suffice. From this package root:

```text
python3 coupled/critical_dynamics/check_coupled_dynamics.py --out fresh_dynamics.json
python3 coupled/parameter_geometry/check_geometry.py fresh_geometry.json
python3 coupled/packet_balance/verify_ledger.py
```

The packet verifier reconstructs249 retained packets by a separate
Bernoulli/source and direct-binomial localization path. It also checks the
omitted tail bounds and center-location precision. Its saved bounded replay
took125.26seconds. The small dynamics check uses existing certified jets and
the model geometry check uses explicitly stored finite coefficient lifts.

The independent review is under `coupled/review/`. Each computation has a
contract, retained outputs, and a manifest. `MANIFEST_ROOTS.json` states the
execution root for each manifest. Preserve the delivered package before
running scripts that refresh their output records. Checksums certify artifact
identity, not mathematical truth.
