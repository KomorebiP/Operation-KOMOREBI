# Guide to the formal companion

58/87 complete formal mappings, 1 partial, and 28 unformalized. P1 through P57 are mapped completely.

The source correspondence is a reviewed dictionary. Lean checks formal propositions and dependencies. It does not read the English manuscript or infer that measured data satisfy a declared observation protocol.

## Current proof paths

- P50 derives the full matrix-embedding probability cone and compact base from a definite interior. Actual weighted congruences yield validity and exact atlas transport. The later ambient trace-norm discussion remains separate.
- P51 uses the exact rational two-by-two embedding and congruences of the unchanged rotation model. Every word probability is unchanged and P46 still excludes finite positive generators.
- P52 constructs actual continuous kernels, measurable update versions, complete finite record measures, prefix consistency and exact reciprocal reference invariance from Bochner operator densities.
- P53 turns actual interval Gram, coefficient and moment checks into the actual matrix-domain density instrument and all-horizon probability semantics.
- P54 derives moment Gram invertibility, population reconstruction and one fixed induced-norm error bound. Signed-reset confidence retains the declared expectation, independence, coverage and reset protocol.
- P55 constructs distinct strictly positive continuous laws with equal low moments and actual TV13epsilon/40. Independent product moments agree at every length with scalar event realizations.
- P56 proves actual all-horizon record-measure pushforward equality for bin-history policies and the density-weighted cell posterior. Valid point sampling remains distinct from integration.

The preceding checkpoint's guide is preserved under `history/`. It explains the conditional expectation, grammar accounting, whole-record Bayesian refinement, missing intervention, reset concentration, observable completion, sequential confidence and covariance proof paths. All current scopes and endpoints are listed in `COVERAGE.md`.

## Boundaries retained by the proofs

A finite table does not certify global rank or missing intervention coverage. Matrix inversion does not prove fitted-model positivity. Conditioning retains its positive evidence requirements. Complete signed synthesis is distinct from a probability mixture. Statistical coverage is supplied by the declared observation protocol. Finite positive generators are a sufficient certificate language; P46 does not prohibit curved or quadratic certificates.

No active proof uses placeholders, new project axioms, native_decide or unsafe execution. All explicitly named declarations are audited against the standard dependencies propext, Classical.choice and Quot.sound. Module kernel replay checks the compiled environment beyond the source-index count.

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
