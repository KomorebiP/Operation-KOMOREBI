# Paper VI Migration and Expansion Map

## Revised article

**Transfer Semigroups, Probabilistic Refinement, Fractional Operators, and Memory**

The original Paper VI was a 26 page realization paper. The revised article is a 54 page standalone manuscript. The general linear material is stated once in semigroup language, while the probabilistic, Bayesian, fractional, finite difference, elimination, memory, and survival sections are treated as exact realizations with their own hypotheses.

| Original block | Revised destination | Change |
|---|---|---|
| Finite semigroup reconstruction and block convolution | Sections 2 and 3 | Expanded to differential, Laplace, resolvent, Dyson path, Duhamel, resolvent defect, and holomorphic defect formulas |
| Exact refinement and Duhamel defect | Section 4 | Expanded to a bounded inverse limit theorem, weighted summable adjacent defects, range leakage, and generator based closure criteria |
| Markov lumping | Section 5 | Added a canonical quotient obstruction, exact coordinate characterization, continuous time descent, finite horizon error, and stationary descent |
| Conditional expectation towers | Section 6 | Reorganized as orthogonal packet projectors, martingale differences, energy decomposition, and total variance |
| Hermite example | Section 7 | Expanded to the Ornstein Uhlenbeck semigroup, Hermite reconstruction, generator, Dirichlet form, spectral gap, and fractional Hermite transfer |
| Bayesian packet evidence | Sections 8 through 10 | Expanded to perturbation bounds, prior stability, exact two stage updates, fixed coarse sufficiency, the coarsest sufficient partition, exact information splitting, Bayesian flows, and hidden Markov stability |
| Spectral fractional powers | Section 11 | Added Balakrishnan representation, exact naturality, a quantitative defect estimate, stable subordination, and the Poisson formula |
| One dimensional Green example | Section 12 | Expanded to exact nodal reconstruction, quadrature, an inverse maximum bound, a Poisson solution estimate, and low mode transfer |
| Finite Feynman Kac identity | Section 13 | Added continuous time transfer, alternating propagation and killing, positivity, and semigroup composition |
| Schur Feshbach identity and memory kernel | Sections 14 and 15 | Expanded to exact closure criteria, primary and Jordan decompositions, rational self energy, certified optimal block retention, auxiliary state realization, and Volterra trajectory bounds |
| Survival and hazard formulas | Section 16 | Expanded to state dependent killing, transforms, moments, residual life, and competing risks |
| Numerical certificates | Section 17 and `verification/` | Kept separate from proof and expanded into baseline and strengthened exact numerical suites |

## Conjectures converted into delimited theorems

The original source listed five conjectural targets. Four are now resolved in finite or bounded settings with explicit hypotheses.

1. **Uniform stochastic refinement under summable defects** became the weighted summable defect completion theorem and the asymptotic closure criterion.
2. **Canonical stochastic obstruction packets** became the canonical lumping obstruction on the kernel of the aggregation map.
3. **Naturality of fractional powers** became exact finite dimensional naturality and a spectral gap dependent defect bound.
4. **Packet characterization of Bayesian sufficiency** became the fixed coarse sufficiency theorem and the coarsest partition theorem.
5. **Weighted compression of memory kernels** became a certified primary block selection rule and a Volterra trajectory estimate.

These results do not establish arbitrary continuum limits, unbounded generator convergence, general statistical sufficiency, or globally optimal nonnormal model reduction.
