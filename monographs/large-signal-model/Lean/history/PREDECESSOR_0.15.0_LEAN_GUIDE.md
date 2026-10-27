# Guide to the formal companion

48/87 complete formal mappings, 1 partial, and 38 unformalized. P1 through P45 are now all mapped completely.

The source correspondence is a reviewed dictionary. Lean checks the formal propositions and their dependencies. It does not read the English manuscript, infer that measured data satisfy an experiment protocol, or validate the source of real-world observations.

## New proof paths

- P11 constructs conditional expectations as actual L2 projections and derives residual orthogonality, the exact risk identity and monotonicity. It also proves the ordinary integral formulation for finite measures and complete real Hilbert targets.
- P23 treats summable infinite grammar evidence, exact posterior total variation, bounded predictive events, omitted-evidence budgets and convergence along every increasing exhaustive active-set sequence.
- P24 preserves normalized prior mass, whole-record evidence, child and other posteriors, and predictive events under the stated joint-likelihood mixture relation. It rejects both fresh prior duplication and per-step switching substitutions.
- P31 constructs actual one-state stochastic instruments. Every passive word has the same probability at every length, while the missing intervention distinguishes the models with certainty.
- P35 derives Hoeffding concentration from bounded independent trials, takes the finite experiment union, and transfers that single event to every covered core, shifted-block and initial-vector entry and norm.
- P37 constructs the canonical probability cone in observable coordinates and combines exact realization, normalized histories, atlas transport and packet synthesis. The same reset event yields simultaneous subspace and operator certificates; filtering uses the retained state and likelihood margins on that event.
- P48 takes expectations of actual conditional failure bounds and then a countable union. Its measurable simultaneous coverage event supports robust acceptance and every selected or stopped stage, with initial-state coverage retained.
- P66 is a checked partial mapping: predictable residual concentration for Nat-indexed rules on standard Borel sample spaces. General sample-space, interval-affine and rule-index transport remain explicit obligations.
- P68 derives bounded-test discrepancy from actual general-measure total variation and proves the pathwise lower certificate on the supplied residual event. It does not supply P66's missing regimes.
- P57 derives the actual integral covariance correction, its positive semidefiniteness, the affine variance formula and the normalized interval variance coefficient h²/12.

Additional mappings, including their exact accepted or partial scope, appear in `COVERAGE.md`. Read the source declarations named there before reusing a result in another setting.

## Boundaries retained by the proofs

The finite table does not certify global rank or missing intervention coverage. Matrix inversion does not prove positivity of a fitted model. A normalization bound requires its likelihood margin. A complete signed packet decomposition preserves full synthesis, while a probability mixture needs the separate positivity contract. Conditional statistical coverage must be supplied by the declared observation protocol.

No active proof uses placeholders, new project axioms, native_decide or unsafe execution. All explicitly named declarations are audited against the allowed standard dependencies propext, Classical.choice and Quot.sound. Compiler-generated environment content is checked by module kernel replay rather than by the source-index count.

## Spectral construction and decoder

The following detailed guide preserves the preceding spectral proof mechanism. Historical progress and verification counts in the preserved predecessor record describe that predecessor, while current counts and receipts are given by `RELEASE_COUNTS.json` and `verification/current/report.json`.

## Exact result

Let X,N:E→F be linear maps between finite-dimensional real inner-product spaces. Write r=dim(range X)>0, s=σ_r(X), Y=X+N, and assume ‖N‖≤ε<s/2. The nonnegative noise budget follows from ‖N‖≤ε. Let P project onto range X. The release constructs Q from the first r ordered right Gram modes of Y and their images, and proves that Q is the span of r orthonormal left singular modes.

\[
\sigma_r(Y)\ge s-\varepsilon,\qquad
\sigma_{r+1}(Y)\le\varepsilon,\qquad
\|(I-Q)Y\|=\sigma_{r+1}(Y),\qquad
\|P-Q\|\le 2\varepsilon/s<1.
\]

Singular values are the actual pinned Mathlib singular values, indexed from zero and padded with zero. Thus manuscript σ_r is index r−1, and σ_(r+1) is index r. The zero convention at maximum possible rectangular rank is proved explicitly.

For any orthonormal bases U and Uhat of range X and Q, let C=UhatᵀU. The formal matrix entries are inner products of the estimated and true basis vectors, and equality with the literal transpose product is proved in an arbitrary ambient orthonormal basis. Then

\[
\sigma_{\min}(C)\ge\sqrt{1-(2\varepsilon/s)^2}.
\]

The estimated coordinate map is injective on range X. The explicit decoder uses the ordinary matrix inverse,

\[
D=U(Uhat^\top U)^{-1},\qquad
D(Uhat^\top x)=x\quad(x\in\operatorname{range}X),\qquad
Uhat^\top Dy=y,
\]

and

\[
\|D\|\le [\sqrt{1-(2\varepsilon/s)^2}]^{-1}.
\]

This remains a finite-table statement. It does not establish that the selected history/test table captures every process mode or supply missing intervention coverage.

## Proof mechanism

The previous release supplied the actual right Gram eigenbasis, the weighted squared-norm identity and the exact pseudoinverse norm 1/s. This release uses the span of the first k basis vectors and its orthogonal complement. Their coordinate supports give lower and upper norm estimates from the ordered singular values.

Mapping the retained span through A gives the left subspace. The discarded image is orthogonal to that subspace, so its residual projection equals A applied to the discarded right projection. The upper estimate gives the tail bound; the next basis vector attains it. If k is the full domain dimension, zero padding gives the zero tail. Positive modes give injectivity of A on the retained span and hence its dimension. Normalized image modes are orthonormal eigenvectors of AA*, proving the correspondence with leading left singular vectors.

For perturbation at index k below the domain dimension, intersect the first k+1 right modes of A with the complement of the first k right modes of B. Their dimensions sum to one more than the domain dimension, so the intersection contains a nonzero vector. On it, the spectral lower bound for A, upper bound for B and triangle inequality yield σ_k(A)≤σ_k(B)+‖A−B‖. Swapping A and B gives the absolute perturbation inequality. Above the domain dimension both spectra are zero. This proves the required spectral inequalities without invoking an unverified min-max or Weyl theorem.

The noise bounds force Y to have at least r positive singular values, so the constructed Q has dimension r. Its proved tail bound feeds the block13 inverse construction and block12 projection argument. No desired tail, inverse bound, dimension equality or projection gap is assumed by the final noisy endpoint.

The cross matrix acts as projection P→Q expressed through the two orthonormal coordinate isometries. The earlier coordinate lower bound therefore controls its smallest singular value, evaluated on its actual final Gram basis vector. The constructed coordinate equivalence has an inverse matrix; the matrix multiplication identities identify that matrix with the ordinary nonsingular inverse C⁻¹. This proves the explicit decoder formula, both inverse laws and its norm bound.

## Source map

| Module | Contribution |
|---|---|
| SpectralSubspaces | Retained right spans, dimensions, coordinate support and two spectral bounds. |
| SpectralTail | Constructed left subspace, dimension, residual identity and exact tail norm. |
| SingularPerturbation | Dimension intersection; all-index absolute singular-value perturbation; noisy lower and upper bounds. |
| LeftSingularModes | Normalized left modes, orthonormality, left Gram eigenvector relation and span equality. |
| NoisySpectralSubspace | Data-selected subspace, derived rank/dimension/tail and full spectral/projection endpoint; rectangular maximum-rank convention. |
| BasisCoordinates | Cross matrix, coordinate maps, actual minimum-singular-value bound and injectivity. |
| BasisDecoder | Ordinary inverse matrix, explicit decoder, both inverse laws, true-range membership and norm bound. |
| DecoderMatrixFormula | Ambient basis columns, literal transpose product and matrix decoder formula. |
| FiniteTableP32 | Unified basis-conditioning and decoder endpoint with only P32's noise hypotheses. |
| Block14Examples | Seven exact checks, including sharp perturbation, retained/discarded scalar modes and the rectangular zero-tail boundary. |

## Reproduce the current companion

Use the current commands in README.md and the matching portable kit. The complete source-bound result is verification/current/report.json, with the source inventory and exact runtime/dependency pins. Historical development attempts and predecessor reproduction details are preserved in history/ and are not current continuation instructions.

## Continue the open formalization

The current state is 48 complete mappings, one partial mapping (P66), and 38 unformalized propositions. Every proposition P1 through P45 is complete. P46 is the first chronological unformalized obligation. P66 still needs the explicit sample-space, interval-affine conditional-expectation and rule-index transports in its coverage entry. Read CONTINUE_HERE.md and the versioned PROGRESS_LEDGER.md before resuming.
