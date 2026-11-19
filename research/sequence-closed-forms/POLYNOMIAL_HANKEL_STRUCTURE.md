# Polynomial-weighted Hankel determinants: Chebyshev transforms and bounded-rank structure

Author: Komorebi P.  
Date: 19 November 2026.  
Scope: exact algebraic identities, constructive matrix factorization, and a reproducible rational-arithmetic algorithm.  
Historical priority: not assessed.

This continuation generalizes the special falling-factorial moments in Closed Forms Collections II and III. It does **not** claim that an arbitrary linear combination of their individual Hankel determinants is another determinant: determinants are nonlinear. Instead, it constructs the moment matrix itself for **every polynomial weight** and proves that every separated off-diagonal block has uniformly bounded rank.

The structural formula is independent of numerical experiments. The exact tests compare it against separately generated Chebyshev polynomials and direct Hankel determinants. The source implementation is [sequence_polynomial_hankel.py](../../tools/sequence_polynomial_hankel.py), with [independent tests](../../tools/test_sequence_polynomial_hankel.py).

## 1. Arbitrary polynomial weights

Let \(P(m)\in\mathbb K[m]\) have degree \(D\), over a characteristic-zero field \(\mathbb K\). Write it in the falling-factorial basis,

\[
P(m)=\sum_{d=0}^D a_d m^{\underline d},
\quad
m^{\underline d}=m(m-1)\cdots(m-d+1).
\]

The moment functional is

\[
F_P[x^{2m}]=P(m)\binom{2m}{m},
\qquad
F_P[x^{2m+1}]=0.
\]

Perturb it by differentiation, and define its size-\(N\) Hankel determinant:

\[
L_{P,c}[f]=F_P[f]+cF_P[f'],\qquad
W_N(P,c)=\det[L_{P,c}[x^{i+j}]]_{0\le i,j<N},
\qquad W_0=1.
\]

The polynomial weight \(P=1\) reproduces the unweighted swinging-factorial Hankel family. The choice \(P(m)=m^{\underline d}\) reproduces \(W_N^{[d]}(c)\). A general \(P\) is **not** restricted to one such weight.

For any shift parameter \(\lambda\), replacing the moments by \(L_{P,c}[(x+\lambda)^n]\) leaves \(W_N\) unchanged. Indeed, the change from monomials to shifted monomials is unitriangular, so it preserves the Gram determinant by congruence.

## 2. The exact Chebyshev transform

Use

\[
C_0(x)=2,\quad C_1(x)=x,\quad
C_{n+1}(x)=xC_n(x)-C_{n-1}(x).
\]

Thus \(C_n(x)=2T_n(x/2)\), and \(C_n\) is monic for \(n\ge1\).

**Theorem A.** For \(d\ge1\) and \(n\ge1\),

\[
\boxed{
F_d[C_{2n}]
=\frac{(2d)!}{d!}\binom{n+d-1}{2d-1}
=\frac{2n}{(d-1)!}\prod_{j=1}^{d-1}(n^2-j^2).
}
\]

At \(n=0\), the correct value is \(F_d[C_0]=0\) for \(d\ge1\); for \(d=0\), \(F_0[C_0]=2\) and \(F_0[C_{2n}]=0\) for \(n\ge1\). All odd Chebyshev polynomial moments vanish by parity.

For **every** \(d\ge0,n\ge0\), the derivative transform is

\[
\boxed{
F_d[C'_{2n+1}]
=\frac{2n+1}{d!}\prod_{j=0}^{d-1}
\left(n(n+1)-j(j+1)\right).
}
\]

The product is empty and equals \(1\) when \(d=0\). Every derivative moment \(F_d[C'_{2n}]\) vanishes.

Equivalently, in the Chebyshev index \(t\), introduce the odd polynomials

\[
U_d(t)=\frac{t}{4^{d-1}(d-1)!}
\prod_{j=1}^{d-1}(t^2-4j^2),\qquad d\ge1,
\]

\[
V_d(t)=\frac{t}{4^d d!}
\prod_{j=0}^{d-1}(t^2-(2j+1)^2),\qquad d\ge0.
\]

Set

\[
\Phi_P(t)=\sum_{d=1}^D a_dU_d(t),
\qquad
\Psi_P(t)=\sum_{d=0}^D a_dV_d(t).
\]

Then, for positive even \(t\), \(F_P[C_t]=\Phi_P(t)\), and for positive odd \(t\), \(F_P[C'_t]=\Psi_P(t)\). The exceptional value at \(t=0\) is \(F_P[C_0]=2P(0)\).

### Proof of Theorem A

Define the auxiliary functional \(F_s[x^{2m}]=s^m\binom{2m}{m}\), with odd moments zero. The rational Chebyshev generating identity is

\[
\sum_{n\ge0}C_n(x)z^n
=1+\frac{1-z^2}{1-xz+z^2}.
\]

Applying \(F_s\) gives the formal identity

\[
F_s\!\left[\sum_{n\ge0}C_n(x)z^n\right]
=1+\frac{1-z^2}{\sqrt{(1+z^2)^2-4sz^2}}.
\]

Since \(\partial_s^ds^m|_{s=1}=m^{\underline d}\), differentiating \(d\ge1\) times and specializing \(s=1\) gives

\[
\sum_{n\ge0}F_d[C_n]z^n
=\frac{(2d)!}{d!}\frac{z^{2d}}{(1-z^2)^{2d}}.
\]

The binomial theorem supplies the first boxed formula, including the zero initial segment.

Next, the Chebyshev derivative identity gives

\[
C'_{2n+1}(x)
=(2n+1)\left(1+\sum_{k=1}^n C_{2k}(x)\right).
\]

For \(d\ge1\), insert the first formula and apply the hockey-stick identity:

\[
\sum_{k=1}^n \binom{k+d-1}{2d-1}
=\binom{n+d}{2d}.
\]

Hence

\[
F_d[C'_{2n+1}]
=(2n+1)\frac{(2d)!}{d!}\binom{n+d}{2d},
\]

which is the second boxed formula. The \(d=0\) case follows from \(F_0[1]=1\) and orthogonality. This proves both identities. No inference from finite data is needed.

## 3. Uniform off-diagonal rank

Let \(G_N\) be the moment Gram matrix in the basis \(C_0=2,C_1,\ldots,C_{N-1}\):

\[
G_{ij}=L_{P,c}[C_iC_j].
\]

The first basis vector has leading coefficient \(2\), while the remaining vectors are monic. Therefore

\[
\boxed{\det G_N=4W_N(P,c)\quad(N\ge1).}
\]

The elementary product identity

\[
C_iC_j=C_{i+j}+C_{|i-j|}
\]

holds for all nonnegative \(i,j\).

For strictly separated indices \(i>j\), both \(i+j\) and \(i-j\) are positive. Consequently,

\[
G_{ij}=
\begin{cases}
\Phi_P(i+j)+\Phi_P(i-j),&i-j\text{ even},\\
c\bigl(\Psi_P(i+j)+\Psi_P(i-j)\bigr),&i-j\text{ odd}.
\end{cases}
\]

**Theorem B (bounded quasiseparable rank).** Let \(P\) have degree \(D\). For every pair of index sets \(I,J\) with \(\min I>\max J\),

\[
\boxed{\operatorname{rank}G_{I,J}\le2(D+1).}
\]

When \(c=0\), the sharper bound is \(2D\). Both bounds are independent of \(|I|,|J|\) and the determinant size \(N\).

**Proof.** Both \(\Phi_P(t)\) and \(\Psi_P(t)\) are odd polynomials, of degrees at most \(2D-1\) and \(2D+1\), respectively. For an odd polynomial \(f(t)\), expansion of \(f(i+j)+f(i-j)\) contains only the even powers \(1,j^2,\ldots\) of the column index \(j\). The even/odd parity selector is

\[
\frac{1\pm(-1)^i(-1)^j}{2}.
\]

Thus every separated block column belongs to the span of

\[
1,j^2,\ldots,j^{2D},
\quad
(-1)^j,(-1)^jj^2,\ldots,(-1)^jj^{2D},
\]

a space of dimension at most \(2(D+1)\). If \(c=0\), the derivative branch vanishes, and only degrees through \(j^{2D-2}\) remain. This proves the bounds.

The rank statement is about separated off-diagonal blocks, not the rank of the entire Hankel or Gram matrix.

### Explicit generators

Write

\[
\Phi_P(t)=\sum_{h=0}^{D-1}b_ht^{2h+1},
\qquad
\Psi_P(t)=\sum_{h=0}^{D}e_ht^{2h+1}.
\]

For \(0\le k\le D\), set

\[
A_k(i)=2\sum_{h=k}^{D-1}
b_h\binom{2h+1}{2k}i^{2h+1-2k},
\]

\[
B_k(i)=2\sum_{h=k}^{D}
e_h\binom{2h+1}{2k}i^{2h+1-2k}.
\]

Here \(A_D=0\). Let \(\epsilon_i=(-1)^i\), and form the vectors

\[
u_i=\left(
\frac{A_k(i)+cB_k(i)}2,\
\frac{\epsilon_i(A_k(i)-cB_k(i))}2
\right)_{k=0}^{D},
\]

\[
v_j=\left(j^{2k},\ \epsilon_jj^{2k}\right)_{k=0}^{D},
\]

where the first components for all \(k\) precede the second components. Direct substitution yields

\[
\boxed{G_{ij}=u_i^{\mathsf T}v_j\quad(i>j).}
\]

The diagonal is \(G_{00}=4P(0)\) and \(G_{ii}=2P(0)+\Phi_P(2i)\) for \(i\ge1\). These are the complete inputs to the structured solver.

## 4. Initial zero blocks for every polynomial weight

Suppose \(P\ne0\), and let \(\nu\) be the smallest integer with \(a_\nu\ne0\). Since \(P(m)=0\) for \(m<\nu\), the moments \(L_{P,c}[x^n]\) vanish for every \(n<2\nu\).

**Theorem C.** Every \(c\) satisfies

\[
\boxed{
W_N(P,c)=0\ (1\le N\le2\nu),\qquad
W_{2\nu+1}(P,c)=(-1)^\nu
\left(a_\nu\frac{(2\nu)!}{\nu!}\right)^{2\nu+1}.
}
\]

Indeed, the first nonzero leading Hankel matrix is anti-triangular, with its entire anti-diagonal equal to the first nonzero even moment. Its determinant is the displayed signed power. The derivative parameter \(c\) cannot change that anti-diagonal.

This includes the prior result for \(P(m)=m^{\underline d}\) and explains how to initialize an exact solver without dividing by a zero leading minor.

## 5. A fixed-width exact Schur algorithm

Set \(r=2(D+1)\). Let \(V_m\) be the matrix with rows \(v_0^\mathsf T,\ldots,v_{m-1}^\mathsf T\), and suppose the leading Gram block \(G_m\) is invertible. Maintain the \(r\times r\) matrix

\[
K_m=V_m^\mathsf TG_m^{-1}V_m.
\]

For the next index \(m\), the scalar Schur pivot is

\[
s_m=G_{mm}-u_m^\mathsf TK_mu_m.
\]

If \(s_m\ne0\), the determinant and state update exactly:

\[
\det G_{m+1}=\det G_m\,s_m,
\]

\[
\boxed{
K_{m+1}=K_m+
\frac{(K_mu_m-v_m)(K_mu_m-v_m)^\mathsf T}{s_m}.
}
\]

This follows directly from the block-matrix inverse identity. The state width \(r\) does not grow with \(m\). After an \(O(D^3)\)-arithmetic initialization, nonsingular scalar steps require \(O(D^2)\) arithmetic each. Consequently, an uninterrupted scalar-pivot run requires \(O(D^3+ND^2)\) rational-arithmetic operations. This is not a fixed-bit-cost complexity guarantee.

### Singular leading minors

A zero scalar pivot means the next leading determinant vanishes. It **does not** imply that every subsequent leading determinant vanishes. The exact implementation uses block lookahead.

For a block \(J=\{m,\ldots,m+\ell-1\}\), form

\[
S_J=G_{J,J}-U_JK_mU_J^\mathsf T
\]

from the recorded generators. If \(S_J\) is singular, the corresponding leading determinant is zero. Find the first \(\ell\) for which \(S_J\) is invertible. The determinant then updates by \(\det S_J\), and the state becomes

\[
K_{m+\ell}
=K_m+(K_mU_J^\mathsf T-V_J^\mathsf T)
S_J^{-1}(U_JK_m-V_J).
\]

This uses no division by singular pivots and returns every intermediate zero determinant correctly. Large exceptional lookahead blocks can increase complexity, so the generic \(O(D^3+ND^2)\) estimate is not asserted as an unconditional worst-case bound.

A concrete example is \(P(m)=1+m\), \(c=2\):

\[
W_0,\ldots,W_4=1,\ 1,\ 0,\ -256,\ 44536.
\]

The zero at size \(2\) is followed by a nonzero determinant at size \(3\). The block update recovers it.

The monomial-basis direct determinant and this Chebyshev generator algorithm are independently implemented in the verification suite.

## 6. Zero geometry and positivity: a sharp qualification

**Theorem D.** For every polynomial weight \(P\),

\[
W_N(P,-c)=W_N(P,c),\qquad
\deg_c W_N(P,c)\le2\lfloor N/2\rfloor.
\]

To prove it, order monomial indices by even and odd parity. The moment matrix becomes

\[
\begin{pmatrix}A&cB\\cB^\mathsf T&D\end{pmatrix}.
\]

Changing \(c\) to \(-c\) is congruence by a diagonal sign matrix. Its determinant is therefore an even polynomial. Each determinant term contains at most \(2\min(\#\text{even},\#\text{odd})\) cross-parity factors.

For a **positive definite** real moment functional \(F\), a more general matrix-pencil argument proves that \(\det(F[p_ip_j]+cF[(p_ip_j)'])\) has only real, nonzero roots in \(c\), whenever roots exist. Its positive definite Gram matrix \(A\) gives the real symmetric pencil \(I+cA^{-1/2}BA^{-1/2}\).

However, one cannot assume such positivity for an arbitrary polynomially weighted central-binomial functional.

**Theorem E (positivity rigidity).** If \(P\in\mathbb R[m]\) and

\[
F_P[q(x)^2]\ge0
\quad\text{for every real polynomial }q,
\]

then \(P\) must be a nonnegative constant. Conversely, every nonnegative constant weight gives a positive semidefinite functional.

**Proof.** By the classical moment representation theorem, a positive functional has a finite positive representing measure with total mass \(P(0)\). If \(P\) is nonconstant with negative leading coefficient, sufficiently high even moments are negative, a contradiction. If its leading coefficient is positive, its moments satisfy

\[
F_P[x^{2m}]=P(m)\binom{2m}{m}
\sim \frac{\operatorname{lc}(P)}{\sqrt{\pi}}
4^m m^{D-1/2}.
\]

Their even-root growth forces the representing measure to be supported in \([-2,2]\). It would then satisfy
\(F_P[x^{2m}]\le4^mP(0)\), contradicted by the displayed asymptotic when \(D\ge1\). The case \(P(0)=0\) is already incompatible with nonzero positive moments. Thus only constants remain, and the arcsine moment functional establishes the converse.

This explains why real-rootedness of the unweighted \(d=0\) Hankel family cannot be transferred by positivity to all polynomial weights. It does not exclude other special zero-geometry statements proved by different methods.

## 7. Reproduction and scope

Use Python 3.10+ with the standard library only:

```bash
python -B tools/sequence_polynomial_hankel.py
python -B -m unittest discover -s tools -p 'test_sequence_polynomial_hankel.py' -v
```

The implementation accepts rational coefficients in the falling-factorial basis and rational \(c\). The helper `power_to_falling` performs exact basis conversion. It returns all leading determinants, including zero prefixes and later singular blocks, without floating-point arithmetic.

The new theorem is distinct from the earlier fixed-size Chebyshev remainder formula for the single weight \(m^{\underline d}\). That specialized formula remains valuable and may be faster for its own family. Here the advance is **one bounded-rank matrix construction for an arbitrary polynomial \(P\)**. Existing archive proofs, integer terms and OEIS snapshot receipts are not modified.

Historical priority and whether the quasiseparable formulation is already recorded elsewhere remain open. The derived identities and algorithm are mathematically separate from that question.
