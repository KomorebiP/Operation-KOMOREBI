# Arithmetic consequences and exact support boundaries

All conclusions retain TARGET_CONTRACT.md's inherited geometric hypotheses.
Write H(C) for the complete set of variable rational prime divisors q of C
with h_q=v7(q^f_q-1)>=2. Arbitrary additional h<=1 divisors are permitted in
all statements that restrict H(C).

## Universal highest-layer exclusion

No nontrivial actual eta has highest-layer ramification contained in97/293.
This holds even when additional primes197,491 or arbitrarily large others
divide C. It does not assert that a larger highest-layer support containing
97 or293 is impossible. Additional actual ramification contributes new rows'
columns and can change the conclusion.

## B57.6. Full diagonal triviality on expanded support classes

Let U be the ten-prime universe in FINITE_CLASSIFICATION.md. If the actual
highest-layer support is contained above U and eta is nontrivial, then1567
must itself ramify, and one of the two five-ideal patterns in B57.5 occurs.
In particular,

    H(C) subset U\{1567} => eta=1 mod7^n, n<=3.

The numerical depth bound uses the retained nonzero beta: if eta is trivial,
its local inertia order at beta support is1, so s=0 and n=t. The SAME local
Frobenius is also trivial on its diagonal correction, so h>=n. Since the
largest h in U\{1567} is3, n<=3. If n=3, beta must ramify at the inert1373
place, t=3, v7(v_1373(C))=2, and the local Kummer row forces a3/a5=1.
The unit coefficient is not thereby determined.

If1373 is also excluded, the stronger statement is

    H(C) subset {97,197,293,491,587,883,1471,1667}
                     => eta=1 mod7^n, n<=2.

At depth2 some actual beta-supporting q still has v7(v_q(C))=1. This is not
a contradiction and does not eliminate depth2.

## B57.7. Depth at most three on the full ten-prime high-divisor class

Even with1567 present, one has

    H(C) subset U => n<=3.                              (1)

If eta is trivial, the proof is the h>=n argument above. Suppose eta is
nontrivial. B57.5 gives global exponent e=1 and n>=3. At beta support,
the inherited identity n=t+2s and inertia order7^s imply s<=e. Also

    v(p)>=n-s>=n-e,     v(yr)>=n-e,
    Q-1=px+ry

in the SAME toric factorization. Therefore h>=n-e, or n<=h+e. Since all
variable high primes have h<=3, n<=4. At n=4, every beta-supporting prime
must have h>=3, hence must be the inert1373 place. It is unramified in eta,
and rational cancellation in B57.5 makes its Frobenius correction trivial.
Thus eta is locally trivial there. At beta support this gives s=0, t=n, and
h>=n by the same factorization. But h_1373=3<4, a contradiction. Hence n<=3.

This argument excludes the potential depth4 case using an ACTUAL local
value of the classified character. It does not invent good reduction at1373
or rely on the invalid implication 'eta unramified implies eta locally trivial'.

If eta is nontrivial under H(C) subset U, then n=3 and one of the two patterns
in B57.5 occurs. At each nonzero inertia component, its order is7, so
v(N11)=n-1=2. In the toric factorization x is a unit and y is nonunit, giving
t+s=2 with t,s>=1. Thus t=s=1 and v(N21)=t+2s=3=n. Every displayed eta-supporting
prime therefore also ramifies in beta at depth3, and v7(v_q(C))=0 there.
This does not extend the implication 'eta ramified => beta ramified' to
arbitrary depth or arbitrary supports.

For completeness, beta's possible ramification under this COMPLETE H(C)
hypothesis is especially narrow. In pattern A (ratio3), it is exactly the
five displayed eta places. In pattern B (ratio1), those five places are
forced and the inert1373 place is the only possible extra ramification;
if it occurs, t=3 and v7(v_1373(C))=2. To see this, a nonzero local alpha
excludes beta support. Every remaining unramified inert place has locally
trivial eta by rational cancellation, so h>=3 is required. The only such
place in U is1373, whose Kummer row (0,3,4) vanishes only at ratio1. The
unused split prime's Kummer row is nonzero in either opposite pattern.
Low-h additional primes cannot support beta at n=3 because h>=m=2.

## What remains unrestricted

There is no bound on H(C) for a general hypothetical solution. A highest layer
using primes outside U is not classified here. Even within U, the two retained
patterns at depth3 are not excluded. Depth1 and general depth2 remain open.
No new integer upper bound for C is obtained. The CM nonboundary-point branch,
three higher Hilbert levels, full signature, and full Beal remain separate.
