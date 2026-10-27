# B76.5. Exact abelianization and the global uniformizer field

These are additional consequences of the depth-one image theorem. They do not
eliminate any arithmetic pattern or assert anything analogous at higher depth.

## The continuous abelianization is exactly the two endpoint coordinates

Let H=J_B and define

    pi:H -> k direct-sum B,
    pi(M)=(M12 mod7, (M21/7) mod7).

The residual diagonals are1, so both coordinates add under multiplication. This
surjective homomorphism is precisely(alpha,beta) on G_(K_infty). Let D be the
CLOSED commutator subgroup of H. Necessarily D is contained in ker pi.

At the first layer, a commutator of U(s) with an element I+7bE21 has leading matrix

    sb H0 - s^2 b E12.

The s and -s combinations, together with square polarization, give all kH0 and
kE12. Thus D intersect K1 has the full first layer allowed by ker pi. Since D is
normal in H, commutators of its diagonal first directions with H's nonzero lower
first direction give all kE21 at the second layer. Seventh powers give the other
second directions. Power propagation and closedness then give K2 subset D.
Any element of ker pi has residual identity and first lower direction0. Match
its first diagonal and upper entries with D; the remaining element is in K2.
Therefore

    D=ker pi,
    BOX: H_ab = H/D = k direct-sum B.                     (12)

The quotient has exponent7 and order7^(2+d). For the eight retained patterns,
its order is7^3=343. This does not say the full image is abelian. Its nonabelian
finite quotient modulo343 has order7^13 in that same case.

## The global seventh root of7 does not lie in the full torsion field

Set T=K_infty(J[7^infty]), the field cut out by the actual full cyclotomic image.
Then

    BOX: K_infty(7^(1/7)) is NOT a subfield of T.           (13)

Proof. On G1=G_(K(mu7)), include the fourth Kummer coordinate xi=[7]. Valuations
at7,3,5 and the same unit argument show that phi,3,sqrt5,7 are independent. Degree-
six norm restriction preserves this. The joint(alpha,xi) image is k direct-sum F7.
The exact commutator argument in B76.1, now with chi-weight3 on both coordinates,
preserves that image on Ginf as well. Thus xi|Ginf is nonzero and independent
of the two F7 components of alpha.

If the seventh-root field in(13) were contained in T, xi would factor through H
as a continuous F7-valued homomorphism. Equation(12) then makes it an F7-linear
functional of alpha and beta. Conjugation by an element with chi=3 acts by3 on
alpha, by5 on beta, and by3 on xi. Comparing these actions forces the beta part
of that functional to vanish, since3-5 is a unit modulo7. This would make xi a
functional of alpha alone, contradicting the independent Kummer coordinate.
This proves(13). No explicit defining equations for T have been computed. QED.

Equivalently, some element of the GLOBAL Galois group fixes all actual7-power
torsion and all cyclotomic roots but moves7^(1/7). This is a statement about
GLOBAL fields. It must NOT be transported to a local completion or interpreted
as saying that the local period valuation is zero.

## Why the fixed-seven trace construction remains consistent

At the finite precision of Block74, the local uniformizer probe has determinant1
and alpha=beta=0. Its matrix modulo343 therefore lies in the REDUCTION of D: any
determinant-one integral lift with those first coordinates belongs to ker pi.
This statement does not assert that the finite-level tau_3 fixes every cyclotomic
root or that its full matrix belongs to H. A global abelian character of H cannot
detect the represented commutator part. The mixed trace can detect it because it
is a product-sensitive, nonabelian function, not a homomorphism H->k.

The local valuation map on a specified decomposition group need not factor as a
global abelian character of H. Its nonzero value on the probe is therefore fully
compatible with(12)-(13). No claim of nu7=0 or contradiction with local toric
uniformization follows.

This excludes a proposed simplification of the remaining global problem: one
cannot identify the independent GLOBAL [7] Kummer character with an abelian
coordinate of the actual full depth-one Tate image. The correct comparison must
retain the local embedding and the nonabelian deformation data.
