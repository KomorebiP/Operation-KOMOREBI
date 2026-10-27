# Exact p-adic contact and an explicit small-prime denominator budget

## A. The depleted determinant

For every s>=1 define

\[
F_{s,p}(t)=\sum_{p\nmid k}\frac{t^k}{k^s},
\qquad
\mathcal H_{r,p}(t)=\det(F_{i+j+1,p}(t))_{0\le i,j<r}.
\]

These series converge for v_p(t)>0. Their Cauchy-Binet expansion is the expansion
in 03_Hankel_Determinant.md restricted to p-unit indices.

Let u_1<...<u_r be the first r positive integers not divisible by p. Explicitly

\[
u_j=j+\left\lfloor\frac{j-1}{p-1}\right\rfloor,
\qquad S_{p,r}=\sum_{j=1}^r u_j.
\]

Here the symbol u_j denotes the unit index, not a valuation vector from earlier papers.
For h>=1 put s_h=(p-1)p^{h-1}, write r=q_h s_h+b_h with 0<=b_h<s_h, and set

\[
E_{p,r}=\sum_{h\ge1}\left(s_h\binom{q_h}{2}+b_hq_h\right).
\]

The sum is finite: its terms vanish once s_h>=r.

### Theorem 4. Exact local valuation

If v_p(t)=e>=1, then

\[
\boxed{v_p(\mathcal H_{r,p}(t))=eS_{p,r}+2E_{p,r}.}
\]

In particular this value is finite, so the depleted determinant is nonzero.

Proof. For any r distinct p-unit indices, the p-adic valuation of their Vandermonde
is the sum, over h>=1, of the number of pairs equal modulo p^h. There are s_h
available unit residue classes. For fixed r the number of coincident pairs is
minimized when the class counts differ by at most one. The minimum is
s_h binom(q_h,2)+b_hq_h.

The first r positive p-units simultaneously realize this minimum for every h:
each block of p^h consecutive integers contains each unit residue once. Therefore
their Vandermonde valuation is E_{p,r}, and every other subset has at least that
valuation. They also uniquely minimize the sum of the indices. The corresponding
term has valuation e S_{p,r}+2E_{p,r}; every other term has strictly greater
valuation. The ultrametric inequality with a unique minimum proves the assertion.

For r=2 this specializes to

\[
v_p(\mathcal H_{2,p}(t))=
\begin{cases}3e,&p\ne2,\\4e+2,&p=2.\end{cases}
\]

For p>r the general formula is simply e r(r+1)/2.

## B. Remove dependence on p-depletion where possible

The undepleted H_r is one universal expression in ordinary polylogarithms.
At each p it has a convergent power-series interpretation when v_p(t)>0, but its
coefficients need not be p-integral.

### Theorem 5. Exact good-prime valuation

If p>3r-1 and v_p(t)=e>=1, then

\[
v_p(\mathcal H_r(t))=e\,r(r+1)/2.
\]

Proof. Write a=2r-1 (only in this proof), s=r(r+1)/2. A term with ordered
indices k_i has valuation

\[
e\sum_i k_i+2\sum_{i<j}v_p(k_j-k_i)-a\sum_i v_p(k_i).
\]

For h>=1, p> a+r implies p^h-r>a h; the h=1 case is immediate and successive
increments are larger than a. Therefore, if p|k_i, then
k_i-i >= p^{v_p(k_i)}-r > a v_p(k_i).
If p does not divide k_i, the denominator loss is zero and k_i>=i.
Thus every subset other than {1,...,r} has valuation strictly above e s.
The first subset has coefficient a p-adic unit. This gives exact equality.

### Theorem 6. A fixed small-prime correction for all primes

Let a_r=2r-1 and define

\[
C_{r,p,i}=\max\left(0,\sup_{h\ge1}
\left\{a_r h-\left(p^h\left\lceil\frac i{p^h}\right\rceil-i\right)\right\}\right),
\quad C_{r,p}=\sum_{i=1}^r C_{r,p,i}.
\]

The supremum is a finite maximum because p^h grows faster than h. The budget
vanishes for p>3r-1. Hence

\[
B_r=\prod_{p\le3r-1}p^{C_{r,p}}
\]

is a fixed positive integer depending only on r. Then, for every prime p and
v_p(t)=e>=1,

\[
\boxed{v_p(B_r\mathcal H_r(t))\ge e\,r(r+1)/2.}
\]

Here v_p(0)=+infinity; unlike Theorem 4, this lower bound alone does not prove
nonvanishing at the finitely many small primes.

Proof. Each k_i>=i is a multiple of p^{h_i}, h_i=v_p(k_i). Thus

\[
a_rh_i-(k_i-i)\le C_{r,p,i}.
\]

The term valuation is at least

\[
e s+\sum_i[(k_i-i)-a_rh_i]\ge e s-C_{r,p}.
\]

The numerator Vandermonde only improves the estimate. All terms converge, so the
same lower bound holds for their sum. Multiplication by B_r proves the claim.

For r=2 one valid, not necessarily minimal, budget is B_2=2^7*3^3=3456.
This is NOT a theorem about the denominator of a motivic class. It is a theorem
about the explicitly defined convergent analytic series at its small p-adic argument.

## C. What this does not establish

None of the above identifies a complex value H_r(t), a p-adic value H_r(t),
and the different sector arguments a/c, b/c, c/a as the absolute values of one
nonzero algebraic number. A product formula cannot be applied to this collection
without an independently constructed arithmetic realization and norm comparison.
