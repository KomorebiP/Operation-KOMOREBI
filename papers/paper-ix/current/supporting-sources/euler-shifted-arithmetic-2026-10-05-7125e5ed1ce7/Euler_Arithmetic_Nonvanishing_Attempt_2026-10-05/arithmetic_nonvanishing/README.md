# Actual Euler nonvanishing: focused arithmetic attempt

Checkpoint: `Euler-arithmetic-nonvanishing-20261005`.
Parent: `Euler-coupled-stationarity-20261005`.

**The requested arithmetic nonvanishing theorem remains open.** This
checkpoint records direct attempts at that theorem. It does not add a new
range of parameter digits or claim that the Euler simplicity program is
closed.

## Exact target and current gap

For each ordinary T>=0 such that

    r=(17659+2^18T)2^640-161

has true terminal161, prove that the actual critical value on the deep
argument chart is nonzero. In the established independent deformation this
is Phi_r(2^(2r-25)) !=0. The earlier exact stationary geometry remains the
starting point, not the missing proof.

Put E=2r-25 and a=Phi_r(0). A hypothetical singular actual member must obey

    0=a+2^E Phi_r'(0)+2^(2E+26)V_0(2^E),
    V_0=1 mod8.

The unknown arithmetic implication is that the actual Bernoulli coefficients
cannot satisfy this entire equation. In particular, the dependence E=2r-25
must be retained. No argument here proves that exclusion.

## Decisive results of the attempt

1. **The weighted Bernoulli identity has been transferred with its cutoff.**
   With g(z)=z coth z, the exact relation g(z)g(2z)=(z/sinh z)^2+2z^2
   produces the required nonunit factor4^r. Its full tail relation also
   produces a finite cross-boundary polynomial. At the first packet, that
   polynomial cancels the apparent4^r forcing exactly. A proof that omits
   it would be false. The Riccati and Newton-operator forms are also exact.
   See [the weighted kernel proof](unit_identity/WEIGHTED_KERNEL_ATTEMPT.md).

2. **A finite resummation exposes the remaining shifted series.** The actual
   Euler tail F_r=Ecal-S_r satisfies

       F_r=-(2N+1)M_r+(s*9^(s+1)/3)u_r(s-1/2),
       N h=s[h(s)-h(s-1/2)].

   Here M_r has an explicit finite rational-exponential expression, while
   u_r is still an infinite Bernoulli series. The second term is forced by
   the analytic half-shift branch9^(1/2)=-3. Its value and derivative have
   not been separated from the finite expression at a hypothetical double
   root. See [the half-shift proof](structural/WEIGHTED_TAIL_TRANSLATION.md).

3. **The proposed parity/leading-unit exclusion is false on an actual index.**
   At T=22831001499602523078606181325, the actual critical value has exact
   valuation91 and leading unit15mod32. This is a nonzero critical value,
   not a singular Euler member. It proves that those two features alone
   cannot exclude singularity. See [the exact discriminator](root/UNIT_FILTER_RESULT.md).

4. **Two possible methods of closing the proof have precise obstructions.**
   The full depleted packet family cannot have a local analytic multiplier
   extension agreeing even with its admissible ordinary members. Its
   factorial parameter poles survive depletion. Separately, for each fixed
   ordinary r, the rational sequence G_r(n) has no eventual finite linear
   polynomial-coefficient recurrence over Q or Q2. These theorems rule out
   those specific constructions, not every scalar critical-value argument
   or nonlinear identity. See [carry and poles](carry_nonintersection/CARRY_AND_POLE_ATTEMPT.md)
   and [the recurrence obstruction](root/NO_FINITE_LINEAR_CLOSURE.md).

## Other exact arithmetic structure retained

The [moment route](structural/STRUCTURAL_MOMENT_ROUTE.md) gives a source-free
Euler interpolation, its exact first two derivative valuations, and an
explicit two-moment criterion for a repeated residual root. It also derives
the nonzero Euler Hankel determinants. The attempted identification of our
residual with an orthogonal-polynomial remainder fails at two rational
examples, so those determinants do not prove the target.

The natural ordinary square-test argument x=r+10363 is also ruled out as
a witness whenever v2(K(c))>=7: it stays at dyadic distance2^-2
from the critical center, where the actual value is then necessarily a nonzero
square. Detecting the critical obstruction this way requires an argument
much closer to the actual center.

## Evidence and continuation

The independent review reconstructs the narrow proved statements and checks
the finite computations. Its verdict on the target is **incomplete**.
See [the independent review](review/INDEPENDENT_REVIEW.md). Exact scripts,
contracts, outputs and provenance are retained with each route. No new Lean
compilation was attempted. No external transcendence theorem is assumed.

The next unresolved mathematical step is a strict valuation separation for
the remaining terms in the transferred weighted/half-shift relation under
simultaneous value and derivative cancellation. This must use their actual
Bernoulli coefficients and the ordinary index r. The constant forcing term,
leading unit, generic transfer-operator factorization and full-family
analytic interpolation do not supply it. This route remains open; the
present identities alone do not complete that step.

The parent checkpoint is included unchanged in the enclosing package, so
the original Euler definitions, finite certificates, and fixed-r deformation
proofs remain available as explicit dependencies.
