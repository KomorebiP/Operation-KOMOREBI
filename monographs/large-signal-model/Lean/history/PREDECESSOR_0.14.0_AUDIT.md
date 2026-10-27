# Large Signal Model Lean 0.14.0

Komorebi P. — 2026-10-15. Frozen theory 1.0.0; PR-LASM production software 2.3.0 unchanged.

P32 is complete in its stated finite-table scope. This block constructs the leading singular subspace, proves singular-value perturbation and the exact observed residual, and proves the ordinary matrix inverse decoder and its conditioning. It adds 54 named Lean theorems (47 supporting and seven examples), nine definitions, ten proof modules and two rejection controls. Coverage is now 39/87 complete, zero partial and 48 not formalized.

## Primary verdict

**Proved as written**, for P32 in frozen Foundations 1.0.0 §33, lines 1388–1426, statement/proof span SHA256 `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`. This is a self-review verdict on formal-statement correspondence. The formal modules compile; cumulative release acceptance is stated below.

PASS: 282 cumulative stages; 84 metadata/tooling checks. Exact delivered-ZIP replay is recorded separately in the external verification JSON.

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

## Self-review obligation matrix

| Obligation | Result and evidence |
|---|---|
| Actual sorted singular-value definition and zero-based indexing | Passed; inherited spectral expansion and new perturbation theorem. |
| Retained span, its dimension, and coordinate support | Passed; SpectralSubspaces. |
| Actual left singular subspace rather than an assumed candidate | Passed; SpectralTail and LeftSingularModes. |
| Exact residual norm, including k=0 and k=domain dimension | Passed; leadingLeft_tail_norm, scalar boundary examples. |
| All-index perturbation, rectangular maps and padded zeros | Passed; singularValue_abs_sub_le, singularValue_zero_at_max_rank. |
| Positive true rank and data-derived dimension equality | Passed; noisy_rank_lower and learnedLeft_finrank. |
| Projection gap from only the stated noise/rank premises | Passed; finite_table_stability. |
| Cross matrix equals UhatᵀU with correct operation order | Passed; cross_entry and cross_eq_transpose_mul. |
| Actual minimum singular value and coordinate injection | Passed; cross_min_singular and coordinates_injective. |
| Ordinary matrix inverse, both decoder inverse laws, true-range image | Passed; BasisDecoder. |
| Literal matrix decoder and claimed operator norm | Passed; decoder_matrix_formula and decoder_norm_bound. |
| Frozen P32 statement/proof correspondence | Passed by self-review; the complete finite-table conclusion is covered. |
| Source and archive cumulative replay | See verification status and exact-archive JSON. |
| Exhaustive upstream rebuild or independent referee | Not performed. |
| Full-process coverage and statistical confidence | Out of scope for P32; not inferred. |

## Dependency and source checks

Pinned Gram spectral theorem and ordered singular-value definition → weighted norm expansion → retained/tail coordinate estimates. Those estimates plus dimension intersection → all-index perturbation. Positive image modes → actual leading-left span and dimension; orthogonality and the next Gram vector → exact residual norm. Noise inequalities → data-derived rank and tail. Inherited exact pseudoinverse norm and one-sided-to-full projection argument → full gap. Coordinate isometries and that gap → cross-matrix lower bound; actual final Gram vector → minimum singular value. Coordinate equivalence plus matrix composition identities → ordinary inverse decoder and norm bound.

No dependency points back to a conclusion as an input. The strongest noisy endpoints take X, N, positive rank and the original noise inequalities; no spectral perturbation, observed tail, gap, inverse bound or matrix nonsingularity is supplied. Auxiliary conditional lemmas retain their own explicit hypotheses.

External mathematical leaves are the exact local pinned Mathlib sources: SingularValues.lean, Spectrum.lean, PiL2.lean, Orthogonal.lean, Projection/Basic.lean, Projection/FiniteDimensional.lean, LinearAlgebra/Dimension/{Constructions,Finrank,StrongRankCondition}.lean, FiniteDimensional/Lemmas.lean, Matrix/{ToLin,NonsingularInverse}.lean and Analysis/Normed/Lp/Matrix.lean. The new perturbation argument is proved internally, so no named external perturbation theorem is imported on trust. Upstream compiled dependencies remain part of the stated verification boundary.

The seven examples use exact Lean identities, not numerical estimates. Two new controls request residual ≤1 for the scalar-two map with no modes retained, and singular-value change ≤1 for scalar two versus zero. Both are mathematically false and must be rejected. They test the new bounds' sharpness without treating finite examples as universal proof.

No mathematical proof obstruction remains for P32. The failed development steps were implementation diagnostics or environment failures, recorded below. Alternative min-max-library and best-low-rank-approximation routes were not needed once the dimension-intersection construction succeeded; they are not reported as failed or exhausted research routes.
## Preserved development record

There were 22 recorded tool invocations: 10 succeeded and 12 failed. Of these, 21 invoked Lean and one diagnostic tracing attempt was blocked before Lean ran. Every attempted source snapshot and its output is retained in `verification/development_block14/`.

Nine failures were ordinary Lean proof or warnings-as-errors diagnostics: an incorrect namespace and a deprecated Fin accessor; coercion/type inference around a finite span's dimension; unfolding a Gram eigenbasis and normalizing inverse arithmetic; function versus finitely supported function coercions; unused finite-dimensional section assumptions; subtype equality and continuous/linear-map coercions; and explicit scalar operator-norm simplification. Typed intermediate facts, the pinned API and explicit coercions resolved them. The stated mathematical target was not weakened.

Two tail-module runs reached output-file creation and failed while disk space was critically low. Already-saved duplicate extraction/build trees were removed, and the unchanged tail source then compiled. A `strace` diagnostic was rejected by process tracing permissions; no bypass was attempted. These are environment failures, not rejected mathematical claims. The logs are preserved and the cumulative verifier rebuilds all project objects from scratch.

The first metadata pass also failed because an inherited roadmap check still required 49 unfinished propositions. The check was updated to 48 after P32 completion, while retaining exact set equality and disjoint coverage of all 87 propositions. This diagnostic is recorded separately in BLOCK14_METADATA_DEVELOPMENT.json.

## Preservation

All 89 predecessor proof files, 1,378 declaration records and 79 rejection-control files remain unchanged. The frozen Foundations 1.0.0 manuscript and proof register retain their hashes. Prior progress records remain historical evidence: their then-partial P32 status is not retroactively changed.

The compact 0.13.0 source snapshot was made from the exact delivered ZIP (`7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5`). It preserves all non-archive files and records omitted nested ZIP payloads. Its original manifest is renamed; the source snapshot is not represented as the original delivered archive. The original archive remains saved separately. All historical non-archive records are retained. To avoid disk exhaustion and repeated nested payloads, older ZIP files are represented by exact hashes and member paths in HISTORY_ARCHIVE_REFERENCES.json; their bytes are preserved inside the separately saved exact 0.13.0 archive. The immediate 0.13.0 source snapshot stays embedded. This changes packaging, not current proof content or predecessor diagnostics.

## Continuation

No P32 implication remains open in the stated finite-table theorem. The broader program has 48 unformalized propositions; see ROADMAP_1.0.json for the exhaustive disjoint list.

Next bounded target: P31, missing-intervention nonidentifiability, in frozen Foundations §32. The exact manuscript construction uses one hidden state and two observations. Both models give (1/2,1/2) under action a; they give (1,0) and (0,1) under b. Formalize actual stochastic models, prove every a-only word has common probability 2^(-length), and exhibit the one-step b disagreement. Existing instrument and word-probability APIs should supply the construction. P31 is not counted as proved by this handoff.

P35's reset-experiment probability certificate and P37's conditional observation-based completion remain further parts of the learning chain. P32 does not silently supply their statistical or coverage assumptions.
