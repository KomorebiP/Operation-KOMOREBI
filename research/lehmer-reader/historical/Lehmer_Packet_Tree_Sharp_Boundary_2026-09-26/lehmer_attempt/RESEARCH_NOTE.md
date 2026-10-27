# Lehmer packet tree: exact boundaries and the obstruction to local correction

Research checkpoint LEHMER-TREE-SHARP-01, 26 September 2026.

**The original goal is not reached.** This attempt does not prove Lehmer's
conjecture. It proves an exact formula for every dyadic mixed-sign boundary,
and shows why the proposed sector-preserving completion cannot establish
nonvanishing by making all packets have one sign. Proof status is a written
mathematical argument with exact computational checks and self-review.
There is no Lean certificate or claim of historical priority.

## 1. Target and conventions

The target is

\[
\tau(n)\ne0\quad\text{for every integer }n\ge1,
\qquad
\Delta(q)=q\prod_{m\ge1}(1-q^m)^{24}
=\sum_{n\ge1}\tau(n)q^n.
\]

Write

\[
\mathcal V_n=\{v\in\mathbb Z^5:
v_i\equiv i\pmod5,\ \sum_i v_i=0,\ \|v\|^2=10n\},
\qquad W(v)=\frac1{288}\prod_{i<j}(v_i-v_j).
\]

Han's Theorems 1.1 and 1.2, specialized to five-cores and hook parameter 25,
give the classical identity

\[
\tau(n)=\sum_{v\in\mathcal V_n}W(v).
\]

The quotient is an integer by the determinant of binomial polynomials.
All coordinate differences are nonzero since their residues modulo 5 differ.
Define

\[
c_i(v)=(v_i-i)/5,\qquad J(v)_i=-v_{(-i\bmod5)}.
\]

Then J preserves the shell and W. For M=2^k, a sector means the equivalence
class of c(v) modulo M, allowing J. Equivalently its key is the lexicographically
smaller of c(v) mod M and c(J(v)) mod M. A mixed sector contains a positive
and a negative W. All sums in this note include original packet multiplicities.

It is enough to settle prime indices. Here is the reduction, included to fix
the goal exactly. The Hecke recurrence has roots alpha, beta with
alpha+beta=tau(p), alpha beta=p^11. Equal roots would require
tau(p)^2=4p^11, impossible. If tau(p^m)=0, then alpha/beta is a root of unity zeta.
Thus

\[
\frac{\tau(p)^2}{p^{11}}=2+\zeta+\zeta^{-1}
\in\mathbb Q\cap\overline{\mathbb Z}\cap[0,4]
=\{0,1,2,3,4\}.
\]

For p>=5, the odd p-adic valuation of c p^11 for c in {1,2,3,4}
excludes a square. Hence tau(p)=0. For p=2,3 the known values -24 and 252
make tau(p)^2/p^11 nonintegral, so no prime power of either can vanish.
Multiplicativity completes the reduction.

## 2. Audit of the coarse split

For i<j, the sign of v_i-v_j is positive precisely when c_i>c_j.
There are ten pairs, so

\[
\operatorname{sgn}W(v)=(-1)^{\#\{i<j:c_i>c_j\}}.
\]

The number r of odd coordinates is even, and
r=||v||^2 mod 4=2n mod 4. Thus odd n has r=2, and even n has r=0 or 4.
Modulo J the parity patterns consist of one all-even pattern, three patterns
with four odd coordinates, and six with two odd coordinates. These counts
refer to possible patterns, not to the number occupied by a particular shell.

Let A, B, C be the corresponding weighted generating series.
The bijection from the all-even sector is

\[
u_j=v_{2j\bmod5}/2\in\mathcal V_{n/4}.
\]

The coordinate permutation has sign -1. Hence W(v)=-2^10 W(u), proving
A(q)=-2^10 Delta(q^4). The Hecke recurrence at 2 then gives

\[
B(q)=-24\Delta(q^2)-2^{10}\Delta(q^4),
\qquad
C(q)=\Delta(q)+24\Delta(q^2)+2^{11}\Delta(q^4).
\]

The earlier coarse formulas survive the audit. If a symmetric homogeneous Q
of degree d is universally null, scaling similarly gives A_Q=0. Odd and even
support separate C_Q from A_Q+B_Q, so B_Q=C_Q=0 as well.

**This proves nullity for the three aggregate classes A, B, C. It does not
prove nullity inside each of the six finer C parity sectors.**

## 3. Exact first mixed-sign boundary at every depth

**Theorem.** Let k>=1, M=2^k, and define

\[
N_k=\frac{20M^2+2M+\gamma_k}{7},\qquad
\gamma_k=\begin{cases}
7&k\equiv1\pmod3,\\
1&k\equiv2\pmod3,\\
6&k\equiv0\pmod3.
\end{cases}
\]

Every depth-k sector of every shell n<N_k is sign-pure. At n=N_k there is
a mixed sector. Thus N_k is the exact first mixed shell, over all positive
integer indices. The theorem does not assert that N_k is prime.

Equivalently,

\[
N_k=\left\lceil\frac{100M^2+10M+2}{35}\right\rceil.
\]

### Lower bound

Take opposite-sign packets v,w in one sector. Apply J to w if needed so that
w-v=5Md with nonzero d in A4. Put a=5M/2 and m=(v+w)/2. Since k>=1,
a and m are integral. Equal norms give

\[
m\cdot d=0,\qquad
10n=\|m\|^2+a^2\|d\|^2.
\]

The norm ||d||^2 is a positive even integer. It cannot be 2. In that case
d=+/-(e_i-e_j), and m dot d=0 forces v_i-v_j=+/-5M, contrary to
v_i-v_j=i-j mod 5.

If ||d||^2>=6, then

\[
n\ge\frac{15}{4}M^2>
\frac{100M^2+10M+2}{35}\quad(M\ge2).
\]

It remains to consider ||d||^2=4. Such d has two entries 1, two entries -1,
and one entry 0. Of its ten coordinate pairs, eight have unequal d entries.
For such a pair set delta=d_i-d_j. Its contribution to D(v)D(w) is

\[
(m_i-m_j)^2-a^2\delta^2.
\]

The two pairs with equal d entries have strictly positive contributions.
If all eight unequal pairs contributed negatively, D(v)D(w) would be positive.
Since v,w have opposite signs, at least one unequal pair contributes positively.
Its integral coordinate difference satisfies

\[
|m_i-m_j|\ge a|\delta|+1.
\]

Project e_i-e_j orthogonally to d-perp. Its squared norm is
2-delta^2/4. Since m is orthogonal to d, Cauchy gives

\[
\|m\|^2\ge
\frac{(a|\delta|+1)^2}{2-\delta^2/4}.
\]

For |delta|=1 this is 4(a+1)^2/7. For |delta|=2 it is (2a+1)^2,
which is larger. Therefore

\[
10n\ge4a^2+\frac47(a+1)^2,
\qquad
n\ge\frac{100M^2+10M+2}{35}.
\]

Taking the ceiling proves the lower bound. For powers of 2, M mod 7 cycles
through 2,4,1. Direct integer division gives the stated values of gamma_k.

### Attaining the lower bound

For k=1 take

\[
v=(-5,-4,2,-2,9),\qquad w=(5,6,-8,-2,-1).
\]

They lie in V_13, have opposite weights, and w-v is divisible coordinatewise
by 10.

For the remaining k the following table specifies 7v and 7w. Every row has
sum zero and squared norm 490 N_k before division by 49. Each vector has
the required coordinate residues after division by 7.

| k mod 3 | Range | 7v | 7w |
|---|---|---|---|
| 1 | k>=4 | (-20M+5, -10M-8, -10M-1, 20M+16, 20M-12) | (15M+5, -10M-8, 25M-1, -15M+16, -15M-12) |
| 2 | k>=2 | (-25M-5, 10M+2, -15M+4, 15M-4, 15M+3) | (10M-5, 10M+2, 20M+4, -20M-4, -20M+3) |
| 0 | k>=3 | (-20M-15, 10M-3, 10M+4, 20M+1, -20M+13) | (15M-15, -25M-3, 10M+4, -15M+1, 15M+13) |

In the first two rows (w-v)/(5M)=(1,0,1,-1,-1). In the last it is
(1,-1,0,-1,1). All coordinate differences are affine functions of M.
Their signs are constant on the displayed ranges, and the two Vandermonde
products have opposite signs. The verification script checks these statements
as coefficient identities and linear inequalities valid for every real M
above the row's minimum, rather than inferring them from sampled powers.

For clarity, the coefficient identities used are

\[
\sum_i(7v_i)^2=\sum_i(7w_i)^2
=1400M^2+140M+70\gamma_k=490N_k.
\]

This completes the all-depth proof.

| k | N_k |
|---:|---:|
| 1 | 13 |
| 2 | 47 |
| 3 | 186 |
| 4 | 737 |
| 5 | 2935 |
| 6 | 11722 |
| 7 | 46849 |
| 8 | 187319 |

The earlier bound n<(5/2)4^k remains a sufficient bound for separation of
distinct J-orbits. The new bound concerns signs and is sharper for that purpose.
Sign-purity and uniqueness of an orbit are different statements.

## 4. The proposed local completion fails

Let a finite shell be partitioned into sectors S_r. Define its sector mass

\[
t_r=\sum_{v\in S_r}W(v).
\]

**Conservation obstruction.** Suppose every allowed correction satisfies

\[
\sum_{v\in S_r}W(v)Q_j(v)=0
\quad\text{for every sector }r.
\]

Then any F=1+sum a_j Q_j leaves the corrected sector mass equal to t_r.
If two t_r have opposite nonzero signs, no such correction can make all
corrected packets have one weak sign. This follows immediately by summing
that putative sign condition within each of the two sectors.

This obstruction occurs already at p=7 and depth 1.

| Sector key c mod 2, modulo J | Packet count | t_r | sum W Q8 in sector |
|---|---:|---:|---:|
| (0,0,0,0,0) | 2 | -1848 | -67060224000000 |
| (1,0,0,1,0) | 2 | -17248 | 65383718400000 |
| (1,1,0,0,0) | 2 | 2352 | 1676505600000 |

The three Q8 sums add to zero, but none is individually zero. Thus the global
null correction Q8 does not remain null when simply restricted to each parity
sector. The earlier p=7 elimination works by transferring signed mass between
these sectors. It cannot be implemented by corrections preserving them all.

At sufficient depth each sector is a single J-orbit. For a J-invariant Q,
sector nullity then forces Q(v)=0 at every packet, because the orbit weight
is |orbit| W(v), which is nonzero. Without J-invariance the individual values
may change, but their orbit sum is still fixed, so the sign obstruction remains.

More generally, the spaces of corrections null in every depth-k sector are
nested downward with k. Refinement adds constraints. A J-invariant function
that is sector-null at every depth, on every shell, vanishes on every packet.

This is not a refutation of arbitrary tree-based methods. It excludes the
specific finishing argument that first separates signs and then uses only
sector-preserving corrections to make their global sum one-signed.

## 5. Two further attempts at the remaining arithmetic step

### A. A unique lowest valuation after resolution

If one sector mass has strictly smaller ell-adic valuation than all the others,
then the sum is nonzero. This is a valid sufficient criterion. However,
resolution does not ensure its hypothesis.

Every W(v) is 1 modulo 5. Indeed, its Vandermonde numerator has the same
residue as the product of i-j, namely 288, and 288 is a unit modulo 5.
Thus every fully resolved orbit mass |orbit| W(v), with orbit size 1 or 2,
is a 5-adic unit. If there is more than one orbit, there is no unique minimum.

For an index prime p>20, every W(v) is also a p-adic unit. For any pair,

\[
0<|v_i-v_j|\le\sqrt{20p}<p,
\]

and p does not divide 288. Orbit multiplicities 1 and 2 are p-adic units too.
Thus terminal refinement supplies no unique least p-adic packet either.

At p=31, depth 2 already resolves all 16 J-orbits. Eight have positive mass
and eight have negative mass. Four have the minimum 2-adic valuation 3.
At depth 1 there are two masses at that minimum. Therefore the unique-minimum
test fails at every positive depth for ell=2 in this example as well.
The total tau(31)=-52843168 is nevertheless nonzero, with 2-adic valuation 5.

This closes the proposed automatic unique-minimum mechanism. It does not
exclude using additional residue information about sums of the tied terms.
The earlier prime-index interpolation failure remains relevant to that route.

### B. Completeness of global null corrections

Allowing mass transfer between sectors avoids the conservation obstruction.
But merely enlarging the space of permissible zero-sum transfers does not
force nonvanishing.

On one shell write its nonzero packet or orbit masses as w_1,...,w_N and
T=sum w_i. Even allow **every** rational correction vector q satisfying
sum w_i q_i=0. Then

\[
\exists q:\ w_i(1+q_i)\text{ have one weak sign and are not all zero}
\quad\Longleftrightarrow\quad T\ne0.
\]

The forward implication is conservation. For the reverse implication take

\[
q_i=\frac{T}{Nw_i}-1.
\]

All corrected masses are T/N and the weighted correction sums to zero.
This is an exact equivalence, not a nonvanishing proof. It shows why a
completeness theorem for correction vectors would still need arithmetic input
to exclude T=0.

If T=0, the positive numbers y_i=|w_i|/sum |w_j| supply a persistent dual:
for every weighted-null q,

\[
\sum_i y_i\operatorname{sgn}(w_i)(1+q_i)=0.
\]

Such a dual cannot be removed by additional valid null corrections. This
distinguishes a removable obstruction from an actually zero target sum.
The finite p=31 dual in the older correction span was removable, but that
example supplies no theorem that every positive dual is removable.

## 6. Verification and limits

The verifier uses exact Python integers and rational Fractions only.
The shell enumerator solves the last two coordinates by their sum and square
sum. Its completeness follows from solving that quadratic. A separate
four-coordinate enumerator agrees through n=32. The weighted shell sum agrees
with a Jacobi recurrence through all n<=512 and at n=737,2411. The recurrence
also agrees with a direct expansion of the defining product through n=512.

The run verifies parity formulas, the Q8 aggregate null sums, the involution,
the inversion-parity sign, all depths 1 through 6 in the tested shells, the
p=7 restriction counterexample, and boundary witnesses through k=64.
The three witness families additionally have exact symbolic coefficient and
linear-sign certificates. The universal lower bound is the proof in Section 3.

The first exploratory script could not import SymPy in either available Python
runtime. It was rewritten using rational 3 by 3 matrix algebra from the standard
library. Those environment failures did not produce mathematical evidence.
They are recorded separately in FAILURES.md.

The global modularity proof for all fourteen older harmonic corrections was
not re-audited in this block. None of the new obstruction theorems needs it.
The coarse Q8 identities were checked finitely here and their universal version
remains the prior archive's result.

## 7. Current research state

The sharp split theorem answers the geometric question at every depth.
It does not imply that the positive and negative total masses differ.

The strict sector-preserving sign-correction route is refuted by p=7.
The automatic unique-lowest-valuation route is refuted in its proposed form.
Completeness of global weighted-null corrections would not by itself prove
nonvanishing, as Section 5B shows.

What remains necessary for a Lehmer proof is a uniform arithmetic constraint
on the signed total. One possible form is a residue certificate, with precision
depending on p, that cannot vanish for an actual prime shell. Another is a
construction of intersector corrections with an independently proved nonzero
sign margin. Neither has been established here.

The broader arithmetic and intersector routes remain open. No increasing
finite test range, sharper separation threshold, or unproved correction-space
completeness is being substituted for this missing implication.

## Sources checked

1. Guo-Niu Han, *The Nekrasov-Okounkov hook length formula: refinement,
   elementary proof, extension and applications*, arXiv:0805.1398v1,
   9 May 2008, Theorems 1.1 and 1.2, printed page 3.
   https://arxiv.org/pdf/0805.1398
   The normalization |lambda|=||v||^2/10-1 and prefactor 1/288 were checked.
2. Jennifer S. Balakrishnan, William Craig, Ken Ono,
   *Variations of Lehmer's conjecture for Ramanujan's tau-function*,
   arXiv:2005.10345, Theorem 2.2 in the retrieved nine-page PDF.
   https://arxiv.org/pdf/2005.10345
   Used for the explicitly stated Hecke recurrence and multiplicativity.
3. The parent archive is pinned by SHA-256 in BASE.json. The subsequent split
   discussion was supplied in the current conversation. Its displayed numbers
   were treated as claims to check, not as a substitute for proof or source code.

Source checks took place on 26 September 2026. No broad novelty search was
performed for the sharp boundary formula. No originality claim follows from
its derivation in this attempt.
