# B61.2. Cohomological descent of the restricted-support opposite class

Let S={197,883,1373,1667}. All these rational primes are inert in K/Q and are
1 modulo7. Write V=k(chi^-1), with k=F49. This module itself extends to G_Q
using the mod-seven cyclotomic character. This fact is NOT a statement that
the actual Tate representation or its endpoint lattices descend.

Let beta in H^1(K,V) be unramified outside the four places above S and locally
zero at seven. We prove that beta has a unique preimage

    gamma in H^1(Q,V).

No restriction of its coefficients to F7 is imposed.

## Inertia localization is injective

This is the inherited Block49 Selmer input. For clarity, a class with zero
inertia at every finite place and zero local class at seven restricts over
L=K(zeta7) to an everywhere-unramified abelian exponent-seven character.
The ordinary class-group seven-part of L vanishes. Thus that character is
zero. Restriction from K to L is injective, since [L:K]=6 is prime to7.
Real inertia causes no seven-primary obstruction. Hence the original class
is zero. This also proves injectivity on any specified S without choosing a
basis of the Selmer group.

## Conjugation fixes the inertia data

The natural action of Gal(K/Q) on H^1(K,V) includes the coefficient action.
It is independent of a representative in G_Q because inner action is trivial
on cohomology (Milne CFT II, Remark1.28(b)). For each q in S choose a rational
arithmetic Frobenius representative sigma_q. Because q is inert it represents
the nonidentity automorphism of K/Q. On tame inertia, conjugation raises to q;
on coefficients the cyclotomic character is q^-1. On mod-seven inertia data
both effects are trivial since q=1 mod7. Wild inertia is a pro-q group and
has no nonzero homomorphism to the additive seven-group V. Therefore sigma_q
fixes the localized inertia of beta at q.

The representative can be chosen separately at each place precisely because
the action on cohomology is independent of inner choices. Outside S the
inertia data are zero. The conjugate is still locally zero at seven. Thus
sigma beta-beta has all inertia zero and is split at seven. By the preceding
injectivity it is zero. Hence beta is invariant under Gal(K/Q).

## Inflation–restriction and local conditions

The five-term sequence, with quotient Gal(K/Q) of order2, gives

    H^1(Q,V)  --restriction-->  H^1(K,V)^Gal(K/Q)

as an isomorphism: the outer H^1 and H^2 of the quotient vanish because2 is
invertible on V. The continuous version follows by finite quotients, or by
the continuous inflation–restriction sequence. This proves existence and
uniqueness of gamma. The exact sequence and the prime-to-seven vanishing are
checked in Milne CFT II, Remark1.35(a) and Corollary1.31.

At every rational prime outside S, gamma is unramified: away from5, K/Q is
unramified, so its inertia agrees with that seen over K. At5, restriction on
inertia has index at most2, and the same prime-to-seven injectivity excludes
an extra ramified class. At7, local restriction is injective, so gamma is
locally zero. At a split rational prime, the corresponding local field is
Q_q itself. Thus beta's full local zero at29,71,491 gives full local zero for
gamma there.

## Boundaries

This result is about an additive residual cocycle in a specified Selmer
space. It constructs no semilinear automorphism of the Frey Tate lattice,
identifies no base-field radical with a coefficient-field element, and does
not descend the natural Kummer coefficients. It need not apply unchanged
when beta ramifies at split primes or at other unrestricted prime patterns.
