# The retained universal jet filter

Define

\[
P_m(X)=X\prod_{j=1}^m(jX-1)=\sum_{s=1}^{m+1}c_{m,s}X^s,
\qquad
\Phi_m(t)=\frac1{(m+1)!}\sum_{s=1}^{m+1}c_{m,s}\operatorname{Li}_s(t).
\]

Using the defining series of Li_s gives

\[
\Phi_m(t)=(-1)^m\sum_{k\ge1}\binom{k}{m+1}\frac{t^k}{k^{m+2}}.
\]

The first nonzero coefficient is at k=m+1, and therefore

\[
\operatorname{ord}_0\Phi_m=m+1,
\qquad
[t^{m+1}]\Phi_m=\frac{(-1)^m}{(m+1)^{m+2}}.
\]

The coefficients of P_m alternate in sign. Evaluating their absolute-coefficient
polynomial at 1 gives

\[
\sum_s |c_{m,s}|=\prod_{j=1}^m(j+1)=(m+1)!.
\]

Since c_{m,1}=(-1)^m, the numerator vector is primitive. The normalized l1 norm is 1.
This is a coefficient identity, not a bound on the arithmetic height of its period
or motivic realization. The number of participating weights grows with m.

For a prime p, deleting the terms with p|k produces

\[
\Phi_{m,p}(t)=(-1)^m\sum_{p\nmid k}\binom{k}{m+1}\frac{t^k}{k^{m+2}}
\in\mathbb Z_p[[t]].
\]

If v_p(t)=e>=1, its valuation is exactly (m+1)e when p does not divide m+1,
and exactly (m+2)e otherwise. In the second case the first surviving index is
m+2 and its coefficient is (up to sign) 1/(m+2)^{m+1}, a p-adic unit.
All subsequent terms have strictly larger valuation.

The differential identity is

\[
(t\,d/dt)^{m+2}\Phi_m(t)=(-1)^m\frac{t^{m+1}}{(1-t)^{m+2}}.
\]

These local and formal statements are valid. They do not identify the p-dependent
functions Phi_{m,p} with the places of a single nonzero algebraic number.
