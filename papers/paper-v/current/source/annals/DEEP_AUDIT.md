# Deep Mathematical Audit

## Scope of this audit

This audit reviews the final manuscript at the level of definitions, hypotheses, algebraic identities, norm estimates, limiting arguments, probability bounds, and stated boundaries. It is an internal audit. It is not a substitute for independent review by specialists in harmonic analysis, approximation theory, wavelets, and statistical signal recovery.

## Audit result

No unresolved theorem target remains in the manuscript. Every theorem, proposition, lemma, and corollary has a proof. The one result labeled as a standard fact is the classical Gibbs phenomenon and is supported by citations rather than reproved.

The final audit found several points that required stricter wording. They were corrected before the release build.

## Corrections made during the final audit

### Local Sobolev hypotheses

The higher order singular packet theorem originally described each smooth piece through classical differentiability and an \(L^p\) highest derivative. That wording was not strong enough by itself to guarantee absolute continuity of the preceding derivative. The final theorem assumes directly that every piece belongs to \(W^{r,p}\). This is the correct hypothesis for the trace matching and gluing argument.

### Trace packet uniqueness

The uniqueness proof now uses the one dimensional Sobolev representatives whose derivatives through order \(r-1\) have matching one sided traces. It no longer relies on an informal statement about classical smoothness.

### Filter bank domain

The filter bank section now states that all banks act boundedly on the relevant polyphase \(\ell^2\) spaces. This makes the Fourier multiplier, Plancherel, frame, and pseudoinverse arguments unambiguous.

### Formal Cauchy products

The nonlinear residue theorem now states that the series are formal power series. It also records the analytic version for series converging on a common disk. This removes an implicit convergence assumption.

### Shifted Haar grids

The half cell argument is now proved by an explicit case split modulo the cell length. The Haar section also states that signals are defined on the line or have a declared extension beyond a finite observation interval, so shifted supports near endpoints are meaningful.

## Section by section assessment

### Signal generation and lattice packets

The impulse orbit statements reduce to density of finitely supported sequences. The \(p=\infty\) boundary is stated correctly. The finite index lattice analysis is an exact partition of \(\mathbb Z^d\), and its norm identity is immediate for every \(1\leq p\leq\infty\). Translation covariance and nested refinement use unique coset decompositions.

### Convolution transfer

The packet kernel formula follows by separating every input address into a residue and a sublattice element. The rowwise \(\ell^1\) identity is exact. The operator norm estimate is also inherited from Young's inequality through an isometric coordinate change. Composition follows from conjugation.

### Filter banks and lifting

The perfect reconstruction criterion and the reconstruction defect bound are Fourier multiplier statements on \(\ell^2\). The frame inequalities follow from pointwise singular value bounds and Plancherel. The perturbation estimates use only the triangle inequality for operator norms. The lifting theorem is a direct triangular factorization identity.

### Packet trees

The unitary pruning theorem is proved by induction. The nonunitary bounds correctly propagate the worst lower and upper child factors. The best basis recursion covers finite trees with additive node costs. The stability theorem is finite and does not claim robustness for nonadditive objectives.

### Singular packets

The truncated power packet has a unit jump at exactly one derivative order. Subtracting the full finite packet matches all traces through order \(r-1\). Standard one dimensional Sobolev gluing then gives the global \(W^{r,p}\) remainder. The retained packet identity is exact algebra. The estimated packet theorem cleanly separates smooth approximation and packet estimation.

### Region and geometry formulas

The scalar and partition formulas are exact integrations over disjoint intersections. The higher order packet location bound follows from differentiation with respect to the knot and Minkowski's inequality. The tube estimate is conditional on the displayed geometric measure bound and does not claim that every boundary satisfies it.

### Deterministic jump recovery

The adjacent contrast error is bounded by \(Mh+2\varepsilon\). The strict gap

\[
a_{\min}>2(Mh+2\varepsilon)
\]

is sufficient and yields a nonempty threshold interval. Exact cell recovery follows by separating jump and nonjump contrasts. The location estimate is the cell midpoint bound. Finite \(L^p\) packet consistency follows because each location disagreement interval shrinks with the grid.

### Probability recovery

The difference of two independent \(\sigma\) sub Gaussian variables has variance proxy \(2\sigma^2\). The stated tail bound and the union bound over \(n\) cells give the displayed finite probability certificate. The paper explicitly notes that fixed noise with one observation per grid point does not lead to the claimed consistency regime.

### Haar and finite differences

The smooth Haar estimate and exact step coefficient have the correct powers of the support length. The two grid theorem removes exact alignment at one fixed scale. The finite difference statements are exact for piecewise polynomial sequences, with noise growth controlled by the \(\ell^1\) norm of the binomial stencil.

### Gibbs statement

The article does not claim a new Fourier convergence theorem. It proves that if the jump packet is retained, the remaining approximation error is exactly the smooth error. For an estimated packet, the residual packet norm appears explicitly. The boundary between conditional packet separation and unconditional Gibbs removal is stated.

### Nonlinear residue laws

The Cauchy product law is a modular degree identity. The shifted pointwise monomial formula includes the required coarse carry when a shift crosses a residue boundary.

### Cayley coordinates

The fractional linear action is a conjugate of disk rotation. Its group law, order, radial invariance, and coprime label factorization follow directly from the conjugacy and the Chinese remainder theorem. This section is marked as secondary to the main signal recovery line.

## Remaining external review priorities

Independent reviewers should focus first on:

1. The exact scope of the one dimensional Sobolev gluing statement
2. The relation of the jump recovery theorem to existing change point results
3. Historical priority for the combined singular packet error calculus
4. Whether the article is best positioned as one long paper or as separate analytic and statistical manuscripts
5. Whether the secondary Cayley section strengthens or distracts from the main submission

The internal audit found no contradiction or unhandled assumption after the corrections above. That conclusion remains provisional until independent mathematical review is completed.
