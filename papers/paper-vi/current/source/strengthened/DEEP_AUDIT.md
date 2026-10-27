# Paper VI Deep Mathematical Audit

## Audit result

No unresolved internal contradiction or missing proof was found in the final manuscript. The final source contains 84 proved results and 84 proof environments. The conclusions are limited to the hypotheses printed in the paper. Independent specialist review remains necessary.

## Corrections made during the final audit

1. **Weighted refinement.** The completion theorem now carries the exact norms of the accumulated coarsening and reconstruction maps. The contractive version is stated as a corollary rather than silently assumed.
2. **Generator defect assumptions.** Contractivity of both connecting maps is now explicit in the generator defect corollary.
3. **Semigroup closure.** Adjacent consistency and invariance of the reconstructed fine range are treated as separate conditions. A convergent reconstructed family is not called a semigroup until range leakage vanishes.
4. **Markov descent.** The obstruction is defined intrinsically as the restriction of the aggregated operator to the kernel of aggregation. The finite horizon theorem now keeps the declared aggregation map fixed.
5. **Bayesian sufficiency.** A coarse description is called sufficient only when it reproduces coarse posterior masses and leaves packet conditional distributions unchanged. This removes the vacuous one block aggregation loophole. The common likelihood level sets then form the unique coarsest fixed sufficient partition.
6. **Fractional powers.** The quantitative defect estimate retains the common positive spectral lower bound. No uniform Lipschitz claim is made at the null space.
7. **Finite difference estimate.** The low mode proof now derives the trigonometric inequality on its stated range rather than invoking it without explanation.
8. **Memory expansion.** The rational self energy formula is proved directly from the nilpotent primary resolvent expansion, so it holds throughout the resolvent set. Its Laplace interpretation is then stated on a right half plane.
9. **Modal selection.** The largest weight rule is called optimal only for the certified blockwise upper bound. The paper states that cancellations can make the true best approximation different.
10. **Survival formulas.** Stability, nonnegative exit rates, and the distinction between decreasing survival and nonmonotone hazard are explicit.

## Highest risk theorem chains

### Refinement and limiting evolution

The chain is

\[
\text{adjacent defect summability}
\longrightarrow
\text{uniform reconstructed limit}
\longrightarrow
\text{range leakage control}
\longrightarrow
\text{semigroup closure}.
\]

The first implication is a telescoping norm estimate. The second is not automatic and is supplied by the separate closure theorem. The generator criterion is restricted to bounded contraction models with orthogonal reconstructed ranges.

### Bayesian coarse descriptions

The exact two stage formula always uses prior dependent packet averages. A fixed coarse likelihood exists with no hidden local change exactly when the fine likelihood is constant in each packet. The relative entropy chain rule then separates the coarse contribution from the conditional contribution.

### Fractional defect estimate

The Balakrishnan integral converts the ordinary defect into a resolvent sandwich. The integral constant is

\[
\frac{\sin(\pi\alpha)}{\pi}
\int_0^\infty\frac{s^\alpha}{(s+m)^2}\,ds
=
\alpha m^{\alpha-1}.
\]

The estimate is therefore valid only with the declared lower bound \(m>0\).

### Hidden dynamics and memory

The Schur Feshbach identity, time domain elimination, primary decomposition, and Volterra stability bound are algebraically compatible. A finite hidden block gives a strictly proper rational self energy. It does not give an arbitrary constant correction or an arbitrary memory law.

## Boundaries retained

The article does not claim:

1. a general theorem for unbounded generators or varying domains
2. universal stochastic refinement for arbitrary projective systems
3. statistical sufficiency beyond the stated finite likelihood model
4. locality of fractional powers
5. higher dimensional or irregular mesh Green identities
6. optimal model reduction in the presence of modal cancellation or severe nonnormality
7. finite realization of an arbitrary memory kernel
8. monotonicity of every phase type hazard
