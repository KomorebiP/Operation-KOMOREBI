## Precise background statement

Let \(H\) be a real Hilbert space. In particular \(H\) is complete and contains zero, even when \(H\) is the zero-dimensional space. For every nonempty closed convex set \(C \subseteq  H\) there is a unique point \(p \in  C\) such that

\[
\forall x\in C,\qquad \|p\|\le \|x\|.
\]

Putting the point to be projected equal to zero in `lem:projection-tool` gives

\[
\forall x\in C,\qquad
\langle -p,x-p\rangle\le0,
\quad\text{equivalently}\quad
\langle p,x-p\rangle\ge0.                 \tag{1}
\]

Consequently

\[
\begin{aligned}
\|x\|^2
 &=\|p\|^2+2\langle p,x-p\rangle+\|x-p\|^2\\
 &\ge\|p\|^2+\|x-p\|^2,
\end{aligned}
\]

so

\[
\forall x\in C,\qquad
\|x-p\|^2\le\|x\|^2-\|p\|^2.           \tag{2}
\]

This is the exact sign needed for the argument. For a general convex \(C\) it is an inequality, not an equality. In the affine case, applying (1) to both signs of every direction gives orthogonality and therefore equality.

## Nested convex projection lemma

**Statement with quantifiers.** Let \((C_n)\) indexed by \(n \in  \mathbb{N}\) be sets in a real Hilbert space \(H\). Assume

\[
\begin{gathered}
\forall n\in\mathbb N,\quad
C_n\ne\varnothing,\quad C_n\text{ is closed and convex},\\
\forall n,m\in\mathbb N,\quad n\le m\Longrightarrow C_m\subseteq C_n.
\end{gathered}
\]

Let \(p_n\) be the unique minimum-norm element of \(C_n\). Then

\[
n\le m\Longrightarrow
\|p_n\|\le\|p_m\|,
\qquad
\|p_m-p_n\|^2\le\|p_m\|^2-\|p_n\|^2. \tag{3}
\]

Moreover, the following conditions are equivalent:

\[
\bigcap_{n\in\mathbb N}C_n\ne\varnothing,
\qquad
\exists M\in[0,\infty)\ \forall n\in\mathbb N,\quad\|p_n\|\le M.
                                                               \tag{4}
\]

When they hold, there is a unique minimum-norm point \(p_*\) in the intersection, \(p_n \to  p_*\) in norm, and

\[
\forall n\in\mathbb N,\qquad
\|p_*-p_n\|^2\le\|p_*\|^2-\|p_n\|^2.  \tag{5}
\]

For any specified \(M\) bounding all the norms, \(\|p_*\|\le M\). If the intersection is empty, the minimum norms tend to positive infinity in the precise sense

\[
\forall R\in\mathbb R\ \exists N\in\mathbb N\ \forall n\ge N,
\qquad \|p_n\|>R.                       \tag{6}
\]

**Proof.** For \(n \le  m\), nesting puts \(p_m\) in \(C_n\). Minimality gives the norm comparison, and (2) with \(C = C_n\), \(p = p_n\), and \(x = p_m\) gives (3).

Suppose a finite \(M\) bounds all norms. The increasing real sequence \(e_n = \|p_n\|^2\) lies in \([0,M^2]\). Let

\[
L=\sup\{e_n:n\in\mathbb N\}.
\]

This is a finite real number. For every \(\varepsilon > 0\), the defining approximation property of the supremum gives an index \(N\) with

\[
L-e_N<\varepsilon^2.
\]

For arbitrary \(m,n \ge  N\), exchange the two indices if needed so that \(n \le  m\). By (3), monotonicity, and the upper bound \(L\),

\[
\|p_m-p_n\|^2\le e_m-e_n\le L-e_N<\varepsilon^2.
\]

The norm is nonnegative, hence \(\|p_m-p_n\| < \varepsilon\). This proves the full Cauchy condition, not merely a bound on successive differences. Completeness supplies \(p_*\) with \(p_n \to  p_*\) in norm. Fix \(k\). Every \(n \ge  k\) satisfies \(p_n \in  C_k\). Closedness of \(C_k\) therefore gives \(p_* \in  C_k\). Since \(k\) was arbitrary, \(p_*\) lies in the intersection. Norm continuity also gives \(\|p_*\| \le  M\).

For any \(x\) in the intersection and every \(n\), minimality in \(C_n\) gives \(\|p_n\| \le  \|x\|\). Passing to the limit gives \(\|p_*\| \le  \|x\|\). The intersection is closed and convex, because each of its constituent sets is closed and convex. It is now known to be nonempty. Uniqueness of its minimum-norm point follows from the projection lemma. Applying (2) directly to \(x = p_*\) in \(C_n\) proves (5). Equivalently, (5) follows by passing \(m \to  \infty\) in (3).

Conversely, if \(x\) belongs to the intersection, then the finite number \(M = \|x\|\) bounds every \(\|p_n\|\). This proves (4). If the intersection is empty, the minimum norms cannot be bounded. Given \(R \ge  0\), choose \(N\) with \(\|p_N\| > R\) and use monotonicity for every \(n \ge  N\). For \(R < 0\), nonnegativity suffices with \(N = 0\). This proves (6).

**What the lemma does not say.** An arbitrary sequence \(x_n \in  C_n\) need not converge. It is the sequence of unique minimum-norm points \(p_n\) that converges when its norms are bounded. No effective rate is supplied unless a rate for the scalar energy deficit \(L-e_n\) is separately available. Formula (5) is an exact bound relative to that deficit, not a computable uniform rate over all input problems.

## WR01: bounded approximate feasibility

Let \(H\) and \(Y\) be real Hilbert spaces, \(T : H \to  Y\) a bounded linear map, and \(r \in  Y\). Fix a real number \(M \ge  0\). The useful fixed-budget form is

\[
\begin{aligned}
&\exists a\in H,\quad \|a\|\le M\ \text{ and }\ Ta=r\\
&\quad\Longleftrightarrow\quad
\exists (u_j)_{j\in\mathbb N}\subseteq H,\quad
 (\forall j,\ \|u_j\|\le M)
 \ \text{ and }\ \|Tu_j-r\|\longrightarrow0.       \tag{7}
\end{aligned}
\]

The theorem's unfixed-budget equivalence follows by existentially quantifying \(M\). A sequence whose norms have some finite upper bound has such a nonnegative upper bound, so this is the usual meaning of bounded sequence.

**Forward implication.** If \(a\) solves the equation with \(\|a\| \le  M\), choose \(u_j = a\) for every \(j\). Its residual is identically zero.

**Reverse implication.** Suppose the sequence \(u_j\) satisfies the right side of (7). For \(n \in  \mathbb{N}\) put

\[
\delta_n=\frac1{n+1},\qquad
C_n=\{a\in H:\ \|a\|\le M,\quad\|Ta-r\|\le\delta_n\}. \tag{8}
\]

Here \(n+1\) is interpreted as a positive real number. Thus \(\delta_n > 0\), \(\delta_n\) decreases with \(n\), and \(\delta_n \to  0\).

Each \(C_n\) is nonempty. Indeed, residual convergence gives some \(j\) with \(\|Tu_j-r\| < \delta_n\), while the original uniform norm bound already gives \(\|u_j\| \le  M\). No assertion that the same \(j\) works for all \(n\) is used. No monotone selection of such indices is needed.

Each \(C_n\) is closed. The two maps \(a \mapsto  \|a\|\) and \(a \mapsto  \|Ta-r\|\) are continuous, the latter because \(T\) is bounded and linear. Their real sublevel sets at \(M\) and \(\delta_n\) are closed, and \(C_n\) is their intersection.

Each \(C_n\) is convex. For \(a,b \in  C_n\) and \(\theta  \in  [0,1]\), linearity and the triangle inequality give

\[
\|\theta a+(1-\theta)b\|
 \le\theta\|a\|+(1-\theta)\|b\|\le M,
\]

and

\[
\begin{aligned}
\|T(\theta a+(1-\theta)b)-r\|
 &=\|\theta(Ta-r)+(1-\theta)(Tb-r)\|\\
 &\le\theta\|Ta-r\|+(1-\theta)\|Tb-r\|\le\delta_n.
\end{aligned}
\]

Finally, \(C_m \subseteq  C_n\) whenever \(n \le  m\), since \(\delta_m \le  \delta_n\).

Let \(p_n\) be the minimum-norm point of \(C_n\). Its membership gives \(\|p_n\| \le  M\). The nested convex projection lemma supplies a norm limit \(p_*\) belonging to every \(C_n\). Hence

\[
\|p_*\|\le M,
\qquad
\forall n,\quad\|Tp_*-r\|\le\frac1{n+1}.
\]

The last nonnegative norm must be zero: if it were positive, choose \(n\) with \(1/(n+1)\) smaller than it. Therefore \(Tp_* = r\), establishing (7).

This constructs a strongly convergent sequence of auxiliary minimizers \(p_n\). It makes no strong-convergence assertion about the given sequence \(u_j\) and does not assert that \(p_n\) is a subsequence of \(u_j\). The original monograph's orthonormal-sequence counterexample remains valid without alteration.

**Optional selection observation.** The intersection of the sets in (8) is precisely the set of exact solutions of norm at most \(M\). The auxiliary limit is its unique minimum-norm point. It is also the minimum-norm point of the full nonempty exact fiber: any exact solution of smaller norm would lie in the same budget ball and contradict minimality. This observation is not needed to change the principal WR01 statement.

**Escape corollary with exact quantifiers.** Suppose \(r \notin  \operatorname{ran} T\) and \(Tu_j \to  r\) in norm. Then \(\|u_j\| \to  \infty\). If not, there is \(R \ge  0\) with arbitrarily late indices \(j\) satisfying \(\|u_j\| \le  R\). Recursively choose strictly increasing such indices \(j_k\). The subsequence remains residual-convergent and is bounded by \(R\). Applying (7) to this subsequence produces a preimage of \(r\), a contradiction. The corollary does not claim that arbitrary unattainable data have approximate preimages. When \(r\) is outside the closure of the range, no residual-convergent sequence of this kind exists.

## WR02: the affine equality and all conclusions

Suppose \((A_n)\) is a nested sequence of nonempty closed affine subsets of \(H\), and let \(a_n\) be its minimum-norm points. These sets are convex, so the preceding nested lemma already proves the equivalence between nonempty intersection and bounded minimum norms, strong convergence in the bounded case, uniqueness of the least-norm limit, and divergence of norms in the empty-intersection case.

To retain the exact WR02 identities, fix \(n\) and write \(A_n = a_n + L_n\), where \(L_n\) is its linear direction space. For every \(h \in  L_n\), both \(a_n+h\) and \(a_n-h\) lie in \(A_n\). The two instances of (1) give

\[
\langle a_n,h\rangle\ge0,
\qquad
-\langle a_n,h\rangle\ge0.
\]

Thus \(a_n\) is orthogonal to \(L_n\). If \(n \le  m\), then \(a_m \in  A_n\) and \(a_m-a_n \in  L_n\). The norm expansion now has zero cross term:

\[
\|a_m\|^2
 =\|a_n\|^2+\|a_m-a_n\|^2.
\]

Consequently

\[
\|a_m-a_n\|^2=\|a_m\|^2-\|a_n\|^2\qquad(n\le m). \tag{9}
\]

If the minimum norms are bounded, the strong limit \(a_*\) belongs to \(A_n\) for every \(n\). Therefore \(a_*-a_n \in  L_n\), and the same orthogonality proves directly

\[
\|a_*-a_n\|^2=\|a_*\|^2-\|a_n\|^2.                \tag{10}
\]

This preserves all clauses of the inherited WR02 statement. Affinity is essential to (9) and (10). For nested convex subsets \([1,\infty)\) and \([2,\infty)\) of \(\mathbb{R}\), the minimum points are 1 and 2. Their squared distance is 1 while the difference of squared norms is 3. Thus the general convex inequality is strict in this elementary example.

## WR03: fixed-budget attainment without weak subsequences

Continue with \(T : H \to  Y\) bounded linear, \(r \in  Y\), and \(M \ge  0\). Define

\[
B_M=\{a\in H:\|a\|\le M\},\qquad
S_M=\{\|r-Ta\|:a\in B_M\},\qquad
\beta(M)=\inf S_M.                                \tag{11}
\]

Since \(0 \in  B_M\), the set \(S_M\) is nonempty and contains \(\|r\|\). It is bounded below by zero. Therefore \(\beta(M)\) is a finite real number with \(0 \le  \beta(M) \le  \|r\|\), and

\[
\forall a\in B_M,\qquad \beta(M)\le\|r-Ta\|.        \tag{12}
\]

For every positive \(\delta\), the defining infimum property supplies an \(a \in  B_M\) such that

\[
\|r-Ta\|<\beta(M)+\delta.                          \tag{13}
\]

To justify the strict inequality, if all residuals were at least \(\beta(M)+\delta\), that larger number would be a lower bound of \(S_M\), contrary to \(\beta(M)\) being its greatest lower bound.

Set, for every \(n \in  \mathbb{N}\),

\[
C_n=\{a\in H:\ \|a\|\le M,\quad
           \|r-Ta\|\le\beta(M)+1/(n+1)\}.          \tag{14}
\]

Property (13) proves nonemptiness. Continuity and the convexity calculation in Section 5.3 prove closedness and convexity. The residual thresholds decrease, so the sets are nested. Their minimum-norm points \(p_n\) all have norm at most \(M\). The nested convex projection lemma gives a strong limit \(a_M\) in every \(C_n\). Thus \(\|a_M\| \le  M\) and

\[
\forall n,\qquad
\|r-Ta_M\|\le\beta(M)+1/(n+1).
\]

Letting \(n \to  \infty\) gives \(\|r-Ta_M\| \le  \beta(M)\). Inequality (12) gives the reverse inequality. Hence

\[
\|a_M\|\le M,\qquad \|r-Ta_M\|=\beta(M).          \tag{15}
\]

The infimum is attained. This proof does not presuppose that \(T(B_M)\) is closed, and it does not assume the residual-minimizing corrections are bounded independently of \(M\). \(M\) is fixed throughout this construction.

The intersection in (14) consists exactly of the budget-optimal corrections. Thus the auxiliary construction selects their unique minimum-norm member. Existence of some optimum, rather than this additional selection description, is the inherited principal claim.

## Remaining WR03 clauses

These arguments retain the source theorem's precise scope and can be combined with Section 5.5 to give a complete replacement proof.

### Monotonicity

If \(0 \le  M_1 \le  M_2\), then \(B_{M_1} \subseteq  B_{M_2}\). Taking the infimum over the larger set cannot increase it, so

\[
\beta(M_2)\le\beta(M_1).
\]

### Convexity on the nonnegative budget ray

Let \(M_1,M_2 \ge  0\) and \(\theta  \in  [0,1]\). Choose attained minimizers \(a_1,a_2\) supplied by (15). The correction \(a_{\theta}  = \theta a_1+(1-\theta )a_2\) satisfies

\[
\|a_\theta\|\le\theta M_1+(1-\theta)M_2.
\]

Its residual is \(\theta (r-Ta_1)+(1-\theta )(r-Ta_2)\). Therefore

\[
\begin{aligned}
\beta(\theta M_1+(1-\theta)M_2)
 &\le\|r-Ta_\theta\|\\
 &\le\theta\beta(M_1)+(1-\theta)\beta(M_2).
\end{aligned}
\]

This proves convexity, including \(\theta  = 0\), \(\theta  = 1\), and equal or zero budgets.

### The operator-norm Lipschitz bound

Suppose \(0 \le  M_1 \le  M_2\). If \(M_2 = 0\) then \(M_1 = 0\) and the desired estimate is equality. Otherwise \(M_2 > 0\). Choose an optimum \(a_2\) at \(M_2\) and let \(a' = (M_1/M_2)a_2\). Since \(0 \le  M_1/M_2 \le  1\),

\[
\|a'\|\le M_1,
\quad
\|a_2-a'\|=(1-M_1/M_2)\|a_2\|\le M_2-M_1.
\]

Using the candidate \(a'\), the triangle inequality, boundedness of \(T\), and then monotonicity,

\[
\begin{aligned}
\beta(M_1)
 &\le\|r-Ta'\|\\
 &\le\|r-Ta_2\|+\|T(a_2-a')\|\\
 &\le\beta(M_2)+\|T\|(M_2-M_1),
\end{aligned}
\]

and hence

\[
0\le\beta(M_1)-\beta(M_2)\le\|T\|(M_2-M_1).        \tag{16}
\]

### Limit as the budget tends to infinity

Let \(C\) be the closure of \(\operatorname{ran} T\). It is a closed linear subspace of \(Y\). The inherited projection lemma supplies \(b = P_C r\) with \(r-b\) orthogonal to \(C\). Put \(q = \|r-b\|\). For every \(a \in  H\), the vector \(b-Ta\) lies in \(C\). The Pythagorean identity gives

\[
\|r-Ta\|^2=q^2+\|b-Ta\|^2.                        \tag{17}
\]

Thus every residual is at least \(q\), so \(\beta(M) \ge  q\) for every \(M \ge  0\).

For every \(\varepsilon > 0\), the fact \(b \in  \operatorname{closure}(\operatorname{ran} T)\) gives some \(a_{\varepsilon} \in  H\) with

\[
\|b-Ta_\varepsilon\|<\varepsilon.
\]

Set \(M_0 = \|a_{\varepsilon}\|\). For every real \(M \ge  M_0\), this one correction is feasible and

\[
q\le\beta(M)\le\|r-Ta_\varepsilon\|
 \le\|r-b\|+\|b-Ta_\varepsilon\|<q+\varepsilon.
\]

This proves the real-parameter limit directly:

\[
\forall\varepsilon>0\ \exists M_0\ge0\ \forall M\ge M_0,
\quad |\beta(M)-q|<\varepsilon.
\]

The order of choices is explicit: choose an approximate preimage depending on \(\varepsilon\), then choose the budget threshold. No uniform correction bound as \(\varepsilon \to  0\) is asserted.

### Equality with the residual floor

For fixed \(M \ge  0\), suppose \(\beta(M) = q\). Choose an attained optimum \(a_M\) from (15). Substituting in (17) gives

\[
q^2=q^2+\|b-Ta_M\|^2,
\]

so \(Ta_M = b\) and \(\|a_M\| \le  M\). Conversely, if \(a\) satisfies \(Ta = b\) and \(\|a\| \le  M\), its residual is \(q\), giving \(\beta(M) \le  q\). The opposite inequality already holds. Thus

\[
\beta(M)=q
\quad\Longleftrightarrow\quad
\exists a\in H,\quad Ta=b\text{ and }\|a\|\le M.    \tag{18}
\]

Finally, independently of whether \(q\) is zero in advance, attainment implies

\[
\beta(M)=0
\quad\Longleftrightarrow\quad
\exists a\in H,\quad Ta=r\text{ and }\|a\|\le M.    \tag{19}
\]

For the forward direction use an attained optimizer and the fact that a vector of norm zero is zero. For the reverse direction evaluate the nonnegative infimum at the exact correction. This avoids silently presupposing \(q = 0\) before exact feasibility is known.

## Closed budget-ball images and the stated uniqueness distinctions

The prose after WR03 states that \(T(B_M)\) is closed and convex even if \(\operatorname{ran} T\) is not closed. This also has a proof independent of weak subsequences once Section 5.3 is available.

Convexity follows because \(B_M\) is convex and \(T\) is linear. To prove closedness, take any sequence \(y_j \in  T(B_M)\) converging in norm to \(y\). For each \(j\) choose \(u_j \in  B_M\) with \(Tu_j = y_j\). Then \(\|u_j\| \le  M\) and \(Tu_j \to  y\). Applying (7) with datum \(y\) yields \(u \in  B_M\) satisfying \(Tu = y\). Thus \(y \in  T(B_M)\). Sequential closedness is closedness in the norm metric on \(Y\).

The set \(T(B_M)\) is nonempty because it contains zero. Projection of \(r\) onto this nonempty closed convex set therefore gives a unique reachable datum \(y_M\) minimizing its distance to \(r\). The residual vector \(r-y_M\) is unique, regardless of whether \(T\) is injective. This is uniqueness of the best image and residual, not uniqueness of all its preimages.

The fiber \(F = \{a \in  H : Ta = y_M\}\) is a nonempty closed affine set. Its minimum-norm point \(a_{\mathrm{min}}\) exists and is unique. Some member \(a_0\) of the fiber has norm at most \(M\) because \(y_M \in  T(B_M)\). Therefore \(\|a_{\mathrm{min}}\| \le  \|a_0\| \le  M\). Hence this uniquely selected least-norm fiber point is itself a budget-optimal correction. Other budget-optimal corrections can exist if the fiber contains further points inside the ball.

The range is the union of the closed budget images at integer budgets: every \(a\) has finite norm, so there is an integer \(n\) with \(\|a\| \le  n\). No conclusion that this increasing union is closed is used or valid in general.

## Boundary cases and scope checks

| Case | Conclusion and proof check |
|---|---|
| \(M = 0\) | The budget ball is \(\{0\}\). WR01's premise forces \(r = 0\) since \(Tu_j = T0 = 0\) for all \(j\). WR03 has \(\beta(0) = \|r\|\) with optimizer \(0\). The nested sets used in both proofs contain \(0\) whenever their stated hypotheses hold. |
| \(H = \{0\}\) | \(T\) is the zero map. WR01 is equivalent to \(r = 0\). WR03 gives \(\beta(M) = \|r\|\) for every \(M \ge  0\), \(C = \{0\}\), \(b = 0\), and \(q = \|r\|\). The fiber for the optimal image is \(\{0\}\). |
| \(Y = \{0\}\) | \(r = 0\) and \(T = 0\). WR01 always has solution \(0\). WR03 gives \(\beta(M) = 0\) for every \(M \ge  0\). Residual uniqueness remains true. Corrections need not be unique when \(H\) is nontrivial. |
| General \(T = 0\) | Same constant budget profile \(\|r\|\), no division by \(\|T\|\), and the Lipschitz right side is zero. |
| A zero minimum norm in the nested lemma | No division by a norm occurs. The supremum energy proof works unchanged, including when \(L = 0\). |
| An empty constraint set | Excluded explicitly in the nested projection lemma. It cannot silently be passed to the projection theorem. Nonemptiness is separately proved for every constructed \(C_n\). |
| Empty intersection | Allowed. It occurs exactly when the minimum norms are unbounded, and monotonicity strengthens unboundedness to divergence to infinity. |
| A supposedly empty Hilbert space | Not a possible vector-space case, because zero exists. Zero dimension is the relevant degenerate case. |
| Nonclosed \(\operatorname{ran} T\) | Allowed throughout. Fixed-budget attainment does not imply global range closedness. |
| Nonseparable \(H\) or \(Y\) | Allowed. The proof makes no separability assumption and no basis choice. |

The nested convex lemma is stated for a countable nested sequence. The applications only require countably many residual thresholds. This file does not claim a general theorem for an arbitrary directed family of closed convex sets.
