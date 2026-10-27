# Scalar Frobenius and compatible Kummer coordinates

This note proves B52.5--B52.9. The coefficients below are always the single
global coefficient vector in H4. No independent local basis choice is used
to invent a ratio between global coefficients.

## 1. The exact good-13 locus

Assume13 does not divide C. Complete point counts under the residual
character contract leave precisely

    (A,B) mod13 = (0,b),   b in {1,5,8,12}.                 (10)

Every one of these four pairs has

    N1=14, N2=222,
    P13(T)=T^4-26T^2+169=(T^2-13)^2.                      (11)

The complete good equation set has156 pairs. Thus (10) is not inferred
from a convenient example. For the integer equation it also implies
13|A, B^4=1 mod13, and BC=1 mod13. The last assertion follows because
seventh powering permutes F_13^* and, on these four roots, C=B^(-1).

## 2. From repeated eigenvalues to an actual scalar

Let pi be Frobenius on the reduction of J over F13. The algebra Q[pi] is
reduced, being a product of fields. This is the classical Frobenius
semisimplicity input checked in Milne, ChapterII, Remark1.4. Applying
Cayley--Hamilton to (11) and using reducedness yields

    pi^2 = 13 id.                                         (12)

Equivalently, the semisimple rational Tate action has minimal polynomial
dividing T^2-13. The prime13 is inert in K, so its K-Frobenius is pi^2.
The character nu there is -1. Hence the ACTUAL twisted representation has

    rho(Frob_(13)) = -13 I.                               (13)

This equality holds on the rational Tate module and therefore on every
stable integral lattice. Reduction modulo7 is the identity. At this good
place inertia is also trivial, so

    alpha|K_(13) = 0,   beta|K_(13) = 0.                   (14)

The semisimplicity step is indispensable. A Jordan matrix with diagonal
entries -13 has repeated eigenvalues but need not be scalar. A negative
control in the verifier retains exactly this failure mode.

## 3. Isolating the global unit coefficient

Use the residue field F169=F13[r]/(r^2-5). For a unit, the seventh-power
symbol is x^24. Exact arithmetic gives

    phi^24 = 10+5r != 1,
    3^24 = 1,
    r^24 = 1.                                            (15)

The first element has exact order7. An independent enumeration of the
24-element seventh-power image gives the same membership decisions.
Since13 is not7, a local unit is a seventh power precisely when its residue
is: seventh powering is an automorphism on principal units by Hensel's
lemma. Thus the local image of [phi] is nonzero, while [3] and [sqrt5]
vanish. Restricting the SAME global expansion H4 and applying (14) yields

    0 = a_phi * res_13[phi],
    therefore a_phi = 0 in k.                             (16)

Consequently

    13 does not divide C  implies
    alpha = a_3[3]+a_5[sqrt5], with a_3*a_5 != 0.           (17)

This calculates an actual global coefficient on a stated subcase. It does
not determine a_3/a_5, and it says nothing about a_phi when13 divides C.
A common global rescaling cannot change the vanishing in (16).

The original projective coefficient candidates with a_3*a_5!=0 number
49*48=2352. Condition(16) leaves48: choose a_5=1 once globally, and set
r=a_3/a_5 in k^*. These are Kummer-coordinate candidates, not Galois
representations, integer solutions, or a percentage of Beal completed.

## 4. A genuine value of the higher diagonal character

In the fixed global Frobenius-at-three eigenbasis, (13) gives

    a_n(Frob_(13)) = d_n(Frob_(13)) = -13 mod7^n.

For eta_n=a_n/chi_7, the corresponding value is

    eta_n(Frob_(13)) = -1/13 mod7^n.                       (18)

The local character is unramified and these values lift compatibly through
all powers of7, using the unit -1/13 in Z_7. This is a calculation of one
actual local restriction in compatible bases. It is not a calculation of
the global eta_n and does not assert that its ramified local restrictions
lift. In particular it does not erase the higher diagonal obstruction.

## 5. Three explicit local functionals in the same global coordinates

At q in {29,43,71}, all three Kummer generators are units. Their images
lie in a one-dimensional k-space of unit classes. The image of the GLOBAL
generator3 is nonzero at each listed place, so it can serve as the anchor
for writing local relations among the same three global generators.

For a split place specify the image of sqrt5. In each row L_v satisfies

    res_v(alpha) = L_v(a_phi,a_3,a_5) * res_v([3]).         (19)

| rational q | image of sqrt5 | L_v(a_phi,a_3,a_5) |
|---:|---:|---|
| 29 | 11 | 4 a_phi + a_3 + 5 a_5 |
| 29 | 18 | 3 a_phi + a_3 + 5 a_5 |
| 43 | inert | a_3 + 2 a_5 |
| 71 | 17 | 2 a_phi + a_3 |
| 71 | 54 | 5 a_phi + a_3 |

All integer coefficients in this table are interpreted in F7 inside k.
For example, at29 the symbol of3 is23; the symbols of sqrt5 and phi at
sqrt5=11 are25=23^5 and20=23^4. At43 the symbol of3 is4, sqrt5 has symbol16,
and phi has symbol1. At71 the symbol of3 is48, sqrt5 has symbol1, and the
two phi symbols are48^2 and48^5. The executable record includes all values.

These are exact relations in each local Kummer group, not an identification
between the local groups. The global coefficients in (19) are unchanged.
Scaling a local unit-space generator multiplies the whole functional and
cannot alter its zero locus or manufacture equality of unrelated cocycles.

## 6. Good reduction supplies inequalities, not just trace congruences

At good29 or good43, every residue surviving the full residual polynomial
has v_7(#J^nu(F_Q))=2. If the natural local class alpha vanished, the whole
natural residual rank-two representation would be the identity: chi=1 at
these places and inertia is trivial. All four-dimensional7-torsion points
would then be rational, forcing7^4 to divide #J^nu(F_Q), a contradiction.
Therefore alpha is locally NONZERO at every such good place.

By (19) this gives the compatible necessary inequalities

    29 not dividing C  implies
       4a_phi+a_3+5a_5 != 0 and 3a_phi+a_3+5a_5 != 0;
    43 not dividing C  implies  a_3+2a_5 != 0.             (20)

When13 does not divide C, write r=a_3/a_5. Conditions(20) become

    good29 implies r != 2,
    good43 implies r != 5.                                (21)

Both good primes leave46 of the48 projective Kummer candidates. Again,
these are necessary coefficient restrictions, not realized representations.

## 7. The simultaneous depth-one support obstruction

Suppose13 does not divide C and n=1. At every eligible place where the
ACTUAL opposite class beta ramifies, H5 gives t=1,s=0, hence alpha is
locally zero. This holds without the extra ordinary hypotheses.

At71 the local forms in (19) reduce to a_3, which is nonzero. Thus beta
cannot ramify above71, even though B52.4 forces71 to divide C.

At29 an actually ramified place forces a_3+5a_5=0, or r=2. At43 it forces
a_3+2a_5=0, or r=5. These are incompatible because a_5!=0. We obtain

    n=1 and13 not dividing C imply:
      beta is unramified above71;
      beta cannot ramify over both29 and43;
      at least one OTHER eligible rational prime divides C.           (22)

The last clause uses H3: beta must ramify somewhere and71 is unavailable.
That other prime may be29,43, or any other eligible prime. If all eligible
prime divisors lie in {29,43,71}, then r is2 or5 and the entire ramified
support must lie over one of29 or43, not both. This is a support restriction,
not an assertion that every bad prime ramifies in beta.

## 8. Inert-minus support and the ordinary depth-three regime

Assume13 does not divide C. Let q outside {3,5,7} be inert in K and q=-1
mod7. The rational units3 and5 are seventh powers in F_q because
7 does not divide q-1. In the local Kummer group,
2[sqrt5]=[5]=0, so [sqrt5]=0 too. Principal units cause no obstruction.
Thus (17) implies alpha is locally zero at all these places.

At any actual ramified upper endpoint n=t+2h, H5 instead requires alpha
nonzero. Therefore such inert primes cannot support an upper-endpoint beta.
The corresponding rational residue classes are13 and27 modulo35.

In the explicitly ordinary regime (all eligible t=h=1), n is1 or3 by
Block51. At n=3 every ramified place is an upper endpoint. On the subcase
13 not dividing C, at least one ramified supporting prime must therefore
lie in

    {1,8,22,29} modulo35,                                 (23)

rather than the old six-class set. The fixed divisibilities29*43*71|C hold
at this depth, but do not by themselves say which primes ramify in beta.
Neither the ordinary hypotheses nor13 not dividing C is automatic.

## 9. Removing the old nonliftable ray example on this subcase

At the historical prime q=1504231, both split places have seventh-power
symbols1 for3 and sqrt5, and nontrivial symbols for phi. Thus (17) implies
alpha is locally zero there when13 does not divide C.

The Block50 ray family has nonzero local delta(a_n) there for every n>=2.
It cannot be the actual diagonal family on this subcase: the inherited
identity [alpha] cup [beta] = -delta(a_n) would have zero left side locally
and nonzero right side. This excludes THAT proposed realization, not all
ray characters and not all actual endpoint characters.

When13 divides C, the old family is not removed by this argument. Its
Block51 realization cost n=3+v_7(v_q(C)) remains a necessary condition,
not a contradiction or a realization theorem.
