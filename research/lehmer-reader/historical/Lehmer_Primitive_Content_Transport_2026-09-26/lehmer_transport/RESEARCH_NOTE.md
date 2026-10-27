# Primitive content and exact transport in the Lehmer packet problem

Checkpoint LEHMER-CONTENT-TRANSPORT-02, 26 September 2026.
Parent checkpoint: LEHMER-TREE-SHARP-01, pinned in BASE.json.

**Lehmer's conjecture remains unresolved.** This continuation constructs a
hierarchy of actual null transfers, identifies a conserved arithmetic split,
and proves that the primitive packet residual is nonzero at every square.
Its odd prime-power factors carry exactly the original prime nonvanishing
obligation. The uniform statements below have written proofs. Computational
ranks and certificates have their stated finite scope. There is no Lean
verification or claim of historical priority.

## 1. Definitions and fixed target

The target is tau(n) != 0 for every positive integer n. Continue with

\[
\mathcal V_n=\{v\in\mathbb Z^5:
v_i\equiv i\pmod5,\quad \sum_i v_i=0,\quad \|v\|^2=10n\},
\qquad
W(v)=\frac1{288}\prod_{i<j}(v_i-v_j).
\]

The classical five-core identity gives tau(n)=sum_{v in V_n} W(v).
Every weight is a nonzero integer. The involution
J(v)_i=-v_{(-i mod 5)} preserves W. Dyadic sectors use
c_i=(v_i-i)/5 modulo 2^k, identifying residues related by J.

A correction Q in the retained family is a symmetric homogeneous polynomial
in v with

\[
\sum_{v\in\mathcal V_n}W(v)Q(v)=0\quad\text{for every }n\ge1.
\]

Finite rational linear combinations are permitted. The coefficient choices
may depend on the target shell. After they are fixed, the total null identity
still holds on every shell. Local sector identities need not hold elsewhere.

## 2. Transfer matrices and the exact refinement law

Fix a shell and a finite list Q_1,...,Q_h. At depth k, let its occupied sectors
be S_{k,1},...,S_{k,s_k}. Define the mass vector and transfer matrix

\[
t_{k,r}=\sum_{v\in S_{k,r}}W(v),\qquad
(M_k)_{rj}=\sum_{v\in S_{k,r}}W(v)Q_j(v).
\]

Applying coefficients a changes the sector masses to t_k+M_k a.
Let A aggregate child sectors into parent sectors. Then, exactly,

\[
t_k=A t_{k+1},\qquad M_k=A M_{k+1}.
\]

Every column of M_k sums to zero. Put H_k=ker(1^T) and
T_k=im(M_k), so T_k is a subspace of H_k. The quotient

\[
E_k=H_k/T_k
\]

records total-preserving mass changes unavailable in this correction space.
It is a vector-space defect. It is not a count of failed sign certificates.
In particular a sign certificate may exist even when E_k is nonzero.

**Refinement theorem.** There is an exact sequence

\[
0\longrightarrow
\frac{\ker A}{M_{k+1}(\ker M_k)}
\longrightarrow E_{k+1}\longrightarrow E_k\longrightarrow0.
\]

To prove this, A maps H_{k+1} onto H_k, since each occupied parent has a child.
It maps T_{k+1} onto T_k. Its intersection kernel is

\[
T_{k+1}\cap\ker A=M_{k+1}(\ker M_k),
\]

because A M_{k+1} a=M_k a. Passing to quotients gives the sequence.
Equivalently, if r_k=rank M_k,

\[
\dim E_{k+1}-\dim E_k
=(s_{k+1}-s_k)-(r_{k+1}-r_k).
\]

Thus refinement introduces s_{k+1}-s_k detail directions, and new effective
columns resolve r_{k+1}-r_k of them. This is ordinary exact linear algebra
applied to these packet transfers, not a separately claimed new general theorem.

If N is a matrix whose columns form ker M_k, then

\[
B_k=M_{k+1}N,\qquad A B_k=0
\]

is an explicit basis-generating matrix of transfers confined within the
parent sectors. This repairs the failed localization proposal: Q_j is not
multiplied by an arbitrary sector indicator. Instead, combinations are solved
so that their parent effects cancel exactly.

## 3. Executed transport resolution

The fourteen older corrections have degrees through 20. This block constructs
22 further corrections: four of degree 22, five of degree 24, six of degree 26,
and seven of degree 28. There are 36 retained corrections in total.

At prime 31 the exact ranks are:

| Invariant degree cutoff | Coarse sectors | Coarse rank | Orbit sectors | Orbit rank | Remaining zero-total defect |
|---:|---:|---:|---:|---:|---:|
| 14 | 6 | 5 | 16 | 5 | 10 |
| 20 | 6 | 5 | 16 | 14 | 1 |
| 22 | 6 | 5 | 16 | 15 | 0 |

At degree 22 the detail transfer space has dimension 15-5=10. The stored
certificate performs two exact operations. It first eliminates five coarse
sector totals. It then uses coefficients in ker M_1 to eliminate all but one
fine-sector total without changing any coarse total. The survivor is
-52843168, independently equal to tau(31).

The first solve supplies only the five elimination equations. It does not
assume a value of tau(31). Computing the survivor is still a finite coefficient
calculation, not a uniform nonvanishing theorem.

The file also contains a nonconstant functional annihilating the degree-20
orbit transfer columns and its nonzero pairings with the degree-22 columns.
This identifies the removed defect explicitly. It is not a positive dual
obstruction to one-sign correction. The older degree-20 sign certificate at
31 remains valid despite that space's one-dimensional transfer defect.

Further finite resolutions are:

| Prime | Number of J-orbits | Degree cutoff giving full zero-total transfer rank |
|---:|---:|---:|
| 31 | 16 | 22 |
| 37 | 19 | 22 |
| 41 | 22 | 24 |
| 59 | 30 | 26 |
| 71 | 36 | 28 |

These are cutoffs in the constructed family. They do not establish optimality
among arbitrary polynomial corrections or a theorem for all primes.

Using the first five corrections through degree 14, the coarse transfer rank
was s_1-1 at all 94 odd primes below 500. Among all 250 odd indices below 500,
the only failures were 9 and 81. The next section explains the conserved
structure visible in those failures. No all-prime coarse-rank claim is made.

## 4. The arithmetic split that really is conserved

For a packet set g(v)=gcd(v_0,...,v_4), taking a positive gcd. Necessarily
5 does not divide g. Write chi(g)=(g/5), the quadratic character modulo 5.
The permutation j -> g j mod 5 has sign chi(g). This is checked directly
for the four units modulo 5.

The map

\[
u_j=v_{gj\bmod5}/g
\]

takes packets of exact content g to primitive packets with gcd 1. Their norm
becomes 10n/g^2. Since u has the standard residues and zero sum, its squared
norm is divisible by both 5 and 2. Consequently g^2 divides n. The map is a
bijection with the primitive shell at n/g^2. Its weights satisfy

\[
W(v)=\chi(g)g^{10}W(u).
\]

Define the primitive residual

\[
R(n)=\sum_{\substack{v\in\mathcal V_n\\g(v)=1}}W(v).
\]

Then the exact decomposition and its Mobius inverse are

\[
\boxed{\tau(n)=\sum_{g^2\mid n}\chi(g)g^{10}R(n/g^2),}
\]

\[
\boxed{R(n)=\sum_{d^2\mid n}\mu(d)\chi(d)d^{10}\tau(n/d^2).}
\]

Terms divisible by 5 have chi=0, so the formulas include all positive d,g
without introducing nonexistent content sectors.

**Content conservation theorem.** Every symmetric homogeneous universally
null correction, and every finite linear combination of such corrections,
is null inside each exact-content sector on every shell.

For Q of degree d, define R_Q(n) with the same primitive restriction. Scaling
gives

\[
\Theta_Q(n)=\sum_{g^2\mid n}\chi(g)g^{10+d}R_Q(n/g^2).
\]

If Theta_Q(n)=0 for all n, induction on n gives R_Q(n)=0 for all n: the g=1
term is R_Q(n), and every other nonzero term uses a smaller index. Thus every
exact-content contribution also vanishes. Linearity proves the stated span
version. This argument does not assert the result for arbitrary nonhomogeneous
null functions outside that span.

Unlike the individual parity sectors, these content sectors therefore carry
genuine invariants of all the homogeneous null corrections.

At terminal orbit resolution, if N orbits occupy c nonempty content classes,
the transfer rank is at most N-c. Exact ranks through degree 28 attain that
bound in the following cases:

| n | J-orbits | Contents | Rank |
|---:|---:|---|---:|
| 9 | 4 | 1, 3 | 2 |
| 49 | 22 | 1, 7 | 20 |
| 81 | 31 | 1, 3, 9 | 28 |

For prime n all packets have content 1, so this obstruction contributes no
additional conserved sector beyond the total.

An instructive composite counterexample is n=121:

\[
R(121)=-25439104668,\qquad
11^{10}R(1)=25937424601,
\]

and their sum is tau(121)=498319933. These two conserved masses have opposite
signs. Therefore no degree increase in this entire homogeneous-null span can
turn all packets at 121 into a common-sign sum. The obstruction is intrinsic
to that permitted span, not a numerical search failure. The direct content
enumeration and the identities tau(11)=534612 and
tau(121)=tau(11)^2-11^11 give the displayed numbers independently.

## 5. Local arithmetic after primitive extraction

Since tau and the square-supported Mobius factor are multiplicative, R is
multiplicative. At a prime p its formal generating series is

\[
\boxed{
\sum_{r\ge0}R(p^r)X^r
=\frac{1-\chi(p)p^{10}X^2}{1-\tau(p)X+p^{11}X^2}.}
\]

Thus, for r>=2,

\[
R(p^r)=\tau(p^r)-\chi(p)p^{10}\tau(p^{r-2}).
\]

This gives a recurrence variable at a fixed prime. No analytic interpolation
in the prime index is used.

The external arithmetic inputs are the classical Hecke recurrence,
tau(p) congruent to p(1+p) modulo 5, and the parity fact that tau(p) is even
for odd primes. These exact statements were checked in [B]. In particular,
for p!=5,

\[
a:=\tau(p)\equiv p+\chi(p)\pmod5.
\]

## 6. Uniform nonvanishing of the primitive even blocks

**Theorem.** For every prime p and every m>=1,

\[
\boxed{R(p^{2m})\ne0.}
\]

Consequently, by multiplicativity and R(1)=1,

\[
\boxed{R(s^2)\ne0\quad\text{for every integer }s\ge1.}
\]

### Step 1: a residue separates three prime classes

For p!=5, write chi=chi(p). Modulo 5 the Hecke recurrence has sum of roots
p+chi and product p chi, because chi=p^2 mod 5. Hence

\[
\tau(p^r)\equiv C_r:=\sum_{i=0}^r p^{r-i}\chi^i\pmod5.
\]

Also chi p^10=1 mod 5. Since chi^2=1, for r>=2 we obtain

\[
R(p^r)\equiv C_r-C_{r-2}
=p^{r-1}(p+\chi)\pmod5.
\]

This is nonzero whenever p is 1,2 or 3 modulo 5. It handles both even and odd
exponents in these prime classes. Only p=5 and p=4 mod 5 require more work.

### Step 2: valuation separates the ordinary cases

Suppose p=4 mod 5. Then chi=1 and a=0 mod 5. Put b=p^11. The recurrence
T_0=1, T_1=a, T_r=aT_{r-1}-bT_{r-2} has expansion

\[
T_r=\sum_{j=0}^{\lfloor r/2\rfloor}
(-1)^j\binom{r-j}{j}b^j a^{r-2j}.
\]

If a!=0, let t=v_p(a). For t<=4 the first term of T_{2m} has uniquely least
valuation 2mt. The correction p^10 T_{2m-2} has strictly larger valuation.
Thus

\[
v_p(R(p^{2m}))=2mt\quad(t\le4).
\]

If t>=6, the constant-in-a term of T_{2m} has uniquely least valuation 11m.
The correction has valuation 11m-1, so

\[
v_p(R(p^{2m}))=11m-1\quad(t\ge6).
\]

If a=0, direct substitution instead gives the nonzero value

\[
R(p^{2m})=(-1)^m p^{11m-1}(p+1).
\]

These arguments leave only t=5. They have not assumed a!=0 universally.

### Step 3: the tied valuation case

Let a=p^5 u with p not dividing u. Divide T_r by p^{5r}. The normalized
recurrence is

\[
H_0=1,\quad H_1=u,\quad H_r=uH_{r-1}-pH_{r-2}.
\]

If R(p^{2m}) were zero, then

\[
H_{2m}(u)-H_{2m-2}(u)=0.
\]

This is a monic integer polynomial F_m(x) in x=u^2. Its constant coefficient
and reduction modulo p are

\[
F_m(0)=(-1)^m p^{m-1}(p+1),\qquad
F_m(x)\equiv x^{m-1}(x-1)\pmod p.
\]

An integer root x=u^2 divides the constant coefficient. Since p does not divide
u, it follows that x divides p+1. The congruence gives x=1 mod p. Therefore

\[
u^2=1\quad\text{or}\quad u^2=p+1.
\]

The first case is impossible: a is divisible by 5, p is not, so u is divisible
by 5. The second case would factor the prime as
p=(|u|-1)(|u|+1). Its only prime possibility is p=3, excluded by p=4 mod 5.
This closes the tied valuation case for every m, without an exponent bound.

### Step 4: the prime 5

Here chi(5)=0, so R(5^r)=tau(5^r). More generally, for any integer a in the
recurrence, its even terms cannot vanish: if a=0 they equal (-5^11)^m, and
otherwise 2v_5(a) differs from 11. This makes either the first term or the
constant-in-a term uniquely least-valued. For the actual value tau(5)=4830,
v_5(a)=1 and v_5(tau(5^r))=r for every r, including odd r.

All prime cases are covered. In fact, the even-block proof works for any
integer recurrence parameter a with a=p+chi(p) mod 5 when p!=5, and for any
integer a when p=5. The tau values are a specialization. The proof uses no
bound on |tau(p)| and does not assume Lehmer's conjecture.

## 7. Odd blocks preserve the prime obstruction by an odd multiplier

**Theorem.** For an odd prime p!=5 and m>=0, there is an odd integer U_{p,m}
such that

\[
\boxed{R(p^{2m+1})=\tau(p)U_{p,m}.}
\]

The statement defines U by an integer polynomial, so it still makes sense if
tau(p)=0. For nonzero tau(p) it implies the exact valuation law

\[
\boxed{v_2(R(p^{2m+1}))=v_2(\tau(p)).}
\]

Proof. Put a=tau(p), b=p^11, c=chi(p)p^10. The odd recurrence polynomials are
divisible by a. For m>=1 the quotient

\[
\frac{T_{2m+1}-cT_{2m-1}}{a}
\]

is an integer polynomial in a^2 whose constant coefficient is

\[
(-1)^m b^{m-1}\big((m+1)b+mc\big).
\]

Both b and c are odd, so this coefficient is odd. Since a is even, every
other term is even. The quotient is therefore odd. For m=0 take U=1.
The displayed quotient notation means polynomial division before evaluation,
so it does not divide by zero when a=0.

The cases p=2,5 are nonzero at every exponent: p=2 follows from the modulo-5
formula and tau(2)=-24, and p=5 was settled above.

Combining Sections 6 and 7 with multiplicativity gives the exact zero criterion

\[
R(n)=0\quad\Longleftrightarrow\quad
\exists p:\ v_p(n)\text{ is odd and }\tau(p)=0.
\]

The usual Hecke prime-power reduction gives the same criterion for tau(n).
Its proof is recorded in the parent note: a prime-power zero forces the ratio
of the two Hecke roots to be a root of unity, and the rational algebraic integer
tau(p)^2/p^11 can then only be 0,1,2,3 or 4. Primality excludes the nonzero
possibilities except at 2,3, which their explicit tau values exclude.
Therefore

\[
\boxed{R(n)=0\quad\Longleftrightarrow\quad\tau(n)=0.}
\]

The primitive extraction introduces no new zeros. It also does not eliminate
the original prime obstruction, since R(p)=tau(p).

## 8. Why the null polynomials are universal

This section records the external dependency and the project-specific step
needed for all 36 corrections. Write s_j=sum v_i^j and
D=product_{i<j}(v_i-v_j). The symbolic operator is defined by

\[
\Delta_{A_4}(DQ)=D\mathcal L Q,
\]

with

\[
\mathcal Ls_m=m\sum_{a=0}^{m-2}s_as_{m-2-a}
-\frac{m(m-1)}5s_{m-2},\qquad s_0=5,\ s_1=0,
\]

and chain-rule metric

\[
\nabla s_m\cdot\nabla s_n
=mn\left(s_{m+n-2}-s_{m-1}s_{n-1}/5\right).
\]

These formulas follow by differentiating D and restricting to sum v_i=0.
The apparent denominator in the logarithmic derivative cancels pairwise:
(v_i^{m-1}-v_j^{m-1})/(v_i-v_j) is a polynomial. Higher power sums are reduced
using Newton's identities. The implementation uses sparse rational polynomial
arithmetic and a separately written rational linear solver.

For completeness, the lattice is L=sqrt(5) A4. Its discriminant group is
A4*/5A4, of size 3125. In a coset representative a_i+t/5, two coinciding
residues a_i mod 5 imply an odd transposition stabilizer, so that coset
contributes nothing to an alternating theta component. Distinct residues
force t=0. The remaining regular cosets form one free S5 orbit. Their sign
representation has dimension one.

The quadratic form sum a_i^2/10 is integral on a regular coset. Thus T acts
as 1 on this sign line. The Weil representation has even rank and descends to
SL2(Z). It commutes with S5, so the line is invariant. The relation
(ST)^3=S^2 forces S=1 there as well. Hence the harmonic theta series of DQ,
for symmetric homogeneous Q of even degree d, is a scalar full-level cusp
form of weight 12+d. The general harmonic theta statement is checked in [IW].

The constructor solves LQ=0 and kills coefficients 1 through floor((12+d)/12).
The level-one valence formula [S] then forces its theta series to vanish
identically. This is the universal justification for the null identities.
The finite extra shell tests are independent checks of the implementation.

## 9. Audit, limits and next obligation

The new exact run checked 36 symbolic harmonic identities, 88 initial zero
coefficients for the valence argument, and 108 direct second-derivative tests
in four coordinates. Those derivative tests use the metric inverse
I-(1/5)11^T and differentiate DQ directly, providing a different check from
the power-sum operator.

It checked 128 primitive Mobius identities, 5847 content-scaling packets,
6876 content-restricted null sums, 250 coarse ranks, 144 refinement ranks,
and the complete rational two-stage certificate at p=31. Actual prime-power
tests cover all 95 primes through 500 and exponents 2 through 40. Synthetic
tests include 33 nonzero inputs in the exceptional t=5 case and hypothetical
a=0 inputs. The provenance manifest passed its hash and structure validation.

The synthetic zero inputs are an important control. For a=0 at a prime
p=4 mod 5, the used congruence and parity inputs are consistent, every even
primitive block remains nonzero, and every odd block vanishes. Thus the new
theorems themselves cannot prove a!=0. They isolate its role explicitly.

The next arithmetic obligation is still to exclude tau(p)=0 for actual prime
shells. The content transform has removed and classified radial contributions
and shown that its new factors cannot create additional zeros. It supplies
no contradiction at a hypothetical prime zero.

At the geometric level, a possible next claim is that homogeneous null
transfers span all changes preserving the exact-content totals, at sufficiently
high degree. This remains open. Even a proof of that span statement would
still need a nonzero arithmetic residual to finish Lehmer.

## Sources and scope

[H] Guo-Niu Han, *The Nekrasov-Okounkov hook length formula: refinement,
elementary proof, extension and applications*, arXiv:0805.1398v1,
Theorems 1.1 and 1.2. https://arxiv.org/pdf/0805.1398

[B] Jennifer S. Balakrishnan, William Craig and Ken Ono,
*Variations of Lehmer's conjecture for Ramanujan's tau-function*,
arXiv:2005.10345v1. Equation (1.2) supplies the modulo-5 congruence,
Theorem 2.2 supplies the Hecke recurrence and multiplicativity, and the opening
of Section 3 proves the parity criterion using Jacobi's identity.
https://arxiv.org/pdf/2005.10345

[IW] Tomoyoshi Ibukiyama and Brandon Williams,
*Hermitian modular forms and algebraic modular forms on SO(6)*,
arXiv:2505.23497v1, Section 3.4, printed pages 18-19. Only the established
harmonic theta construction is used, not the paper's conjectural correspondences.
https://arxiv.org/pdf/2505.23497

[S] William Stein, *Modular Forms: A Computational Approach*,
chapter Modular Forms of Level 1, Theorem 2.11.
https://wstein.org/books/modform/modform/level_one.html

All relevant passages were checked on 26 September 2026. An alternative
historical PDF link failed to load. It was not used as evidence. The required
congruence was verified in [B]. No global novelty search was performed.
