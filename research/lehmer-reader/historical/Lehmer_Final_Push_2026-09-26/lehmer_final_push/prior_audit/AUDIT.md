# Independent audit of the primitive arithmetic theorems

Date: 26 September 2026. Reviewer: isolated subagent `prior_audit`.

**Normalized claim and verdict: proved as written.** With the packet residual
R defined in the audited note, R(s^2) is nonzero for every positive integer s,
and R(n)=0 if and only if tau(n)=0 for every positive integer n.

This verdict concerns the two stated residual theorems. It is not a proof of
Lehmer's conjecture. The raw proofs were reconstructed rather than accepted
from the previous audit. The reviewer inherited project context and therefore
this is an independent derivation, not a blind review. No formal verification
or novelty classification is claimed.

## Pinned target and scope

- Base checkpoint: LEHMER-CONTENT-TRANSPORT-02.
- Base archive SHA256:
  `ce2c5dc5a0e82b788d2a5970537511d765f79891d0e1ca9682b25c9a0c4d502c`.
- Raw target: `lehmer_transport/RESEARCH_NOTE.md`, Sections 4–7; SHA256
  `3136761c55dcc5a067a51f4c1ef1d5a0f4869be43b6427cbdeb131832a7dcf66`.
- Hecke reduction: `lehmer_attempt/RESEARCH_NOTE.md`, Section 1; SHA256
  `0fe22c423a50b54f02114771e65bf0c5c73b77dfa3edbd863668ec4e05f38770`.

The claims quantify over positive integer indices. The character chi is the
quadratic character modulo 5, extended by zero at multiples of 5. All recurrence
calculations are in Z; no analytic convergence or interpolation is needed.
The rank certificates and harmonic-null construction are not dependencies of
the two audited conclusions and were not reaudited.

## Dependency graph

1. Han's packet identity gives tau(n) as the sum of W(v) on the residue-labelled
   shell with norm squared 10n. [External theorem, exact specialization checked.]
2. Gcd extraction partitions that finite shell and gives the square-divisor
   convolution between tau and R. [Internal proof reconstructed.]
3. Square-divisor Mobius inversion and Hecke multiplicativity imply R is
   multiplicative, R(1)=1, and
   R(p^r)=T_r-chi(p)p^10 T_(r-2) for r>=2. [Internal algebra using external
   Hecke recurrence.]
4. The mod-5 congruence and an exact valuation/rational-root argument show every
   even local residual is nonzero. [External congruence plus internal proof.]
5. Parity of tau at odd primes gives an odd polynomial multiplier for every odd
   local residual. [External parity criterion plus internal proof.]
6. A root-of-unity argument reduces tau's zeros to prime zeros at odd exponents.
   [Internal algebra using the same Hecke recurrence.]
7. Multiplicativity combines the local statements. [Internal proof.]

There is no dependency on Lehmer's conjecture, on any positivity certificate,
or on bounded computational evidence.

## Obligation matrix

| Obligation | Result | Decisive reason |
|---|---|---|
| Packet normalization and index shift | Passed | t=5 gives denominator 1!2!3!4!=288, positive sign, and partition size n-1 |
| Gcd sector bijection | Passed | Reindex by multiplication by g mod5, then divide by g |
| Character in weight scaling | Passed | Multiplication permutations have signs +,-,-,+ for residues 1,2,3,4 |
| Divisibility g^2 divides n | Passed | Rescaled norm is divisible by 5 and by 2 |
| Mobius inversion and multiplicativity | Passed | Square-supported factors are multiplicative |
| Local formula, r=0,1 boundary | Passed | R(1)=1 and R(p)=tau(p); correction begins at r=2 |
| Mod-5 recurrence calculation | Passed | Character squared is 1 and chi*p^10 is 1 mod5 |
| Ordinary p-adic valuations | Passed | Extremal terms have coefficient 1 and uniquely minimal valuation |
| a=0 case | Passed | Explicit nonzero even term; no valuation of zero is taken |
| Exceptional valuation t=5 | Passed | Integer root lies in {1,p+1}; both squares excluded under the stated hypotheses |
| p=5 | Passed | Even recurrence extremes cannot tie since 2t is even and 11 is odd |
| Odd multiplier at m=0 | Passed | Multiplier is 1 |
| Odd multiplier at a=0 | Passed | Polynomial division precedes evaluation |
| p=2 and p=5 odd exponents | Passed | Mod5 formula for p=2; valuation r for p=5 |
| Standard Hecke zero criterion | Passed | Rational algebraic integer in {0,1,2,3,4}; explicit primes 2,3 handled |
| Excluding tau(p)=0 | Not addressed by these theorems | The hypotheses have explicit synthetic zero models |

## Reconstructed arithmetic proof

Put a=tau(p), b=p^11, c=chi(p)p^10, and T_0=1, T_1=a,
T_r=aT_(r-1)-bT_(r-2). Direct induction gives

\[
T_r=\sum_{j=0}^{\lfloor r/2\rfloor}
(-1)^j\binom{r-j}{j}b^j a^{r-2j}.
\]

For p different from 5, chi=p^2 modulo 5 and a=p+chi modulo 5. The recurrence
therefore has the same mod-5 solution as the complete symmetric polynomials
C_r in p and chi. Because chi^2=1 and c=1 modulo 5,

\[
R(p^r)\equiv C_r-C_{r-2}=p^{r-1}(p+\chi)\pmod5
\quad(r\ge2).
\]

This rules out zero at every positive exponent for p congruent to 1,2,3 modulo
5, using R(p)=a separately at exponent 1. Only p=5 and p congruent to 4 remain.

For p congruent to 4, c=p^10 and 5 divides a. If a is nonzero and t=v_p(a)<=4,
the valuation of the j-th summand of T_(2m), before any extra valuation of its
integer binomial coefficient, is 2mt+j(11-2t). The j=0 coefficient is 1.
The correction p^10*T_(2m-2) starts at valuation 10+(2m-2)t, strictly above
2mt. Thus v_p(R(p^(2m)))=2mt.

For t>=6, the final term of T_(2m) has valuation 11m and coefficient plus or
minus 1; every preceding term has strictly larger valuation. The correction
has valuation 10+11(m-1)=11m-1 and dominates. This includes m=1, when the
correction is simply p^10. If a=0, evaluation directly gives

\[
R(p^{2m})=(-1)^m p^{11m-1}(p+1)\ne0.
\]

At t=5, write a=p^5u with p not dividing u. The normalized recurrence is
H_r=uH_(r-1)-pH_(r-2), H_0=1, H_1=u. A zero residual would require a root
x=u^2 of the monic polynomial F_m(x)=H_(2m)(u)-H_(2m-2)(u). Its constant
coefficient is (-1)^m*p^(m-1)*(p+1), while modulo p it is x^(m-1)*(x-1).
Consequently x is a positive divisor of p+1 and x=1 modulo p, so x is 1 or p+1.
The first is impossible because 5 divides u. In the second case
p=(|u|-1)(|u|+1); primality forces |u|=2 and p=3, outside the present residue
class. This handles m=1 as well: F_1(x)=x-p-1.

For p=5, c=0. If a is nonzero, the two possible extremal valuations of the
even recurrence expansion cannot tie, since 2v_5(a) cannot equal 11. One term
has uniquely minimal valuation. If a=0 the even term is (-5^11)^m. For the
actual a=4830, v_5(a)=1 and the leading term a^r has uniquely minimal valuation
r for every r. Thus all powers of 5 are nonzero. Multiplicativity now proves
R(s^2) is nonzero, including s=1 because R(1)=1.

For an odd prime p other than 5, both b and c are odd and a is even. For m>=1,
the polynomial (T_(2m+1)-c*T_(2m-1))/a lies in Z[a^2] and its constant is

\[
(-1)^m b^{m-1}((m+1)b+mc).
\]

This constant is odd because (m+1)+m is odd. All other terms contain a^2 and
are even. Hence the multiplier is odd, including when a=0. At m=0 the
multiplier is 1. This proves the exact primitive zero criterion. For the
special p=2 the mod-5 formula is nonzero; p=5 was handled above.

To check the corresponding tau criterion, let alpha,beta be the roots of
X^2-aX+p^11. They are distinct because a^2=4p^11 has odd p-adic valuation
on the right (also at p=2). They are nonzero. If T_r=0, the formula for T_r
forces alpha/beta to be a root of unity zeta. Then a^2/p^11=2+zeta+zeta^(-1)
is rational, an algebraic integer, and real in [0,4]. It is one of 0,1,2,3,4.
For p>=5 every nonzero possibility has odd p-adic valuation and cannot be a
square. For p=2,3 the actual values -24 and 252 make a^2/p^11 nonintegral.
Therefore a=0 is necessary, and direct recurrence evaluation shows that a=0
makes precisely the odd exponents vanish. Multiplicativity gives the same
criterion for tau and R.

## Smallest cases and independent controls

No computation is needed for the verdict. The smallest symbolic cases are

\[
R(p)=a,\qquad R(p^2)=a^2-b-c,\qquad
R(p^3)=a(a^2-2b-c).
\]

At an odd prime other than 5 the multiplier in the final expression is odd.
For p=5 the even correction disappears, as required. For the tied valuation
case the m=1 polynomial is x-p-1, agreeing with direct substitution into
R(p^2). These checks do not replace the universal proofs above.

## Sources, extraction and notation

The reviewed primary PDFs were accessed on 26 September 2026. No PDF source
cache was created in this audit; locators and internal version markers were
checked in the retrieved full texts. No exact-source leaf remains conditional.

1. Guo-Niu Han, *The Nekrasov-Okounkov hook length formula: refinement,
   elementary proof, extension and applications*, arXiv:0805.1398v1,
   9 May 2008, Theorems 1.1 and 1.2, printed page 3.
   https://arxiv.org/pdf/0805.1398
   The t=5 V-coding conditions are precisely the packet residue and zero-sum
   conditions. The size formula becomes |lambda|=norm^2/10-1 and the weight
   factor becomes D/288. The z=25 product supplies exponent 24. This is the
   exact normalization required for the packet identity.
2. Jennifer S. Balakrishnan, William Craig, Ken Ono, *Variations of Lehmer's
   conjecture for Ramanujan's tau-function*, arXiv:2005.10345v1,
   20 May 2020. https://arxiv.org/pdf/2005.10345
   The PDF's internal version marker is v1. Equation (1.2) gives the mod-5
   congruence used here; Theorem 2.2(1–3) gives multiplicativity, recurrence and
   its root formula; the opening of Section 3 gives the parity criterion via
   Jacobi's identity. The displayed initial expansion gives tau(2), tau(3)
   and tau(5). Symbols tau, p and the q normalization agree directly.

The direct URL https://arxiv.org/pdf/2005.10345v1 returned a disabled fetch
error. The unversioned URL succeeded and authenticated the exact v1 text by
its internal first-page marker. This retrieval failure has no mathematical
effect but is recorded rather than silently omitted.

This was theorem verification, not a novelty search. Han supplies the packet
formula and Balakrishnan–Craig–Ono supplies classical arithmetic inputs; neither
is asserted to state the primitive conclusions verbatim.

## Exact remaining gap and a synthetic obstruction

There is no repair needed in the two reviewed proofs. They also cannot be
sharpened into prime nonvanishing using only their arithmetic leaves.

To see this globally, fix any prime q congruent to 4 modulo 5. Define a new
multiplicative integer sequence f by keeping every prime parameter tau(p)
except replacing the parameter at q by 0, and extend every prime-power block
by the same Hecke recurrence. Then:

- f(q)=0;
- every Hecke recurrence and multiplicativity identity still holds;
- f(n)=tau(n) modulo 5 at every n, because the changed parameter was already
  0 modulo 5 and the recurrence is integral;
- f(n) is odd precisely at odd squares, because every odd-prime parameter is
  even, so the recurrence modulo 2 alternates 1,0,1,0,...; the unchanged
  2-power block is even at every positive exponent;
- even the local bound |f(p)|<=2*p^(11/2) remains true, since replacing a
  parameter by zero preserves it.

The same primitive transform of f satisfies all the audited residual theorems
while vanishing at q. This is a countermodel to any implication from those
arithmetic properties alone to prime nonvanishing. It is not asserted to be a
modular form or to have the same packet realization. Precisely that extra
structure would have to supply a new discriminator.

The strongest safe outcome is the two proved residual theorems, their exact
local valuation statements, and the explicit equivalence of the remaining
prime problem. The cheapest productive next check is to identify a concrete
property of actual prime packet shells or the fixed modular form Delta that
the synthetic sequence violates, then prove that this property excludes zero.
Repeating the same local recurrence, parity or mod-5 calculations cannot do so.
