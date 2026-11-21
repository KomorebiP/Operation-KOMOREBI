# Weighted central-binomial Hankel determinants

**Uniform recurrences and complete mixed-linear order classification**

Komorebi P. Final edition 1.0. 21 November 2026.

## Abstract

We study Hankel determinants built from polynomially weighted central-binomial
moments and first-order differential operators. For quadratic weights with the
identity operator, we prove an explicit uniform constant-coefficient recurrence
of order at most 63 and exhibit a specialization with minimal eventual order
63. For linear weights and arbitrary first-order operators, we prove a uniform
bound of 112, show that it is generically attained, and give a complete finite
algebraic rule for the minimal eventual order at every parameter over a
characteristic-zero field. The classification includes zero parameters,
repeated roots, spectral collisions, and their intersections. Exact portable
certificates support the finite algebraic leaves of the proofs. The empty
determinant is retained separately from recurrences beginning at index one.

This edition consolidates Theorems K, L, M, and N from the completed source
edition. Its mathematical review provenance is project self-review.
Independent review, historical novelty, and Lean formalization are unassessed.

## 1. Results, conventions, and reading guide

Let the coefficient field have characteristic zero. For the mixed linear
family, fix four field elements and define
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0=1.
 \end{aligned}                                                    \tag{E1}
\]
These are the moments obtained by applying the operator
\(\mathcal D=u+v\partial_x\) to the even-moment functional with weight
\(P(m)=a+bm\). The elementary formal binomial expansion
\((1-4z)^{-1/2}=\sum_{m\ge0}\binom{2m}{m}z^m\) explains the
central-binomial kernel. The proofs below work with formal Laurent series;
they require no positive measure or endpoint integrability.

Write \(S\) for the forward shift: \((SW)_N=W_{N+1}\).
An eventual scalar constant-coefficient recurrence of order \(r\) is an
identity \(\sum_{j=0}^r d_jW_{N+j}=0\), with \(d_r=1\), for all
sufficiently large \(N\). Its coefficients belong to the original field.
The minimal eventual order is the least such \(r\); order zero means
eventual vanishing. It is distinct from the size of a transfer matrix or the
degree of an unreduced candidate denominator.

**Main result.** Theorems M and N together determine the minimal eventual
order of (E1) for every \((a,b,u,v)\). Theorem L supplies a uniform bound
of 112 and its generic sharpness. The reduced recurrences in the
classification hold from \(N=1\); the convention \(W_0=1\) is separate.

| Family | Result | Scope of minimality |
|---|---|---|
| \(P(m)=a+bm+cm(m-1)\), identity operator | Theorem K: uniform bound 63 | Sharp at \((a,b,c)=(1,1,1)\); pointwise classification is not asserted |
| Linear weight, first-order operator | Theorem L: uniform bound 112 | Minimal order 112 on a nonempty Zariski-open set |
| Mixed linear family, \(abuv=0\) | Theorem M: complete ordered boundary table | Every zero-parameter intersection included |
| Mixed linear family, \(abuv\ne0\) | Theorem N: exact polynomial-gcd decision rule | Every root multiplicity and spectral collision included |

To classify a mixed-linear parameter, first test whether both weight
coefficients or both operator coefficients are zero; the order is then zero.
For every other point on \(abuv=0\), read the ordered table in
[Theorem M](#final-4-the-coordinate-boundary).
For \(abuv\ne0\), use \(t=b/a\) and \(q=(v/u)^2\), form the
degree-four and degree-sixteen polynomials in
[Theorem N](#final-5-every-nonzero-mixed-parameter), and compute the stated
gcd degrees and collision correction. This is a finite algebraic rule;
it does not require numerical root separation or recurrence fitting.

The quadratic functional developed in [section 2](#final-2-the-formal-functional-and-the-quadratic-bound)
provides the common proof foundation. [Section 3](#final-3-the-uniform-mixed-linear-bound)
then treats general quartic functionals and derives (E1). Sections 4 and 5
complete its boundary and nonzero classifications, respectively.
[Section 6](#final-6-certificates-and-reproduction) explains the certificate
logic and gives one-command reproduction instructions.

The letters K, L, M, and N, and their equation labels, are retained so the
paper can be checked against the archived sources. Subsection references
such as K.6 or N.3 refer within the corresponding theorem section. Auxiliary
symbols are local to their sections: in particular, the polynomial
coefficient \(q\) in K is distinct from the normalized ratio \(q\) in N.
The normalization of \(R\) is restated whenever it changes.

The [exact order explorer](https://komorebip.github.io/Operation-KOMOREBI/sequence-hankel-compression.html#interior-order-calculator)
accepts rational normalized parameters and links to this paper. The theorem
also covers algebraic parameters, including the order-64 triple-root case.
Negative rational \(q\) is interpreted in a quadratic extension containing
its square root; it is not a claim that a negative number is a real square.

## 2. The formal functional and the quadratic bound

### K.0. Statement

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

### K.1. A fixed formal moment functional

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

### K.2. Orthogonal polynomials after the singular initial block

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
 =\frac{2n(n-1)}{(n-3)(n-4)}\ne0.                         \end{aligned}\tag{K5}
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

### K.3. The transformed determinant, without an external theorem

For generic parameters write
\[
 R(x)=a(x-r)(x+r)(x-s)(x+s),\quad
 r=z+z^{-1},\quad s=w+w^{-1}.
\]
Here \(a,r,s,rs(r^2-s^2)\) are nonzero; excluded specializations are
recovered in subsection K.6. The determinant identity needed is
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

### K.4. Nine bases and polynomial degree six

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

### K.5. The initial boundary

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

### K.6. Every specialization and sharpness

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
The exact reduced-OGF certificate described in section 6 proves minimal
eventual constant-coefficient order 63 at this specialization. Thus 63 is
the best possible uniform bound. Theorems L, M, and N below treat the
mixed linear family.

## 3. The uniform mixed-linear bound

### L.1. The quartic-functional theorem

Use the formal functional from [the sharp quadratic proof](#final-2-the-formal-functional-and-the-quadratic-bound):
\[
 \nu[f]=[x^{-1}]f(x)(x^2-4)^{-5/2}.
\]
For any polynomial \(R(x)=r_4x^4+r_3x^3+r_2x^2+r_1x+r_0\), let
\[
 \mu_j=\nu[R(x)x^j],\qquad
 W_N(R)=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0(R)=1.
\]
Define \(C_0(x)=2\), \(C_1(x)=x\),
\(C_k(x)=xC_{k-1}(x)-C_{k-2}(x)\). For \(1\le k\le16\), set
\[
 T_k=2^k\operatorname{Res}_x(R,C_k).
\]
Here the resultant uses the fixed degree-four coefficient list for \(R\),
including when \(r_4=0\); it is the polynomial determinant of its Sylvester
matrix. Define
\[
 \begin{aligned}
 d_0&=1,\\
 d_j&=-\frac1j\sum_{k=1}^j d_{j-k}T_k\quad(1\le j\le16),\\
 \chi_R(X)&=\sum_{j=0}^{16}d_jX^{16-j}.
 \end{aligned}                                             \tag{L1}
\]
These formulas are explicit and involve only finitely many polynomial
determinants and divisions by the nonzero integers 1 through 16. In particular
every \(d_j\) is a polynomial over \(\mathbb Q\) in the five coefficients of
\(R\); no leading-coefficient division is required.

**Theorem L.** Over every characteristic-zero field, for every
quartic coefficient list, including degree drops and the zero polynomial,
\[
 \boxed{\chi_R(S)^7W_N(R)=0\quad(N\ge1).}                 \tag{L2}
\]
Thus these Hankel determinants have a uniform constant-coefficient recurrence
of order at most 112.

### L.2. Sixteen bases and degree six

The sharp quadratic proof already establishes the formal orthogonal
polynomials, their nonzero norms from degree five onward, and the augmented-
Vandermonde identity. Its determinant proof does not require an even \(R\).
For generic \(R=r_4\prod_{i=1}^4(x-t_i)\), put
\(t_i=z_i+z_i^{-1}\), and use its definitions
\[
 P_n(t_i)=F_n(z_i)+F_n(z_i^{-1}),\qquad
 F_n(z)=z^n\ell_n(z),\qquad
 \ell_n(z)=(n-3)(n-4)-2n(n-4)z^{-2}+n(n-1)z^{-4}.
\]
The same normalization gives, for \(N\ge5\),
\[
 W_N(R)=\frac{(2r_4)^N}{4608N(N-1)\Delta(t)}
              \det(P_{N+j}(t_i))_{1\le i\le4,\ 0\le j<4}.
                                                               \tag{L3}
\]
Expand this determinant by choosing \(u_i=z_i\) or \(z_i^{-1}\) in each row.
After extracting \(\prod_i u_i^N\), the coefficient determinant is
\[
 Q_n(u)=\det(u_i^j\ell_{n+j}(u_i))_{1\le i\le4,\ 0\le j<4}.
\]
It has degree at most eight in \(n\). At \(n=0\), columns one and three
coincide, since \(u\ell_1(u)=u^3\ell_3(u)\). At \(n=1\), columns zero and
two coincide, since \(\ell_1(u)=u^2\ell_3(u)\). Therefore
\(Q_n/[n(n-1)]\) is a polynomial of degree at most six. Equation (L3) is an
exponential polynomial with sixteen possible bases
\[
 \lambda_\epsilon=2r_4\prod_{i=1}^4z_i^{\epsilon_i},
 \qquad\epsilon_i\in\{-1,1\},                             \tag{L4}
\]
whose coefficients have degree at most six in \(N\).

Their power sums are
\[
 \begin{aligned}
 \sum_\epsilon\lambda_\epsilon^k
 &=(2r_4)^k\prod_i(z_i^k+z_i^{-k})\\
 &=(2r_4)^k\prod_i C_k(t_i)
 =2^k\operatorname{Res}_x(R,C_k)=T_k.
 \end{aligned}
\]
Newton's identities therefore identify
\(\prod_\epsilon(X-\lambda_\epsilon)\) with the explicit polynomial
\(\chi_R\) in (L1). To see the coefficient recursion directly, expand
\(\prod_\epsilon(1-\lambda_\epsilon z)\), differentiate its formal logarithm,
and compare coefficients. Each degree-six exponential component is killed by
the seventh power of its base factor. This proves (L2) for the generic tail.

### L.3. The boundary and every specialization

The exponential polynomial extends to index one. The necessary boundary
calculation is finite and uniform in the four coefficients of a monic
quartic. For \(N=2,3,4\), use
\[
 P_2=4x^2+8,\qquad P_3=12x,\qquad P_4=24,
\]
and \(P_n=(n-3)(n-4)p_n\) at \(n=5,6,7\). Reduce these polynomials modulo
\(R=x^4+r_3x^3+r_2x^2+r_1x+r_0\). If \(M_N\) is the four-by-four matrix
whose columns are the coefficient vectors of the remainders of
\(P_N,\ldots,P_{N+3}\), the identities are
\[
 2^N\det M_N=4608N(N-1)
        \det(\nu[Rx^{i+j}])_{0\le i,j<N}.                 \tag{L5}
\]
All coefficients of these three polynomial identities in
\(\mathbb Q[r_0,r_1,r_2,r_3]\) are checked by both the exploratory symbolic
calculation and the separate sparse-polynomial replay. The remainder
construction is valid because the evaluation matrix is the Vandermonde
matrix times \(M_N\); its determinant divided by \(\Delta(t)\) is
\(\det M_N\). Homogeneity restores arbitrary nonzero \(r_4\).

For the boundary limit at one, subtract column zero from column two before
dividing by \(n-1\). The vanishing-column derivative has no logarithm of
\(z_i\), since \(F_3(z_i)-F_1(z_i)=0\) already branch by branch. Its sum of
the two branches is
\[
 J(x)=-2x^3+8x.
\]
At \(N=1\), the four columns are therefore
\(12x,4x^2+8,J(x),24\). Their coefficient determinant is 2304, giving
\(2r_4\cdot2304/4608=r_4=\mu_0\). At zero, subtract column one from column
three; the columns become \(24,12x,4x^2+8,J(x)\), with determinant -2304.
The additional factor \(n-1=-1\) gives the exponential continuation value
\(1/2\), whereas \(W_0=1\).

Thus the exponential formula agrees with the actual sequence for every
\(N\ge1\). For each such fixed \(N\), the residue in (L2) is a polynomial
over \(\mathbb Q\) in the five coefficients of \(R\). The generic proof
therefore specializes to every coefficient list, including repeated roots,
degree drops, singular minors and zero weights. The uniform start cannot be
lowered to zero when \(r_4\ne0\): its residue there is
\(\chi_R(0)^7/2=(2r_4)^{112}/2\ne0\).

### L.4. Every linear weight and first-order operator

Let \(F_P[x^{2m}]=(a+bm)\binom{2m}{m}\), with odd moments zero, and let
\(\mathcal D=u+v\partial_x\). The induced moments are
\[
 \mu_{2m}=u(a+bm)\binom{2m}{m},\qquad
 \mu_{2m+1}=v(2m+1)(a+bm)\binom{2m}{m}.                   \tag{L6}
\]
Writing \(\sigma=x^2-4\), the functional \(F_P\) is
\((a\sigma^2+2b\sigma)\nu\). Formal integration by parts for the derivative
term gives exactly \(R\nu\), with
\[
\begin{aligned}
 R(x)&=u[a\sigma^2+2b\sigma]+vx[a\sigma+6b],\\
 r_4&=ua,\qquad r_3=va,\\
 r_2&=u(-8a+2b),\\
 r_1&=v(-4a+6b),\\
 r_0&=u(16a-8b).
\end{aligned}                                               \tag{L7}
\]
Indeed \(\nu[Qf']=-\nu[(Q'-5xQ/\sigma)f]\), and
\(-Q'+5xQ/\sigma=x(a\sigma+6b)\) for
\(Q=a\sigma^2+2b\sigma\). The quotient here is polynomial because
\(\sigma\) divides \(Q\). Theorem L applied to (L7) proves the uniform
order-at-most-112 recurrence for all \(a,b,u,v\), including pure odd,
identity, zero and degree-drop cases.

At \((a,b,u,v)=(1,1,1,2)\), the quartic is
\(x^4+2x^3-6x^2+4x+8\). Formula (L1) gives
\[
\begin{aligned}
 \chi_R(X)={}&X^{16}-16X^{15}+384X^{14}+1600X^{13}-21568X^{12}\\
 &+129792X^{11}+649216X^{10}-2378752X^9+9340416X^8\\
 &-9515008X^7+10387456X^6+8306688X^5-5521408X^4\\
 &+1638400X^3+1572864X^2-262144X+65536.
\end{aligned}
\]
This is exactly the reversed degree-16 generating-function factor in the
published order-112 example. Its reduced numerator is reconstructed from the
new formula and actual determinant values; the retained degree-preserving
modular Bezout witness checks coprimality. Thus the uniform bound is optimal.

### L.5. Generic minimality

The mixed-family minimal eventual order is 112 on a nonempty Zariski-open
set of parameters. Here is the precise argument. Put
\[
 D(z)=z^{112}\chi_R(z^{-1})^7,\qquad
 N(z)=\left[D(z)\sum_{j\ge0}W_jz^j\right]_{\le112}.
\]
The recurrence proves that the generating function is \(N/D\).
Both polynomial coefficient lists depend polynomially on \(a,b,u,v\).
At the certified sample they have degree 112 and are coprime, so their
fixed-degree resultant is a polynomial in the parameters that is nonzero at
that sample. On the nonempty open set where that resultant and the leading
coefficient of \(D\) are nonzero, the reduced denominator has degree 112.
Every eventual constant-coefficient scalar recurrence must annihilate that
denominator, so its order is at least 112. The bound proves equality there.

Theorems M and N below classify minimal orders on the exceptional parameter
locus. The bound 63 for quadratic weights with the identity operator remains
the separate Theorem K. The broader scope is stated in section 7.

## 4. The coordinate boundary

### M.1. Statement and complete boundary table

Over a characteristic-zero field, use
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\qquad W_0=1.
 \end{aligned}
\]
The minimal order below always means the minimal **eventual scalar
constant-coefficient recurrence order**. Order zero means eventual vanishing.
The uniform bound 112 and generic minimality are established in the
[preceding mixed-family theorem](#final-3-the-uniform-mixed-linear-bound).

**Theorem M.** Suppose \(abuv=0\). If \((a,b)=(0,0)\) or
\((u,v)=(0,0)\), the minimal order is zero. Otherwise the following table
is exhaustive. Its families are read in order, so intersections are included.

| Family | Further condition | Minimal order |
|---|---|---|
| \(v=0,\ u\ne0\) | \(a=0\) | 3 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b=0\) | 1 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b=2a\) | 7 |
| \(v=0,\ u\ne0\) | \(a\ne0,\ b\notin\{0,2a\}\) | 9 |
| \(u=0,\ v\ne0\) | \(a=0\) | 14 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=0\) | 6 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=a/3\) | 26 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b=2a/3\) | 18 |
| \(u=0,\ v\ne0\) | \(a\ne0,\ b\notin\{0,a/3,2a/3\}\) | 42 |
| \(b=0,\ auv\ne0\) | \(v^2+16u^2=0\) | 10 |
| \(b=0,\ auv\ne0\) | \(v^2+16u^2\ne0\) | 12 |
| \(a=0,\ buv\ne0\) | \(9v^2+16u^2=0\) | 22 |
| \(a=0,\ buv\ne0\) | \(9v^2+16u^2\ne0\) | 28 |

The reduced recurrence in every row holds from index one. The zero-index
empty determinant is retained separately. The two quadratic-relation rows
with orders 10 and 22 have no nonzero real solutions for \(u,v\); they
matter over fields containing the required square roots of -1.

This theorem classifies the entire coordinate boundary. Section 5 classifies
the complementary fully nonzero locus \(abuv\ne0\).

### M.2. Smaller uniform recurrences from formal moment functionals

Put \(\sigma=x^2-4\), and define formal residues at infinity by
\[
 \begin{aligned}
 \rho_1[f]&=[x^{-1}]f(x)\sigma^{-3/2},\\
 \rho_2[f]&=[x^{-1}]f(x)\sigma^{-5/2}.
 \end{aligned}
\]
The second functional is the \(\nu\) of the preceding proofs, and
\(\rho_1=\sigma\rho_2\). Their even moments are respectively
\(m\binom{2m}{m}/2\) and \(m(m-1)\binom{2m}{m}/12\); odd moments vanish.

For \(n\ge3\), the monic formal orthogonal polynomials for \(\rho_1\) are
\[
 q_n=\frac{\sigma^{3/2}}{(2n-3)!/(n-3)!}
                   \partial_x^n\sigma^{n-3/2}.
\]
The Rodrigues expression is monic, and formal integration by parts gives
orthogonality. More explicitly, its norm is
\[
 \begin{aligned}
 \rho_1[q_n^2]&=\rho_1[q_nx^n]\\
 &=\frac{(-1)^n n!}{(2n-3)!/(n-3)!}\\
 &\quad{}\cdot(-4)^{n-1}\binom{n-3/2}{n-1}\\
 &=-\frac{2n}{n-2}\ne0.
 \end{aligned}
\]
The size-three base Gram determinant is -1.
Consequently
\[
 H_N(\rho_1)=\frac{(-2)^N(N-1)(N-2)}{16}\quad(N\ge3).
\]
The operator \(\sigma\partial_x^2-x\partial_x\) is formally self-adjoint
because \((\sigma\sigma^{-3/2})'=-x\sigma^{-3/2}\). Orthogonality and
nonsingularity give \(\sigma q_n''-xq_n'=n(n-2)q_n\). Its monic solution
is unique, since the eigenvalue difference at degree \(j<n\) is
\((n-j)(n+j-2)\ne0\). With \(x=z+z^{-1}\), substitution therefore gives
\[
 (n-2)q_n(x)=(n-2)C_n(x)-nC_{n-2}(x),
 \qquad C_n(z+z^{-1})=z^n+z^{-n}.
\]
The coefficients of the two exponential branches have degree one in \(n\).
These assertions also have separate exact polynomial, orthogonality and norm
checks in the replay. The Rodrigues/orthogonality argument is the same formal
residue argument as in [Theorem K](#final-2-the-formal-functional-and-the-quadratic-bound), with the displayed
exponent changed; it uses no positive measure.

For a quadratic \(R=A x^2+B x+C\) multiplying \(\rho_1\), the two-root
augmented-Vandermonde identity therefore has four bases and coefficient
degree at most two. Their base polynomial is
\[
 X^4+2CX^3+(4B^2-8AC-8A^2)X^2+8A^2CX+16A^4.
\]
Indeed, if the two roots are \(r=z+z^{-1}\), \(s=w+w^{-1}\), the bases
are \(-2Az^{\pm1}w^{\pm1}\). Their elementary symmetric functions use
\(r+s=-B/A\) and \(rs=C/A\), giving the displayed polynomial.
Its cube is a uniform order-12 annihilator. The normalization of the raw
two-root determinant is \((-2A)^N/16\). Its initial indices one and two
agree with the actual determinants by coefficient identities; its value
at zero is 1/2. For even \(R\), the four branches give three distinct bases
generically, so the bound improves to nine. The resulting characteristic
factor for \(u=1\) is the previously published
\((X-2a)(X^2-4(a-b)X+4a^2)\); scaling the functional by \(u\) scales
every exponential base by \(u\).

For a quadratic multiplying \(\rho_2\), use the raw polynomials
\(P_n=(n-3)(n-4)p_n\) from Theorem K. The normalization is
\[
 \frac{(2A)^N(N-1)(N-2)}{4608}.
\]
The determinant of two raw branches has coefficient degree at most four;
the extra factor has degree two. Thus four bases give the uniform bound 28,
with seventh powers of
\[
 X^4-2CX^3+(4B^2-8AC-8A^2)X^2-8A^2CX+16A^4.
\]
Indices one through four are exact coefficient identities, using the same
low raw polynomials as Theorem L; the zero-index continuation is 1/8.

Finally, for the odd cubic \(R=d x(x^2-r^2)\) multiplying \(\rho_2\), the
three-root determinant has normalization \((-2d)^N/4608\). Every odd-size
determinant vanishes. The roots \(0,r,-r\), with \(r=z+z^{-1}\), give the
six possible full-sequence bases
\[
 \{\pm2id,\ \pm2id z^2,\ \pm2id z^{-2}\}.
\]
Each coefficient has degree at most six, so their seventh powers give a
uniform order-42 recurrence. Here \(i^2=-1\) is used in an algebraic extension
only; the resulting characteristic polynomial has coefficients in the
original field. For \(d=av\), \(r^2=4-6b/a\), it is
\[
 \left[(X^2+4a^2v^2)
 \{X^4+(8a^2-96ab+144b^2)v^2X^2+16a^4v^4\}\right]^7.
\]
For the initial boundary, divide the raw polynomials by the monic cubic
\(x^3-r^2x\) and take the three-by-three remainder coefficient determinant.
The identities at indices one through four agree coefficientwise with the
actual moment determinants. At zero the continuation is 1/4.

For all three constructions, the generic calculation takes place where the
displayed root determinants are nonsingular. For each fixed recurrence index,
the residue is a polynomial in the original coefficients. Thus the identities
extend to all specializations, including repeated roots and degree drops.
No inverse singular minor or limiting inference from numeric roots is used.

### M.3. Four normalized generating-function certificates

The boundary functionals reduce exactly as follows:
\[
\begin{aligned}
 b=0:&\quad L=a[u\sigma+vx]\rho_1,\\
 a=0:&\quad L=2b[u\sigma+3vx]\rho_2,\\
 u=0:&\quad L=vx[a\sigma+6b]\rho_2,\\
 v=0:&\quad L=u[a\sigma+2b]\rho_1.
\end{aligned}
\]
The first identity uses the central-binomial functional
\(F_1[f]=[x^{-1}]f\sigma^{-1/2}=\rho_1[\sigma f]\) and formal integration
by parts; the others follow either the same way or from Theorem L's explicit
quartic functional. Hence the smaller recurrence bounds above apply.

Use the following normalized variables. In each row the generating function
is \(N_t(s)/Q_t(s)^e\), with \(Q_t(0)=1\).

| Family | Normalization | \(Q_t(s)\) | \(e\) | Degree bound for \(N_t\) |
|---|---|---|---|---|
| \(v=0,\ au\ne0\) | \(t=b/a,\ s=auz\) | \((1-2s)(1-4(1-t)s+4s^2)\) | 3 | 9 |
| \(b=0,\ au\ne0\) | \(t=(v/u)^2,\ s=auz\) | \(1-8s+(24+4t)s^2-32s^3+16s^4\) | 3 | 12 |
| \(a=0,\ bu\ne0\) | \(t=9(v/u)^2,\ s=2buz\) | \(1+8s+(24+4t)s^2+32s^3+16s^4\) | 7 | 28 |
| \(u=0,\ av\ne0\) | \(t=b/a,\ s=(avz)^2\) | \((1+4s)(1+(8-96t+144t^2)s+16s^2)\) | 7 | 21 |

The last row is the generating function of the even subsequence, since every
odd term is zero. Its denominator degree in \(s\) must be doubled to obtain
the full-sequence recurrence order in \(z\).

The exact numerator coefficient lists are retained in the certificate JSON.
They are defined without fitting an infinite recurrence: convolve the stated
denominator with the defining moment determinants, through the listed degree.
The smaller recurrence proves that later coefficients vanish.

These numerator coefficients are polynomials in \(t\). Their degree bounds at
coefficient index \(j\) are, respectively, \(j,\lfloor j/2\rfloor,
\lfloor j/2\rfloor,2j\). Homogeneity of a determinant in its functional
coefficients gives these bounds. In the two squared-ratio rows, reversing the
sign of the odd coefficient is the basis change \(x\mapsto-x\), so only its
even powers remain. The 10, 7, 15 and 43 distinct interpolation nodes in the
certificate therefore determine every coefficient. The replay evaluates all
coefficients at exactly those nodes and checks the stated bounds.

### M.4. Minimality for every parameter in each normalized family

For each row, the certificate supplies polynomials \(U_t,V_t\) such that
\[
 U_t(s)N_t(s)+V_t(s)Q_t(s)=H(t).
\]
All coefficients of these identities are checked over \(\mathbb Q[t,s]\).
The right sides are exactly
\[
\begin{aligned}
 H_{v=0}(t)&=8t^5(t-2),\\
 H_{b=0}(t)&=2t^3(t+16),\\
 H_{a=0}(t)&=80t^7(t+16)^3,\\
 H_{u=0}(t)&=79254226206720\,t^{10}(3t-2)^7(3t-1)^7.
\end{aligned}
\]
Thus outside the listed roots of \(H\), the numerator is coprime to
\(Q\), hence to \(Q^e\). Its reduced denominator has full degree.
No other exceptional parameter in that normalized family is possible.

At the roots of \(H\), exact cross multiplication checks the following
reduced denominators. Separate rational Bezout identities certify that each
reduced numerator is coprime to its displayed denominator.

| Family | \(t\) | Reduced denominator in \(s\) | Degree |
|---|---|---|---|
| \(v=0\) | 0 | \(1-2s\) | 1 |
| \(v=0\) | 2 | \((1-2s)^3(1+2s)^4\) | 7 |
| \(b=0\) | 0 | \(1-2s\) | 1 |
| \(b=0\) | -16 | \((1+2s)^4(1-12s+4s^2)^3\) | 10 |
| \(a=0\) | 0 | \((1+2s)^3\) | 3 |
| \(a=0\) | -16 | \((1-2s)^8(1+12s+4s^2)^7\) | 22 |
| \(u=0\) | 0 | \((1+4s)^3\) | 3 |
| \(u=0\) | 1/3 | \((1+4s)^7(1-4s)^6\) | 13 |
| \(u=0\) | 2/3 | \((1+4s)^9\) | 9 |

Replacing \(s\) by a nonzero multiple of \(z\) preserves coprimality and
degree. Replacing it by \((avz)^2\) preserves coprimality by substituting
into the Bezout identity and doubles the denominator degree. A reduced
rational generating function's denominator degree is the minimal eventual
constant-coefficient recurrence order. This proves all normalized rows.

### M.5. Remaining intersections and the empty determinant

The normalizations above omit two nonzero boundary intersections. Their
closed expressions, for \(N\ge1\), are
\[
 \begin{aligned}
 a=v=0:&\quad W_N=\frac{(-4bu)^N(N-1)(N-2)}{16},\\
 a=u=0:&\quad W_N=\frac{(N-1)^2(N-2)^2(N-3)^2}{1152}
          \{(12ibv)^N+(-12ibv)^N\}.
 \end{aligned}
\]
The first is the \(\rho_1\) base determinant scaled by \(2bu\); the second
is the one-root transform \(6bv x\rho_2\), using the same orthogonal
polynomials at zero. In detail,
\(H_N(cx\rho)=(-c)^NH_N(\rho)p_N(0)\), and for even \(N\ge6\)
the raw formula gives \(p_N(0)=8(-1)^{N/2}(N-1)/(N-4)\).
Odd indices vanish by parity. Their distinct nonzero exponential modes and nonzero
leading polynomial coefficients give minimal orders 3 and 14. Indices one
through four check the singular initial boundaries directly.

If \(b=u=0\), the corresponding expression is
\[
 W_N=\frac{(N-1)^2}{8}
                \{(2iav)^N+(-2iav)^N\}\quad(N\ge1),
\]
with minimal order six when \(av\ne0\). This follows from the same one-root
identity for \(avx\rho_1\), with
\(q_N(0)=4(-1)^{N/2}(N-1)/(N-2)\) at even \(N\ge4\).
If \(b=v=0\), it is
\(W_N=(2au)^N/2\) for \(N\ge1\), with minimal order one when \(au\ne0\).
These also agree with the appropriate normalized-family reductions.

Each nonzero family's reduced numerator has the same degree as its reduced
denominator; their leading coefficient ratio is nonzero. Consequently the
reduced recurrence starts at one and cannot include index zero. The
exponential continuations at zero are 1/2, 1/4, 1/8 or 1/16, depending on the
stratum, whereas the actual empty determinant is always one. Zero functionals
give \(W_N=0\) for \(N\ge1\), also with the start at one.

This completes the coordinate-boundary classification using the written
derivations and the replayed coefficientwise certificate leaves. Those leaves are finite
polynomial identities with proved coverage bounds, not sampled evidence for
an infinite pattern. Review remains project self-review; historical novelty,
independent review and Lean formalization are unassessed.

## 5. Every nonzero mixed parameter

### N.1. A finite algebraic classification

Work over a characteristic-zero field. Use the moments and empty determinant
of [Theorem M](#final-4-the-coordinate-boundary):
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\\
 W_0&=1.
 \end{aligned}
\]
Suppose \(abuv\ne0\), and put
\[
 t=b/a,\qquad w=v/u,\qquad q=w^2.
\]
Dividing the functional by \(au\) scales \(W_N\) by \((au)^{-N}\),
which preserves its minimal eventual scalar constant-coefficient order.
The normalized quartic from [Theorem L](#final-3-the-uniform-mixed-linear-bound) is
\[
 \begin{aligned}
 R(x)={}&x^4+wx^3+(2t-8)x^2\\
       &+w(6t-4)x+16-8t.
 \end{aligned}                                                   \tag{N1}
\]

The following polynomials make the answer computable without choosing roots.
Set \(C_0(x)=2\), \(C_1(x)=x\),
\(C_k=xC_{k-1}-C_{k-2}\), and define
\[
 \begin{aligned}
 T_k&=\operatorname{Res}_x(R,C_k)\quad(1\le k\le8),\\
 c_0&=1,\qquad
 c_j=-\frac1j\sum_{k=1}^j c_{j-k}T_k\quad(1\le j\le8),\\
 F(Y)&=c_8Y^8+\sum_{j=0}^7c_j(Y^{16-j}+Y^j).
 \end{aligned}                                                   \tag{N2}
\]
Every \(c_j\) is a polynomial in \(t,q\). The source package retains their
exact sparse coefficient lists, as well as a separate replay of this definition.
Define also
\[
 \begin{aligned}
 H(Z)={}&q^2Z^4+q^2Z^3+q(2t-8)Z^2\\
       &+q(6t-4)Z+16-8t,\\
 G&=\operatorname{monic\ gcd}(H,H'),\qquad g=\deg G,\\
 h&=\deg\left(F/\gcd(F,F')\right),\\
 B(t,q)&=q^2+(36t^2-16t+32)q+64(t-2)^2,\\
 \delta&=\begin{cases}1,&B(t,q)=0,\\0,&B(t,q)\ne0.\end{cases}
 \end{aligned}                                                   \tag{N3}
\]
Primes denote derivatives in the displayed polynomial's variable. Constant
monic gcds are one. Since \(q\ne0\), \(H(Z)=R(wZ)\) has degree four
and has exactly the root multiplicities of \(R\).

**Theorem N.** The minimal eventual order is given by this exhaustive table:

| Exact condition | Root multiplicities of \(R\) | Minimal order |
|---|---|---|
| \(g=0\) | \(1+1+1+1\) | \(7h-\delta\) |
| \(g=1\) | \(2+1+1\) | \(7h+4-\delta\) |
| \(g=2,\ \gcd(G,G')=1\) | \(2+2\) | 69 |
| \(g=2,\ \deg\gcd(G,G')=1\) | \(3+1\) | 64 |

The case \(g=3\) cannot occur. In the last two rows, respectively,
\((h,\delta)=(9,0)\) and \((8,0)\). Every minimal recurrence holds
from index one; the separate value \(W_0=1\) cannot be included in that
minimal recurrence. All polynomial gcds are over the original field.

This is an exact finite algebraic decision rule: two polynomial gcds, of
degrees at most four and sixteen, determine the order, with one quadratic
gcd distinguishing the last two rows. Together with Theorem M, it covers every
parameter of the mixed linear-weight, first-order-operator family.

### N.2. The sixteen bases and their leading coefficients

Let the roots of \(R\), counted with multiplicity, be \(x_i\), and choose
\(z_i\) with \(x_i=z_i+z_i^{-1}\) in an algebraic extension.
For distinct roots, Theorem L gives the exponential polynomial
\[
 \widehat W_N=\frac{2^N}{4608N(N-1)\Delta(x)}
               \det(P_{N+j}(x_i))_{1\le i\le4,\ 0\le j<4},          \tag{N4}
\]
where \(P_n(x_i)=z_i^n\ell_n(z_i)+z_i^{-n}\ell_n(z_i^{-1})\) and
\[
 \ell_n(z)=(n-3)(n-4)-2n(n-4)z^{-2}+n(n-1)z^{-4}.
\]
Its sixteen labeled normalized bases are \(\prod_i z_i^{\epsilon_i}\),
\(\epsilon_i\in\{-1,1\}\); the actual bases are \(2au\) times these.
Their power sums are \(T_k\), and their multiset is closed under inversion.
Thus their monic characteristic polynomial is exactly \(F\) in (N2).
Replacing \(w\) by \(-w\) negates all four roots and leaves these power
sums unchanged. This proves the asserted polynomial dependence on \(t,q\).

For a rowwise choice \(v_i\in\{z_i,z_i^{-1}\}\), define
\[
 Q_n(v)=\det(v_i^j\ell_{n+j}(v_i))_{1\le i\le4,\ 0\le j<4}.
\]
It is divisible by \(n(n-1)\), as in Theorem L. Every coefficient in \(n\)
is alternating in the \(v_i\), so it is also divisible by \(\Delta(v)\)
in the Laurent polynomial ring. These two factors are coprime. Consequently
\[
 L_n(v)=Q_n(v)/(n(n-1)\Delta(v))
\]
is a Laurent polynomial whose degree in \(n\) is at most six. This fact
controls the lower coefficients as well as the leading one; it excludes
additional poles when roots merge.

Since
\(x_j-x_i=(v_j-v_i)(1-(v_iv_j)^{-1})\), the coefficient of this branch
has leading term \(A(v)n^6/4608\), where
\[
 A(v)=\frac{\prod_i(1-v_i^{-2})^2}
             {\prod_{i<j}(1-(v_iv_j)^{-1})}.                       \tag{N5}
\]
For distinct nonendpoint roots it is nonzero. The next coefficient, divided
by the leading one, is
\[
 -15-6S(v),\qquad S(v)=\sum_i\frac1{v_i^2-1}.                      \tag{N6}
\]
To check (N6), use the expansion
\[
 \ell_{n+j}(v)=A_0(v)n^2+(2jA_0(v)+B_0(v))n+\cdots
\]
with the following coefficients:
\[
 A_0(v)=(1-v^{-2})^2,\qquad
 B_0(v)/A_0(v)=-7-6/(v^2-1).
\]
Multilinearity gives the coefficient ratio
\(2\sum_{j=0}^3j+\sum_iB_0(v_i)/A_0(v_i)\) at degree seven before
division by \(n(n-1)\). That division adds one to the ratio, giving (N6).

### N.3. All collisions with simple roots

The nonzero hypotheses give
\[
 R(2)=12tw,\qquad R(-2)=-12tw.                                  \tag{N7}
\]
No two distinct roots of \(R\) can be opposites. Indeed, if \(r,-r\)
were roots with \(r\ne0\), the even and odd parts of (N1), with
\(\sigma=r^2-4\), would give
\(\sigma(\sigma+2t)=0\) and \(\sigma+6t=0\). Their combination is
\(24t^2=0\), a contradiction. A zero root occurs only at \(t=2\);
its derivative is \(8w\ne0\), so it is always simple.

Two sign vertices at Hamming distance one can collide only if some
\(z_i^2=1\), contradicting (N7). At distance two, the condition is
\((z_i^{\epsilon_i}z_j^{\epsilon_j})^2=1\), which would give equal
or opposite roots. Thus a collision has distance three or four.
There cannot be a cluster of three vertices: relative to one vertex, two
distinct flip sets of sizes at least three have symmetric difference of
size at most two. Every cluster therefore has size at most two.

For a distance-three pair put \(v_1v_2v_3=e\), \(e\in\{1,-1\}\).
Inverting these three branches changes the ratio of (N5) by
\[
 \frac{A(v_1^{-1},v_2^{-1},v_3^{-1},v_4)}{A(v)}
 =-\frac{\prod_{i=1}^3(v_4v_i-1)}{e\prod_{i=1}^3(v_4-v_i)}.
\]
If the two leading coefficients canceled, subtraction of these cubic
products would give
\[
 e\prod_{i=1}^3(v_i-e)\,v_4(v_4+e)=0.
\]
Every factor is nonzero: a zero factor would be a zero branch or an endpoint
root. Thus the aggregate coefficient still has degree six.

For distance four, put \(V=\prod_i v_i\). Directly from (N5),
\(A(v^{-1})=VA(v)\). At a positive full collision, \(V=1\), the
leading terms add. At a negative full collision, \(V=-1\), they cancel.
Since \(S(v^{-1})=-4-S(v)\), (N6) gives the retained degree-five
coefficient
\[
 -12A(v)(2+S(v))/4608.                                         \tag{N8}
\]
It is nonzero in this mixed family. Here are the necessary details.
Let \(s_j\) be the elementary symmetric functions of the four \(v_i\)
with \(s_4=-1\), and let \(J(z)=\prod_i(z-v_i)\). Then
\[
 2+S(v)=\frac{s_1^2-s_3^2-4s_2}{J(1)J(-1)}.
\]
The root identities from (N1) give
\[
 \begin{aligned}
 s_1-s_3&=-w,\\
 s_1s_3&=4-2t,\\
 s_2(s_1+s_3)&=6tw.
 \end{aligned}
\]
If the numerator vanished, these equations would force
\(q+16t+16=0\). The coefficientwise identity
\[
 B(t,-16(t+1))=-576t^3
\]
rules this out at a negative full collision, because
\[
 F(1)=q^2(q+36t^2)^2,\qquad F(-1)=B(t,q)^2.                    \tag{N9}
\]
Both identities in (N9) are checked over \(\mathbb Q[t,q]\).
There is exactly one cluster at the negative base when it occurs. Every
other distinct base contributes order seven, and that one contributes six.
This proves \(7h-\delta\) for simple roots, including every intersection
of their collision conditions.

### N.4. What confluence does to a coefficient degree

Suppose a root of multiplicity \(m\) is split formally as
\(r+e_1,\ldots,r+e_m\), and choose a local branch \(z\), with
\(r=z+z^{-1}\). Its logarithmic derivative is
\(\alpha=1/(z-z^{-1})\ne0\). Choose \(k\) of the plus branches and
\(m-k\) inverse branches. In the denominator following (N5), exactly the
\(k(m-k)\) cross-branch factors vanish. Each has linear part
\(\alpha(e_i-e_j)\), with \(i\) in the plus set and \(j\) outside it.
All other factors have nonzero limits.

Group the choices of the plus set before taking the confluent divided
difference. This grouped numerator is alternating in the root variables,
so division by their Vandermonde is regular. Every coefficient of \(L_n\)
is Laurent polynomial, and hence has no further poles. Consequently the
coefficient degree can increase by at most \(d=k(m-k)\).

The leading coefficient increases by exactly \(d\). To see that it does not
cancel, take the leading degree-six term and expand its exponential factor.
Up to a common nonzero factor, the required local limit is
\[
 \sum_{\substack{I\subseteq\{1,\ldots,m\}\\ \#I=k}}
 \frac{\exp(\tau\sum_{i\in I}e_i)}
      {\prod_{i\in I,\ j\notin I}(e_i-e_j)},
 \qquad \tau=2\alpha n.
\]
For the multiplicities needed here, its value at all \(e_i=0\) is

| \((m,k)\) | Local value |
|---|---|
| \((2,1)\) | \(\tau\) |
| \((3,1)\) | \(\tau^2/2\) |
| \((3,2)\) | \(\tau^2/2\) |

These identities are algebraic divided differences. The first is
\((e^{\tau e_1}-e^{\tau e_2})/(e_1-e_2)\). The second is its second
divided difference, whose coincident value is the quadratic Taylor coefficient
\(\tau^2/2\). For the third, use the complement of the two-element set;
the expression becomes \(e^{\tau\sum e_i}\) times the second divided
difference of \(e^{-\tau x}\), with the same value. This uses only finite
Taylor coefficients over a characteristic-zero field. It does not use an
analytic limit or an assumption about positive measures.

All common factors are nonzero, including \(\alpha\) and the nonvanishing
factors of (N5). Lower powers of \(n\) have the same pole bound and cannot
cancel this highest power. Thus the exact degree of this grouped coefficient is
\[
 6+k(m-k).
\]
For several repeated roots the contributions add; in particular two double
roots give degree \(6+k_1(2-k_1)+k_2(2-k_2)\).

After this confluence, the coefficient functions are regular whenever the
distinct root groups stay distinct and avoid the endpoints. Further spectral
collisions therefore combine finite coefficient polynomials; they do not create
another degree increase.

### N.5. A double root and every collision on its locus

Let the roots be \(r,r,s,t_0\). The double root is nonzero, by (N7) and
the zero-root derivative calculation. There are eight modes in which its two
branches have the same sign; call these the A modes. They have degree six and
their leading coefficients are the regular repeated-entry values of (N5).
The four mixed-sign modes from that double root, the B modes, have bases
\(2au\,z_s^{\pm1}z_{t_0}^{\pm1}\) and degree seven.

The four B bases are distinct and none is \(\pm2au\): otherwise the two
simple roots would be equal or opposite, or an endpoint would occur.
A collision involving B and one or more A modes retains degree seven,
because only one B mode belongs to each such cluster.

An A-only cluster has at most two modes. Regard an A sign vector as a
four-bit vector with its first two bits equal. A distance-two collision that
flips those first two bits would require \(z_r^4=1\), hence
\(r\in\{0,2,-2\}\), all excluded. The other distance-one and distance-two
collisions were already excluded in subsection N.3. The same binary-code argument
therefore applies. Distance-three pairs retain degree six; the calculation
in subsection N.3 permits repeated entries in (N5). A positive full pair also
retains degree six. The negative full pair has exact degree five by (N8);
the symmetric identities proving its nonvanishing also permit repeated entries.

Exactly four of the \(h\) clusters contain B modes. Their contributions
are eight each, and the others contribute seven, except for the one possible
negative full pair. Thus the order is
\[
 4\cdot8+(h-4)\cdot7-\delta=7h+4-\delta.
\]
This includes intersections of confluence with every spectral collision,
without assuming that the discriminant locus is smooth.

### N.6. The two remaining multiplicity types

For two double roots, write \(R=(x^2+sx+p)^2\). Coefficient comparison gives
\[
 2s=w,\quad p=6t-4,\quad s^2+2p=2t-8,\quad p^2=16-8t.
\]
Since \(t\ne0\), these imply
\[
 t=10/9,\qquad q=-400/9,\qquad
 R=(x^2+wx/2+8/3)^2.                                         \tag{N10}
\]
At this exact rational \((t,q)\), the coefficientwise characteristic replay
and exact polynomial gcd give \(h=9\). There are at most nine confluent
bases, indexed by \((k_1,k_2)\in\{0,1,2\}^2\), so this check proves
that all nine are distinct. Four have degree six, four have degree seven,
and the central mode has degree eight. Their order is
\(4\cdot7+4\cdot8+9=69\). The check also gives \(\delta=0\).
This is exhaustive for this root type because (N10) is forced, not inferred
from a sample.

For a triple root, write \(R=(x-r)^3(x-s)\), with \(y=r^2\).
Matching the two lower coefficients, after using the upper coefficients to
eliminate \(t,w\), gives
\[
 \begin{aligned}
 26r^3+33r^2s+9rs^2+60r+20s&=0,\\
 r^3s+12r^2+12rs+16&=0.
 \end{aligned}
\]
Here \(r\ne0\), and \(y+12\ne0\), since the second equation would
otherwise be \(-128=0\). Therefore
\[
 \begin{aligned}
 s&=-\frac{4(3y+4)}{r(y+12)},\\
 P(y)&=13y^4+144y^3+480y^2+1280y-768=0,\\
 t&=\frac{3y^2+8y+48}{2(y+12)},\\
 q&=\frac{(3y^2+24y-16)^2}{y(y+12)^2}.
 \end{aligned}                                                \tag{N11}
\]
Substitution into the first equation, multiplied by \(r(y+12)^2\), gives
exactly \(2P(y)\); the replay checks every coefficient of this identity.

The eight potential bases are \(2au\,z_r^{2k-3}z_s^{\epsilon}\),
\(k=0,1,2,3\), \(\epsilon\in\{-1,1\}\). Within a fixed sign of
\(\epsilon\), a collision would require \(y\in\{0,1,4\}\).
Between the two signs, it would require
\(s=\pm C_j(r)\), \(j=0,1,2,3\).
Put
\[
 D(y)=y(y+12)^2,\qquad M(y)=16(3y+4)^2,
 \qquad s^2=M(y)/D(y).
\]
The certificate supplies exact Bezout identities between \(P\) and each of
\[
 \begin{aligned}
 &y(y-1)(y-4),\quad M-yD,\quad M-4D,\\
 &M-(y-2)^2D,\quad M-y(y-3)^2D,\\
 &y(y+12),\quad 3y^2+8y+48,\quad 3y^2+24y-16.
 \end{aligned}                                                \tag{N12}
\]
Each identity has the form \(UP+VQ=1\) over \(\mathbb Q[y]\), checked
coefficientwise by the separate replay. The first five exclude every listed
collision, and the remaining ones verify the denominators and nonzero
parameters in (N11). All eight bases are therefore distinct, over every
characteristic-zero field. Four coefficients have degree six and four have
degree eight, giving order \(4\cdot7+4\cdot9=64\). Their distinctness
also gives \(h=8\) and \(\delta=0\).

Finally, a quadruple root \(R=(x-r)^4\) would have \(r\ne0\) and,
with \(y=r^2\), would require
\[
 17y+20=0,\qquad y^2+24y+16=0.
\]
The latter's remainder modulo the former is \(-3136/289\ne0\).
Thus no further multiplicity type exists in this nonzero family.

### N.7. Minimality, coefficient field, and initial index

An exponential polynomial \(\lambda^N p(N)\), with \(\lambda\ne0\)
and \(\deg p=d\), has a generating-function pole of exact order \(d+1\)
at \(z=\lambda^{-1}\). Its leading pole coefficient contains the nonzero
factor \(d!\) times the leading coefficient of \(p\). Distinct bases give
distinct poles. Hence the minimal eventual recurrence order is exactly the
sum of these \(d+1\), after combining equal bases. This proves the lower
bounds as well as the annihilators counted above.

The calculations can be made in a finite splitting field. Permuting roots
or inverting the chosen lifts permutes the summands. Consequently the monic
minimal annihilator is invariant under the splitting field's Galois group,
so it lies in the original field. Its order is unchanged by that extension.
Likewise, the gcd degrees in (N3) are unchanged by field extension.

For repeated roots, (N4) uses the rows of derivatives divided by their
factorials and the confluent Vandermonde
\(\prod_{i<j}(r_j-r_i)^{m_im_j}\). The low-index boundary identities of
Theorem L are polynomial identities in the quartic coefficients, so they
remain valid under this confluence. Equivalently, the initial coefficient
determinants are unchanged when evaluations are replaced by these normalized
jets. Thus the exponential polynomial gives the actual \(W_N\) for every
\(N\ge1\). Its continuation at zero is still \(1/2\), by the same
degree-three boundary determinant as in Theorem L.

Every base is nonzero. The minimal annihilator therefore has nonzero constant
coefficient, and its residual at zero is half that coefficient, since the actual
empty determinant is one. The recurrence cannot be extended to index zero
without increasing its order. This completes the stated classification.

### N.8. Exact examples and reproduction

These examples use \(a=u=1\), \(b=t\), and \(v^2=q\). Negative or
nonsquare \(q\) can be interpreted in the corresponding quadratic extension.

| \(t\) | \(q\) | Root type | \(h\) | \(\delta\) | Minimal order |
|---|---|---|---|---|---|
| 1 | 4 | \(1+1+1+1\) | 16 | 0 | 112 |
| 1 | 1 | \(1+1+1+1\) | 14 | 0 | 98 |
| 1 | -36 | \(1+1+1+1\) | 15 | 0 | 105 |
| \(8/9\) | \(-16/9\) | \(1+1+1+1\) | 15 | 1 | 104 |
| 2 | -144 | \(1+1+1+1\) | 14 | 1 | 97 |
| 2 | \(-36/5\) | \(1+1+1+1\) | 12 | 0 | 84 |
| \(2/15\) | \(8/3\) | \(2+1+1\) | 12 | 0 | 88 |
| \(10/9\) | \(1/54\) | \(2+1+1\) | 12 | 0 | 88 |
| \(10/9\) | \(-400/9\) | \(2+2\) | 9 | 0 | 69 |
| \(40/27\) | \(-400/81\) | \(2+1+1\) | 12 | 0 | 88 |

An order-64 example is given exactly by (N11), taking the unique positive
root of \(P(y)\). It lies between \(49/100\) and \(1/2\): the endpoint
values have opposite signs and \(P'(y)>0\) for \(y>0\).

For rational \(t,q\), the defining determinants can be calculated without
choosing a square root. Divide moment number \(j\) by \(w^j\). The new
even and odd moments are respectively
\[
 \frac{(1+tm)\binom{2m}{m}}{q^m},\qquad
 \frac{(2m+1)(1+tm)\binom{2m}{m}}{q^m}.
\]
The determinant of these rational moments, multiplied by
\(q^{N(N-1)/2}\), is the normalized \(W_N\). This follows from the
diagonal row and column basis change, including singular minors.

The separate standard-library replay verifies the nine characteristic
coefficient lists on 45 degree-complete parameter nodes. At coefficient
index \(j\le8\), homogeneity gives degree at most \(j\) in \(t\)
and at most \(j\) in \(w\); evenness in \(w\) gives degree at most
\(\lfloor j/2\rfloor\) in \(q\). The 9-by-5 grid therefore proves
coefficient coverage; reciprocal symmetry supplies the other coefficients.
It also verifies (N9), (N12), the triple-root elimination, and the two-double
support calculation.

The ten sample GFs are reconstructed under Theorem L's all-index bound and
have exact cross-multiplication and degree-preserving modular Bezout
certificates. Their parameter interpolation uses 57 distinct squared nodes,
covering the proved degree at most 56 in \(q\) through \(W_{112}\).
The finite confluence regressions independently use rational lifted roots,
polynomial jets, and actual monomial determinants. Those regression quartics
need not belong to the mixed family; their orders are checks of the mechanism.

Finite samples alone do not prove this theorem. Universal coverage follows
the collision and confluence arguments above and the coefficientwise leaves
with their proved bounds. Section 7 states the remaining broader scope.

## 6. Certificates and reproduction

### 6.1. How a finite certificate proves an all-index assertion

The written proofs supply the uniform annihilators and their start indices.
Finite determinant values alone would not supply those conclusions.
For clarity, the algebraic bridge used by the generating-function
certificates is recorded here.

**Certificate lemma.** Suppose a sequence satisfies a monic recurrence
\(A(S)W_N=0\) of order \(r\) for every \(N\ge1\). Set
\[
 \begin{aligned}
 G(z)&=\sum_{N\ge0}W_Nz^N,\\
 D(z)&=z^rA(z^{-1}),\\
 H(z)&=[D(z)G(z)]_{\le r}.
 \end{aligned}                                                    \tag{E2}
\]
Then \(D(0)=1\) and \(G=H/D\). The numerator \(H\) is determined by
\(W_0,\ldots,W_r\). If proposed polynomials \(U,V\), with \(V(0)=1\),
satisfy \(UD=HV\), then \(G=U/V\). If they are coprime, its reduced
denominator has degree \(\deg V\), which is exactly the minimal eventual
scalar constant-coefficient recurrence order.

**Proof.** The coefficient of \(z^{N+r}\) in \(DG\) is the stated
recurrence residual. Thus every coefficient above degree \(r\) vanishes,
which proves (E2) and the cross-multiplication assertion. If a monic
recurrence of order \(d\) holds eventually, multiplication of \(G\) by
its reversed polynomial yields a polynomial. Coprimality of \(U,V\) forces
\(V\) to divide that reversed polynomial, so \(d\ge\deg V\).
Conversely, multiplication by \(V\) gives an eventual recurrence of order
\(\deg V\). This proves equality, including order zero.

The modular witnesses in the source package establish coprimality after
clearing rational denominators. They retain both polynomial degrees and
verify a Bezout identity equal to one modulo the stated prime. A nonconstant
common factor over the rationals would retain a nonconstant common factor
under that degree-preserving reduction, contradicting the identity. This
supplies an exact lower bound, rather than an inference from a fitted list.

### 6.2. Portable replay

Extract the current sequence-formula source ZIP into a fresh directory.
Python 3.10+ and its standard library suffice for the mathematical replay:

```sh
python -B tools/verify_sequence_final_edition.py --output final-edition-checks
```

The command runs the six retained replayers supporting this edition: the
quadratic order-63 sample, the mixed order-112 sample, the sharp uniform
quadratic theorem, the uniform mixed theorem, the complete boundary table,
and the complete nonzero rule. It checks the component outputs and writes a
combined receipt. The original certificates are proposed coefficient lists;
the replayers reconstruct and verify their identities.

The N replay includes 45 degree-complete characteristic nodes, eight exact
Bezout leaves, ten reduced generating-function certificates, confluence
regressions, and 2,732 direct defining determinant comparisons. The written
collision and confluence arguments provide universal coverage. Some general
quartics in the confluence regressions lie outside the mixed family; those
checks do not assert that every regression order occurs in that family.

For an individual normalized parameter, use, for example:

```sh
python -B tools/sequence_hankel_orders.py --coefficients verification/sequence-library/hankel-compression/interior-coefficients.json --t 1 --q 1
```

This returns minimal eventual order 98. For a negative fractional argument,
use the equals form, for example `--q=-16/9`. The browser engine can be
compared with the Python engine using the optional Node.js 24 checks:

```sh
python -B -m unittest discover -s tools -p test_sequence_hankel_orders.py -v
node --test tools/test_sequence_hankel_orders.mjs
```

The versioned PDF and standalone HTML are produced from this same manuscript.
Their build receipt pins the manuscript, the four imported proof sources,
the renderer, and the output hashes. PDF rendering uses the retained MathJax
SVG runtime and a Chromium browser; it is separate from the standard-library
mathematical replay. Typography may vary with a different rendering engine.

### 6.3. Source lineage and review

This edition is based on source revision
`af2d91ead77d06f7903239f1da293e26bb00f240` and its 101-member source archive,
whose SHA-256 is
`e7a43e634553bf7d814518cd65a14769a2d2094afd8db85e5641675afca52ccd`.
That archive is retained unchanged as
`sequence-formula-source-af2d91ea.zip`.
The predecessor mathematical notes and their certificates remain unchanged.
The assembly report records the editorial joins, updated historical scope
sentences, and local cross-reference labels used in the consolidated paper.
Every imported TeX expression is checked against its source.

The source reviews are retained as `SHARP_QUADRATIC_REVIEW.md`,
`UNIFORM_MIXED_REVIEW.md`, `EXCEPTIONAL_ORDERS_REVIEW.md`, and
`INTERIOR_ORDERS_REVIEW.md`. The final-edition review checks their integration,
the boundary/nonzero partition, notation, certificate dependencies, and the
new certificate lemma. These are project self-reviews. Automated code tests,
browser checks, and source hashes serve their stated purposes; they do not
constitute independent mathematical review or Lean formalization.

## 7. Scope of the final edition

The mixed linear-weight, first-order-operator minimal-order classification
is complete as stated by Theorems M and N, with Theorem L giving the optimal
uniform bound. The quadratic identity-operator bound in Theorem K is also
sharp, but it does not classify the minimal order at every quadratic weight.
Pointwise quadratic-weight orders, higher-degree weights, and higher-order
mixed operators remain separate research targets.

This is a finalized edition of those stated results and their reproducible
evidence. It makes no historical novelty claim. Later corrections or
extensions should receive a new version while preserving this edition's
sources and hashes.
