# Block 15 — Infinite reconstruction in strong, compact and Hilbert–Schmidt topologies

Komorebi Physics Lean v0.15.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 34 of 550, printed page 21, Section 6.8, equations (6.57)–(6.67). The source page image was inspected. The source PDF is preserved unchanged. A completed `verification/final/report.json`, not this narrative or the declaration inventory alone, determines cumulative verification status.

## 1. Inventory and scope

| Module | New theorem declarations | New definitions | Role |
|---|---:|---:|---|
| StrongReconstruction | 11 | 1 | Exact decomposition, state bounds, comparison bounds and strong limits |
| CompactReconstruction | 7 | 0 | Uniform compact-set convergence and actual compact-operator reconstruction |
| HilbertSchmidtCore | 26 | 4 | Actual column Hilbert sums, basis independence and two-sided norm bounds |
| HilbertSchmidtReconstruction | 9 | 0 | Dominated column convergence and the full HS reconstruction limit |
| AtlasReconstruction | 10 | 1 | Constructed finite-subset orthogonal contractive cutoffs |
| GraphReconstruction | 6 | 1 | Domain-correct generator reconstruction and quantified graph-error bounds |
| HilbertSchmidtExamples | 18 | 3 | Exact nonzero infinite-tail HS and operator-norm errors |
| ReconstructionExamples | 24 | 3 | Actual compact counterexample, adjoint obstruction and spectral-domain bridge |
| **Block 15** | **111** | **13** | **124 new inventoried declarations** |

The cumulative inventory contains **1,371 theorem declarations, 1,626 inventoried names and 86 mathematical modules**. It contains 39 recovered Paper VII theorem declarations and 1,332 full-edition declarations. All 78 mathematical modules from Block 14 are byte-identical. The new count is 69 general/support theorems and 42 example/support theorems. These are declaration counts, not independent physical discoveries or a completion percentage for the 550-page edition.

Strong reconstruction is proved on complex normed spaces under an explicit uniform contraction bound. Compact left reconstruction has the same scope. The self-adjoint right/compact and Hilbert–Schmidt statements use complete complex Hilbert spaces. The cutoffs can be indexed by a general filter; the concrete atlas implementation uses the actual directed net of finite subsets. Neither finite-dimensionality nor separability is imposed on the general Hilbert results. A Hilbert basis is explicit in the HS interface, and membership and norm are proved independent of its choice.

## 2. An actual sandwich and a proved strong limit

Define

    compression S X = S * X * S.

For arbitrary bounded operators S and X, the actual noncommutative algebra gives

\[
SXS-X=SX(S-I)+(S-I)X.
\]

No convergence is used to prove this identity. With the separate bound ||S||<=1, applying it to a vector x gives

\[
\boxed{\|(SXS-X)x\|\le\|X\|\,\|(S-I)x\|+\|(S-I)Xx\|.}
\]

When S_a x tends to x for every fixed x, both terms tend to zero. `compression_strong` proves actual `Tendsto` of the sandwich applied to every state. These are (6.57) and (6.60)–(6.62). The proof does not install sandwich convergence as an input field.

The same cutoff has a proved nonexpansive action on operator differences,

    ||SXS-SYS|| <= ||X-Y||,

and the source comparison estimate is established separately:

\[
\boxed{\|SXS-X\|\le2\|X-Y\|+\|SYS-Y\|.}
\]

This checks the algebraic estimate in (6.63). Y is arbitrary; its reconstruction error is not silently set to zero. A further theorem permits an actual changing approximation Y_a with ||Y_a-X|| tending to zero.

## 3. Compact reconstruction, including the right-hand cutoff

`uniform_compact` proves that a strongly convergent family of contractions converges uniformly on every compact set. The proof takes a finite epsilon-net of that set and combines the finitely many strong limits with the uniform operator bound. Uniform convergence is a conclusion.

For an actual `IsCompactOperator X`, the image of the unit ball is contained in a compact set. Therefore

\[
\|(S_a-I)X\|\longrightarrow0.
\]

This left-sided result does not need self-adjointness. The right-sided proof has its own argument. Assume S_a is self-adjoint and contractive. The Gram operator X*X is compact because it is a bounded composition with X. The C*-norm identity and ||S_a-I||<=2 give

\[
\boxed{\|X(S_a-I)\|^2\le2\|(S_a-I)(X^*X)\|.}
\]

The right side tends to zero by the left compact theorem. Thus the right error also tends to zero. Combining both sides with the sandwich identity yields

\[
\boxed{\|S_aXS_a-X\|\longrightarrow0\quad\text{for compact }X.}
\]

This proves (6.58), (6.63) and (6.64) under an explicit sufficient cutoff contract. The proof does not assume that strong convergence of arbitrary operators implies strong convergence of their adjoints. It also does not need an unproved compact-adjoint theorem or an assumed finite-rank approximation of X. Self-adjoint contractions are sufficient, not asserted necessary.

## 4. The Hilbert–Schmidt quantity is an actual basis-independent norm on its class

For a Hilbert basis b, define membership by

    IsHS b X := Summable (fun i => ||X(b_i)||^2).

Given this proof, `columns b X hX` is an actual lp-2 vector with entries X(b_i). Its norm is proved equal to

\[
\|X\|_{\mathrm{HS}}=\sqrt{\sum_i\|Xb_i\|^2}.
\]

`energy` and `hsNorm` are total scalar definitions in Lean. Their interpretation as the Hilbert–Schmidt energy/norm is restricted to `IsHS`. No norm axiom on all bounded operators is asserted. In particular, the infinite identity is proved NOT to satisfy `IsHS`; a totalized divergent sum must not be interpreted as a vanishing physical norm.

The formalization proves genuine joint summability of the nonnegative squared matrix entries using Parseval and Tonelli. From that summability, it proves that membership and the displayed norm do not depend on the chosen Hilbert basis, and that

\[
\|X^*\|_{\mathrm{HS}}=\|X\|_{\mathrm{HS}}.
\]

The actual column Hilbert norm supplies addition/subtraction bounds. The two-sided operator-ideal bounds are proved:

\[
\|AX\|_{\mathrm{HS}}\le\|A\|\,\|X\|_{\mathrm{HS}},\qquad
\|XA\|_{\mathrm{HS}}\le\|A\|\,\|X\|_{\mathrm{HS}}.
\]

Membership of both products is proved, not an extra unsupported convention. The operator norm is dominated by the HS norm, and zero HS norm implies X=0 under the membership hypothesis. This is enough actual norm structure for the reconstruction proof. It is not presented as a fully bundled Schatten theory, singular-value characterization, trace-norm theory, or a proof of completeness of a separate bundled HS operator space.

## 5. Dominated convergence proves the actual HS reconstruction limit

For each basis column, strong convergence gives

    (S_a-I)X b_i -> 0.

The squared norms obey the summable bound

\[
\|(S_a-I)Xb_i\|^2\le4\|Xb_i\|^2.
\]

Tannery's dominated-convergence theorem therefore proves that the actual sum of squared column errors tends to zero. Taking square roots establishes

\[
\|(S_a-I)X\|_{\mathrm{HS}}\longrightarrow0.
\]

For self-adjoint S_a, the separately proved adjoint invariance identifies the right error with the left error of X*:

    ||X(S_a-I)||_HS = ||(S_a-I)X*||_HS.

Thus both statements in (6.65) are established. The error is proved to belong to the HS class, and the exact sandwich decomposition plus the norm bounds gives

\[
\boxed{\|S_aXS_a-X\|_{\mathrm{HS}}\longrightarrow0.}
\]

This checks (6.59). Operator-norm convergence follows separately from the proved opNorm<=hsNorm inequality. No swap of an unproved infinite double sum is used.

## 6. The cutoffs and the generator-domain limit are constructed

For the existing actual strong orthogonal atlas P, define

\[
S_F=\sum_{i\in F}P_i\qquad(F\text{ a finite subset of labels}).
\]

`AtlasReconstruction` proves that this is a bounded operator whose evaluation equals the previously checked vector partial sum. It proves ||S_F||<=1, self-adjointness, idempotence and strong convergence to I. All bounded, compact and HS reconstruction theorems are then specialized to this actual net.

Finitely many sectors need not have finite-dimensional total range. No finite-rank claim is inferred from finite F alone. The sequence-space coordinate cutoffs are a separate concrete realization.

For a `DomainAtlas T I`, its finite sum is domain-valued. Therefore the new `reconstructed` is the legitimate expression

    S_F (T (P.partialSum F x)),     x in D(T).

Every unbounded application has its domain proof. The exact identity is

\[
S_FTS_Fx-Tx=S_F(TS_Fx-Tx)+(S_F-I)Tx.
\]

The norm estimate retains both contributions:

\[
\|S_FTS_Fx-Tx\|\le\|TS_Fx-Tx\|+\|(S_F-I)Tx\|
\le\|S_Fx-x\|_T+\|(S_F-I)Tx\|.
\]

Graph compatibility supplies convergence of the first term, while strong completeness supplies the second. Consequently

\[
\boxed{S_FTS_Fx\longrightarrow Tx\quad(x\in D(T)).}
\]

This checks (6.66)–(6.67) and includes a cofinal-subsequence version. Neither symmetry, closedness nor boundedness of T is needed for this implication once graph compatibility is supplied. The diagonal spectral example supplies graph compatibility from its existing proved maximal-domain construction. This is ambient Hilbert-norm convergence, not a claim that the resulting generator images converge in graph norm or lie in a second operator domain.

## 7. Exact nonzero infinite-tail example

On the actual infinite l2 space, construct the bounded diagonal operator

\[
(Xx)_n=2^{-n}x_n.
\]

For the coordinate Hilbert basis, the proved sum is

\[
\sum_n\|Xe_n\|^2=\sum_n4^{-n}=\frac43.
\]

Let S_M keep coordinates n<M and E_M=X-S_MXS_M. A genuine HasSum theorem for the residual columns gives

\[
\boxed{\|E_M\|_{\mathrm{HS}}^2=\frac43\,4^{-M},\qquad
\|E_M\|=2^{-M}.}
\]

The first equality is a full infinite-series computation, and the second is the actual infinite-space operator norm, using the first omitted coordinate and the proved tail bound. Both errors tend to zero; E_M is nonzero at EVERY finite cutoff. At M=2,

    ||E_2||=1/4,       ||E_2||_HS^2=1/12.

Thus the two norms are genuinely different. No floating-point experiment is used, and no nonzero tail is discarded.

## 8. An actual compact counterexample to an insufficient cutoff hypothesis

Let e_n be coordinate basis vectors and define

\[
P=|e_0\rangle\langle e_0|,\quad
R_n=|e_0\rangle\langle e_{n+1}|,\quad
S_n=I+R_n.
\]

P is proved idempotent, norm one and compact by factorization through the one-dimensional complex space. The approximations satisfy the proved uniform bound ||S_n||<=2. For every actual l2 vector x,

    ||S_n x-x||=|x_(n+1)| -> 0.

Nevertheless, exact rank-one multiplication yields

\[
\boxed{S_nPS_n-P=R_n,\qquad\|S_nPS_n-P\|=1.}
\]

The compact norm-convergence statement is therefore false if its cutoff hypothesis is read as arbitrary strong convergence alone, even with a uniform bound of two. This does not contradict the intended orthogonal-atlas version: S_n is proved non-self-adjoint and is not claimed contractive or idempotent.

The missing adjoint control is also exact:

    S_n* e_0-e_0=e_(n+1),

so the adjoints fail to converge strongly on e_0. Self-adjointness is a sufficient hypothesis in our theorems, not a claim that every non-self-adjoint approximation fails.

Separately, the actual orthogonal spectral cutoffs converge strongly while ||I-S_M||=1 for every M. This rejects operator-norm reconstruction for arbitrary bounded X, even when the cutoffs satisfy the full orthogonal contractive contract.

## 9. Audit and remaining boundaries

The cumulative verifier rebuilds all 86 mathematical modules and the aggregate with one worker and warnings as errors, audits all 1,626 inventoried declarations, and requires all 108 invalid controls to produce their designated proof diagnostics. Every proof-bearing definition is included. All 78 parent mathematical sources are checked against a new Block 14 preservation layer, with every older layer retained. The unchanged Block 14 baseline was freshly reverified before extending the inventory.

Only propext, Classical.choice and Quot.sound are permitted transitive axiom dependencies. No active admissions, custom axioms, native evaluation or kernel bypass are used. Lean is 4.34.0-rc2, Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06, and nine clean dependency revisions are checked. Imported compiled caches are reused, not rebuilt wholesale. The seven runtime parts and combined archive were SHA-256 verified during restoration; runtime bytes remain external.

Failed development snapshots are retained under `verification/development/block15`; see `BLOCK_15_FAILURES.md`. A complete final PASS and a separate fresh-extraction recheck determine release status. Timeout or import failure is not a successful negative test.

This closes Section 6.8 in the stated bounded/compact/HS and graph-compatible scopes. It does not prove operator-norm reconstruction of every bounded operator, convergence without appropriate cutoff control, Hilbert–Schmidt convergence of non-HS inputs, automatic graph compatibility, graph-norm convergence of the generator images, a general Schatten-p theory, or any continuum/empirical physics claim. Earlier harmonic half-power, ladder-product, general spectral/Stone, differential-oscillator, nonlinear/dissipative existence, density positivity, entropy-boundary, countable-dilation and gravitational/cosmological obligations remain. Chapter 3 is not fully inventoried. Section 6.9's historical numerical residuals were not rerun.

**Next literal target:** Chapter 7, (7.1)–(7.23), finite pointwise derivation no-go and actual noncommutative corner derivations. Preserve the distinction between a finite product of complex fields and an arbitrary finite-dimensional commutative algebra. Then derive exact matrix Leibniz, star compatibility and trace integration by parts before tackling curvature and corner routing.
