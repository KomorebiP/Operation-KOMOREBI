# Strong projection route for WR01–WR03

Prepared 2026-10-12 as an alternate written proof and formalization plan. This file does not change the inherited monograph or claim a new Lean verification. The principal WR01, WR02, and WR03 conclusions are preserved.

## Source identity and scope

The supplied base archive identifier is `914bb768686bc186d4baefd53c1e13690346b0f506560ede916d1fb87d7e6794`. The local inherited source root is `work/Komorebi_Space_Monograph_v1.7.0/source/`.

Read source files and SHA-256 digests:

| Source | SHA-256 |
|---|---|
| `chapters/05f_bounded_realization.tex` | `ba8225a03190d4040260eeced4b4c9372d05b85266b27ce53f8cc7ff9ca56acf` |
| `chapters/05g_budget_certificates.tex` | `2c82d9800d3ee58958f953888f95734b47d61f0b05030dd931ce39f51037219b` |
| `chapters/12_proof_tools.tex` | `f98d41969e3048a63a3ed7e19a0e7181ffb309a835ff6cb303a9ced6c5f748bd` |

The only Hilbert-space existence result used below is the monograph's already proved projection lemma, `lem:projection-tool`. Completeness, continuity, elementary real infimum/supremum facts, and the real inner-product norm identity remain explicit dependencies. No weak topology, adjoint, separability argument, diagonal subsequence selection, or finite-dimensional restriction is required for WR01–WR03 by this route.

The new auxiliary lemma concerns nested closed convex sets. WR02 retains its original affine hypothesis and its stronger equality. The auxiliary convex result must not be substituted for that equality.

## 1. Precise background statement

Let H be a real Hilbert space. In particular H is complete and contains zero, even when H is the zero-dimensional space. For every nonempty closed convex set C ⊆ H there is a unique point p ∈ C such that

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

This is the exact sign needed for the argument. For a general convex C it is an inequality, not an equality. In the affine case, applying (1) to both signs of every direction gives orthogonality and therefore equality.

## 2. Nested convex projection lemma

**Statement with quantifiers.** Let (C_n) indexed by n ∈ ℕ be sets in a real Hilbert space H. Assume

\[
\begin{gathered}
\forall n\in\mathbb N,\quad
C_n\ne\varnothing,\quad C_n\text{ is closed and convex},\\
\forall n,m\in\mathbb N,\quad n\le m\Longrightarrow C_m\subseteq C_n.
\end{gathered}
\]

Let p_n be the unique minimum-norm element of C_n. Then

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

When they hold, there is a unique minimum-norm point p_* in the intersection, p_n → p_* in norm, and

\[
\forall n\in\mathbb N,\qquad
\|p_*-p_n\|^2\le\|p_*\|^2-\|p_n\|^2.  \tag{5}
\]

For any specified M bounding all the norms, \(\|p_*\|\le M\). If the intersection is empty, the minimum norms tend to positive infinity in the precise sense

\[
\forall R\in\mathbb R\ \exists N\in\mathbb N\ \forall n\ge N,
\qquad \|p_n\|>R.                       \tag{6}
\]

**Proof.** For n ≤ m, nesting puts p_m in C_n. Minimality gives the norm comparison, and (2) with C = C_n, p = p_n, and x = p_m gives (3).

Suppose a finite M bounds all norms. The increasing real sequence e_n = ‖p_n‖² lies in [0,M²]. Let

\[
L=\sup\{e_n:n\in\mathbb N\}.
\]

This is a finite real number. For every ε > 0, the defining approximation property of the supremum gives an index N with

\[
L-e_N<\varepsilon^2.
\]

For arbitrary m,n ≥ N, exchange the two indices if needed so that n ≤ m. By (3), monotonicity, and the upper bound L,

\[
\|p_m-p_n\|^2\le e_m-e_n\le L-e_N<\varepsilon^2.
\]

The norm is nonnegative, hence ‖p_m−p_n‖ < ε. This proves the full Cauchy condition, not merely a bound on successive differences. Completeness supplies p_* with p_n → p_* in norm. Fix k. Every n ≥ k satisfies p_n ∈ C_k. Closedness of C_k therefore gives p_* ∈ C_k. Since k was arbitrary, p_* lies in the intersection. Norm continuity also gives ‖p_*‖ ≤ M.

For any x in the intersection and every n, minimality in C_n gives ‖p_n‖ ≤ ‖x‖. Passing to the limit gives ‖p_*‖ ≤ ‖x‖. The intersection is closed and convex, because each of its constituent sets is closed and convex. It is now known to be nonempty. Uniqueness of its minimum-norm point follows from the projection lemma. Applying (2) directly to x = p_* in C_n proves (5). Equivalently, (5) follows by passing m → ∞ in (3).

Conversely, if x belongs to the intersection, then the finite number M = ‖x‖ bounds every ‖p_n‖. This proves (4). If the intersection is empty, the minimum norms cannot be bounded. Given R ≥ 0, choose N with ‖p_N‖ > R and use monotonicity for every n ≥ N. For R < 0, nonnegativity suffices with N = 0. This proves (6).

**What the lemma does not say.** An arbitrary sequence x_n ∈ C_n need not converge. It is the sequence of unique minimum-norm points p_n that converges when its norms are bounded. No effective rate is supplied unless a rate for the scalar energy deficit L−e_n is separately available. Formula (5) is an exact bound relative to that deficit, not a computable uniform rate over all input problems.

## 3. WR01: bounded approximate feasibility

Let H and Y be real Hilbert spaces, T : H → Y a bounded linear map, and r ∈ Y. Fix a real number M ≥ 0. The useful fixed-budget form is

\[
\begin{aligned}
&\exists a\in H,\quad \|a\|\le M\ \text{ and }\ Ta=r\\
&\quad\Longleftrightarrow\quad
\exists (u_j)_{j\in\mathbb N}\subseteq H,\quad
 (\forall j,\ \|u_j\|\le M)
 \ \text{ and }\ \|Tu_j-r\|\longrightarrow0.       \tag{7}
\end{aligned}
\]

The theorem's unfixed-budget equivalence follows by existentially quantifying M. A sequence whose norms have some finite upper bound has such a nonnegative upper bound, so this is the usual meaning of bounded sequence.

**Forward implication.** If a solves the equation with ‖a‖ ≤ M, choose u_j = a for every j. Its residual is identically zero.

**Reverse implication.** Suppose the sequence u_j satisfies the right side of (7). For n ∈ ℕ put

\[
\delta_n=\frac1{n+1},\qquad
C_n=\{a\in H:\ \|a\|\le M,\quad\|Ta-r\|\le\delta_n\}. \tag{8}
\]

Here n+1 is interpreted as a positive real number. Thus δ_n > 0, δ_n decreases with n, and δ_n → 0.

Each C_n is nonempty. Indeed, residual convergence gives some j with ‖Tu_j−r‖ < δ_n, while the original uniform norm bound already gives ‖u_j‖ ≤ M. No assertion that the same j works for all n is used. No monotone selection of such indices is needed.

Each C_n is closed. The two maps a ↦ ‖a‖ and a ↦ ‖Ta−r‖ are continuous, the latter because T is bounded and linear. Their real sublevel sets at M and δ_n are closed, and C_n is their intersection.

Each C_n is convex. For a,b ∈ C_n and θ ∈ [0,1], linearity and the triangle inequality give

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

Finally, C_m ⊆ C_n whenever n ≤ m, since δ_m ≤ δ_n.

Let p_n be the minimum-norm point of C_n. Its membership gives ‖p_n‖ ≤ M. The nested convex projection lemma supplies a norm limit p_* belonging to every C_n. Hence

\[
\|p_*\|\le M,
\qquad
\forall n,\quad\|Tp_*-r\|\le\frac1{n+1}.
\]

The last nonnegative norm must be zero: if it were positive, choose n with 1/(n+1) smaller than it. Therefore Tp_* = r, establishing (7).

This constructs a strongly convergent sequence of auxiliary minimizers p_n. It makes no strong-convergence assertion about the given sequence u_j and does not assert that p_n is a subsequence of u_j. The original monograph's orthonormal-sequence counterexample remains valid without alteration.

**Optional selection observation.** The intersection of the sets in (8) is precisely the set of exact solutions of norm at most M. The auxiliary limit is its unique minimum-norm point. It is also the minimum-norm point of the full nonempty exact fiber: any exact solution of smaller norm would lie in the same budget ball and contradict minimality. This observation is not needed to change the principal WR01 statement.

**Escape corollary with exact quantifiers.** Suppose r ∉ ran T and Tu_j → r in norm. Then ‖u_j‖ → ∞. If not, there is R ≥ 0 with arbitrarily late indices j satisfying ‖u_j‖ ≤ R. Recursively choose strictly increasing such indices j_k. The subsequence remains residual-convergent and is bounded by R. Applying (7) to this subsequence produces a preimage of r, a contradiction. The corollary does not claim that arbitrary unattainable data have approximate preimages. When r is outside the closure of the range, no residual-convergent sequence of this kind exists.

## 4. WR02: the affine equality and all conclusions

Suppose (A_n) is a nested sequence of nonempty closed affine subsets of H, and let a_n be its minimum-norm points. These sets are convex, so the preceding nested lemma already proves the equivalence between nonempty intersection and bounded minimum norms, strong convergence in the bounded case, uniqueness of the least-norm limit, and divergence of norms in the empty-intersection case.

To retain the exact WR02 identities, fix n and write A_n = a_n + L_n, where L_n is its linear direction space. For every h ∈ L_n, both a_n+h and a_n−h lie in A_n. The two instances of (1) give

\[
\langle a_n,h\rangle\ge0,
\qquad
-\langle a_n,h\rangle\ge0.
\]

Thus a_n is orthogonal to L_n. If n ≤ m, then a_m ∈ A_n and a_m−a_n ∈ L_n. The norm expansion now has zero cross term:

\[
\|a_m\|^2
 =\|a_n\|^2+\|a_m-a_n\|^2.
\]

Consequently

\[
\|a_m-a_n\|^2=\|a_m\|^2-\|a_n\|^2\qquad(n\le m). \tag{9}
\]

If the minimum norms are bounded, the strong limit a_* belongs to A_n for every n. Therefore a_*−a_n ∈ L_n, and the same orthogonality proves directly

\[
\|a_*-a_n\|^2=\|a_*\|^2-\|a_n\|^2.                \tag{10}
\]

This preserves all clauses of the inherited WR02 statement. Affinity is essential to (9) and (10). For nested convex subsets [1,∞) and [2,∞) of ℝ, the minimum points are 1 and 2. Their squared distance is 1 while the difference of squared norms is 3. Thus the general convex inequality is strict in this elementary example.

## 5. WR03: fixed-budget attainment without weak subsequences

Continue with T : H → Y bounded linear, r ∈ Y, and M ≥ 0. Define

\[
B_M=\{a\in H:\|a\|\le M\},\qquad
S_M=\{\|r-Ta\|:a\in B_M\},\qquad
\beta(M)=\inf S_M.                                \tag{11}
\]

Since 0 ∈ B_M, the set S_M is nonempty and contains ‖r‖. It is bounded below by zero. Therefore β(M) is a finite real number with 0 ≤ β(M) ≤ ‖r‖, and

\[
\forall a\in B_M,\qquad \beta(M)\le\|r-Ta\|.        \tag{12}
\]

For every positive δ, the defining infimum property supplies an a ∈ B_M such that

\[
\|r-Ta\|<\beta(M)+\delta.                          \tag{13}
\]

To justify the strict inequality, if all residuals were at least β(M)+δ, that larger number would be a lower bound of S_M, contrary to β(M) being its greatest lower bound.

Set, for every n ∈ ℕ,

\[
C_n=\{a\in H:\ \|a\|\le M,\quad
           \|r-Ta\|\le\beta(M)+1/(n+1)\}.          \tag{14}
\]

Property (13) proves nonemptiness. Continuity and the convexity calculation in Section 3 prove closedness and convexity. The residual thresholds decrease, so the sets are nested. Their minimum-norm points p_n all have norm at most M. The nested convex projection lemma gives a strong limit a_M in every C_n. Thus ‖a_M‖ ≤ M and

\[
\forall n,\qquad
\|r-Ta_M\|\le\beta(M)+1/(n+1).
\]

Letting n → ∞ gives ‖r−Ta_M‖ ≤ β(M). Inequality (12) gives the reverse inequality. Hence

\[
\|a_M\|\le M,\qquad \|r-Ta_M\|=\beta(M).          \tag{15}
\]

The infimum is attained. This proof does not presuppose that T(B_M) is closed, and it does not assume the residual-minimizing corrections are bounded independently of M. M is fixed throughout this construction.

The intersection in (14) consists exactly of the budget-optimal corrections. Thus the auxiliary construction selects their unique minimum-norm member. Existence of some optimum, rather than this additional selection description, is the inherited principal claim.

## 6. Remaining WR03 clauses

These arguments retain the source theorem's precise scope and can be combined with Section 5 to give a complete replacement proof.

### 6.1 Monotonicity

If 0 ≤ M₁ ≤ M₂, then B_{M₁} ⊆ B_{M₂}. Taking the infimum over the larger set cannot increase it, so

\[
\beta(M_2)\le\beta(M_1).
\]

### 6.2 Convexity on the nonnegative budget ray

Let M₁,M₂ ≥ 0 and θ ∈ [0,1]. Choose attained minimizers a₁,a₂ supplied by (15). The correction a_θ = θa₁+(1−θ)a₂ satisfies

\[
\|a_\theta\|\le\theta M_1+(1-\theta)M_2.
\]

Its residual is θ(r−Ta₁)+(1−θ)(r−Ta₂). Therefore

\[
\begin{aligned}
\beta(\theta M_1+(1-\theta)M_2)
 &\le\|r-Ta_\theta\|\\
 &\le\theta\beta(M_1)+(1-\theta)\beta(M_2).
\end{aligned}
\]

This proves convexity, including θ = 0, θ = 1, and equal or zero budgets.

### 6.3 The operator-norm Lipschitz bound

Suppose 0 ≤ M₁ ≤ M₂. If M₂ = 0 then M₁ = 0 and the desired estimate is equality. Otherwise M₂ > 0. Choose an optimum a₂ at M₂ and let a′ = (M₁/M₂)a₂. Since 0 ≤ M₁/M₂ ≤ 1,

\[
\|a'\|\le M_1,
\quad
\|a_2-a'\|=(1-M_1/M_2)\|a_2\|\le M_2-M_1.
\]

Using the candidate a′, the triangle inequality, boundedness of T, and then monotonicity,

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

### 6.4 Limit as the budget tends to infinity

Let C be the closure of ran T. It is a closed linear subspace of Y. The inherited projection lemma supplies b = P_C r with r−b orthogonal to C. Put q = ‖r−b‖. For every a ∈ H, the vector b−Ta lies in C. The Pythagorean identity gives

\[
\|r-Ta\|^2=q^2+\|b-Ta\|^2.                        \tag{17}
\]

Thus every residual is at least q, so β(M) ≥ q for every M ≥ 0.

For every ε > 0, the fact b ∈ closure(ran T) gives some a_ε ∈ H with

\[
\|b-Ta_\varepsilon\|<\varepsilon.
\]

Set M₀ = ‖a_ε‖. For every real M ≥ M₀, this one correction is feasible and

\[
q\le\beta(M)\le\|r-Ta_\varepsilon\|
 \le\|r-b\|+\|b-Ta_\varepsilon\|<q+\varepsilon.
\]

This proves the real-parameter limit directly:

\[
\forall\varepsilon>0\ \exists M_0\ge0\ \forall M\ge M_0,
\quad |\beta(M)-q|<\varepsilon.
\]

The order of choices is explicit: choose an approximate preimage depending on ε, then choose the budget threshold. No uniform correction bound as ε → 0 is asserted.

### 6.5 Equality with the residual floor

For fixed M ≥ 0, suppose β(M) = q. Choose an attained optimum a_M from (15). Substituting in (17) gives

\[
q^2=q^2+\|b-Ta_M\|^2,
\]

so Ta_M = b and ‖a_M‖ ≤ M. Conversely, if a satisfies Ta = b and ‖a‖ ≤ M, its residual is q, giving β(M) ≤ q. The opposite inequality already holds. Thus

\[
\beta(M)=q
\quad\Longleftrightarrow\quad
\exists a\in H,\quad Ta=b\text{ and }\|a\|\le M.    \tag{18}
\]

Finally, independently of whether q is zero in advance, attainment implies

\[
\beta(M)=0
\quad\Longleftrightarrow\quad
\exists a\in H,\quad Ta=r\text{ and }\|a\|\le M.    \tag{19}
\]

For the forward direction use an attained optimizer and the fact that a vector of norm zero is zero. For the reverse direction evaluate the nonnegative infimum at the exact correction. This avoids silently presupposing q = 0 before exact feasibility is known.

## 7. Closed budget-ball images and the stated uniqueness distinctions

The prose after WR03 states that T(B_M) is closed and convex even if ran T is not closed. This also has a proof independent of weak subsequences once Section 3 is available.

Convexity follows because B_M is convex and T is linear. To prove closedness, take any sequence y_j ∈ T(B_M) converging in norm to y. For each j choose u_j ∈ B_M with Tu_j = y_j. Then ‖u_j‖ ≤ M and Tu_j → y. Applying (7) with datum y yields u ∈ B_M satisfying Tu = y. Thus y ∈ T(B_M). Sequential closedness is closedness in the norm metric on Y.

The set T(B_M) is nonempty because it contains zero. Projection of r onto this nonempty closed convex set therefore gives a unique reachable datum y_M minimizing its distance to r. The residual vector r−y_M is unique, regardless of whether T is injective. This is uniqueness of the best image and residual, not uniqueness of all its preimages.

The fiber F = {a ∈ H : Ta = y_M} is a nonempty closed affine set. Its minimum-norm point a_min exists and is unique. Some member a₀ of the fiber has norm at most M because y_M ∈ T(B_M). Therefore ‖a_min‖ ≤ ‖a₀‖ ≤ M. Hence this uniquely selected least-norm fiber point is itself a budget-optimal correction. Other budget-optimal corrections can exist if the fiber contains further points inside the ball.

The range is the union of the closed budget images at integer budgets: every a has finite norm, so there is an integer n with ‖a‖ ≤ n. No conclusion that this increasing union is closed is used or valid in general.

## 8. Boundary cases and scope checks

| Case | Conclusion and proof check |
|---|---|
| M = 0 | The budget ball is {0}. WR01's premise forces r = 0 since Tu_j = T0 = 0 for all j. WR03 has β(0) = ‖r‖ with optimizer 0. The nested sets used in both proofs contain 0 whenever their stated hypotheses hold. |
| H = {0} | T is the zero map. WR01 is equivalent to r = 0. WR03 gives β(M) = ‖r‖ for every M ≥ 0, C = {0}, b = 0, and q = ‖r‖. The fiber for the optimal image is {0}. |
| Y = {0} | r = 0 and T = 0. WR01 always has solution 0. WR03 gives β(M) = 0 for every M ≥ 0. Residual uniqueness remains true. Corrections need not be unique when H is nontrivial. |
| General T = 0 | Same constant budget profile ‖r‖, no division by ‖T‖, and the Lipschitz right side is zero. |
| A zero minimum norm in the nested lemma | No division by a norm occurs. The supremum energy proof works unchanged, including when L = 0. |
| An empty constraint set | Excluded explicitly in the nested projection lemma. It cannot silently be passed to the projection theorem. Nonemptiness is separately proved for every constructed C_n. |
| Empty intersection | Allowed. It occurs exactly when the minimum norms are unbounded, and monotonicity strengthens unboundedness to divergence to infinity. |
| A supposedly empty Hilbert space | Not a possible vector-space case, because zero exists. Zero dimension is the relevant degenerate case. |
| Nonclosed ran T | Allowed throughout. Fixed-budget attainment does not imply global range closedness. |
| Nonseparable H or Y | Allowed. The proof makes no separability assumption and no basis choice. |

The nested convex lemma is stated for a countable nested sequence. The applications only require countably many residual thresholds. This file does not claim a general theorem for an arbitrary directed family of closed convex sets.

## 9. Lean implementation obligations

These are mathematical obligations, not claims that particular declarations already exist. No Lean API identifier is invented below. Any actual declaration must be located in the pinned source tree, its full type read, and its hypotheses matched before use.

1. Represent H and Y as complete real inner-product spaces and T as a bounded continuous linear map. Preserve the real field and completeness hypotheses of the written statements.
2. Obtain projection to a nonempty closed convex set and its minimum property or variational inequality. Derive (2) with the correct inner-product sign. If only the minimum property is convenient, derive the variational inequality from feasible segments before proceeding.
3. Choose the uniquely determined minimum-norm point for every C_n. Record membership and the minimum property so projection choice does not hide any empty-set case.
4. Prove the nested norm comparison and squared-distance inequality (3). Handle arbitrary pair order explicitly when turning this inequality into a Cauchy proof.
5. Establish convergence of the bounded monotone energy sequence, or use its real supremum directly. Show the ε² comparison implies the ε norm bound using nonnegativity. Completeness then yields a norm limit.
6. Transfer eventual membership to each fixed closed C_k. Distinguish the quantifiers “for each fixed k, all sufficiently large n” from simultaneous membership of p_n in all C_k.
7. Establish the elementary threshold sequence facts: positivity and antitonicity of 1/(n+1), its limit zero, and existence of an index below any positive tolerance.
8. For WR01, prove each residual sublevel set closed and convex, prove nonemptiness from the supplied sequence, and construct the exact limit in the same fixed ball. The auxiliary minimizers need not be related to the original sequence by a subsequence map.
9. For WR02, derive orthogonality from both affine directions and retain equalities (9) and (10). A convex-only formal theorem does not by itself cover these equality clauses.
10. For WR03, formalize the real infimum with both nonemptiness and a lower bound, prove near-minimizers (13), and show the nested intersection is precisely the minimizer set. A real infimum API may use a default value on empty or unbounded-below sets, so those hypotheses must remain visible.
11. Complete every WR03 clause, including monotonicity, convexity, the M₂ = 0 branch of the Lipschitz proof, the real-parameter M → ∞ limit, and both finite-budget equivalences. A compilation containing only attainment must not be marked as full WR03 coverage.
12. If the closed-image prose is included in formal scope, prove sequential closedness using bounded lifts and then convert it to closedness in the metric topology. If uniqueness prose is covered, distinguish uniqueness of the projected image, uniqueness of a minimum-norm preimage, and nonuniqueness of arbitrary preimages.
13. Connect the abstract T : H → Y theorem to the actual protected kernel only through a proved complete-space instance and the bounded restriction map. The mathematical fact that a continuous linear kernel is closed must be reflected in that bridge.

A successful implementation still requires compiler acceptance in the pinned environment, actual statement comparison, a declaration inventory, an axiom audit, and relevant rejection controls. This alternate written route supplies none of those records by itself.

## 10. Source synchronization cautions

No inherited source is edited by this file. If the alternate proof is adopted later, the theorem statements and WR labels should be preserved, while the following surrounding descriptions need synchronized edits:

- The introduction to `05f_bounded_realization.tex` and its WR01 proof currently motivate and use weak subsequences. The explicit weak-subsequence lemma can remain as an independent background result. It should not be falsely marked as formalized merely because the revised WR01 no longer depends on it.
- The paragraph after the orthonormal-sequence example currently describes WR01's conclusion as obtaining a weak limit along a subsequence. Under this route, say instead that an exact solution exists and that the auxiliary minimum-norm corrections converge strongly, without asserting strong convergence of the supplied sequence.
- The first paragraph of the WR03 proof and the budget-ball-image paragraph in `05g_budget_certificates.tex` currently use weak convergence. Sections 5 and 7 replace those exact dependencies.
- The final dependency paragraph of `12_proof_tools.tex` currently states that budget attainment uses the weak-subsequence lemma. That description would need updating if this alternate proof is adopted.
- `05h_regularized_repair.tex`, in WR08's step strengthening weak convergence to norm convergence, still invokes a weak subsequence and “the adjoint pairing argument of WR01.” Replacing WR01 would remove that named local argument from its original location. Either retain it as a separate helper, spell it out at its WR08 use, or separately prove and audit an alternate WR08 argument. Do not leave this cross-reference dangling or treat WR08 as newly formalized.

## 11. Optional downstream observation for WR08

This observation is outside the WR01–WR03 proof package and makes no coverage claim for WR08. It records why the route may reduce another dependency later.

Suppose a_α is the already constructed positive-parameter regularized solution, b = Ta_* is the attained projection of r onto the range closure, and a_* is its minimum-norm preimage. From the normal equation, using r−b orthogonal to ran T, one obtains

\[
\langle a_\alpha,a_*-a_\alpha\rangle
 =\frac{\|T(a_\alpha-a_*)\|^2}{\alpha}\ge0.
\]

Consequently

\[
\|a_\alpha-a_*\|^2
 \le\|a_*\|^2-\|a_\alpha\|^2.                     \tag{20}
\]

The usual minimizer comparison gives ‖a_α‖ ≤ ‖a_*‖. If ‖a_α‖ failed to approach ‖a_*‖ as positive α → 0, there would be a positive-parameter sequence α_j → 0 and a fixed M < ‖a_*‖ with ‖a_{α_j}‖ ≤ M. Once the already required residual convergence Ta_α → b is established, WR01's fixed-budget form yields a preimage of b with norm at most M, contradicting minimum-norm selection of a_*. Thus the norms converge, and (20) gives strong convergence.

When ‖a_*‖ = 0, the comparison ‖a_α‖ ≤ ‖a_*‖ already makes every a_α zero, so no choice of a negative bound is made. This route does not supply the residual-convergence premise, the positive-residual-floor classification, the unattained case, or WR08's complete parameter-limit formalization. Those remain separate obligations.

## 12. Review and execution record

The new derivation was checked against the exact WR01, WR02, and WR03 statements and the existing projection appendix. Review covered inner-product signs, all quantifiers in the nested argument, the distinction between convex inequalities and affine equalities, finite-infimum hypotheses, preservation of the fixed budget, and zero-space and zero-budget cases. No inherited theorem statement or proof file was modified.

This is a written mathematical self-review, not independent referee approval or kernel verification. No Lean compilation was attempted for this file.

During source inspection, one executor request failed because its transport disconnected. A subsequent read recovered successfully. Another exploratory read used an incorrect guessed WR08 filename and returned a missing-file error. Searching the actual chapter directory identified `05h_regularized_repair.tex`. Neither failed read affected or modified source files.
