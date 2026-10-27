# B61.1. Full opposite local triviality from the natural period obstruction

All uses of the actual curve retain TARGET_CONTRACT.md. This lemma strengthens
an unramifiedness condition to a Frobenius condition for beta, not for eta.

## A same-lattice determinant lemma

Suppose eta_n=1 mod7^n at a variable bad place with norm Q=1 mod7. The exact
toric trace and determinant give, for an arithmetic Frobenius lift,

    F=[[a,b],[7^n c,d]],  tr(F)=Q+1,  det(F)=Q,
    a=Q mod7^n, d=1 mod7^n.

Write d=1+7^n D. The exact trace gives a=Q-7^n D. Expanding the determinant,

    ad = Q + 7^n (Q-1)D - 7^(2n)D^2,
    b c = (Q-1)D - 7^n D^2.                         (1)

If beta is unramified but nonzero locally, then its Frobenius value is nonzero:
the local coefficient character chi^-1 is trivial, so unramified H^1 is
identified with k through Frobenius and there are no nonzero coboundaries.
In the actual endpoint coordinates beta(F)=bar(c)/bar(chi(F)). Hence c is a unit.
Equation (1) forces b in7O, since Q-1 is divisible by7. Thus the entire natural
residual Frobenius is I. Natural residual inertia at this variable prime is
already trivial. Consequently the whole natural J[7] is rational over K_v.

The inherited marked period cross-ratio now forces phi to be a seventh-power
residue. If beta were ramified, Block59 already supplies this same requirement.
Taking the contrapositive proves:

    eta_n=1 mod7^n, Q=1 mod7, phi NOT a seventh-power residue
                     => beta|G_(K_v)=0.             (2)

This is full local vanishing of the cohomology class, not just absence of
ramification. For actual n=2, eta_2=1 is inherited globally.

## The three forced bad rational primes

At n=2,29,71,491 divide C. Each splits in K, has q=1 mod7, and both phi roots
fail the seventh-power test. With roots in increasing order:

| q | roots of X^2-X-1 | x^((q-1)/7) |
|---|---|---|
|29|6,24|20,16|
|71|9,63|32,20|
|491|74,418|223,240|

Thus beta is zero on the full local groups at all six prime ideals above these
three rational primes. No good reduction at them is assumed. Their being bad
is essential for the exact toric trace in (1).

## A necessary negative control

Dropping eta_n=1 is invalid. At depth2, put

    F=[[22,3],[49,8]], N=[[-147,63],[-343,147]].

One checks tr(F)=30, det(F)=29, N^2=0, FN=29N, NF=N. Natural inertia is trivial
modulo7; the changed endpoint has unramified but nonzero Frobenius beta. The
natural residual upper entry is3, not0. The lower diagonal8 is not1 modulo49,
so the scalar precision hypothesis fails exactly where required. This is an
abstract local representation, not an actual global Frey realization.

The universal proof is (1), not the finite matrix sample. The checker covers
13,608 exact Q(phi) examples, including nonrational coefficients and depth2,
and retains this failed strengthening as a control.
