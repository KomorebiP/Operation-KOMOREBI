# Paper VI Deep Mathematical Audit

## Audit scope

This audit examined the theorem statements, proof dependencies, finite verification, and boundaries of the revised Paper VI. Particular attention was given to statements that were conjectural in the original manuscript or that depend on normalization, topology, spectral gaps, or hidden state elimination.

## Packet semigroup chain

The block convolution theorem follows directly from inserting the finite packet identity between two semigroup factors. The time ordered path expansion is the bounded generator Dyson expansion with the packet identities inserted between off diagonal factors. Absolute convergence is controlled by

\[
\exp(T\lVert D\rVert)
\frac{(T\lVert N\rVert)^m}{m!}.
\]

The minimum transfer order conclusion is valid because a term with fewer than the required number of off diagonal factors vanishes identically.

**Audit result:** no internal gap found.

## Refinement and projective limits

The Duhamel and resolvent identities use the same generator defect

\[
\Delta=CA_f-A_cC.
\]

The several level formula is an exact telescoping identity. The summable defect theorem gives approximate consistency only. The projective limit theorem is stated separately under exact intertwining and uses the product topology. Strong continuity is therefore coordinatewise. The manuscript does not claim that summable defects alone construct an exact limiting generator.

**Audit result:** the distinction between exact and approximate refinement is correctly maintained.

## Markov and conditional expectation sections

The Markov convention uses column probability vectors. The aggregate rate criterion is derived from the entries of \(CQ\). Reversibility is transported by summing detailed balance over pairs of coarse blocks. The conditional expectation matrix is self adjoint in the weighted inner product, and nested partitions yield orthogonal projection differences.

**Audit result:** orientation and normalization are consistent throughout.

## Bayesian sufficiency

The necessary direction is checked using priors supported on one state in each of two different blocks. Equality of posterior block odds forces the likelihood ratio to depend only on the two block labels. Varying the state inside a block proves block constancy. The one block exception is stated explicitly.

The information loss theorem compares two nonnegative evidence vectors and uses the normalization inequality

\[
\left\lVert\frac a{\lVert a\rVert_1}
-
\frac b{\lVert b\rVert_1}\right\rVert_1
\leq
\frac{2\lVert a-b\rVert_1}
{\max\{\lVert a\rVert_1,\lVert b\rVert_1\}}.
\]

**Audit result:** the sufficiency criterion and defect estimate are valid under the stated positivity assumptions.

## Fractional refinement

The exact naturality result uses polynomial approximation on the finite union of the two spectra. The quantitative theorem uses the Balakrishnan representation and the resolvent defect

\[
C(\lambda+L_f)^{-1}
-
(\lambda+L_c)^{-1}C
=
-(\lambda+L_c)^{-1}\Delta(\lambda+L_f)^{-1}.
\]

The scalar integral evaluates to

\[
\frac{\sin(\pi\alpha)}{\pi}
\int_0^\infty
\frac{\lambda^\alpha}{(\lambda+\mu)^2}
\,\mathrm d\lambda
=
\alpha\mu^{\alpha-1}.
\]

The positive gap is essential for a uniform bound when the exponent is below one.

**Audit result:** the constant and the role of the gap were independently checked numerically and symbolically.

## Green operator chain

The inverse of the Dirichlet second difference matrix gives the continuum Green kernel exactly after one quadrature factor. The low mode eigenvalue bound follows from

\[
\sin x\geq x-\frac{x^3}{6}.
\]

The fractional estimate uses the lower bound \(\lambda_{k,h}\geq4k^2\) and the decreasing derivative of \(x^\alpha\).

**Audit result:** exact scaling and dispersion constants were checked for grid sizes from two through seventy nine.

## Feynman Kac chain

The finite state formula uses the backward generator \(Q^T\), consistent with the column distribution convention. The block constant potential theorem follows after transposing the Markov intertwining relation. The perturbation estimate uses the contraction property of killed Markov semigroups in the supremum norm.

**Audit result:** no orientation mismatch found.

## Elimination and memory

The Schur complement and time domain memory equations are two transforms of the same hidden state elimination. The exact local closure theorem compares the projected resolvent with a true resolvent on the retained space. It forces

\[
B=A_{PP}
\]

and a vanishing self energy. The finite moment test follows from the Laurent expansion of the hidden resolvent and Cayley Hamilton.

The rational realization theorem is stated for strictly proper rational matrix functions. Partial fractions and Jordan blocks provide a constructive realization. The compression estimate is finite horizon and assumes a bound on the approximate trajectory. These restrictions are stated in the manuscript.

**Audit result:** the theorem does not overstate locality or optimality.

## Survival section

The transient generator is stable, so all mass is eventually absorbed. The density is minus the derivative of survival. Resolvent integration gives the Laplace transform, and repeated integration gives

\[
\mathbb E[\tau^m]
=m!\mathbf 1^T(-A)^{-m}p_0.
\]

**Audit result:** the sign convention and moment power were checked against random transient generators.

## Highest risk statements for outside review

The following results deserve the closest independent review.

1. The projective limit generator discussion because the ambient space has the product topology rather than one Banach norm.
2. The finite Bayesian sufficiency criterion because its universality depends on quantification over every prior.
3. The fractional refinement constant because it combines two different operator spaces through one intertwiner.
4. The exact local closure criterion because cancellation can occur inside the self energy.
5. The rational realization statement because real and complex realizations require the expected treatment of conjugate poles.

The internal audit found no unresolved proof gap. This does not replace specialist review or establish historical priority.
