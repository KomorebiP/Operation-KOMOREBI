# Closed Forms II and III: further sequence realizations

Author: Komorebi P.  
Mathematical source dates: 18–19 November 2026.

This supplement fills the main gaps in the first Sequence Library publication of Collections II and III. It records universal identities, their validity conditions, the distinction between source results and new specializations, and the exact integer procedures available in the reader. Historical novelty and pairwise distinctness remain unassessed. The complete original PDF supplements retain the longer proofs.

## 1. Universal Hankel four-hypergeometric formula

Define the moment functional by

\[
\mathcal L[x^{2m}]=\binom{2m}{m},\quad
\mathcal L[x^{2m+1}]=0,\quad
\mathcal L_c[p]=\mathcal L[p]+c\mathcal L[p'].
\]

Let \(S_{\lambda,c}(n)=\mathcal L_c[(x+\lambda)^n]\) and \(H_N=\det[S_{\lambda,c}(i+j)]_{0\le i,j<N}\), with \(H_0=1\). The change from monomials to powers of \(x+\lambda\) is unitriangular, so the Hankel determinant is independent of \(\lambda\).

For \(N\ge1\) and every complex \(c\),

\[
H_N(c)=2^{N-1}\,{}_4F_3\left(
\begin{matrix}-N/2,(1-N)/2,(N-1)/2,N/2\\-1/2,-1/4,1/4\end{matrix};
-c^2/16\right).
\]

The terminating expression is exactly

\[
H_N(c)=2^{N-1}\left[1+\sum_{k=1}^{\lfloor N/2\rfloor}
(-1)^k\frac{(2k-1)N(N-1)}{4k}
\binom{N+2k-2}{4k-2}c^{2k}\right].
\]

The first polynomials are \(1,\ 2-c^2,\ 4-18c^2,\ 8-144c^2+36c^4\) for sizes 1 through 4. For \(c=1\) the size-zero-through-size-eight values are \(1,1,1,-14,-100,56,6112,58304,320448\). A163865 is the original moment sequence \(S_{1,1}(n)\), whose first terms are \(1,2,5,16,47,146,447\), not its Hankel transform.

The proof in Collection II uses \(\mathcal F[p]=\mathcal L[xp']/2\), a quadratic Christoffel factor, and monic Chebyshev polynomials. In the Chebyshev basis the Gram matrix is \(D+cB\), with positive diagonal \(D\) and real symmetric \(B\). Thus every zero of \(H_N(c)\) is real and nonzero for \(N\ge2\), including multiplicities. The generating function in \(N\) is rational and its denominator divides \(((1-2z)^4+4c^2z^2)^3\), giving a recurrence of order at most 12 from \(N=13\). The case \(N=0\) is special: direct insertion into the hypergeometric expression is incorrect.

## 2. One terminating hypergeometric form for two delays

For positive integer delays \(p,q\) and complex \(r,u,v\), define the formal coefficients

\[
C_n=[z^n](1-uz^p-vz^q)^{-r}
=\sum_{pi+qj=n}\frac{(r)_{i+j}u^iv^j}{i!\,j!}.
\]

If \(p=q\), combine \(u\) and \(v\). Otherwise exchange the delays if needed so \(p<q\), and put \(d=\gcd(p,q)\). If \(d\nmid n\), the answer is zero. For \(d\mid n\), put \(P=p/d,\ Q=q/d,\ \nu=n/d,\ D=Q-P\). Let \(I\) be the unique residue in \(\{0,\ldots,Q-1\}\) with \(PI\equiv\nu\pmod Q\), then set \(J=(\nu-PI)/Q\) and \(M=I+J\). If \(J<0\) the answer is zero; otherwise

\[
C_n=\sum_{k=0}^{\lfloor J/P\rfloor}
\frac{(r)_{M+Dk}}{(I+Qk)!(J-Pk)!}u^{I+Qk}v^{J-Pk}.
\]

Using \(\Delta(m,a)=(a/m,(a+1)/m,\ldots,(a+m-1)/m)\), the equivalent form for \(v\ne0\) is

\[
C_n=\frac{(r)_Mu^Iv^J}{I!J!}
\,{}_QF_{Q-1}\left(
\begin{matrix}\Delta(P,-J),\Delta(D,r+M)\\
\Delta(Q,I+1)\setminus\{1\}\end{matrix};
(-1)^P\frac{P^P D^D}{Q^Q}\frac{u^Q}{v^P}\right).
\]

One upper parameter is a nonpositive integer, so the series terminates. The lower parameters are positive. The finite sum is the authoritative definition at zero weights and all exceptional parameters, including negative integral \(r\). Differentiation gives the independent exact recurrence

\[
nC_n=u(n+(r-1)p)C_{n-p}+v(n+(r-1)q)C_{n-q},
\quad C_0=1,\quad C_j=0\ (j<0).
\]

For \(p=2,q=5,u=v=r=1\), the subsequence at indices \(5m\) is

\[
C_{5m}={}_5F_4\left(
\begin{matrix}-m/2,(1-m)/2,(m+1)/3,(m+2)/3,(m+3)/3\\
1/5,2/5,3/5,4/5\end{matrix};108/3125\right).
\]

The Padovan convention is \(a_0=1,a_1=a_2=0\), with generating function \((1-z^2)/(1-z^2-z^3)\). Its \(h\)-fold convolution coefficient is

\[
[z^n]A(z)^h=\sum_{j=0}^{\min(h,\lfloor n/2\rfloor)}
(-1)^j\binom hj\,[z^{n-2j}](1-z^2-z^3)^{-h}.
\]

Every coefficient on the right has a terminating \({}_3F_2\) representation, with the initial cases handled explicitly.

## 3. Polynomially weighted binomial jets

For \(d\ge0\) let

\[
J_{n,d}(\lambda)=\sum_{m=0}^{\lfloor n/2\rfloor}
\binom n{2m}m^{\underline d}\binom{2m}{m}\lambda^{n-2m}.
\]

Set \(J_{n,d}=0\) for \(n<2d\). If \(\lambda\ne0\) and \(n\ge2d\),

\[
J_{n,d}(\lambda)=\frac{n^{\underline{2d}}}{d!}
\lambda^{n-2d}
\,{}_2F_1(d-n/2,d+(1-n)/2;d+1;4/\lambda^2).
\]

The finite binomial sum supplies the \(\lambda=0\) endpoint. Falling factorials form a basis for polynomial weights on the even and odd blocks.

For the integer sequence \(u_n^{(d)}=J_{n,d}(1)+nJ_{n-1,d}(1)\),

\[
\sum_{n\ge0}u_n^{(d)}z^n
=\frac{(2d)!}{d!}z^{2d}\,
\frac{1+(2d-1)z-(2d+4)z^2}
{(1-2z-3z^2)^{d+3/2}}.
\]

At \(d=0\) this recovers the supplied A163865. For \(d=1\) the terms begin \(0,0,2,12,48,200,750,2772\), and for \(d=2\) they begin \(0,0,0,0,12,120,660,3360\).

Put \(A_{n,d}=n(n-2d)+2n-2d-1\). The following exact second-order recurrence holds for \(n\ge2d+2\):

\[
\begin{aligned}
&(n-2d)(n(n-2d)-5)u_n^{(d)}\\
&=\big((2n-2d-6)A_{n,d}+3(n-1)(n-2d-1)\big)u_{n-1}^{(d)}\\
&\quad+3(n-1)(A_{n,d}-3)u_{n-2}^{(d)}.
\end{aligned}
\]

The initial values are zero below \(2d\), followed by \((2d)!/d!\) and \(2(2d+1)!/d!\). This cross-multiplied form avoids illegal division at a vanishing leading coefficient.

## 4. Universal weighted Hankel formula and the d=1,2 target

Define \(F_d[x^{2m}]=m^{\underline d}\binom{2m}{m}\), with odd moments zero, and \(L_{d,c}[p]=F_d[p]+cF_d[p']\). The Hankel transform of \(u_n^{(d)}\) is exactly \(W_N^{[d]}(1)\), the \(\lambda=1,c=1\) specialization of Collection III.

Write \(a_d=(2d)!/d!\), \(\rho_d=(-1)^{d+1}2a_d\), \(\gamma_d=2d+1\), and \(k=d+1\). Set \(C_0(x)=2,C_1(x)=x,C_{n+1}(x)=xC_n(x)-C_{n-1}(x)\), with \(C_{-n}=C_n\). Define

\[
\widehat P_n(x)=\sum_{j=0}^{k}(-1)^j\binom kj
n^{\underline j}(n-k-1-j)^{\underline{k-j}}C_{n-2j}(x),
\]

\[
R_d(N)=\prod_{j=0}^{d-1}\frac{j!}{(d+j+1)!}
(N-2d+j)_{d+1}.
\]

Reduce \(\widehat P_n(x)\) modulo \(x^2+\gamma_dcx-4\), giving \(A_n(c)x+B_n(c)\). The exact fixed-size expression is

\[
W_N^{[d]}(c)=
\frac{\rho_d^N d!(d+1)!R_d(N)}
{2^{2d+3}(2d+1)!(2d+2)!}
\big(B_NA_{N+1}-A_NB_{N+1}\big),
\qquad N\ge1.
\]

It remains valid at repeated roots without evaluating any roots, and \(W_0=1\) separately. The initial singular block is

\[
W_N=0\quad(1\le N\le2d),\qquad
W_{2d+1}=(-1)^d\left((2d)!/d!\right)^{2d+1}.
\]

Let \(K=(d+1)(d+2)\). The generating function denominator divides

\[
\left[(1+\rho_dz)^4+(2d+1)^2c^2\rho_d^2z^2\right]^{K+1}.
\]

The *minimal eventual* constant-coefficient recurrence order is \(d(d+1)+1\) for \(c=0\), \(3K+4\) for \((2d+1)c=\pm4i\), and \(4K+4\) otherwise. At \(c=1\), the orders for \(d=0,1,2\) are exactly \(12,28,52\). The all-real-zero theorem of the unweighted \(d=0\) family does not generalize to every \(d>0\).

The published algorithm computes these determinants through polynomial remainders in \(O(dN)\) arithmetic operations rather than expanding an \(N\times N\) Hankel determinant. This is an arithmetic-operation count, not a fixed-bit-complexity bound.

## 5. Six formulas recovered from the papers

**P1: four-block tangent coefficients.** For \(D_4(z)=\cos(z/\sqrt2)\cosh(z/\sqrt2)\),

\[
T_4(n)=\frac{T_2(2n+1)}{2^{2n+1}}
=-\frac{2^{2n+3}(2^{4n+4}-1)}{4n+4}B_{4n+4}.
\]

Bernoulli numbers follow the normalization \(t/(e^t-1)=\sum B_mt^m/m!\).
[Registry source](https://github.com/KomorebiP/Operation-KOMOREBI/blob/d04c44bd6938ba68431a3957cff67e24b709e5d3/monographs/special-functions/supporting-sources/projector-special-functions-registry/Projector_Special_Functions_Registry.tex#L336).

**P2: four-block reciprocal powers.** For normalized coefficients of \(\sec^r z\),

\[
A_4^{[r]}(n)=4^{-n}\sum_{j=0}^{2n}(-1)^j
\binom{4n}{2j}A_2^{[r]}(j)A_2^{[r]}(2n-j).
\]

This follows from factoring \(D_4(z)^{-r}\).
[Registry source](https://github.com/KomorebiP/Operation-KOMOREBI/blob/d04c44bd6938ba68431a3957cff67e24b709e5d3/monographs/special-functions/supporting-sources/projector-special-functions-registry/Projector_Special_Functions_Registry.tex#L242).

**P3: integer Meixner–Pollaczek polynomials.** For \(s>0\), the classical terminating expression is

\[
Q_n(s,x)=i^n(s)_n\,{}_2F_1(-n,s/2+ix;s;2),
\]

with recurrence \(Q_0=1,Q_1=2x,Q_{n+1}=2xQ_n-n(n+s-1)Q_{n-1}\).
The recurrence is a polynomial identity even outside the hypergeometric parameter domain.
[Paper VI](https://github.com/KomorebiP/Operation-KOMOREBI/blob/d04c44bd6938ba68431a3957cff67e24b709e5d3/monographs/special-functions/supporting-sources/projector-generated-special-functions-vi-release/Projector_Generated_Special_Functions_VI.tex#L567).

**P4: shape-transfer beta moments.** For \(a,b>0\), set \(\mu_n=(a)_n/(a+b)_n\). Then

\[
\sum_{n\ge0}\mu_nz^n={}_2F_1(1,a;a+b;z),\qquad
\det[\mu_{i+j}]_{0\le i,j<m}
=\prod_{j=0}^{m-1}\frac{j!(a)_j(b)_j}{(a+b)_{m+j-1}}.
\]

The case \(a=b=1\) is the Hilbert moment determinant.
[Paper VI](https://github.com/KomorebiP/Operation-KOMOREBI/blob/d04c44bd6938ba68431a3957cff67e24b709e5d3/monographs/special-functions/supporting-sources/projector-generated-special-functions-vi-release/Projector_Generated_Special_Functions_VI.tex#L739).

**P5: beta-binomial splitter polynomial.** For \(w_{n,r}=\binom nr(a)_r(b)_{n-r}/(a+b)_n\),

\[
\sum_{r=0}^{n}w_{n,r}z^r={}_2F_1(-n,a;a+b;1-z),\qquad
\sum_{r=0}^{n}r^{\underline\ell}w_{n,r}
=n^{\underline\ell}\frac{(a)_\ell}{(a+b)_\ell}.
\]

[Paper VI](https://github.com/KomorebiP/Operation-KOMOREBI/blob/d04c44bd6938ba68431a3957cff67e24b709e5d3/monographs/special-functions/supporting-sources/projector-generated-special-functions-vi-release/Projector_Generated_Special_Functions_VI.tex#L594).

**P6: squarefree zeta-ratio identity.** Paper III already contains the exact finite expansion

\[
E_{a,\beta,q}(k)=\sum_{j=0}^{2k}(-1)^j\binom{2k}{j}
\frac{\zeta(2a+\beta j)}{\zeta(4a+2\beta j)}
\prod_{p\mid q}(1+p^{-(2a+\beta j)})^{-1}.
\]

It holds for \(a>1/2,\beta>0,q\ge1\) and \(k\ge0\). Its proof uses a finite binomial expansion and an absolutely convergent squarefree Euler product, not a numerical zeta approximation.

## 6. Evidence and release boundaries

The original research archives report 205,982 exact assertions for Collection II and 33,689 for Collection III. These are archived counts and are not the test count of this integration. The separate repository suite checks the finite formulas by independent coefficient extraction, recurrence evaluation, direct exact determinants and polynomial identities.

Existing SHA-256 receipts retain the original integer records and indices. The historical OEIS comparison manifest covers only its original 2,292 records. New specializations remain marked as not yet compared against that snapshot. A163865 is a source-supplied identification, not a novelty claim.
