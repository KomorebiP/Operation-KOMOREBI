# Komorebi Beal Block 46: partial-results addendum

Checked 19 September 2026. This is an additive literature application to the
previously delivered Block 46 v4.6.0. The frozen archive is unchanged.

## Accepted consequence: square-class independence is automatic

**Proposition.** Suppose that positive, pairwise-coprime integers A, B, C satisfy

\[
A^3+B^5=C^7.
\]

Then B is not a square, A and C cannot both be squares, and the classes
[AC] and [BC] are linearly independent in Q*/Q*².

This is a written corollary of established generalized Fermat theorems. It is
not a new Lean theorem and no novelty is claimed.

**Proof, first exclusion.** If B=b², then

\[
(b^5)^2+A^3=C^7.
\]

The transformed triple is positive and primitive. Theorem 1.1 of Poonen,
Schaefer and Stoll gives exactly two possibilities with all three coordinates
positive:

\[
(b^5,A,C)=(2213459,1414,65),\quad(15312283,9262,113).
\]

Neither first coordinate is a fifth power, since

\[
18^5=1889568<2213459<2476099=19^5,
\]
\[
27^5=14348907<15312283<17210368=28^5.
\]

Thus B is not a square. Source: [Twists of X(7) and primitive solutions to
x²+y³=z⁷](https://math.mit.edu/~poonen/papers/pss.pdf), Theorem 1.1;
author manuscript dated 16 July 2006, published in Duke Mathematical Journal
137 (2007), 103–158. The complete theorem statement and the signs of its
solutions were checked.

**Proof, second exclusion.** If A=a² and C=c², rearrangement gives

\[
(c^7)^2+(-B)^5=a^6.
\]

These are nonzero coprime integer bases. This contradicts Theorem 1 of
Bennett–Chen–Dahmen–Yazdani for signature (2,5,6), since
1/2+1/5+1/6=13/15<1. Equivalently, use their Proposition 13 with exponent
n=5. The negative fifth-power base is permitted: the theorem concerns
integer bases, not just positive ones. Source: [Generalized Fermat equations:
a miscellany](https://personal.math.ubc.ca/~bennett/BeChDaYa-IJNT-2015.pdf),
International Journal of Number Theory 11 (2015), 1–28, published online
8 July 2014; Theorem 1 and Proposition 13 were checked.

**Proof of independence.** For coprime positive integers U,V, if UV is a
rational square, it is an integer square and both U and V are squares.
Indeed, coprimality means each prime occurs in at most one factor; the
valuation of that factor must therefore be even.

If AB or BC were a square, B would be a square, contradicting the first
exclusion. If AC were a square, both A and C would be squares, contradicting
the second. Consequently AC, BC and AB are all nonsquares. The only three
potentially nontrivial products of the two classes are

\[
[AC],\qquad[BC],\qquad[AC][BC]=[AB],
\]

and none is trivial. This proves independence. QED.

The usual primitive condition gcd(A,B,C)=1 would suffice: the exponent
equation forces any prime dividing two bases to divide the third, so the
bases are then pairwise coprime.

## Consequence for the quartic construction

The complementary parameters are

\[
a=\frac{A^3}{C^7},\qquad b=\frac{B^5}{C^7},\qquad a+b=1.
\]

Their square classes are [AC] and [BC], since

\[
a=AC\left(\frac{A}{C^4}\right)^2,
\qquad
b=BC\left(\frac{B^2}{C^4}\right)^2.
\]

The proposition therefore supplies the independence hypothesis of Block 45,
`ARITHMETIC_THEOREMS.md`, Section 4. Its radical-tower proof shows that
X⁴−2X²+b is irreducible, and its splitting field is dihedral of degree eight.
For completeness, the degree-four assertion follows by putting s²=a:
Q(s) has degree two, while 1+s cannot be a square there because its norm b
is a nonsquare. A root u with u²=1+s therefore has degree four.

Scaling a root by C² gives the existing integral polynomial

\[
f(X)=X^4-2C^4X^2+CB^5.
\]

Hence, for every hypothetical primitive positive (3,5,7) solution:

- Q[X]/(f) is a quartic field;
- the splitting field has degree eight and group D4 (order eight);
- the field versions of Block 46's discriminant bounds apply without an
  additional square-class independence assumption.

Set K=Q[X]/(f), and let L be the splitting field of f. With rad_o the
product of odd prime divisors, the previously proved bounds now apply
throughout the hypothetical primitive family:

\[
D_K\leq 2^{11}\operatorname{rad}_o(A)^2
\operatorname{rad}_o(B)\operatorname{rad}_o(C)^3,
\]
\[
|D_L|\leq 2^{31}\operatorname{rad}_o(A)^4
\operatorname{rad}_o(B)^4\operatorname{rad}_o(C)^6.
\]

This removes the uneliminated dependent-square-class branch recorded in
Block 45 and the extra field hypothesis retained in Block 46. The more
general étale-algebra theorem remains valid.

Global independence does not imply independence after restriction to every
local field. Nor does this result recover the large divisibility factors
lost into the index I² in disc(f)=I²D_K. That obstruction remains.

## Further exclusions with checked original theorem statements

| Forbidden condition | Exact substituted equation | Known case |
| --- | --- | --- |
| A=a⁵ | (a³)⁵+B⁵=C⁷ | (5,5,7) |
| A=a⁷ | C⁷+(−a³)⁷=B⁵ | (7,7,5) |
| C=c⁴ | (−A)³+(c⁷)⁴+(−B)⁵=0 | (3,4,5) |

The first two use Dahmen–Siksek, [Perfect powers expressible as sums of two
fifth or seventh powers](https://arxiv.org/pdf/1309.4030v2), Theorems 1–2.
Those cases are unconditional; the paper's GRH-dependent results concern
other signatures. The third uses Siksek–Stoll, [Partial descent on
hyperelliptic curves and the generalized Fermat equation
x³+y⁴+z⁵=0](https://arxiv.org/pdf/1103.1979v1), Theorem 1.1.
All substituted bases remain nonzero and coprime. These rows also exclude
higher powers divisible by the indicated exponent, and do not assert that
all other perfect-power bases are possible.

## How the user's list narrows the general problem

If d divides an exponent n, then U^n=(U^(n/d))^d, and replacing a base by a
positive integral power preserves its prime divisors. Thus primitive
solutions descend along coordinatewise divisibility of signatures.

Every integer n>2 either has an odd prime divisor or is divisible by four.
It follows that proving Beal for all signatures whose entries belong to
{4} union {odd primes} would suffice. This remains an infinite set, and
each claimed elimination must retain the correct signs and any exceptional
solutions. In particular, the exponent triple (3,5,7) itself does not reduce
to another listed triple with all exponents greater than one by divisibility.

The useful extra step above is to exploit powers hidden in the bases.
These exclusions are not assumptions that bases may simply be chosen
power-free.

Darmon–Granville finiteness for a fixed hyperbolic signature does not prove
that the solution set is empty, give a usable height bound here, or reduce
the whole conjecture to a finite list of signatures. A bounded numerical
search also does not address solutions beyond its tested range.

## A relevant working-paper result: retain its evidence limitation

Theorem 1 of Dahmen–Siksek's July 2024 [working paper on
x⁵+y³=z⁷](https://few.vu.nl/~sdn249/GFE357.pdf) states stronger restrictions.
With the explicit dictionary (x,y,z)=(B,A,C), its conclusion becomes:

| Branch | Restrictions stated in that draft |
| --- | --- |
| C even | 30 divides C and 7 does not divide AB |
| C odd | 3 does not divide ABC, 5 does not divide AC, and 7 divides A |

The translation is verified. Computational completeness is not independently
verified here: Section 4.3 reports that Casper Putz completed the required
septic-field classification, but defers its details. Sections 5–7 address
the reducible algebra cases. No GRH assumption was found in the checked draft.

This is a potentially useful refinement of the parity split, subject to
accepting the draft's reported classification. It is not used in the
accepted square-class proposition above, and has not been promoted to a
fully audited project input.

## Verification and remaining obligations

The accepted proposition uses two primary-source theorem statements, an
explicit signed substitution, exact fifth-power inequalities, and elementary
prime valuations. A separate agent checked the substitutions and square-class
implication. The draft's theorem translation and deferred dependency received
a separate bounded source review. These were collaborative checks, not a
fresh independent formal proof audit of the entire project.

No new Lean compilation, Magma replay, full audit of the cited papers, or
global literature novelty search was performed. Primary PDFs were inspected
through the web tool, not retained locally; no cached-byte hashes are claimed.
The scope was the results directly relevant to this reduction and the three
additional perfect-power exclusions, not every item or numerical range in
the user's supplied list.

The previous odd-C irreducibility result retains its existing written-proof
status. The C-even irreducibility problem, elimination of all relevant
modular forms at seven, the index-control problem, and nonexistence of
primitive positive (3,5,7) solutions remain open in this project. Beal is
not proved.
