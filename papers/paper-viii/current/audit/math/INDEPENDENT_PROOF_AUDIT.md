# Paper VIII independent mathematical audit

Author of manuscript: Komorebi P. Audit date: 2026-10-06 UTC.

## Normalized claim and primary verdict

The target is the strengthened manuscript's 56 finite internally proved results, its four separately named classical facts, and the mathematical expansions in all six Lean-block supplements. The objects are finite dimensional real or complex Hilbert spaces with a complete orthogonal direct-sum decomposition; finite rectangular matrices; finite rooted representation trees; exact or explicitly quantified perturbed operators; integer error budgets; and declared arithmetic, streaming and scheduling models. The conclusion is exact algebra, support inclusion, model-cost identities, error certificates, finite-model optimization and recorded-case empirical statements. It is not a universal discovery, hardware-optimality, floating-point-kernel correctness or newly reproduced GPU-performance claim.

**Primary verdict: correct only after the stated restrictions and rounding-model correction.** The archived raw manuscript is not literally correct under every printed hypothesis. The already archived amendments fix positive budgets, caps, denominators and empty-object conventions. A further necessary correction is the matrix-product rounding fact: a dimension-only common input-backward perturbation for a general matrix-matrix product is not valid. A precise componentwise forward-error statement is safe. The mixed-chain corollary must explicitly use uniform operator bounds, not bounds for one input vector. With these restrictions and corrections, no additional gap was found in the internally proved finite results reviewed here. General SVD existence and other separately named classical algorithm inputs must retain their external boundaries.

This is an independent read-only mathematical source audit, not a fresh Lean kernel run. It began from the raw statement and proof assets. It read the inherited release descriptions as historical evidence and independently reconstructed the decisive implications. Agreement with earlier internal audits is not a proof. No Lean or Lake executable was run by this audit. Raw sources were not edited. File revisions are pinned in `SOURCE_PINS.json`.

## Dependency graph

- Complete orthogonal projectors → exact reconstruction → block composition → support inclusion → powers/walks, polynomial support and acyclic nilpotence.
- Rectangular matrix multiplication and finite address/event counts → modeled application/storage → streaming events → positive-capacity roofline and memory inequalities.
- Exact BDLR expansion → two-factor thin factors → unrecompressed chain rank. Actual invertibility of D and its small update matrix → Woodbury → inverse norm bound.
- Compact orthonormal factors from actual column spaces + supplied ordered thin SVD equations → diagonal spectral/Frobenius optimality → isometric lift/compression → global small-core recompression against arbitrary ambient competitors.
- Actual directed reachability + finite dimensional invariant reachable subspace + invertibility → inverse support → hidden Schur support inclusion.
- Actual acyclic finite task graph → well-founded predecessor levels → longest-path depth and staged forward substitution. Unit tasks and unlimited concurrency are separate model assumptions.
- Actual commuting projectors and operators → local Krylov inclusion; actual noncommutative power telescoping → approximate Krylov bound. Positive definite block normalization + norm bound below one → condition bound → substitution into separately assumed exact-arithmetic CG convergence.
- Source-supported edge residuals → vector certificate → uniform operator certificate → actual product-chain telescoping or post-product residual recursion. These two error recurrences differ.
- Positive finite nonempty allocation data + positive feasible budget → continuous logarithmic optimum; positive caps → continuous capped scale + global logarithmic comparison → clipped optimum.
- Independently defined finite legal cuts/precision assignments + additive costs/errors → finite minimum and convolution → exact Lagrangian and quantized-budget optima. Stored-table event count → pseudo-polynomial operation model; neither bit complexity nor hardware timing follows.
- Exact case-signature equality and identical contracts/scopes → fair-match equivalence; recorded corpus values → historical measured-case statements. Corpus consistency does not reproduce a timing measurement.

No circular theorem dependency was found in these routes. In particular, the final ordered-SVD structure has reconstruction, orthonormality, order and nonnegativity fields; it has no optimality, tail-error or best-rank field.

## Obligation matrix

| Source items | Obligation independently checked | Status and restriction |
|---|---|---|
| 2.3, 2.5, 2.6 | Complete projector insertion, multiplication order, actual adjoint and tensor semantics | Passed with explicit local-map/ambient-inclusion convention and self-adjoint projectors |
| 2.9, 11.3 | Output conversion; equality of signatures gives reflexive, symmetric, transitive matching | Passed as declared contract policy/equality model |
| 3.1, 3.2, 3.4, 4.1, 4.2 | Stored scalar addresses and two modeled scalar-operation tags per coefficient/right side | Passed in declared event model; equal-width substitution requires positive width; ratios require nonzero denominators |
| 3.6 | Independent edge reads of block/source/target plus writes | Passed in one-pass model; no cache or communication-optimality claim |
| 3.8, 3.9, 3.10 | Capacity division and explicit materialization | Passed for positive operation/bandwidth/scalar-size denominators; rate requires positive time and bytes; representation-only memory |
| 4.3, 4.4 | Fourier sign/normalization and wrapped Toeplitz index | Passed for positive size; n=1 valid; FFT complexity remains a separate algorithmic factorization |
| 4.5, 4.6, 4.7 | Column-major ordinary transpose; modewise contraction; Walsh orthogonality and recursion | Passed; complex scalar event count differs from real FLOPs; empty tensor identity and N=1 have zero work |
| 5.1, 5.2 | BDLR factor expansion and actual correction rank | Passed; one shared diagonal layout; zero-width and empty chain handled |
| 5.3, 5.4 | Two inverse hypotheses; multiplication of proposed inverse; norm bound | Passed; no numerical stability inferred |
| 5.6 | Arbitrary ambient rank-bounded competitors; compact factor rank; two norms and zero endpoints | Passed from supplied ordered thin SVD equations; general SVD existence externally conditional |
| 5.8, 5.9 | Noncommutative telescoping versus inhomogeneous post-product error recurrence | Passed; empty products equal one; post-product residual already contains output scaling |
| 6.1, 6.2, 6.3 | Directed walks of exact length, degree-zero polynomial term, cancellation | Passed; the term “path” must mean walks in the power expansion; no equality of supports |
| 6.5, 6.6, 10.3 | Constructed levels and predecessor stage invariant | Passed in ideal unit-task unlimited-concurrency model; empty graph depth zero; nonempty longest path wording |
| 6.7, 6.8 | Invariant reachable subspace, finite-dimensional inverse closure, hidden entrance/exit | Passed with reflexive reachability, including zero-length hidden connection |
| 7.2, 7.3 | Exact orbit powers, local range/direct sum, noncommutative telescoping | Passed; Krylov conclusion is inclusion; M=0 does not introduce division |
| 7.4, 7.6 | Actual inverse square root; condition estimate and monotone q substitution | Passed for nonempty positive definite coordinate space; CG algorithm bound external |
| 8.1 | Source support and local sensitivity | Passed; source support of residual is essential; an input-specific bound is not yet an operator norm |
| 8.3 | Uniform operator δ_j substituted into factor-chain bound | Failed as a fully explicit argument in raw prose; corrected form specified below and in the third supplement |
| 8.4 | Feasible positive logarithmic optimum | Correct only for finite nonempty edge set, positive sensitivities/costs and τ>0; raw missing hypotheses |
| 8.5 | Positive caps; existence; uniqueness of vector and multiplier endpoint | Correct with positive finite nonempty data; λ unique only below maximal budget; vector unique throughout feasible range |
| 8.7, 9.8, 9.9 | Independent legal objects, infeasible states, nonnegative weights, exact minimum and work model | Passed; finite option sets and integer budget; negative/residual natural subtraction guarded; no backtracking-output or bit-complexity claim |
| 9.2 | Cross-block Hilbert–Schmidt orthogonality and separate operator norm | Passed for supplied complete orthogonal projectors; not autonomous discovery |
| 9.4, 9.5, 9.6, 9.7 | Terminal keep rule; child independence; two optimum inequalities; positive scalarization Pareto claim | Passed in finite additive model; unsupported Pareto points permitted |
| 9.11, 9.12 | Strict solved-score half-gap and valid unchanged sibling caches | Passed; no robustness at ties, and raw local score perturbations alone need not bound solved split scores |
| 10.2 | One batched backend invocation per independent compatible shape class | Passed under explicitly assumed batched backend support; common target accumulation needs independence contract |
| 10.4, 10.5, 10.6 | Strict inequality and smallest integer reuse count | Passed for stated nonnegative one-time costs and strict per-use advantage; denominator positive |
| 5.5 | Best-rank approximation classical input | Ordered-data best-rank conclusions independently reconstructed from sixth supplement; generic SVD existence not newly checked |
| 7.5 | Classical exact-arithmetic CG estimate | Author-hosted primary source verified; symmetric-preconditioning/Hermitian translation derived below |
| 8.2 | Matrix-matrix rounding model | Raw common backward formulation refuted; primary componentwise forward formula verified below |
| 9.1 | General simultaneous normal spectral decomposition | Classical source leaf conditional in this audit: no exact named primary theorem/version checked; no new full formalization claimed |

The register comparison found 56 internally proved-result labels and four separate standard-fact labels. Those are inventory counts, not 56 independent discoveries or a claim that every assertion is newly formally proved.

## Decisive corrections and exact counterexamples

### Rounding is not generally one common perturbed input product

Take decimal floating-point arithmetic with two significant digits and rounding to nearest. The inputs

\[
A=\begin{pmatrix}1.1\\1.3\end{pmatrix},\qquad B=\begin{pmatrix}1.1&1.3\end{pmatrix}
\]

are exactly representable. Ordinary scalar multiplication produces

\[
\widehat C=\begin{pmatrix}1.2&1.4\\1.4&1.7\end{pmatrix},\qquad \det\widehat C=0.08\ne0.
\]

Every product \((A+\Delta A)(B+\Delta B)\) with these same inner dimension one shapes has rank at most one. Thus no input perturbations of any size can represent this rank-two computed matrix as that exact product. There is no overflow or underflow, and each multiplication satisfies the standard relative-error model with unit roundoff 0.05. The defect is the claim's matrix-matrix backward representation, not an exotic violation of floating-point assumptions.

For real ordinary dot-product matrix multiplication with inner dimension p, uniform unit roundoff u, no overflow/underflow, and pu<1, use

\[
\widehat C=AB+R,\qquad |R|\leq\gamma_p|A||B|,\qquad \gamma_p=\frac{pu}{1-pu}.
\]

Complex arithmetic, block FMA and mixed-precision accumulation need their own constants and algorithm hypotheses. A rounded input-output computation is not automatically one fixed linear map on all inputs.

### A vector certificate needs uniformization before the chain theorem

The source-supported residual gives, for every x,

\[
\|E_jx\|\leq\sum_e\|\Delta_{j,e}\|\|P_{j,a(e)}x\|
\leq\left(\sum_e\|\Delta_{j,e}\|\|P_{j,a(e)}\|\right)\|x\|.
\]

Therefore \(\|E_j\|\leq\delta_j:=\sum_e\|\Delta_{j,e}\|\|P_{j,a(e)}\|\). For orthogonal projections, their norms are at most one, so \(\delta_j\leq\sum_e\|\Delta_{j,e}\|\). Substitution in the actual factor-chain bound is then valid. One selected x does not suffice: E=diag(0,1) and x=(1,0) have Ex=0 but \(\|E\|_2=1\). The third supplement states the valid uniform argument.

### Feasibility and empty boundaries

For one edge, s=c=1 and τ=0, the positive tolerance equality ε=0 is infeasible. This is the smallest counterexample to unrestricted Theorem 8.4. For an empty edge set, the written denominator C=Σc equals zero; the formula must not be used. The archived second supplement proves the corrected positive nonempty statement globally using log r≤r−1, not just a stationary-point equation.

An empty task graph has zero stages. The nonempty formula “one plus longest number of edges” cannot be extrapolated to it. At maximal clipped budget, a one-edge s=c=m=1 example admits both λ=1 and λ=1/2 with the same ε=1, so uniqueness concerns the vector while multiplier uniqueness is restricted to submaximal budget.

## Independent derivation of the critical recompression implication

Let Q and V have orthonormal columns and write A=QGV*. For every ambient B of rank at most k, C=Q*BV is an admissible core competitor because multiplication cannot increase rank. It satisfies G−C=Q*(A−B)V. Orthogonal compression contracts both the induced Euclidean operator norm and the Frobenius norm. The latter follows from left/right orthogonal projection, or by extending the frames to unitary bases and discarding entries.

If G_k minimizes the core error, then for either ν∈{2,F},

\[
\|A-QG_kV^*\|_\nu=\|G-G_k\|_\nu
\leq\|G-Q^*BV\|_\nu
=\|Q^*(A-B)V\|_\nu\leq\|A-B\|_\nu.
\]

This proves global ambient optimality. It does not restrict competitors to the input row and column spaces. For ordered nonnegative diagonal data, spectral optimality follows by restricting any rank≤k competitor to the first k+1 coordinates and using rank-nullity to obtain a nonzero supported kernel vector. The diagonal action on this vector has norm at least σ_{k+1} times the vector norm.

For Frobenius optimality, take an orthonormal frame Q_B for the competitor's actual kernel. Its row weights w_i lie in [0,1] and sum to dim ker B≥d−k. Since σ_i² decrease, Σσ_i²w_i≥Σ_{i>k}σ_i². Right compression contracts Frobenius norm and BQ_B=0, giving the required lower bound. Diagonal truncation attains both bounds. The source's explicit coordinate-weight inequality has the correct direction for retained and tail indices.

The reconstructed proof covers rectangular compact cores, rank-deficient input factors, zero factors and empty coordinate spaces, k=0 and k≥d, zero singular values and repeated singular values. Use h=min(d,k) retained columns and zero tail when k≥d. No uniqueness of the best rank-k approximation is asserted at repeated singular values. Actual range dimensions are input-factor ranks, not necessarily the rank of their product.

The final raw `OrderedThinSVD` structure was read directly. It supplies only left/right isometries, nonnegative decreasing values and exact reconstruction. Its diagonal optimality dependencies derive kernel witnesses and weighted tail inequalities. The general existence of such data and their numerical computation remain separate obligations. This source-level review does not attest fresh elaboration of any Lean module.

## Other decisive derivations

Inverse support: the reflexively reachable direct sum X_R is A-invariant because an active edge leaving R would extend reachability. Injectivity of invertible A on finite dimensional X_R implies surjectivity there. Hence A^{-1} maps X_R to itself. This is why finite dimensionality is essential and why the no-route inverse block vanishes. A hidden Schur correction needs an entrance, a reflexive hidden route and an exit. Cancellation prevents the converse.

Frontier monotonicity: adding the two optimizing inequalities at λ_1<λ_2 gives (λ_2−λ_1)(ε_2−ε_1)≤0. Then κ_2−κ_1≥λ_1(ε_1−ε_2)≥0. The cost order needs λ_1≥0; it is present. A terminal tree node can only be kept. An internal split uses independently optimal child cuts. Overlap, rank coupling or nonlocal device costs would remove this independence.

Clipped global optimality: write u_e=min(m_e,t c_e/s_e) for t>0. For every feasible competitor ε, c_e(ε_e/u_e−1)≤(s_e/t)(ε_e−u_e). On a capped coordinate the sign reversal follows from ε_e−m_e≤0. Equal budgets and log r≤r−1 give J(ε)≥J(u), strictly if ε differs. Existence uses continuity from t=0 to T=Σ(m_es_e/c_e), where each coordinate is saturated. At strictly submaximal total tolerance, at least one unsaturated coordinate makes the sum strictly increase, proving multiplier uniqueness.

Post-product residuals: if \(\widehat P_j=A_j\widehat P_{j-1}+E_j\), then D_j=A_jD_{j-1}+E_j. Unrolling gives Σ A_m…A_{j+1}E_j. There is no exact-prefix norm multiplier on E_j. By contrast factor perturbations have the exact prefix A_{j−1}…A_1 and perturbed suffix. The sixth-block small-core truncation error is an output residual suitable for the first recurrence only when measured after that multiplication.

## Primary external-source verification

The search scope was theorem verification and attribution of the CG and rounding leaves, not historical novelty. Search used author-hosted sources and Manchester MIMS eprints. No broad novelty conclusion follows.

1. Nicholas J. Higham and Theo Mary, *Mixed Precision Algorithms in Numerical Linear Algebra*, MIMS EPrint 2021.20 (2021), [author eprint](https://eprints.maths.manchester.ac.uk/2841/1/paper_eprint.pdf), checked 2026-10-06. Section 3 states the standard real floating-point model and γ_n with nu<1, excluding overflow/underflow. Section 4 equation (4.1) is precisely the real matrix-product forward bound above, attributed there to Higham (2002), §3.5. The independent source extraction verifies the safe replacement; it does not support the raw common backward-product sentence. This author eprint was read through web retrieval and not retained as a local full-PDF cache, so no cache content hash is claimed.

2. Yousef Saad, *Iterative Methods for Sparse Linear Systems*, second edition (2003), [author-hosted text](https://www-users.cs.umn.edu/~saad/IterMethBook_2ndEd.pdf), checked 2026-10-06. Theorem 6.29 and equation (6.128), printed pp. 214–215, give the CG energy-norm Chebyshev estimate with κ=λ_max/λ_min. Section 9.2 supplies symmetric preconditioning. Put H=M^{-1/2}AM^{-1/2}, y=M^{1/2}x. Then ||y−y_*||_H=||x−x_*||_A and κ(H) is the stated condition number. Applying exact-arithmetic CG to H gives the project bound. The book writes the base argument over real SPD matrices; its Hermitian extension follows from the same orthonormal eigenbasis and real Chebyshev polynomial argument, which is a translation derived here. No finite-precision CG guarantee is inferred. This author text was read through web retrieval, not locally cached; no cache hash is claimed.

The initial cse-host Saad PDF retrieval timed out; the author's cs-host alias succeeded. Two initially guessed unrelated/obsolete source URLs were inaccessible; they are not mathematical evidence. Snippets served only as discovery. The exact fetched equations above were inspected before drawing conclusions. Generic SVD existence and simultaneous decomposition were not given an authenticated exact-version primary-source leaf in this bounded audit; they remain explicitly external/conditional, not silently supplied by successful finite tests or archive labels.

## Commands, limitations and remaining obligation

Read-only source commands used `sed`, `cat` and `rg`. A Python inventory pass extracted result labels and SHA256-pinned the strengthened source, six supplements, amendment ledger and seven decisive raw recompression modules. It found 56 internal labels and four standard facts. That script establishes provenance and counts, not correctness. The independently written stdlib `check_counterexamples.py` was run and its assertions passed: two-significant-digit decimal nearest rounding has determinant 2/25, all four scalar relative errors obey u=1/20, and the input-specific zero-error control has actual operator norm one. Its exact Fraction results are recorded in `COUNTEREXAMPLE_CHECK.json`. This is a specified toy rounding counterexample, not a simulation or claim about a GPU kernel. No Lean, Lake, GPU measurement or imported Mathlib recheck occurred in this audit. Broader computational reproduction and artifact-integrity reports belong to the separate computation workflow.

The cheapest final check is a read-only diff of the generated traditional source against this correction list: (1) typed inclusion conventions; (2) all archived positive/empty hypotheses; (3) precise forward rounding fact and fixed-linear-map boundary; (4) uniform δ_j in mixed chain; (5) min(d,k) endpoints and arbitrary ambient competitor compression; (6) current evidence distinguished from inherited historical runs; (7) external classical boundaries. The strongest safe result is the finite mathematics under these explicit restrictions, not a general GPU or compiler correctness theorem.
