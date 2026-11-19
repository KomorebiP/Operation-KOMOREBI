# Finite-order differential Hankel calculus

Author: Komorebi P.  
Research date: 19 November 2026.  
Status: Written algebraic derivation and exact computational verification.  
Historical novelty and priority: unassessed.

This note extends [Polynomial-weighted Hankel structure](POLYNOMIAL_HANKEL_STRUCTURE.md) from \(1+c\partial_x\) to **arbitrary finite-order constant-coefficient differential operators**. The rank theorem is uniform in determinant size \(N\), but depends on the polynomial degree \(D\) and operator order \(r\).

## 1. Moments and operator

Let \(P(m)=\sum_{d=0}^{D}a_dm^{\underline d}\) and define the characteristic-zero linear functional

\[
F_P[x^{2m}]=P(m)\binom{2m}{m},\qquad
F_P[x^{2m+1}]=0.
\]

Let \(\mathcal D=\sum_{k=0}^r c_k\partial_x^k\), with no requirement that \(c_0=1\). Set

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

The moment sequence has a second universal representation that is independent of taking Hankel determinants. Put \(h(z)=1-4z^2\) and \(D=\deg P\). The original unperturbed even moments have the generating function

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

Define the formal operator \(\mathscr T f=z\frac{d}{dz}(zf)=z(f+zf')\). Its \(k\)-fold iterate has coefficient identity

\[
[z^n]\mathscr T^kM_P(z)
=n^{\underline k}F_P[x^{n-k}].
\]

Thus the perturbed moment generating function is

\[
M_{P,\mathbf c}(z)=\sum_{n\ge0}\mu_nz^n
=\sum_{k=0}^r c_k\mathscr T^kM_P(z).
\]

**Theorem 1A (algebraic moment generating functions).** For every polynomial \(P\) of degree \(D\) and every finite constant-coefficient differential operator of order \(r\),

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

Consequently the moments satisfy a finite-width recurrence with polynomial coefficients in the index. If \(R(0)=0\), the leading coefficient of that recurrence can vanish at the initial indices, so it must be interpreted with the exact initial moments rather than divided through blindly. No assertion is made that the **Hankel determinant sequence** of an arbitrary polynomial \(P\) has a rational generating function.

For the worked example \(P(m)=1+m\) and \(\mathcal D=1+2\partial_x+\partial_x^2\),

\[
\boxed{
M(z)=\frac{1+2z-8z^2-4z^3+52z^4-16z^5-24z^6}
{(1-4z^2)^{7/2}}.
}
\]

The exact moment sequence begins \(1,2,6,24,66,180,620,1120,4830,6300,\ldots\). The construction was independently checked against the finite monomial definition using rational arithmetic, including exceptional zeros and rational parameter choices.

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

Both parity selectors are linear combinations of \(1\) and \((-1)^i(-1)^j\). Hence each separated block column belongs to the span of

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

The first nonzero Hankel matrix is anti-triangular. Therefore

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

\`\`\`bash
python -B -m unittest discover -s tools -p 'test_sequence_differential_hankel.py' -v
python -B tools/sequence_differential_hankel.py
\`\`\`

The browser’s unified **higher-order differential Hankel** calculator supports falling-factorial weights of degree at most three, operators of order at most three, integer parameters, and determinants up to size 12. It uses exact BigInt moment sums and fraction-free determinants. The mathematical rank theorem is not limited by those user-interface bounds.

The Python tests compare direct monomial calculations, Chebyshev derivatives, quasiseparable generators, exact matrix ranks, leading singular blocks, binomial-shift invariance, first-order specialization, and longer structured determinant prefixes. These tests substantiate the implementation but are not a Lean formalization or a historical-priority assessment. Existing sequence counts, archived integer records, and pinned OEIS receipts are unchanged.
