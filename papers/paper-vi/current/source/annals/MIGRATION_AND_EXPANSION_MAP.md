# Paper VI Migration and Expansion Map

## Revised article

**Title:** Transfer Semigroups, Probabilistic Refinement, Fractional Operators, and Memory  
**Author:** Komorebi P.

The original manuscript developed a finite packet language for semigroups, Markov chains, conditional expectation, Bayesian updating, fractional powers, Green operators, Feynman Kac transfer, hidden state elimination, and survival. The revised article preserves that finite core and reorganizes it around four mechanisms:

\[
\text{packet evolution}
\longrightarrow
\text{refinement}
\longrightarrow
\text{probabilistic coarse graining}
\longrightarrow
\text{elimination and memory}.
\]

## Record migration

| Original material | Revised location | Disposition |
|---|---|---|
| Packet reconstruction and block convolution | Section 2 | Retained and expanded |
| Reducing packets | Section 2 | Retained |
| Laplace resolvent formula | Section 2 | Retained as a packet resolvent statement |
| Generator intertwining and Duhamel defect | Section 3 | Retained and expanded |
| Multilevel refinement | Section 3 | Added exact telescoping and summable defect results |
| Continuum refinement conjecture | Section 3 | Split into exact projective limit evolution and approximate coherence |
| Markov lumping | Section 4 | Expanded to an aggregate rate criterion and reversibility |
| Conditional expectation | Section 5 | Expanded to orthogonal martingale packets and variance decomposition |
| Bayesian evidence and composition | Section 6 | Retained |
| Bayesian sufficiency conjecture | Section 6 | Replaced by a finite necessary and sufficient criterion |
| Bayesian approximation | Section 6 | Expanded to an exact information loss formula and stability bounds |
| Hidden Markov filtering | Section 7 | Added exact and defective coarse filter theorems |
| Fractional spectral semigroup | Section 8 | Retained and expanded |
| Fractional naturality conjecture | Section 8 | Proved for exact intertwiners and quantified under a positive spectral gap |
| One dimensional Green identity | Section 9 | Retained with fractional low mode consequences |
| Finite Feynman Kac formula | Section 10 | Retained with path slicing, perturbation, and coarse transfer |
| Schur Feshbach elimination | Section 11 | Retained and expanded |
| Memory compression conjecture | Section 11 | Replaced by rational realization and a finite horizon stability theorem |
| Survival and hazard | Section 12 | Expanded to Laplace transforms, moments, and phase type rationality |

## Material not carried into the article body

The Ornstein Uhlenbeck and Hermite calculations, the Beta binomial illustration, the elementary random walk example, and long numerical registries were not needed for the central proof chain. Their role is covered by standard references or by the verification supplement. The revised article retains only examples that clarify a theorem or a boundary.

## Conjecture resolution

### Uniform stochastic refinement

The revised article does not infer an exact continuum generator from summable defects. It proves two separate statements.

1. Exact interlevel intertwining defines a semigroup on the projective limit with the product topology.
2. Summable generator defects give uniform asymptotic coherence on bounded time intervals.

### Bayesian sufficiency

For ordinary finite block aggregation, exact Bayesian commutation for every prior is equivalent to a likelihood that is constant inside each block. A separate theorem treats prior families with fixed conditional distributions.

### Fractional naturality

Exact generator intertwining transports every positive fractional power. For approximate intertwining and exponent between zero and one, a positive spectral gap gives the explicit constant

\[
\alpha\mu^{\alpha-1}.
\]

### Memory compression

The revised article does not claim an optimal compression method. It proves that finite auxiliary closure is equivalent to a strictly proper rational memory transform and gives an explicit trajectory bound in terms of the kernel error on a finite interval.

## Remaining boundaries

The article does not establish a general limit theorem for approximate projective systems, a minimal Bayesian statistic in continuous spaces, a gap free operator norm estimate for fractional powers, an optimal rational memory approximation, or a general unbounded operator theory.
