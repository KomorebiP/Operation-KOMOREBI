# Dyadic step amplification after branch recovery

The older bridge report was found and read. It already records displacement-sensitive bounds on the divisor branch and mixed-step bounds. Its dyadic result stops at integrality and parity. Therefore it complements the full dyadic completion in this workspace and does not supersede that completion.

The bridge archive could not be materialized: the required download helper returned HTTP 502. The report and a separately published `NishibuchiCorollary.lean` were inspected using supported read operations. `DisplacementPrecision.lean` was not found as a separately published file. Consequently, no archive hash comparison, source merge or replay of that separate bridge is claimed.

This extension implements a fresh generic argument against the already rebuilt full completion baseline. The new source is independent of the unavailable bridge implementation. It uses the same elementary Newton-expansion mechanism described in the retrieved report.

## New checked bound

Write C_(4,j)(n) for the original normalized rational Euler sequence and E_j(n)=j! C_(4,j)(n). For every j<4 and every natural u,k,n, the new checked theorems give

    precision_2(Delta_u^k C_(4,j)(n)) >= min(k*(1+v_2(u)), n),
    precision_2(Delta_u^k E_j(n)) >= min(k*(1+v_2(u)), n) + v_2(j!).

Here the displayed inequalities mean the project's zero-safe precision predicate: either the difference is zero, or its ordinary valuation is at least the displayed exponent. The underlying ring statements are divisibility inside Z_2. They are not field-divisibility claims.

For the usual valuation interpretation take u>0. Lean also includes u=0 with its natural valuation convention. Positive-order zero-step differences vanish, and order zero reduces to the original integrality and factorial divisibility, so that endpoint is valid.

The factorial term is one for j=2 or j=3 and zero for j=0 or j=1. The result therefore keeps the earlier higher-address gain and adds the valuation of the step. A separate theorem states the guaranteed bound min(k*(s+1),n) at every step 2^s*u, including u=0.

For example, when n>=6, k=2 and u=4, the normalized lower bound rises from two to six. At j=2 or j=3 the unnormalized bound is seven. These are lower bounds; the theorem does not assert equality for those parameters.

## Divisor branch

The actual all-residue divisor-branch capstone is now also present. For prime p, m>0 with m dividing p-1, every j<mp and h=(p-1)/m, it proves

    precision_p(Delta_(u*h)^k E_j(n)) >= min(k*(1+v_p(u)), m*n).

For C_(mp,j), it proves the corresponding exponent with v_p(j!) subtracted. No extra factorial bonus is asserted on this branch. The source applies the independently rebuilt generic theorem to the baseline's original all-residue integral lift. It includes p=2,m=1 as well as the odd-prime cases.

## Generic proof and boundary

At a fixed row n in any commutative coefficient ring, assume all base-step differences satisfy p^min(a,M) | Delta_h^a f(n). Newton expansion and the proved integer estimate

    p^(v_p(u)+1) | choose(u,a)*p^a    (1 <= a <= u)

yield p^min(k*(v_p(u)+1),M) | Delta_(u*h)^k f(n). The proof retains every base-difference offset while inducting on k. It does not assume a period or a bound at shifted rows. The actual dyadic capstone instantiates the hypothesis using `DyadicFourCongruences.base_step_bound`; it introduces no conjectural assumption.

The row cap n is retained. This work does not remove the early-row threshold in the arbitrary-precision period theorem, settle the two unrestricted native conjectures, or claim a minimal period.

## Checked sharp boundary and validation

The same original recurrence proves C_(4,0)(2)=69 and Delta_1 C_(4,0)(1)=70. Its exact valuation is one, so a universal extra digit beyond the new bound is false at this parameter. The extension proves this negation and rejects a deliberately wrong Lean proof demanding precision two from the capstone there.

Four new mathematical modules contain seventeen theorem declarations. All four compile with one thread and warnings treated as errors. A complete explicit-declaration audit reports only `propext`, `Classical.choice`, and `Quot.sound`, or subsets. Source scans found no proof placeholder, explicit axiom, unsafe declaration, or `native_decide`. The negative control fails with a Lean type mismatch, not an import failure, timeout, or runtime failure.

Two development compilations failed before correction. Their logs are preserved alongside the passing logs. `Bridge_Validation.json` records commands, source hashes, the expected and observed declaration sets, the failed archive recovery, and the validation classification. The baseline source was not modified.
