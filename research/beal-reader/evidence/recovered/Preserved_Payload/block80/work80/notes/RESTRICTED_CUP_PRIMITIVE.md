# B80.1. Restricted cup-product primitives exist without auxiliary ramification

Let Sigma be a finite set of places of K=Q(sqrt5) containing the prime over7 and
all real places. Let G_Sigma be the Galois group of the maximal extension
unramified outside Sigma. For the arithmetic application Sigma includes the other
fixed primes and the complete support of beta.

## The dual localization kernel is zero

We first prove

    Sha^1_Sigma(K,mu7)
      =ker(H1(G_Sigma,mu7)->product_(v in Sigma) H1(K_v,mu7))=0.       (1)

Minkowski's ideal bound for the real quadratic field of discriminant5 is
sqrt5/2<2. Every ideal class therefore has a representative of norm1, so Cl(K)=1.
The unit group is {+/-phi^e:e in Z}. Here is an elementary justification of the
fundamental unit assertion. Scaling a unit by a power of phi and by -1 puts its
first real embedding in [1,phi). If it were strictly between1 andphi, a unit of norm -1 would have integral trace a-a^-1 strictly between0 and1, while a unit of norm +1
would have trace a+a^-1 strictly between2 andsqrt5<3. Both are impossible. Thus
the scaled unit is1. Norm(phi)=-1.

A Kummer class unramified outside Sigma has valuations divisible by7 outside
Sigma. Principality lets us remove those valuations by a global seventh power,
leaving a Sigma-unit. If its local class vanishes at every v in Sigma, its
remaining valuations also vanish modulo7. Remove those by a seventh power as
well. The class is now represented by phi^e; the sign is itself a seventh power.

At F=Q7(sqrt5), exact arithmetic in O_F/49 gives

    (phi^48-1)/7 = 5 sqrt5 mod7 !=0.                        (2)

A seventh power unit has its48th power equal1 modulo49: write the unit as its
prime-to-seven torsion part times an element of1+7O_F. Equation(2) therefore says
that phi is not a seventh power in F. For e nonzero modulo7, Bezout would make
phi a seventh power if phi^e were. Thus e=0 modulo7. This proves(1).

The argument applies to arbitrary finite Sigma containing7, not only the four
frozen supports. It uses local vanishing at all Sigma, not a finite-prime sample
purporting to test all global elements.

## Finite-S Poitou--Tate is the required theorem

The Cartier dual of trivial F7 is mu7. For trivial k use the nondegenerate
F7 trace pairing on k to identify its dual with k(chi). Taking two F7 coordinates
in(1) gives Sha^1_Sigma(K,k(chi))=0. Poitou--Tate duality for FINITE Sigma pairs
this group perfectly with Sha^2_Sigma(K,k). Consequently

    H2(G_Sigma,k) -> direct_sum_(v in Sigma) H2(K_v,k)      (3)

is injective. This is not an inference from injectivity on the unrestricted
absolute Galois group. All primes dividing the module order belong to Sigma,
as required by Milne ADT I.4.10. Real Tate-cohomology terms vanish at odd order.

For the nine-prime supports of this project, every support residue norm is1
modulo7. At each of them H2(K_v,k) has k-dimension1 by local duality. The fixed
fields at2,3,5,7 do not contain mu7, so their H2(K_v,k) are zero. The global
invariants of k(chi) also vanish. The last part of the Poitou--Tate sequence
therefore makes(3) an isomorphism with k^9. This statement concerns cohomology,
not a computation of nine numerical local obstruction values for a candidate.

## Applying the theorem to the frozen residual pair

At every beta-supporting place, the inherited natural class is locally zero.
Thus alpha cup beta is locally zero. At each fixed place its target H2 group
vanishes; equivalently the inherited local coboundary property of beta suffices.
It is zero at real places as well. Equation(3) gives

    [alpha cup beta]=0 in H2(G_Sigma,k).                    (4)

Hence there exists a continuous normalized cochain p0 on G_Sigma such that

    dp0=-alpha cup beta.                                 (5)

This conclusion uses only the stated residual and local hypotheses; it does not
assume an actual higher representation in order to obtain its p0. It allows no
new ramification outside Sigma. Normalization p0(1)=0 follows from(5).

It is an EXISTENCE theorem for the bare equation. No defining field for p0, no
values on labelled Frobenius lifts, and no proof that p0 meets the actual trace
and toric affine conditions has been produced. Differences of its solutions are
ordinary global k-characters. Their space has dimension10 for these supports,
as proved explicitly in ORDINARY_LOCALIZATION.md. A zero homogeneous character
is not a preferred or numerically known affine primitive.

External inputs: Milne ADT I.2.3 (local duality), I.4.10 (Poitou--Tate), I.5.1/
Remark5.2(c) as a check on dimensions; classical Kummer theory and Minkowski.
The exact source hypotheses and inspected pages are in SOURCE_CHECK.md.
