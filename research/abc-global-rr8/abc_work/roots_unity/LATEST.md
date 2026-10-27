# ABC roots-of-unity checkpoint RR3

The full ABC conjecture remains unproved. This continuation tests the proposed
use of roots of unity and generalizations, starting from the accepted RR2
archive with SHA-256
`f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469`.

## Positive result: a cyclotomic degree budget

Let A>B>=1 be coprime, n>=1, c=A^n+B^n. For each odd p|c put
d_p=ord_p(A/B), e_p=v_p(A^d_p-B^d_p). Let E_n be the distinct orders d_p
for which e_p>=2, and let D_n=sum_(d in E_n) phi(d).

The exceptional birth factor satisfies

    W_n divides product_(d in E_n) Phi_d(A,B),
    log U(c) <= log A + log n + D_n log(A+B).

Consequently, with gamma=epsilon/(1+epsilon),

    1 + log_2(n) + 2D_n <= gamma n

is a sufficient pointwise condition for the ABC inequality. In particular,
for fixed delta>0, the condition D_n<=n^(1-delta) gives the inequality for
all sufficiently large n uniformly in the bases. The proof is in
[ORDER_BUDGET.md](routes/cyclotomic/ORDER_BUDGET.md) and its separate review is
[order_budget.md](reviews/order_budget.md).

This permits arbitrarily large exceptional primes when their distinct
cyclotomic orders have small total degree. It does not prove that arbitrary
triples satisfy the degree condition. No historical originality is claimed.

There is a stronger prime-size consequence. For every fixed epsilon>0 and
0<delta<1, all sufficiently large n satisfy the ABC inequality whenever every
exceptional odd output prime is at most n^(1-delta), uniformly in A and B.
This improves RR2's sufficient n^(1/2-delta) cutoff. The reason is that the
number of distinct available orders is bounded by the divisor count of 2n,
which is n^o(1). See [the corollary](routes/cyclotomic/ORDER_CUTOFF_COROLLARY.md)
and [its review](reviews/order_cutoff.md). This statement remains restricted
to the common-power family and its displayed exceptional-prime hypothesis.

## What the filters establish exactly

At odd p, let d=ord_p(A/B), s=v_p(A^d-B^d). The order at depth k is

    d_k=d p^max(0,k-s).

Until depth s, the exponent filter does not change. Several prime filters can
also coincide: the joint compatible class has period lcm(d_k), rather than
the product of their separate periods. Full conductor-shell characters
retain the entire valuation, including this plateau.

For the torsion root omega matching A/B modulo p,

    v_p(A/B-omega)=s.

Removing the torsion component preserves this depth. Standard Fourier
resolvent modes likewise preserve the full primitive pole. A fixed integral
combination can cancel primitive depth only within its resultant budget,
whose size must be controlled as conductors and coefficients move.

The existing generalized torsion-distance theorems have coefficient or
subvariety dependent constants. In the two-term case the optimal constant
is exactly p^(-s), so applying them does not independently estimate s.

## Remaining target and checks

A successful continuation needs a global estimate coupling simultaneous
contacts to input height and radical. An adaptive auxiliary polynomial must
also have a proved nonzero value. Neither orthogonality nor a short modular
coefficient vector supplies that nonvanishing condition.

Read [CLAIM_LEDGER_RR3.md](CLAIM_LEDGER_RR3.md) for proof and review scope,
and [HANDOFF.md](HANDOFF.md) for the precise restart point. Finite checks
use exact arithmetic. No Lean code was compiled.
