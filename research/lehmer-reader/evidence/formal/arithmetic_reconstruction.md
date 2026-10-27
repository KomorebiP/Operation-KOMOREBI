# Reconstruction of the primitive arithmetic conclusions

Review date: 9 October 2026. Raw targets:

- `historical/Lehmer_Primitive_Content_Transport_2026-09-26/lehmer_transport/RESEARCH_NOTE.md`, sections 4 to 7.
- `historical/Lehmer_Packet_Tree_Sharp_Boundary_2026-09-26/lehmer_attempt/RESEARCH_NOTE.md`, section 1.
- `historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/prior_audit/SYNTHETIC_MODEL.md`.

**Primary verdict:** the written primitive arithmetic argument is correct
under its named classical tau identities. Authentication of those external
identities is delegated to the release literature review. No bounded
computation is required to establish the universal algebraic implications
checked here. No proof-assistant verification is claimed.

## Dependency graph

Packet identity -> content-scaling bijection -> square-divisor convolution ->
Mobius inversion and multiplicativity -> exact local recurrence.

Local recurrence plus the modulo-5 congruence -> nonzero even primitive
blocks. Local recurrence plus parity -> odd primitive blocks equal to the
prime parameter times an odd integer. Local recurrence plus the actual tau
values at 2 and 3 -> tau's corresponding prime-zero criterion.

Multiplicativity then gives all-square primitive nonvanishing and equality of
the two zero sets. No arrow from these statements to universal prime
nonvanishing is present.

## Content scaling

For a packet with positive gcd g, multiplication by g permutes the residues
modulo 5 with sign chi_5(g). Reindexing by `j -> g j mod 5` and dividing by g
gives a primitive standard-residue packet. Its norm is divisible by 5 from
the residues and by 2 from its zero coordinate sum. Hence `g^2 | n`.
The Vandermonde scales by `chi_5(g) g^10`. This reconstructs the convolution
and its Mobius inverse with the stated character and exponent, including the
zero character at multiples of 5.

## Even blocks

The polynomial recurrence has expansion

\[
T_r=\sum_{j=0}^{\lfloor r/2\rfloor}
 (-1)^j\binom{r-j}{j}p^{11j}a^{r-2j}.
\]

For p different from 5 the actual congruence gives
`a = p+chi_5(p) mod 5`. The recurrence roots modulo 5 may therefore be taken
as p and chi_5(p). Because `chi_5(p)p^10 = 1 mod 5`, the primitive local
coefficient is

\[
R(p^r)\equiv p^{r-1}(p+\chi_5(p))\pmod5\qquad(r\geq2).
\]

This is nonzero when p is 1, 2 or 3 modulo 5. Exponent 1 is handled directly
by the congruence for a.

When p is 4 modulo 5, c is p^10. If a is nonzero put `t=v_p(a)`.
For t <= 4 the initial term has uniquely least valuation in T_(2m), while
the correction has larger valuation, giving `v_p(R(p^(2m)))=2mt`.
For t >= 6 the final recurrence term has valuation 11m and the correction
has valuation 11m-1, giving `v_p(R(p^(2m)))=11m-1`. These assertions include
m=1. The integer binomial coefficients can increase valuations but cannot
lower them, and each relevant extremal coefficient is plus or minus 1.

For t=5 write a=p^5u with p not dividing u. The normalized recurrence is
`H_r=u H_(r-1)-p H_(r-2)`. A zero residual would make x=u^2 a root of the
monic integer polynomial `F_m(x)=H_(2m)-H_(2m-2)`. Its constant coefficient
is `(-1)^m p^(m-1)(p+1)`, and modulo p it equals `x^(m-1)(x-1)`.
The integer-root theorem and coprimality imply x divides p+1, while x is
1 modulo p. The only positive options are 1 and p+1. The first contradicts
5 dividing u. The second would give `p=(|u|-1)(|u|+1)`, whose only prime
possibility is p=3, outside this case. At m=1 this specializes to
`F_1(x)=x-p-1`, so the minimal case is covered.

If a=0 it is evaluated directly, without applying a valuation to zero:

\[
R(p^{2m})=(-1)^m p^{11m-1}(p+1)\ne0.
\]

At p=5 the correction is zero. The two extremal valuations cannot tie,
because `2v_5(a)` cannot equal 11. If a=0 the even block is `(-5^11)^m`.
For actual a=4830 the valuation of every positive exponent block is its
exponent. This completes the even-block proof at every prime. R(1)=1
covers the all-square boundary s=1.

## Odd blocks and tau's zero criterion

For an odd prime different from 5, b and c are odd while a is even. The
polynomial `(T_(2m+1)-c T_(2m-1))/a` has constant coefficient

\[
(-1)^m b^{m-1}((m+1)b+mc),
\]

which is odd. Every other term contains a^2 and is even. This proves an odd
multiplier at m >= 1. At m=0 the multiplier is 1. Polynomial division is
performed before evaluation, so a=0 is included. The prime 2 is covered by
the modulo-5 formula, and 5 by the valuation formula above.

For tau itself, the Hecke roots alpha and beta are distinct and nonzero.
Equality would imply `a^2=4p^11`, impossible from its odd p-adic valuation,
also at p=2. If T_r=0, their ratio zeta is a root of unity. Then

\[
a^2/p^{11}=2+\zeta+\zeta^{-1}
\]

is a rational algebraic integer in [0,4]. Its possibilities are 0,1,2,3,4.
At p >= 5 each nonzero possibility has odd p-adic valuation and cannot be a
square. At p=2 and 3 the actual a values -24 and 252 make the displayed
ratio nonintegral. Thus a=0 is necessary, and its direct recurrence has
exactly the odd exponents zero. Multiplicativity gives the same zero
criterion for tau and R.

## Synthetic-model interpretation

The model changes a single prime parameter q to zero while retaining the
integer Hecke recurrence at all primes. The Chebotarev leaf can choose q
above any coefficient bound with the original parameter already divisible
by 10M. Integral recurrence induction then preserves every coefficient
modulo 10M. At q the even local primitive factor is
`(-1)^m q^(11m-1)(q+1)`, so every square residual remains nonzero.

This is a valid countermodel to the implication from the listed arithmetic
properties to nonvanishing. It is not claimed to be a new modular form,
a different modular form, or an actual zero of tau. If the selected original
parameter were already zero the sequence could equal tau. “Nonmodular” is
therefore not an unconditional conclusion of this construction.

## Obligation matrix

| Obligation | Status | Evidence or limitation |
|---|---|---|
| Index, sign, character and exponent conventions | Passed | Direct scaling reconstruction |
| Boundary n=1 and exponents 0,1 | Passed | R(1)=1 and R(p)=a |
| Homogeneous content induction | Passed | Every other argument is strictly smaller |
| Even local blocks including a=0 and t=5 | Passed | Integer recurrence and root argument |
| Odd multiplier including a=0 and m=0 | Passed | Polynomial-before-evaluation convention |
| Special primes 2,3,5 | Passed | Actual initial values and local cases |
| Source theorem authentication | Separate literature record | Not inferred from memory in this audit |
| Congruence quantifier exchange | Refuted | Per-modulus witnesses need not be the same prime |
| Formal proof-assistant validation | Not supplied | No recovered formal project or source |
| Universal tau prime nonvanishing | Incomplete | No global discriminator excludes a=0 |

The strongest safe statement is the exact primitive square theorem and
zero-set equivalence under the checked classical identities. The cheapest
productive mathematical next input would be a property of actual Delta or
actual prime packet shells that is absent from the synthetic arithmetic
class, together with a proof that it excludes zero.
