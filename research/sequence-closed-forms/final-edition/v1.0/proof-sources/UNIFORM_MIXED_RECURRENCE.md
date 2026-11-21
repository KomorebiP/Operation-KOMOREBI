# A uniform mixed-linear Hankel recurrence

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-21-003, extension L.
Parent publication: 595aa4a61bff25dce221c69b3ca507e43060bd29.
Review status: proved as written in project self-review; independent review,
historical novelty and Lean formalization are unassessed.

## 1. The quartic-functional theorem

Use the formal functional from [the sharp quadratic proof](SHARP_QUADRATIC.md):
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

## 2. Sixteen bases and degree six

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

## 3. The boundary and every specialization

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

## 4. Every linear weight and first-order operator

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

## 5. Generic minimality and remaining scope

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

This does not classify minimal orders on the exceptional parameter locus,
nor settle arbitrary higher-degree weights or higher-order mixed operators.
The more efficient bound 63 for even quadratic weights remains the separate
Theorem K. Review is project self-review; historical novelty, independent
review and Lean formalization remain unassessed.
