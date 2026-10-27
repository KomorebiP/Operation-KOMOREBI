# Guide to the formal companion

66/87 complete formal mappings, 1 partial, and 20 unformalized. P1-P65 and P68 are mapped completely.

Manuscript correspondence is a reviewed dictionary. Lean checks formal propositions and dependencies; it does not read the English manuscript or establish that observed data satisfy a declared protocol.

## New proof paths

- P58: Actual normalized Bochner cell averages on a finite measurable positive-mass partition preserve the original cone, exact integrated mass and every cell operator. The genuine induced probability-cone base norm gives the Lh resolution bound. Actual uniform equal-interval distance integrals give Lh/3. Null/empty conventions and required finite masses, metric and Lipschitz hypotheses remain explicit; a point sample is not substituted for an integral.
- P59: Actual time-dependent Bochner DensityInstrument families on a common finite-dimensional probability cone and probability reference, with finite actions and one common measurable randomized full-history policy, have actual finite record-law TV at most min(1,(e0+sum epsilon)/2). Integrated contraction is derived from positive decompositions, and TV from the signed-measure half-density identity; no branch-density lower margin is required. The optional conditional-event helper proves an eventwise 2TV/min-masses bound with both masses positive, not the stronger adjacent full conditional-law statement.
- P60: Literal fixed-template coefficient/mass matching is a finite real linear system. Fitted coefficient-word observability derives uniqueness among all linear matches, including singular competitors. An invertible match transports the actual matrix-domain polynomial Gram certificate with unchanged Gram data, exact mass and actual finite record laws. Fitted initial PSD and mass normalization remain a separate check. Observability neither supplies invertibility nor guarantees existence.
- P61: Actual supplied finite dimension and polynomial degree with an invertible complete population core derive inverse-moment fitted coefficients, full densities and word likelihoods. The independent P53 finite matrix/Gram/moment witness and transformed initial PSD/mass check for that same family yield actual all-horizon laws. Literal original/atlas event-law transport, a sufficient invertible P60 template constructor, complete signed synthesis with separate packet positivity, actual bin-policy pushforward, P58 Lh and Lh/3 resolution and P59 common-cone/reference/policy budgets are connected to the same fitted instrument. No dimension/degree discovery, empirical coverage or generating-process adequacy is inferred.
- P62: Actual positive-definite metric and centered mass coordinates derive a genuine curved ProbabilityCone, including empty spatial dimension. Literal Q, PSD remainder and nonnegative multiplier plus both inverse-metric orientation inequalities imply cone preservation. Finite interval SOS/Gram/degree/coefficient and exact moment checks construct the actual uniform-reference polynomial DensityInstrument and arbitrary-policy probability laws, word densities and prefixes at every horizon. This is a sufficient replayable certificate, not a completeness result for search.
- P63: The literal fitted polynomial ratio, its invertibility and mass row derive the affine block form and unique fixed center. An actual one-dimensional symmetric invariant-form subspace with a positive-definite member, and an actual rank-one fitted anchor with nonzero normalized displacement, derive the unique normalized positive metric. Complete P62 witnesses, exact mass and initial coverage for the same fitted family then yield actual all-horizon laws. Boundary placement remains a conditional proposal; failed discovery does not prove invalidity.
- P64: Literal Bernstein-Durrmeyer integral coefficients define cone-positive degree-at-most-n polynomial operators with exactly unchanged integrated mass. The actual doubly stochastic kernel has squared displacement 1/(3(n+2)); its actual joint-law variance inequality gives integrated genuine base-norm error L/sqrt(3(n+2)) under the stated induced-norm Lipschitz premise. Actual common-policy record laws obey min(1,TL/(2sqrt(3(n+2)))). No finite true-degree assumption is imposed; adjacent scalar examples are separate.
- P65: Actual fitted positive Bernstein coefficients with exact average mass define a genuine DensityInstrument and finite policy probability laws. Normalized-input genuine base-norm coefficient budgets integrate to their average; the finite-action maximum is added to the actual P64 L/sqrt(3(n+2)) approximation bias. A separately supplied actual correction discrepancy is added by a proved integral triangle inequality. Positivity and mass alone do not erase coefficient error.

The preceding guide is preserved under `history/`. It records the earlier conditional-expectation, grammar, whole-record Bayesian refinement, intervention, reset concentration, observable completion, curved rotation and continuous certificate constructions. Every current mapped scope and endpoint remains in `COVERAGE.md`.

## Retained boundaries

Supplied dimension, degree, coverage and domain assumptions remain visible. Matrix inversion does not prove fitted positivity. Conditioning requires positive evidence. Complete signed synthesis is distinct from assigning each packet a probability law. Bin-history policies retain exact coarsening; within-cell-reactive policies require a separate comparison. Coefficient estimates and model corrections retain their own error budgets.

Internal source review, source identity, compiler acceptance, kernel replay and archive integrity are different checks. No external independent certification is claimed. Active proofs have no placeholders or new project axioms; named dependencies are audited against propext, Classical.choice and Quot.sound. Module replay also checks the generated environment beyond the named source inventory.

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
