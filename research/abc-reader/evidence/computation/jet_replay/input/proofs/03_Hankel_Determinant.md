# A nonzero contact determinant from polylogarithmic moments

## Definition

For r>=1, put

\[
\mathcal H_r(t)=\det(\operatorname{Li}_{i+j+1}(t))_{0\le i,j<r}.
\]

This uses weights 1 through 2r-1. The series is first interpreted formally over Q,
and analytically for |t|<1. No algebraicity of its value at a rational point is assumed.

For r=2,

\[
\mathcal H_2(t)=\operatorname{Li}_1(t)\operatorname{Li}_3(t)-\operatorname{Li}_2(t)^2.
\]

This is built from the same mixed-weight coordinates as the preceding jet filter,
but packages independent moment directions into one determinant.

## Theorem 1. Exact expansion

\[
\mathcal H_r(t)=
\sum_{1\le k_1<\cdots<k_r}
 t^{k_1+\cdots+k_r}
 \frac{\prod_{i<j}(k_j-k_i)^2}{\prod_{i=1}^r k_i^{2r-1}}.
\]

Proof. The moment matrix is the sum of rank-one matrices

\[
\sum_{k\ge1}\frac{t^k}{k}
(1,k^{-1},\ldots,k^{-(r-1)})^T
(1,k^{-1},\ldots,k^{-(r-1)}).
\]

Apply Cauchy-Binet to finite partial sums. A Vandermonde determinant is obtained
for each r-element subset. Passing to the formal limit is coefficientwise valid:
only finitely many subsets contribute to a fixed power of t.

## Theorem 2. Exact contact order

Set s_r=r(r+1)/2. Then

\[
\operatorname{ord}_0\mathcal H_r=s_r,
\qquad
[t^{s_r}]\mathcal H_r=\prod_{k=1}^r k^{-(2k-1)}.
\]

Proof. The unique subset with minimum index sum is {1,...,r}. Its Vandermonde
coefficient is nonzero. Using product_{i<j}(j-i)=product_{j=1}^{r-1}j! simplifies
the coefficient to the displayed product. Thus the growth in contact order is real
Taylor cancellation, not a reinterpretation of a weight label.

## Theorem 3. Positive real nonvanishing and uniform bound

For every r>=1 and 0<t<1,

\[
0<\mathcal H_r(t)\le e^{1/4}\bigl[-\log(1-t)\bigr].
\]

Proof. The expansion consists of positive terms. Equivalently the moment matrix
is positive definite because r distinct nodes already give a nonzero Vandermonde
minor. Hadamard's inequality gives

\[
\mathcal H_r(t)\le\prod_{i=0}^{r-1}\operatorname{Li}_{2i+1}(t)
\le[-\log(1-t)]\prod_{i=1}^{r-1}\zeta(2i+1).
\]

All terms below are positive, so sums can be interchanged:

\[
\sum_{i\ge1}(\zeta(2i+1)-1)
=\sum_{k\ge2}\frac1{k(k^2-1)}=\frac14.
\]

Use log(1+x)<=x to bound the product by e^{1/4}.
For t=a/c and t=b/c the upper bounds become e^{1/4} log(c/b) and
 e^{1/4} log(c/a), respectively.

## The third complex chart

For fixed r, either consistent boundary branch at t=c/a>1 has a bound

\[
|\mathcal H_r(c/a)|\le C_r(1+\log c)^{r^2}
\]

for some constant depending only on r. The integer-order polylogarithm inversion
formula expresses Li_s(x) in terms of Li_s(1/x) and a fixed polynomial in log(-x).
For s>=2 the inverse term is bounded by zeta(s); for s=1 use
Li_1(x)=-log(1-x) and |log(b/a)|<=log c. Each determinant term has total weight
sum_i(i+pi(i)+1)=r^2. No nonvanishing at every point of this third chart is asserted.

## Source and originality boundary

The polylogarithm series and inversion formulas are classical (NIST DLMF 25.12.10
and 25.12.13). Cauchy-Binet, Vandermonde determinants and Hadamard are classical.
The above is a derivation for this continuation, not a historical novelty claim.
