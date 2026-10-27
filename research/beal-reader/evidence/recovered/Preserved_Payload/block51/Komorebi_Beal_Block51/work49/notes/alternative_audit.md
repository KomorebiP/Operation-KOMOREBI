# Independent audit of the alternative elliptic construction

Disposition: ACCEPT for the stated absolute irreducibility proposition,
the local residual conductor calculation away from 3 and 7, and the
explicitly retained variable-conductor boundary. No mathematical BLOCK
was found in those claims. This audit does not add a modularity or
level-lowering theorem and does not transfer irreducibility to the
genus-two representation.

Reviewed note: `work49/notes/alternative_route.md`, SHA256
acfec4999beedf44b25b66041ed589acc2bce53c01c2d70b1cfbcecf09ade8b6.
The owner note and frozen Block48 were not edited.

## Curve, torsion and invariants

Let positive pairwise-coprime A,B,C satisfy A^3+B^5=C^7 and 5|C.
The proposed curve is

    E: y^2+3Axy-B^5y=x^3.

For a1=3A, a3=-B^5 and a2=a4=a6=0, the intermediate invariants are

    b2=9A^2,  b4=-3AB^5,  b6=B^10,  b8=0.

Substitution in the Weierstrass formulas independently gives

    c4=81A^4+72AB^5,
    c6=-729A^6-972A^3B^5-216B^10,
    Delta=-27B^15(A^3+B^5)=-27B^15C^7.

Thus the displayed cubic is nonsingular. At P=(0,0), the derivative
with respect to y is -B^5, which is nonzero; its tangent line is y=0.
That line meets the cubic at P with multiplicity three. Comparing
with the line at infinity gives divisor 3P-3O, so P is a nonzero
rational point of exact order three.

Since 5|C and the variables are pairwise coprime, A and B are units
at five. The relation B^5=-A^3 modulo five gives

    c4 = 9A^4 modulo 5,   v5(Delta)=7v5(C).

Consequently v5(j(E))=-7v5(C)<0. This computation does not require
a choice of minimal model, since j=c4^3/Delta is model independent.

## Rational isogeny obstruction and absolute irreducibility

I independently checked the exact list in Remark 5 of Bourdon--Gill--
Rouse--Watson, *Odd Degree Isolated Points on X1(N) with Rational
j-invariant*, [arXiv:2006.14966v1](https://arxiv.org/html/2006.14966v1#Thmthm5).
The remark covers the four noncuspidal rational X0(21) points giving
non-CM elliptic curves. Their j-values are

    -3^2*5^6/2^3,
     3^3*5^3/2,
    -3^2*5^3*101^3/2^21,
    -3^3*5^3*383^3/2^7.

Their five-adic valuations are 6,3,3,3, respectively. In particular
every value is integral at five. The non-CM hypothesis is addressed
before this list is applied: the negative valuation of j(E) excludes
CM because singular moduli are algebraic integers. I checked this
classical fact as explicitly recalled in the introduction, printed
p.1, of Habegger's [arXiv:1402.1632v1](https://arxiv.org/pdf/1402.1632),
whose actual header is dated 7 February 2014. This audit uses that
integrality fact, not Habegger's separate finiteness theorem about
algebraic units.

If E[7] had a G_Q-invariant F7-line, it would define a rational
cyclic subgroup of order seven. Its direct sum with the rational
order-three subgroup is Galois stable, and is cyclic of order 21
because the two orders are coprime. The quotient isogeny is therefore
defined over Q and supplies a noncuspidal rational X0(21) point.
The checked list contradicts v5(j(E))<0. This proves irreducibility
over F7.

The upgrade to absolute irreducibility is also valid. The Weil pairing
gives determinant chi on E[7]. Complex conjugation c has c^2=1 and
det(c)=-1. As the characteristic is seven, its two eigenvalues are
the distinct values 1 and -1, with eigenspaces defined over F7.
Every putative G_Q-stable line over Fbar7 is stable under c and must
be one of those two lines. It would consequently descend to an
F7-stable line, already excluded. No residual semisimplicity theorem
or classification of Cartan images is required for this step.

Thus the proposition is accepted on the full stated hypothesis 5|C,
and in particular on the current 3990|C branch. It is a proposition
about this elliptic curve's representation only.

## Exact conductor scope away from 3 and 7

Fix q different from 3 and 7 with q|BC. Pairwise coprimality separates
the B and C cases. If q|B, c4=81A^4 modulo q is a unit and
v_q(Delta)=15v_q(B). If q|C, c4=9A^4 modulo q is a unit and
v_q(Delta)=7v_q(C). An integral Weierstrass equation with unit c4
is minimal and has multiplicative reduction when its discriminant
is nonunit. Thus these are the minimal discriminant valuations.
This reasoning includes q=2; no short Weierstrass equation in residue
characteristic two is being assumed.

For completeness, the local Tate argument has precisely the scope
used in the owner note. After at most an unramified quadratic
extension, the multiplicative curve has parameter t_E and

    0 -> mu_7 -> E[7] -> Z/7 -> 0,

whose extension class is the Kummer class of t_E. The product formula
for the Tate discriminant gives v(t_E)=v(Delta_min). Over the maximal
unramified extension the residue field is algebraically closed and
7 is invertible. Hensel's lemma therefore gives a seventh root of
every unit. The Kummer class on inertia is zero exactly when
7 divides v(t_E). The possible unramified quadratic twist changes
no inertia action.

When that valuation is not divisible by seven, tame inertia has a
nonzero rank-one unipotent action: its fixed subspace has dimension
one and its Swan conductor is zero. The residual conductor exponent
is therefore one. When it is divisible by seven, the representation
is unramified and the exponent is zero. Hence the table in the owner
note follows, using gcd(15,7)=1 in the B case.

On 3990|C, no prime in {2,3,5,7,19} divides B. The part of the
residual conductor away from 3 and 7 is consequently exactly

    R7(B) = product of q|B for which 7 does not divide v_q(B).

There is no additional bad prime away from 3BC because Delta is a
unit there. This accepts the variable-prime support without asserting
an exact conductor at 3 or 7. In particular the finite residue check
at seven is not being used as a Tate-prime-unramifiedness argument.

## Source-family and computation checks

The change of variables x=A^2 x0, y=A^3 y0 transforms the curve into

    y0^2+3x0 y0+(-B^5/A^3)y0=x0^3.

This matches E3^+(t) in equation (19) of Pacetti--Villagra Torcomian,
[arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1), at the
stated parameter. I also checked that its Theorems A and B list seven
among their exceptional primes, so those results cannot be imported
as a solution of this target case.

The exact symbolic code was read independently. It represents
polynomials by integer coefficient dictionaries in Z[A,V], uses the
Weierstrass intermediate invariants above, and compares complete
coefficient dictionaries for all four identities. Its rational
j-values and their valuations match the primary list. The residue
loops cover the explicitly declared unit pairs at 5,7,11,19,29,41;
their bounds are not part of the universal irreducibility argument.
The already completed run's manifest was validated afresh and passed.
No duplicate run or additional finite search was needed: the written
identities and local proofs give the universal claims.

| Reviewed artifact | SHA256 |
|---|---|
| `alternative_route.md` | `acfec4999beedf44b25b66041ed589acc2bce53c01c2d70b1cfbcecf09ade8b6` |
| `source_records/alt_x021_rational_j.html` | `d620746e894b0dc70b100e593c1b2d5e47e40df1f7182f6dc9aff7bef44aa162` |
| `computations/alt_elliptic_invariants.py` | `404def78adcb74a382794bece0ad50978a5d6c26888a25190c30bd90929adfce` |
| `computations/alt_elliptic_contract.json` | `78803128c320a13cad03573cf73135df773eb562fcd4391ffcdd794a5a366403` |
| `verification/alt_elliptic_run/result.json` | `1881c733d1abd741868d0863e6f7baa2520a794fd2f37461602eb83f568283fd` |
| `verification/alt_elliptic_run/manifest.json` | `10d6a4f82242c1877d59cd439e7fe3f5175bd4f096fe40ac96b887a6939704ba` |

## Accepted boundary

The alternate elliptic representation is absolutely irreducible on
5|C, while the earlier RM representation is reducible on the current
branch. There is no contradiction: they are different representations.
The explicit conductor calculation leaves the uncontrolled factor
R7(B). The fixed-level Hilbert-form enumeration for the RM surface
therefore cannot be applied to E by substitution. The owner note
correctly stops at this boundary and makes no Diophantine closure claim.
