# Exact test of a direct algebraic realization by truncation

Let K>=r. Replace Li_s(t) by sum_{k=1}^K t^k/k^s and let H_{r,K} be the resulting
determinant. This is a nonzero rational polynomial.

Put L_K=lcm(1,...,K), s=r(r+1)/2, and d=rK-r(r-1)/2. Then

\[
A_{r,K}(t)=L_K^{r^2}\mathcal H_{r,K}(t)\in\mathbb Z[t],
\quad \operatorname{ord}_0 A_{r,K}=s,
\quad \deg A_{r,K}=d.
\]

Integrality follows by scaling row i by L_K^i, column j by L_K^j, and each row
by one further L_K: the entry L_K^{i+j+1} sum t^k/k^{i+j+1} is integral.
The exact degree and order follow from the unique largest and smallest index subsets.

For a reduced rational t=a/c, the obvious integral scalar is

\[
W_{r,K}(a,c)=c^d A_{r,K}(a/c).
\]

### Theorem 7. This construction loses the output-c contact

If p>K and p|c while gcd(a,c)=1, then

\[
p\nmid W_{r,K}(a,c).
\]

Proof. Modulo p only the top-degree coefficient survives. The unique top subset
is {K-r+1,...,K}. Its coefficient is a p-adic unit because all its indices,
differences, and L_K are p-units. The remaining factor a^d is also a unit.

This is a failed candidate for the required output witness, not a universal
impossibility theorem for all determinant methods.

## Small explicit examples

\[
\mathcal H_{2,2}(t)=\frac{t^3}{8},
\qquad
\mathcal H_{2,3}(t)=\frac{t^3}{8}+\frac{4t^4}{27}+\frac{t^5}{216}
=\frac{t^3(27+32t+t^2)}{216}.
\]

Clearing the minimal displayed denominator and the projective denominator in the
second expression gives

\[
W(a,c)=a^3(27c^2+32ac+a^2).
\]

For p>3 dividing c, W is congruent to a^5 modulo p. It has no positive
output-c contact at that prime.

Thus the actual attempted scalar realization does not pass the witness gate.
Taking a long series truncation is not a way around the all-place height problem.
