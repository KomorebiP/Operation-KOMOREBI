# Finite-order differential Hankel calculus

Author: Komorebi P.  
Research date: 19 November 2026.  
Status: Written algebraic derivation and exact computational verification.  
Historical novelty and priority: unassessed.

This note extends [Polynomial-weighted Hankel structure](POLYNOMIAL_HANKEL_STRUCTURE.md) from \(1+c\partial_x\) to **arbitrary finite-order constant-coefficient differential operators**. The rank theorem is uniform in determinant size \(N\), but depends on the polynomial degree \(D\) and operator order \(r\).

## 1. Moments and operator

Let \(D\ge0\) be an integer and \(P(m)=\sum_{d=0}^{D}a_dm^{\underline d}\). Define the linear functional over a characteristic-zero field by

\[
F_P[x^{2m}]=P(m)\binom{2m}{m},\qquad
F_P[x^{2m+1}]=0.
\]

Write \(F_d\) for the special case \(P(m)=m^{\underline d}\), so \(F_P=\sum_{d=0}^{D}a_dF_d\).

Let \(r\ge0\) be an integer and \(\mathcal D=\sum_{k=0}^r c_k\partial_x^k\), with no requirement that \(c_0=1\). The nonnegative integers \(D\) and \(r\) are degree and order bounds. For nonzero inputs they may be chosen to equal the actual degree and order; zero inputs are also allowed. Set

\[
L[f]=F_P[\mathcal D f],\qquad
W_N=\det[L[x^{i+j}]]_{0\le i,j<N},\qquad W_0=1.
\]

The moments are the finite sums

\[
\boxed{\mu_n=\sum_{\substack{0\le k\le\min(r,n)\\n-k\ {\rm even}}}
c_k n^{\underline k}
P\!\left(\frac{n-k}{2}\right)
\binom{n-k}{(n-k)/2}.}
\]

This formula includes every parity and zero-weight boundary. Shifting from \(x^i\) to \((x+\lambda)^i\) is a unitriangular basis change, so every \(W_N\) is independent of the binomial shift \(\lambda\).

### Algebraic ordinary generating function for every finite differential operator

The moment sequence has a second universal representation that is independent of taking Hankel determinants. Put \(h(z)=1-4z^2\). The original unperturbed even moments have the generating function

\[
M_P(z)=\sum_{m\ge0}P(m)\binom{2m}{m}z^{2m}
=\sum_{d=0}^{D}a_d\frac{(2d)!}{d!}
\frac{z^{2d}}{h(z)^{d+1/2}}
=\frac{R_0(z)}{h(z)^{D+1/2}},
\]

where the explicit polynomial

\[
R_0(z)=\sum_{d=0}^{D}a_d\frac{(2d)!}{d!}
z^{2d}h(z)^{D-d}
\]

has degree at most \(2D\).

Define the formal operator \(\mathscr T f=z\frac{d}{dz}(zf)=z(f+zf')\). Its \(k\)-fold iterate has the coefficient identity

\[
[z^n]\mathscr T^kM_P(z)
=n^{\underline k}F_P[x^{n-k}],\qquad n\ge k.
\]

For \(0\le n<k\), the coefficient is zero. Thus the perturbed moment generating function is

\[
M_{P,\mathbf c}(z)=\sum_{n\ge0}\mu_nz^n
=\sum_{k=0}^r c_k\mathscr T^kM_P(z).
\]

**Theorem 1A (algebraic moment generating functions).** For every polynomial \(P\) of degree at most \(D\) and every finite constant-coefficient differential operator of order at most \(r\),

\[
\boxed{
M_{P,\mathbf c}(z)=
\frac{R_{P,\mathbf c}(z)}
{(1-4z^2)^{D+r+1/2}},
\qquad
\deg R_{P,\mathbf c}\le2(D+r).
}
\]

Both the numerator and an exact first-order differential equation are obtained by finite polynomial arithmetic. Starting from \(R_0\) above, define

\[
R_{k+1}(z)=
z h(z)\bigl(R_k(z)+zR_k'(z)\bigr)
+4(2D+2k+1)z^3R_k(z)
\quad(0\le k<r),
\]

and assemble

\[
\boxed{
R_{P,\mathbf c}(z)=
\sum_{k=0}^r c_kR_k(z)h(z)^{r-k}.
}
\]

To prove the degree bound, suppose \(\deg R_k\le2(D+k)\). A coefficient \(b_jz^j\) of \(R_k\) contributes \((j+1)b_jz^{j+1}\) and \(4(2D+2k-j)b_jz^{j+3}\) to \(R_{k+1}\). The second contribution vanishes for \(j=2(D+k)\), so \(\deg R_{k+1}\le2(D+k+1)\). Multiplication by \(h^{r-k}\) gives the asserted common bound. This proves the theorem by formal differentiation, including zero weights and missing identity terms.

Writing \(\beta=D+r+1/2\), the same representation implies the exact differential equation

\[
\boxed{
h(z)R(z)M'(z)=
\bigl[h(z)R'(z)+8\beta zR(z)\bigr]M(z),
\qquad R=R_{P,\mathbf c}.
}
\]

Consequently the moments satisfy a finite-width recurrence with polynomial coefficients in the index. If \(R(0)=0\), the leading coefficient of that recurrence can vanish at the initial indices, so it must be interpreted with the exact initial moments rather than divided through blindly.

This moment derivation alone does not prove rationality of the **Hankel
determinant sequence**. The subsequent [rational Hankel theorem](RATIONAL_HANKEL_TAILS.md)
establishes that separate result for every fixed polynomial weight and finite
constant-coefficient differential operator, including singular minors.

### Removing singular starts: a universal forward recurrence

A stronger computational consequence follows from the known initial zero block. If \(P\not\equiv0\) and \(\mathcal D\not\equiv0\), let \(\nu\) and \(\kappa\) be the least indices with \(a_\nu\ne0\) and \(c_\kappa\ne0\). Put \(\ell=2\nu+\kappa\). The first nonzero moment is

\[
\mu_\ell=c_\kappa a_\nu\frac{\ell!}{\nu!}\ne0.
\]

Because the denominator of \(M(z)\) equals \(1\) at \(z=0\), the algebraic numerator has an exact factor \(R(z)=z^\ell\widetilde R(z)\) with \(\widetilde R(0)=\mu_\ell\). Define the shifted moment series

\[
T(z)=z^{-\ell}M(z)=\frac{\widetilde R(z)}
{h(z)^{D+r+1/2}}
=\sum_{n\ge0}t_nz^n,
\qquad t_n=\mu_{n+\ell}.
\]

Put \(\alpha=D+r+1/2\), and form the explicit polynomials

\[
A(z)=h(z)\widetilde R(z),\qquad
B(z)=h(z)\widetilde R'(z)+8\alpha z\widetilde R(z).
\]

Then \(A(z)T'(z)=B(z)T(z)\), and \(A(0)=t_0=\mu_\ell\ne0\).

**Theorem 1B (regularized polynomial-coefficient recurrence).** Writing \(A(z)=\sum_j A_jz^j\), \(B(z)=\sum_jB_jz^j\), the complete infinite tail of moments is determined by the one nonzero initial value \(t_0=\mu_\ell\) and

\[
\boxed{
t_{n+1}=
\frac{\displaystyle\sum_{j=0}^{\deg B}B_jt_{n-j}
-\displaystyle\sum_{j=1}^{\deg A}A_j(n-j+1)t_{n-j+1}}
{(n+1)A_0},
\qquad n\ge0,
}
\]

where \(t_j=0\) for \(j<0\). No denominator vanishes in characteristic zero. Moreover,

\[
\boxed{\deg A\le 2(D+r)-\ell+2.}
\]

This is a finite-width, polynomial-coefficient recurrence, not generally a constant-coefficient recurrence for the Hankel determinants. It is valid for rational, complex, and other characteristic-zero parameters. If the moment sequence is identically zero, the zero formula is handled separately without an artificial division by \(A_0=0\).

The recurrence follows simply by comparing coefficients in \(AT'=BT\). Its zero-prefix removal is essential: without it, a recurrence derived from the unreduced numerator can have an unusable zero leading coefficient. The exact implementation preserves the original \(\ell\) and reconstructs every \(\mu_n\), including all initial zeros.

For the worked example \(P(m)=1+m\) and \(\mathcal D=1+2\partial_x+\partial_x^2\),

\[
\boxed{
M(z)=\frac{1+2z-8z^2-4z^3+52z^4-16z^5-24z^6}
{(1-4z^2)^{7/2}}.
}
\]

The exact moment sequence begins \(1,2,6,24,66,180,620,1120,4830,6300,\ldots\). The construction was independently checked against the finite monomial definition using rational arithmetic, including exceptional zeros and rational parameter choices.

### Two explicit polynomials for every even and odd moment

The same moments admit a simpler direct formula when the two parities are
separated. For \(\varepsilon\in\{0,1\}\), define the ordinary polynomial

\[
Q_\varepsilon(t)=
\sum_{\substack{s\ge0\\2s+\varepsilon\le r}}
c_{2s+\varepsilon}\bigl(t^{\underline s}\bigr)^2P(t-s).
\]

An empty sum is zero. Here \(t^{\underline0}=1\), and every shifted value
\(P(t-s)\) is a polynomial
evaluation, including when \(t-s\) is negative. These \(Q_0,Q_1\) are distinct
from the Chebyshev transform polynomials \(E,O\) used in Section 3.

**Theorem 1C (polynomial parity formulas).** For every integer \(m\ge0\),

\[
\boxed{
\mu_{2m}=\binom{2m}{m}Q_0(m),\qquad
\mu_{2m+1}=(2m+1)\binom{2m}{m}Q_1(m).
}
\]

This identity holds over the same characteristic-zero field as the original
functional, including zero weights, zero operators, and missing parity terms.
If all \(a_d,c_k\) are integers, both \(Q_\varepsilon\) have integer
coefficients. After constructing the two polynomials, each moment requires one
binomial coefficient and one polynomial evaluation, without computing earlier
moments.

**Proof.** In a moment of index \(2m+\varepsilon\), the only possible
derivative orders are \(2s+\varepsilon\). For \(0\le s\le m\), cancellation
of factorials gives

\[
(2m+\varepsilon)^{\underline{2s+\varepsilon}}
\binom{2m-2s}{m-s}
=(2m+1)^\varepsilon\binom{2m}{m}
\bigl(m^{\underline s}\bigr)^2.
\]

Multiply by \(c_{2s+\varepsilon}P(m-s)\) and sum. When \(s>m\), the derivative
order exceeds the monomial degree, while \(m^{\underline s}=0\). Thus the
additional polynomial terms vanish and the formula remains valid at every
initial index. No factorial or binomial coefficient with a negative argument
is used.

Suppose now that \(P\ne0\), write \(d_P=\deg P\), and suppose the chosen parity
has at least one nonzero derivative coefficient. Set

\[
s_\varepsilon=\max\{s\ge0:2s+\varepsilon\le r,
c_{2s+\varepsilon}\ne0\}.
\]

The summand with index \(s\) has degree \(d_P+2s\) and leading coefficient
\(a_{d_P}c_{2s+\varepsilon}\) when that coefficient is nonzero. The highest
degree occurs in exactly one summand. Consequently

\[
\boxed{
\deg Q_\varepsilon=d_P+2s_\varepsilon,\qquad
[t^{d_P+2s_\varepsilon}]Q_\varepsilon(t)
=a_{d_P}c_{2s_\varepsilon+\varepsilon}\ne0.
}
\]

The binomial and parity factors in Theorem 1C are nonzero in characteristic
zero. The zero moments in a nonzero parity therefore correspond exactly to
the nonnegative integer roots of its polynomial. There are at most
\(d_P+2s_\varepsilon\) such positions. If \(P=0\), both parity polynomials
vanish. If \(P\ne0\), a parity vanishes identically exactly when all derivative
coefficients of that parity are zero.

The binomial ratio also gives a first-order recurrence within each parity.
For every \(m\ge0\) and \(\varepsilon\in\{0,1\}\),

\[
\boxed{
(m+1)Q_\varepsilon(m)\mu_{2m+2+\varepsilon}
=2(2m+2\varepsilon+1)Q_\varepsilon(m+1)\mu_{2m+\varepsilon}.
}
\]

The identity includes polynomial zeros, but solving it for the next moment
requires \(Q_\varepsilon(m)\ne0\). At a root it can reduce to \(0=0\) and
does not by itself determine the next value. The direct polynomial formula
still applies there, and Theorem 1B supplies the earlier universally defined
forward recurrence.

For \(P(m)=1+m\) and \(\mathcal D=1+2\partial_x+\partial_x^2\), these
polynomials are

\[
Q_0(m)=m^3+m+1,\qquad Q_1(m)=2m+2.
\]

They reproduce the worked moment sequence above. As a separate boundary
example, \(P(m)=m-2\) and \(\mathcal D=1+\partial_x\) give
\(Q_0(m)=Q_1(m)=m-2\). Each parity has an isolated zero at \(m=2\), followed
by nonzero moments, illustrating why division at a polynomial root is invalid.

## 2. Exact Chebyshev derivative products

Let \(C_n(x)=2T_n(x/2)\), with \(C_0=2,C_1=x\), and \(C_{n+1}=xC_n-C_{n-1}\). For \(k\ge1,n\ge k\),

\[
C_n^{(k)}(x)=n(k-1)!\,
\mathsf C_{n-k}^{(k)}(x/2),
\]

where \(\mathsf C^{(k)}\) denotes Gegenbauer polynomials. The arcsine functional \(F_0\) averages at \(x=2\cos\theta\). Factoring the Gegenbauer generating function,

\[
(1-2z\cos\theta+z^2)^{-k}
=(1-ze^{i\theta})^{-k}(1-ze^{-i\theta})^{-k},
\]

and integrating eliminates unequal Fourier powers. Consequently, for \(n\ge k\) and \(n\equiv k\bmod2\),

\[
\boxed{
F_0[C_n^{(k)}]
=n(k-1)!
\binom{(n+k-2)/2}{k-1}^{2}.
}
\]

For mismatched parity or \(n<k\) the result is zero. The exceptional unperturbed term is \(F_0[C_0]=2\), while \(F_0[C_n]=0\) for positive \(n\).

**Theorem 1 (weight-raising ladder).** Whenever \(d+k>0\),

\[
\boxed{
F_{d+1}[C_n^{(k)}]
=\frac{n^2-(k+2d)^2}{4(d+k)}
F_d[C_n^{(k)}].
}
\]

To prove it, check on monomials and extend linearly the exact functional identities

\[
F_{d+1}[f]=\tfrac12F_d[xf']-dF_d[f],\qquad
F_d[(4-x^2)f']=(1-2d)F_d[xf].
\]

Differentiating the Chebyshev ODE \(k\) times gives

\[
(4-x^2)C_n^{(k+2)}
-(2k+1)xC_n^{(k+1)}
+(n^2-k^2)C_n^{(k)}=0.
\]

Apply \(F_d\) and the second functional identity:

\[
2(d+k)F_d[xC_n^{(k+1)}]
=(n^2-k^2)F_d[C_n^{(k)}].
\]

Substitute into the first identity and simplify to obtain the boxed ladder. The excluded \(d=k=0\) endpoint is handled separately.

For \(k\ge1\), this gives the explicit product

\[
F_d[C_n^{(k)}]
=F_0[C_n^{(k)}]
\prod_{j=0}^{d-1}
\frac{n^2-(k+2j)^2}{4(k+j)}.
\]

For \(k=0,d\ge1\) and positive even \(n\),

\[
F_d[C_n]
=\frac{n}{4^{d-1}(d-1)!}
\prod_{j=1}^{d-1}(n^2-4j^2).
\]

Thus, at the matching parity and positive Chebyshev index, each transform is an **odd polynomial in the index** with degree at most \(2(d+k)-1\). The exact source code stores coefficients of the polynomial rather than evaluating roots.

## 3. Uniform quasiseparable rank

Let \(G_{ij}=L[C_iC_j]\). The identity

\[
C_iC_j=C_{i+j}+C_{|i-j|}
\]

holds also at the \(C_0=2\) endpoint. Define odd polynomials \(E,O\) from the preceding transforms by collecting respectively even and odd derivative orders, weighted by \(a_d c_k\). Their degrees are at most \(2(D+r)-1\).

For strictly separated indices \(i>j\),

\[
G_{ij}=
\begin{cases}
E(i+j)+E(i-j),& i-j\ {\rm even},\\
O(i+j)+O(i-j),& i-j\ {\rm odd}.
\end{cases}
\]

**Theorem 2.** For any separated index sets \(I,J\) with \(\min I>\max J\),

\[
\boxed{\operatorname{rank}G_{I,J}\le2(D+r).}
\]

**Proof.** For any odd monomial \(t^{2h+1}\),

\[
(i+j)^{2h+1}+(i-j)^{2h+1}
=2\sum_{\ell=0}^{h}\binom{2h+1}{2\ell}
i^{2h+1-2\ell}j^{2\ell}.
\]

Both parity selectors are linear combinations of \(1\) and \((-1)^i(-1)^j\). Hence each separated block row belongs to the span of

\[
1,j^2,\ldots,j^{2(D+r-1)}
\quad\text{and}\quad
(-1)^j,(-1)^jj^2,\ldots,(-1)^jj^{2(D+r-1)},
\]

a space of dimension \(2(D+r)\). If \(D=r=0\), all separated off-diagonal entries vanish. This is a rank bound on **separated blocks**, not on the entire matrix.

Writing \(E(t)=\sum_h e_ht^{2h+1}\), \(O(t)=\sum_h o_ht^{2h+1}\) gives explicit row generators. Let \(M=D+r\) and

\[
A_\ell(i)=2\sum_{h=\ell}^{M-1}e_h\binom{2h+1}{2\ell}i^{2h+1-2\ell},
\quad
B_\ell(i)=2\sum_{h=\ell}^{M-1}o_h\binom{2h+1}{2\ell}i^{2h+1-2\ell}.
\]

With \(\epsilon_i=(-1)^i\),

\[
u_i=\left(\frac{A_\ell(i)+B_\ell(i)}2,
\frac{\epsilon_i(A_\ell(i)-B_\ell(i))}2\right)_{\ell=0}^{M-1},
\]

\[
v_j=(j^{2\ell},\epsilon_jj^{2\ell})_{\ell=0}^{M-1}.
\]

The components are concatenated by parity, and \(G_{ij}=u_i^\mathsf Tv_j\) for \(i>j\). The diagonal is

\[
G_{00}=4c_0P(0),\qquad
G_{ii}=2c_0P(0)+E(2i)\quad(i\ge1).
\]

## 4. Initial singular blocks and exact computation

Assume \(P\not\equiv0\) and \(\mathcal D\not\equiv0\), and let \(\nu\) and \(\kappa\) be the least indices for which \(a_\nu\) and \(c_\kappa\) are nonzero. Set \(\ell=2\nu+\kappa\). Then

\[
\boxed{\mu_n=0\ (n<\ell),\qquad
\mu_\ell=c_\kappa a_\nu\frac{\ell!}{\nu!}.}
\]

The first nonsingular leading Hankel matrix is anti-triangular. Therefore

\[
\boxed{
W_N=0\ (1\le N\le\ell),\qquad
W_{\ell+1}=(-1)^{\ell(\ell+1)/2}\mu_\ell^{\ell+1}.
}
\]

This includes differential operators with \(c_0=0\), not only perturbations of the identity.

Since the Chebyshev change of basis has determinant \(2\),

\[
\det G_N=4W_N\quad(N\ge1).
\]

The exact structured solver maintains a Schur state of width \(2(D+r)\) and uses exact block lookahead when a scalar leading Schur pivot is zero. Ordinary nonsingular updates require \(O((D+r)^2)\) rational operations each, following finite initialization. An uninterrupted nonsingular scalar run costs \(O((D+r)^3+N(D+r)^2)\) arithmetic operations, excluding generator construction and integer bit growth. Exceptional long lookahead blocks can increase the cost, so this is **not an unconditional worst-case bit-complexity claim**.

Reflection \(x\mapsto-x\) simultaneously reverses all odd derivative coefficients without changing \(W_N\):

\[
W_N(P;c_0,-c_1,c_2,-c_3,\ldots)
=W_N(P;c_0,c_1,c_2,c_3,\ldots).
\]

This does not imply independent evenness in each odd coefficient.

## 5. Executable scope and evidence

The mathematical identities apply over characteristic-zero fields. The standard-library Python solver evaluates rational weights and rational operator coefficients exactly:

```bash
python -B -m unittest discover -s tools -p 'test_sequence_differential_hankel.py' -v
python -B tools/sequence_differential_hankel.py
```

The browser’s unified **higher-order differential Hankel** calculator supports falling-factorial weights of degree at most three, operators of order at most three, integer parameters from \(-12\) to \(12\), and determinants up to size \(64\). It displays at most \(32\) consecutive values at a time. Exact rational arithmetic built from BigInt implements the Chebyshev–Schur solver, including initial zero blocks and later singular-pivot lookahead. Every calculation is independently checked against direct moment sums and fraction-free determinants through size \(12\), or through its last requested size if smaller. The mathematical rank theorem is not limited by those interface bounds.

The Python tests compare direct monomial calculations, parity polynomials,
their exact degrees and parity recurrences, Chebyshev derivatives,
quasiseparable generators, exact matrix ranks, leading singular blocks,
binomial-shift invariance, first-order specialization, and longer structured
determinant prefixes. The parity comparisons include rational parameters,
absent parities, initial zeros, and isolated zeros. These tests substantiate
the implementation but are not a Lean formalization or a historical-priority
assessment. Existing sequence counts, archived integer records, and pinned
OEIS receipts are unchanged.
