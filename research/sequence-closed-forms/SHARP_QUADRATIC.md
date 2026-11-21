# A sharp uniform quadratic Hankel recurrence

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-21-003.
Parent publication: 595aa4a61bff25dce221c69b3ca507e43060bd29.
Review status: proved as written in separate project self-review;
no independent review or Lean formalization.

## Statement

Work over a characteristic-zero field. Put
\[
 \begin{aligned}
 P(m)&=a+bm+cm(m-1),\\
 \mu_{2m}&=P(m)\binom{2m}{m},\qquad \mu_{2m+1}=0,\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0=1.
 \end{aligned}
\]
Let \(S\) denote the forward shift in \(N\), and set
\[
\begin{aligned}
 A&=4a^2,\\
 p&=-8a+8b-24c,\\
 q&=24a^2-32ab-96ac+16b^2,\\
 g(X)&=X^4+pX^3+qX^2+ApX+A^2,\\
 k(X)&=X^4+4(b-2a)X^3+(24a^2-16ab+48ac)X^2
              +16a^2(b-2a)X+16a^4,\\
 \Gamma(X)&=(X-2a)g(X)k(X).
\end{aligned}
\]

**Theorem K.** For every \(a,b,c\), including all degree drops
and the zero weight,
\[
 \boxed{\Gamma(S)^7W_N=0\quad(N\ge1).}                 \tag{K1}
\]
This is a uniform constant-coefficient recurrence of order at most 63.
The previously certified specialization \((a,b,c)=(1,1,1)\), or
\(P(m)=1+m^2\), has minimal eventual order 63, so the uniform bound is
optimal. Minimality at every specialization is not claimed.

## 1. A fixed formal moment functional

All expansions below are formal Laurent series at infinity. Define
\[
 \nu[f]=[x^{-1}]f(x)(x^2-4)^{-5/2},
 \qquad (x^2-4)^{-5/2}=x^{-5}(1-4x^{-2})^{-5/2}.
\]
Thus odd moments vanish, the first four moments vanish, and
\[
 \nu[x^{2m}]=\frac{m(m-1)}{12}\binom{2m}{m}\quad(m\ge0).       \tag{K2}
\]
For \(m\ge2\), this follows by expanding the binomial series; both sides
are zero at \(m=0,1\). The elementary central-binomial ratios also give
\[
 \nu[(x^2-4)x^{2m}]=\frac m2\binom{2m}{m},\qquad
 \nu[(x^2-4)^2x^{2m}]=\binom{2m}{m}.
\]
Consequently the functional defining \(\mu_j\) is exactly \(R\nu\), where
\[
 R(x)=a(x^2-4)^2+2b(x^2-4)+12c.                            \tag{K3}
\]
This identity concerns formal moments; no positive measure or endpoint
integrability is assumed.

## 2. Orthogonal polynomials after the singular initial block

Write \(\sigma=x^2-4\). For \(n\ge5\), define
\[
 L_n=\frac{(2n-5)!}{(n-5)!},\qquad
 p_n(x)=\frac{\sigma^{5/2}}{L_n}
                 \frac{d^n}{dx^n}\sigma^{n-5/2}.            \tag{K4}
\]
The derivative is \(\sigma^{-5/2}\) times a polynomial of degree \(n\),
whose leading coefficient is \(L_n\); hence \(p_n\) is monic. Formal
integration by parts uses \([x^{-1}]f'=0\), and proves
\(\nu[p_nx^j]=0\) for \(j<n\). Its squared norm is
\[
\begin{aligned}
 h_n=\nu[p_n^2]&=\nu[p_nx^n]\\
 &=\frac{(-1)^n n!}{L_n}
       (-4)^{n-2}\binom{n-5/2}{n-2}
 =\frac{2n(n-1)}{(n-3)(n-4)}\ne0.                         \tag{K5}
\end{aligned}
\]
The size-five moment matrix of \(\nu\) is anti-triangular with
anti-diagonal entries one, so its determinant is one. Changing the monomial
basis to \(1,x,x^2,x^3,x^4,p_5,\ldots,p_{N-1}\) now proves
\[
 H_N(\nu)=2^{N-5}\frac{(N-1)(N-2)^2(N-3)^2(N-4)}{144}
 \quad(N\ge5).                                           \tag{K6}
\]
In particular every required moment matrix is nonsingular, although the
smaller initial matrices are singular.

The operator \(\mathcal L=\sigma\partial_x^2-3x\partial_x\) is formally
self-adjoint for \(\nu\), since \((\sigma\sigma^{-5/2})'=-3x\sigma^{-5/2}\).
Orthogonality and nonsingularity therefore give
\[
 \mathcal Lp_n=n(n-4)p_n.                                  \tag{K7}
\]
The monic polynomial solution is unique: the difference of the eigenvalues
at degrees \(n\) and \(j<n\) is \((n-j)(n+j-4)\ne0\).

Let \(x=z+z^{-1}\), \(d_n=(n-3)(n-4)\), and
\[
 F_n(z)=z^n\ell_n(z),\qquad
 \ell_n(z)=d_n-2n(n-4)z^{-2}+n(n-1)z^{-4}.
\]
Direct substitution into (K7), using
\(\partial_x=(1-z^{-2})^{-1}\partial_z\), gives
\[
 d_np_n(z+z^{-1})=F_n(z)+F_n(z^{-1})\quad(n\ge5).           \tag{K8}
\]
The right side is a symmetric Laurent polynomial, with leading term
\(d_nx^n\), so uniqueness applies. The direct substitution is also retained
as an exact Laurent-polynomial identity in the replay program.

## 3. The transformed determinant, without an external theorem

For generic parameters write
\[
 R(x)=a(x-r)(x+r)(x-s)(x+s),\quad
 r=z+z^{-1},\quad s=w+w^{-1}.
\]
Here \(a,r,s,rs(r^2-s^2)\) are nonzero; excluded specializations are
recovered in section 6. The determinant identity needed is
\[
 W_N=a^NH_N(\nu)
  \frac{\det(p_{N+j}(t_i))_{0\le i,j<4}}
       {\Delta(t_0,t_1,t_2,t_3)},
 \quad(t_0,t_1,t_2,t_3)=(r,-r,s,-s),\quad N\ge5.            \tag{K9}
\]
For completeness, let \(Q=R/a\), and let \(\nu^{\otimes N}\) act on
separate polynomial variables. Expanding two determinants shows
\(H_N(Q\nu)=\nu^{\otimes N}[\Delta(x)^2\prod_iQ(x_i)]/N!\).
Also
\(\Delta(x,t)=\Delta(x)\Delta(t)\prod_iQ(x_i)\), because
there are four added roots. Express the augmented Vandermonde in any monic
basis in its first \(N\) columns and \(p_N,\ldots,p_{N+3}\) in its last
four columns. After expansion along the \(x\) rows and application of
\(\nu^{\otimes N}\), orthogonality kills every selection containing a
last-four column. The sole remaining selection gives
\(N!H_N(\nu)\det(p_{N+j}(t_i))\), with positive Laplace sign. This proves
(K9), using no orthogonal polynomials below degree five.

Put \(P_n(r)=F_n(z)+F_n(z^{-1})\), and similarly at \(s\). Parity gives
\[
\begin{aligned}
 D_N&=P_N(r)P_{N+2}(s)-P_{N+2}(r)P_N(s),\\
 E_N&=P_{N+1}(r)P_{N+3}(s)-P_{N+3}(r)P_{N+1}(s).
\end{aligned}
\]
Row and column operations give \(\det(P_{N+j}(t_i))=4D_NE_N\), and
\(\Delta(r,-r,s,-s)=4rs(s^2-r^2)^2\). Moreover
\[
 \prod_{j=0}^3d_{N+j}=N(N-1)^2(N-2)^2(N-3)^2(N-4).
\]
Substitution in (K9) yields
\[
 W_N=\frac{(2a)^N D_NE_N}{4608N(N-1)rs(s^2-r^2)^2}
 \quad(N\ge5).                                           \tag{K10}
\]

## 4. Nine bases and polynomial degree six

For \(u\in\{z,z^{-1}\}\), \(v\in\{w,w^{-1}\}\), define polynomials in
the formal variable \(n\):
\[
\begin{aligned}
 B_n(u,v)&=\ell_n(u)v^2\ell_{n+2}(v)
                  -u^2\ell_{n+2}(u)\ell_n(v),\\
 C_n(u,v)&=uv\{\ell_{n+1}(u)v^2\ell_{n+3}(v)
                  -u^2\ell_{n+3}(u)\ell_{n+1}(v)\}.
\end{aligned}
\]
Each has degree at most four in \(n\). Since
\[
 \ell_1(u)=6(1+u^{-2}),\qquad
 u^2\ell_3(u)=6(1+u^{-2}),
\]
we have \(B_1=0\) and \(C_0=0\). Hence
\(b_n=B_n/(n-1)\) and \(c_n=C_n/n\) are polynomials of degree at most
three. These are polynomial quotients, including at indices zero and one.
Expanding (K10) therefore gives the explicit exponential polynomial
\[
 \mathcal W_N=\frac{(2a)^N}{4608rs(s^2-r^2)^2}
 \sum_{\epsilon,\eta,\delta,\theta\in\{-1,1\}}
 b_N(z^\epsilon,w^\eta)c_N(z^\delta,w^\theta)
       (z^{\epsilon+\delta}w^{\eta+\theta})^N.             \tag{K11}
\]
Its nine possible bases are
\[
 \lambda_{ij}=2az^{2i}w^{2j},\qquad i,j\in\{-1,0,1\},
\]
and their coefficients have degree at most six in \(N\). Since
\((S-\lambda)^{d+1}\) annihilates \(\lambda^N\) times a degree-\(d\)
polynomial, \(\prod_{i,j}(S-\lambda_{ij})^7\) annihilates (K11).

Set \(T_1=z^2+z^{-2}=r^2-2\), \(T_2=w^2+w^{-2}=s^2-2\). From (K3),
\[
 T_1+T_2=4-2b/a,\qquad T_1T_2=4-4b/a+12c/a.
\]
Expanding the four corner bases gives \(g\), and the four axis bases give
\(k\):
\[
 \prod_{i,j\in\{-1,1\}}(X-2az^{2i}w^{2j})=g(X),\qquad
 \prod_{v\in\{z,w\}}(X-2av^2)(X-2av^{-2})=k(X).
\]
The remaining base is \(2a\). Thus the annihilator is exactly \(\Gamma^7\).

## 5. The initial boundary

Formula (K11) also gives the actual determinants at indices one through four:
\[
\begin{aligned}
 \mathcal W_1&=a,\\
 \mathcal W_2&=2a(a+b),\\
 \mathcal W_3&=4(a+b)(a^2+2ab+6ac-2b^2),\\
 \mathcal W_4&=8(a^2+2ab+6ac-2b^2)
                   (a^2+4ab-6b^2+24ac-12bc-36c^2).
\end{aligned}                                             \tag{K12}
\]
These are finite Laurent-polynomial identities, obtained by inserting
\(n=1,2,3,4\) into the explicit polynomial quotients in (K11). After
setting \(a=1\), substituting
\(b=(8-r^2-s^2)/2\), \(c=(r^2s^2-16+8b)/12\), and multiplying by
\(4608rs(s^2-r^2)^2\), both sides are Laurent polynomials in \(z,w\).
The replay checks every coefficient; homogeneity restores arbitrary \(a\).
Direct size-at-most-four monomial determinants give exactly (K12).
Together with (K10), this identifies (K11) with \(W_N\) for every \(N\ge1\).
At zero, (K11) instead gives \(1/2\); the convention \(W_0=1\) remains
separate. In particular the uniform start index cannot be lowered to zero
when \(a\ne0\): the residual there is \(\Gamma(0)^7/2\ne0\).

## 6. Every specialization and sharpness

So far the proof takes place in a generic extension where the displayed
denominators are nonzero. For each fixed \(N\ge1\), the residue in (K1) is
a polynomial in \(a,b,c\) with integer coefficients. Substituting the generic
root parameters in (K3) is injective on \(\mathbb Q[a,b,c]\): the independent
variables \(r^2,s^2\) have algebraically independent sum and product, and
adjoining \(z,w\) is algebraic. Since the residue vanishes in this extension,
it is the zero polynomial. Specialization therefore proves (K1) over every
characteristic-zero field, including \(a=0\), \(c=0\), coincident roots,
singular moment matrices and the zero weight.

At \((a,b,c)=(1,1,1)\), the factors become
\[
 \Gamma(X)=(X-2)(X^4-24X^3-88X^2-96X+16)
                    (X^4-4X^3+56X^2-16X+16).
\]
The parent publication's exact reduced-OGF certificate proves minimal eventual
constant-coefficient order 63 at this specialization. Thus 63 is the best
possible uniform bound. This argument does not settle the general mixed-
operator problem, assert novelty, or provide independent review or Lean
formalization. The older order-126 theorem remains valid and preserved.
