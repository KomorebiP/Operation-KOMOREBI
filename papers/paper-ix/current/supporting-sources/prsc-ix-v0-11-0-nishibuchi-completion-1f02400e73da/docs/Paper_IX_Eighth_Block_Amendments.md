# Paper IX eighth-block amendments and claim boundary

**Komorebi P. — v0.8.0**

The status-corrected manuscript is preserved unchanged. These amendments add a proved subcase and clarify the remaining work; they do not replace its all-residue Theorem 7.5 with a weaker theorem and declare the original complete.

## 1. A new unconditional standard-window theorem

Let `p` be prime, `m > 0`, `m | p-1`, `h=(p-1)/m`, and `0 <= j < p`. For all natural `n,k,u`, the original rational packet coefficients satisfy the zero-safe precision statement

    Delta_(u*h)^k C_(m*p,j)(n) = 0
    or v_p(Delta_(u*h)^k C_(m*p,j)(n)) >= min(k,m*n).

The same bound holds for the original unnormalized sequence `j! C_(m*p,j)`. The general statement is ideal divisibility by `p^min(k,m*n)` inside the actual completed ring `Z_p`. The rational statement is proved by identifying the already constructed integral lift with the original rational coefficients in `Q_p`; it is not divisibility in the field `Q_p`.

The result includes `n=0`, `k=0`, zero differences, and `u=0`; the manuscript uses the positive-multiplier subset. It also includes prime two, where the permitted positive divisor is `m=1`. For `m=1` the window contains every allowed residue. No claim of a complete dyadic version of the broader external conjecture is made.

Principal targets: `StandardWindowDwork.standard_window_global_bound`, `StandardWindowDwork.standard_window_global_order`, `StandardWindowPrecision.normalized_window_precision`, `StandardWindowPrecision.unnormalized_window_precision`, and `StandardWindowPrecision.modulus_p_complete_family`, all under `KomorebiPaperIX`.

## 2. Closure is derived using the actual defect

Write `D=d/dt`, `delta=D^(p^2)-D^p` and `B=delta/p` on `Q_p[[t]]`. The integral Hurwitz subring is defined by the actual factorial-scaled coefficients `d! [t^d] f` belonging to `Z_p`. Flatness requires every iterate `B^s f` to lie in that subring. The characteristic-zero product formula for `B` includes the difference of two finite middle sums, whose coefficients are the actual binomial quotients `choose(p^2,a)/p` and `choose(p,a)/p`. Their integrality is proved for primes, not assumed.

The general closure theorem is proved by induction on the defect order. The actual reciprocal theorem proves the inverse's integral coefficients when the input has constant coefficient one, and then derives all higher normalized defects. No desired Euler coefficient bound appears as a closure hypothesis.

## 3. Source identification and nonsingular pivots

The standard-window source has normalized Hurwitz coefficient `1 / choose(d+j,d)` in degrees divisible by `m*p` and zero elsewhere. Its construction uses proved integral unit pivots. Consecutive sources obey

    (d+j+1) g_(j+1)(d) = (j+1) g_j(d).

The Euler-operator commutator with every defect iterate is proved. On degrees divisible by `p`, `d+c` is a unit when `p` does not divide `c`. This yields source flatness throughout `j<p` by induction, starting with the explicit residue indicator. Formal-series encoding then identifies the source with the original factorial-ratio kernel and its reciprocal with the actual original Euler packet. Thus the proof is about the intended family, not an arbitrary flat sequence.

## 4. The higher residue interval is still pending

The nonsingular pivot argument cannot be applied at `c=p,2p,...,(m-1)p`. The source does not assert that such pivots are units. The supporting 18-page prose argument treats those singular ratios through weighted Amice estimates and a dual Mahler pairing, followed by propagation. Those actual-family estimates and the full remaining propagation are not supplied in this release.

Theorem 7.5 therefore remains `PENDING_LEAN`, with proved partial targets documented separately. The full manuscript register stays **23/24**, not 24/24. The two conjectures remain unproved. No percentage of the remaining proof effort is inferred from the fraction of residue labels now covered.

## 5. Boundary examples

The original recurrence gives `C_(6,2)(1)=-1/28`, `C_(6,2)(2)=425/364`, and `C_(6,2)(3)=-2039759/2660`. Hence the second difference at row one is `-949959/1235`, with actual rational three-adic valuation exactly two. The source checks these values and the sharp exponent.

For prime three, the constant EGF coefficient of `B(t*t^2)` is `-2`, whereas the ordinary two-term Leibniz expression is zero. Thus `B` is not a derivation. Additional deliberately invalid controls reject a nonunit singular pivot and a prime-power binomial-divisibility assertion at a composite base.

## 6. Validation scope

The active code uses no new project axioms or admitted proofs. It reuses the pinned Mathlib compiled dependency cache rather than rebuilding Mathlib itself. Source hashes connect the statements to their stored compiler and axiom reports. Numerical mirrors are independent finite tests, not Lean extraction. The original historical numerical suite and Papers I–VIII are not rerun. Reading the manuscript against the Lean types remains mathematical review.
