# 84. Finite exact checking on a continuum

For three predictive coordinates, the spatial unit circle admits two rational charts. For $s\in\{1,-1\}$ and $t\in[-1,1]$, put

$$
d(t)=1+t^2,\qquad
r_s(t)=\frac{s}{d(t)}(1-t^2,2t).
$$

The charts cover the two semicircles, including their endpoints. For an operator $F_a(u)$ and required margin $\kappa\geq0$, form polynomial vectors and scalars

$$
\begin{aligned}
w_{a,s}(u,t)&=F_a(u)(d(t),s(1-t^2),2st)^{\mathsf T},\\
f_{a,s}(u,t)&=w_{a,s,0}(u,t)-\kappa d(t),\\
h_{a,s}(u,t)&=f_{a,s}(u,t)^2-w_{a,s,1}(u,t)^2-w_{a,s,2}(u,t)^2.
\end{aligned}
$$

No square root occurs in these polynomials.

**Proposition 75. Rational semicircle and Bernstein certificate.** If $f_{a,s}$ and $h_{a,s}$ are nonnegative on $[-1,1]^2$ for both charts and every action, then $\sigma_a(u)\geq\kappa$ for every observation. For rational operators and geometry, nonnegative tensor-Bernstein coefficients on a complete rational subdivision of that square give a finite exact witness. If the actual margin is uniformly strictly greater than $\kappa$, sufficiently fine dyadic subdivision succeeds.

**Proof.** The first polynomial inequality establishes output orientation after subtracting $\kappa d$. The second then gives

$$
w_{a,s,0}-\|(w_{a,s,1},w_{a,s,2})\|_2\geq\kappa d.
$$

Divide by $d>0$ to obtain the required margin on the circle. For fixed $u$, the function consisting of affine output mass minus the norm of affine spatial output is concave in the input. Every point in the closed disk is a convex combination of circle points. Concavity therefore extends the lower bound to the disk.

On any rectangle mapped affinely to $[0,1]^2$, the tensor-Bernstein basis functions are nonnegative and sum to one. A polynomial with nonnegative coefficients in that basis is nonnegative throughout the rectangle. If the rectangles cover the square, their inequalities prove the global statement. The reference verifier checks coverage through a complete subdivision tree, not by accepting an arbitrary list of rectangles.

For termination under strict margin, both $f$ and $h$ are strictly positive on the compact square. Their minima are positive. For a fixed-degree polynomial on a small cell of side at most $\delta$, its Taylor expansion at one corner has constant term equal to its value there and nonconstant coefficients bounded uniformly by $O(\delta)$. The linear change from the fixed-degree power basis to the Bernstein basis is fixed and bounded. Thus every Bernstein coefficient differs from that constant value by $O(\delta)$, uniformly over cells. At sufficiently small $\delta$ all coefficients are positive. A finite dyadic subdivision attains that size. $\square$

This proof is a specialized use of classical Bernstein range bounds [R22]. It does not claim that a negative Bernstein coefficient proves the polynomial negative. Such a coefficient can merely mean that further subdivision is needed. A negative evaluated corner, by contrast, is an actual counterexample. At a zero-margin boundary, finite termination of this particular witness language is not promised. The exact conformal and matrix certificates of preceding blocks remain useful there.

The two tests are both necessary to this sufficient certificate. The squared inequality alone also admits reversed mass orientation. Both charts are required. A verifier that omits one chart has not covered the circle.

