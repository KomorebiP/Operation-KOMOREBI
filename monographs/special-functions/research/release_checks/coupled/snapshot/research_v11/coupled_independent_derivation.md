# Independent derivation and adversarial review of coupled growth

Checkpoint: SF-DISCOVERY-110. Date: 2026-10-09.

**Normalized claim.** For every real quadruple (0<q,r,a,b<1), there is a unique pair of entire functions satisfying

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

Both functions have the same order \(\rho>0\), determined uniquely by

\[
\operatorname{spr} A(\rho)=1,\qquad
A(s)=\begin{pmatrix}q^s&r^s\\a^s&b^s\end{pmatrix}.
\]

**Primary verdict: proved as written.** The argument below additionally proves positive finite lower and upper type, and identifies the ratio of the two component types. It does not establish a limiting leading constant or historical novelty.

This review was assigned the exact equation and proposed conclusion before seeing another author's proof. Its critical derivation uses explicit polynomial times exponential differential barriers, developed independently. During that work the other proof agent sent an unsolicited outline of a different logarithmic comparison argument. The final type-alignment observation was suggested by that agent and independently checked below. Thus the barrier proof is a distinct reconstruction, while the type-alignment section is a cross-check of a shared observation. No numerical experiment is used as proof.

## 1. Exact definitions and dependency graph

Write \(F_1=U,F_2=V\), and

\[
(p_{11},p_{12})=(q,r),\qquad(p_{21},p_{22})=(a,b).
\]

The entries in row \(i\) are the scales at which the first and second components occur in the equation for \(F_i'\). This establishes the orientation of the matrix. The relevant function space is entire functions on \(\mathbb C\), with ordinary power-series coefficients. The normalization is exactly as displayed above.

The proof dependencies are:

1. Formal coefficient recursion gives uniqueness, oddness, positivity and a tangent majorant.
2. The tangent majorant gives a local analytic solution. Strict contraction of every argument extends it to the whole plane.
3. An elementary two by two calculation produces \(\rho\) and positive right and left eigenvectors.
4. Positive coefficients identify maximum modulus with evaluation on the positive real axis.
5. Delayed comparison and explicit upper and lower barriers give logarithmic growth comparable to \(R^\rho\).
6. Integral inequalities identify the lower and upper type vectors.

Every leaf needed for the conclusion is derived below. The use of the local tangent series is the elementary identity \((\tan z)'=1+\tan^2 z\), whose nearest poles have modulus \(\pi/2\). No project-specific theorem, external novelty claim, computation output or conditional asymptotic ansatz is required.

## 2. Existence, uniqueness and positivity

Let

\[
F_i(z)=\sum_{n\geq0}c_{i,n}z^{2n+1}.
\]

The normalization imposes \(c_{1,0}=c_{2,0}=1\), and for \(n\geq1\),

\[
(2n+1)c_{i,n}
=\sum_{j+k=n-1}c_{1,j}c_{2,k}
p_{i1}^{2j+1}p_{i2}^{2k+1}.
\]

These recursions uniquely determine the formal pair and give \(c_{i,n}>0\). Recursion in all ordinary degrees, starting from zero constant term, gives zero coefficients in every even degree, so no additional nonodd analytic solution is lost by the displayed form.

If \(t_n\) are the coefficients of \(\tan z\), then induction gives \(c_{i,n}\leq t_n\), because every scale factor is at most one. The pair therefore converges on \(|z|<\pi/2\). In particular,

\[
x\leq F_i(x)\leq\tan x\qquad(0\leq x\leq1).
\]

Set \(Q=\max(q,r,a,b)<1\). If the functions are analytic on \(|z|<R\), their right-hand sides are analytic on \(|z|<R/Q\). Integrating those right-hand sides from zero produces analytic extensions, and the extensions agree with the existing solution by the differential equations. Iteration gives the entire pair. Formal uniqueness and the identity theorem give uniqueness among normalized entire solutions.

Since all coefficients are nonnegative,

\[
M_i(R):=\max_{|z|=R}|F_i(z)|=F_i(R).
\]

Both components are strictly increasing on the nonnegative real axis and satisfy \(F_i(x)\geq x\) for all \(x\geq0\).

## 3. The characteristic root and eigenvectors

The equation \(\det(I-A(s))=0\) is

\[
(1-q^s)(1-b^s)=(ra)^s.
\]

For \(s>0\), its left side increases strictly from zero to one, and its right side decreases strictly from one to zero. Consequently there is exactly one root \(\rho>0\).

At this root, one eigenvalue of \(A(\rho)\) is one. The other eigenvalue is \(q^\rho+b^\rho-1\), which lies strictly between minus one and one. Thus the spectral radius is one. Conversely, if the spectral radius is one, the positive two by two matrix has positive largest eigenvalue one, so the determinant condition follows. This can also be checked directly from its quadratic eigenvalue formula.

Positive right and left eigenvectors are, respectively,

\[
v^{(0)}=(r^\rho,1-q^\rho)^T,\qquad
w^{(0)}=(a^\rho,1-q^\rho)^T.
\]

Normalize the right eigenvector \(v\) by \(\max(v_1,v_2)=1\), and write \(v_*:=\min(v_1,v_2)>0\). The identities used in the proof are

\[
v_i=p_{i1}^\rho v_1+p_{i2}^\rho v_2,\qquad i=1,2.
\]

No orientation can be inferred merely from the scalar spectral radius, because transposition preserves that radius. The explicit eigenvectors above resolve that ambiguity: the growth vector is a **right** eigenvector for the displayed row convention.

## 4. Delayed differential comparison

Let \(m=\min(q,r,a,b)>0\). Suppose a positive differentiable pair \(W_i\), defined for \(x\geq mX\), satisfies

\[
W_i(x)\leq F_i(x)\quad(mX\leq x\leq X),
\]

and

\[
W_i'(x)\leq1+W_1(p_{i1}x)W_2(p_{i2}x)\quad(x\geq X).
\]

Then \(W_i\leq F_i\) on the whole ray \([mX,\infty)\). Indeed, on \([X,X/Q]\) all delayed arguments are at most \(X\) and at least \(mX\). The differential inequalities and the seed ordering can therefore be integrated. Repetition on \([X/Q^j,X/Q^{j+1}]\) proves the assertion. Reversing both inequalities gives the upper comparison. Positivity is essential because it makes each product increasing in its two arguments.

## 5. Independent polynomial-exponential barriers

Put

\[
d=\rho-1,\qquad C_i=(p_{i1}p_{i2})^d,\qquad
C_*:=\min_i C_i,\quad C^*:=\max_i C_i.
\]

For arbitrary constants \(D,k>0\), consider

\[
W_i(x)=D x^d\exp(kv_i x^\rho)\quad(x>0).
\]

The characteristic identity gives the exact formulas

\[
W_1(p_{i1}x)W_2(p_{i2}x)
=D^2 C_i x^{2d}\exp(kv_i x^\rho),
\]

\[
\frac{W_i'(x)}{W_1(p_{i1}x)W_2(p_{i2}x)}
=\frac{k\rho v_i+d x^{-\rho}}{D C_i}.
\]

These are identities, not a leading-order substitution. The common power \(d=\rho-1\) is what cancels the polynomial powers in the ratio.

### 5.1 Explicit lower barrier

Define

\[
c=e^{-1}\min(1,m^{2-\rho}),\qquad
X\geq\max\left(1,
\sqrt{\frac{\rho+(\rho-1)_+}{cC_*}}\right),
\]

\[
D=cX^{2-\rho},\qquad k=X^{-\rho}.
\]

For \(x=Xt\) with \(m\leq t\leq1\),

\[
\frac{W_i(x)}x=c t^{\rho-2}\exp(v_i t^\rho)
\leq ce\max_{m\leq t\leq1}t^{\rho-2}\leq1.
\]

Thus \(W_i(x)\leq x\leq F_i(x)\) on the seed interval. For \(x\geq X\),

\[
k\rho v_i+d x^{-\rho}
\leq[\rho+(\rho-1)_+]X^{-\rho}
\leq cC_*X^{2-\rho}
\leq DC_i.
\]

The derivative ratio is therefore at most one. In particular,

\[
W_i'(x)\leq W_1(p_{i1}x)W_2(p_{i2}x)
\leq1+W_1(p_{i1}x)W_2(p_{i2}x).
\]

Comparison proves

\[
\log F_i(x)\geq kv_i x^\rho+d\log x+\log D\qquad(x\geq X).
\]

This proof includes \(\rho<1\). A negative derivative of the comparison function at some early points is harmless for a lower differential comparison.

### 5.2 Explicit upper barrier

Let \(d_+=\max(d,0)\) and \(d_-=\max(-d,0)\). Choose \(K>0\) satisfying all of

\[
K\geq1,\qquad
K\geq\frac{\log(\tan(1)/m^{d_+})}{v_*m^\rho},
\]

\[
K\rho v_*\geq d_-+2C^*,\qquad
K\rho v_*\geq2d_-,\qquad
Kv_*\geq[\log(1/C_*)]_+.
\]

Take \(W_i(x)=x^d\exp(Kv_i x^\rho)\). On \([m,1]\),

\[
W_i(x)\geq m^{d_+}\exp(Kv_*m^\rho)\geq\tan(1)\geq F_i(x).
\]

Write \(P_i(x)=W_1(p_{i1}x)W_2(p_{i2}x)\). For \(x\geq1\), the exact derivative ratio gives \(W_i'(x)/P_i(x)\geq2\). Also

\[
\frac{d}{dx}\log P_i(x)=\frac{2d+K\rho v_i x^\rho}{x}\geq0,
\]

and \(P_i(1)=C_i e^{Kv_i}\geq1\). Hence

\[
W_i'(x)\geq2P_i(x)\geq1+P_i(x),\qquad x\geq1.
\]

Upper comparison proves

\[
\log F_i(x)\leq Kv_i x^\rho+d\log x\qquad(x\geq1).
\]

### 5.3 Consequence

Define lower and upper type at exponent \(\rho\) by

\[
\ell_i=\liminf_{R\to\infty}\frac{\log M_i(R)}{R^\rho},\qquad
\tau_i=\limsup_{R\to\infty}\frac{\log M_i(R)}{R^\rho}.
\]

The barriers establish

\[
0<kv_i\leq\ell_i\leq\tau_i\leq Kv_i<\infty.
\]

Consequently both the lower order and the order of each entire function equal \(\rho\). In particular, the proposed common entire order theorem is fully proved.

## 6. Exact alignment of the two type vectors

This strengthens the bounds without asserting a limiting leading constant. Write \(H_i(R)=\log F_i(R)\). Monotonicity and the integral equation imply, for all sufficiently large \(R\),

\[
H_i(R)\leq\log(2R)+H_1(p_{i1}R)+H_2(p_{i2}R).
\]

Indeed the integral is at most its interval length times the endpoint product, and the product is eventually at least one. Integration over the final unit interval also gives

\[
H_i(R)\geq H_1(p_{i1}(R-1))+H_2(p_{i2}(R-1)),\qquad R>1.
\]

Dividing by \(R^\rho\), applying the elementary rules for the limsup and liminf of a finite sum, and using the already proved finite bounds yields

\[
\tau\leq A(\rho)\tau,\qquad \ell\geq A(\rho)\ell.
\]

Let \(w>0\) be the left eigenvector from Section 3. Multiplication by \(w^T\) shows that each componentwise inequality is equality, since a nonzero nonnegative vector has strictly positive dot product with \(w\). The eigenspace for eigenvalue one is one dimensional. Therefore

\[
\ell=\alpha v,\qquad\tau=\beta v,\qquad
0<\alpha\leq\beta<\infty.
\]

Thus both the lower-type ratio and upper-type ratio are exactly \(v_1:v_2\). If a full limit \(\log F_i(R)/R^\rho\) exists for either component, then \(\alpha=\beta\), and the full limit exists for the other component as well. This argument does **not** prove \(\alpha=\beta\), the existence of a common leading scalar, or convergence of \(H_1(R)/H_2(R)\). It also does not assert anything about directional complex-plane indicators.

## 7. Degeneracies, attempted counterexamples and scope

### 7.1 Scalar diagonal

If \(q=r=a=b=c\), uniqueness gives \(U=V\). The matrix equation is \(2c^\rho=1\), exactly the scalar characteristic law. Both type vectors are multiples of \((1,1)\).

More generally, if \(\{q,r\}=\{a,b\}\), a diagonal pair solves both equations and hence is the unique pair. The relevant root is \(q^\rho+r^\rho=1\). These degeneracies do not contradict the coupled theorem. They do mean that a claim that every parameter choice gives a nonreducible new family would be false.

### 7.2 Relabeling the two components

Exchanging \(U\) and \(V\) changes the scales to \((q',r',a',b')=(b,a,r,q)\). The new matrix is \(P A(s)P\), where \(P\) interchanges the two coordinates. Both the spectral radius and the type-vector transformation are consistent.

### 7.3 Zero-scale boundary is a genuine obstruction

The hypothesis that every scale is strictly positive cannot be dropped. Set \(q=0\), keeping \(0<r,a,b<1\). Then \(U(z)=z\), and

\[
V'(z)=1+azV(bz),\qquad
V(z)=\sum_{n\geq0}\frac{a^n b^{n^2}}{(2n+1)!!}z^{2n+1}.
\]

Both entire functions have order zero. For \(V\), this follows directly by bounding the logarithm of its summands by a quadratic in \(n\), which gives \(\log M_V(R)=O((\log R)^2)\). Nevertheless, the naive matrix equation has a positive root because

\[
1-b^\rho=(ra)^\rho
\]

still has one. For example \(r=a=b=1/2\) gives \(2^{-\rho}=(\sqrt5-1)/2\). Thus extending the theorem to zero scales would produce a false conclusion. A zero argument annihilates a product and changes the interaction graph.

### 7.4 Unit scales and signed or complex coefficients

If every scale equals one, uniqueness gives \(U=V=\tan z\), which is meromorphic and not entire. The strict upper bound on scales is also essential. Cases with some unit scales require a separate analysis. Complex or signed scales are outside the claim: coefficient positivity, positive-axis maximum modulus, and the monotone comparison proof all depend on the stated real positive domain.

## 8. Obligation matrix and closeout

| Obligation | Status | Evidence |
|---|---|---|
| Exact normalization and ordinary-series conventions | Passed | Sections 1 and 2 |
| Unique normalized entire pair | Passed | Coefficient recursion and contraction extension |
| Characteristic root exists and is unique | Passed | Strictly opposite monotonicity in the determinant equation |
| Matrix orientation and type eigenvector | Passed | Row-by-component derivation and explicit eigenvectors |
| Upper growth bound at the critical exponent | Passed | Exact supersolution with seed bound by tangent |
| Positive lower growth bound at the critical exponent | Passed | Exact subsolution seeded solely by \(F_i(x)\geq x\) |
| Both components have order and lower order \(\rho\) | Passed | Positive finite type bounds |
| Exact ratios for lower and upper type | Passed | Integral inequalities and positive left eigenvector |
| Limit of type or a leading scalar | Not addressed | Would require \(\alpha=\beta\) |
| Historical novelty or priority | Out of scope | No priority conclusion is drawn |
| Boundary with a zero scale | Failed extension | Explicit order-zero counterexample |
| General complex scales or unit scales | Out of scope | Positivity or entire continuation can fail |
| Numerical reproduction of the universal theorem | Not required | The proof is analytic and self-contained |

There is no remaining gap in the normalized claim. The strongest safe statement established here is existence, uniqueness, positive coefficients, exact common order and lower order, positive finite lower and upper type, and common positive-eigenvector alignment of those two type vectors. The cheapest useful check for a manuscript implementation is to substitute the barrier into the differential inequality symbolically and verify the seed-interval inequalities. A numerical fit to a finite coefficient range cannot replace those steps and cannot decide equality of lower and upper type.
