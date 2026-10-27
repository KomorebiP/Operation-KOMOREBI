# Large Signal Model Lean 0.13.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production PR-LASM 2.3.0 unchanged.

This block proves the exact spectral norm of the existing orthogonal pseudoinverse and constructs the bounded right inverse on the actual column space. It removes the inverse and inverse-norm hypotheses from the previous noisy-subspace theorem. It adds 20 named Lean theorems (16 supporting and four examples), four definitions and two rejection controls. P32 remains partial; coverage remains 38/87 complete, one partial and 48 not formalized.

## Primary verdict

Full P32: **incomplete, with the smallest missing implication** being the perturbation and leading-left-subspace tail results for the actual noisy table. The spectral lower bound, sharp pseudoinverse norms, constructed right inverse and the stated conditional noisy gap are proved as written in Lean.

PASS: 260 cumulative verification stages; 84 metadata/tooling checks.

## Main result

Let A:E→F be a linear map between finite-dimensional real inner-product spaces. Let r=dim(range A)>0 and s=σ_r(A), the smallest positive singular value of the actual map. Lean's singular-value sequence is zero-indexed, so s is `A.singularValues (r-1)`.

The release proves

\[
s\|x\|\leq\|Ax\|\quad(x\in(\ker A)^\perp),\qquad
\|A^\dagger\|=s^{-1}.
\]

The existing orthogonal pseudoinverse is used, with its earlier proved Penrose identities. Its restriction R:range A→E is constructed and satisfies ARy=y and ‖R‖=s⁻¹. These are conclusions, not fields or supplied hypotheses.

## Proof route

Choose the actual ordered orthonormal eigenbasis b_i of A* A. The pinned singular-value definition identifies its eigenvalues with σ_i². Adjointness and the eigenvector relation give

\[
\langle Ab_i,Ax\rangle=\sigma_i^2\langle b_i,x\rangle,\qquad
\|Ax\|^2=\sum_i\sigma_i^2\langle b_i,x\rangle^2.
\]

A zero singular mode has Ab_i=0. If x lies in (ker A)⊥, its coefficient at every zero mode is zero. On the other modes, ordering gives σ_i≥s. Parseval therefore gives ‖Ax‖²≥s²‖x‖². Nonnegativity gives the stated lower norm bound. This lower-bound theorem also accommodates rank zero with s=0; positivity is asserted only when r>0.

For y∈F, the existing pseudoinverse satisfies A†y∈(ker A)⊥ and AA†y=P_range(A)y. Applying the lower bound and projection contraction gives s‖A†y‖≤‖y‖. Hence ‖A†‖≤1/s, and the range restriction has the same upper bound.

For sharpness, choose the eigenbasis vector at index r−1. Its norm is one, its image norm is s, and its positive eigenvalue places it in (ker A)⊥. The pseudoinverse maps its image back to that unit vector. The operator norm inequality therefore gives 1≤‖A†‖s, and also 1≤‖R‖s. The upper and lower estimates yield both exact norm identities.

## Noisy-table consequence

Let X,N:E→F, let Q be an actual subspace of F of dimension rank(X)>0, and put s=σ_r(X). Suppose 0≤ε<s/2, ‖N‖≤ε and the observed tail satisfies ‖(I−Q)(X+N)‖≤ε. Then

\[
\|P_{\operatorname{range}X}-Q\|\leq 2\varepsilon/s<1.
\]

`gap_from_observed_tail` constructs R from X, proves XR=id on the true range and supplies the derived norm bound to the block12 residual theorem. It does not assume that Q is a leading singular subspace or prove that its observed tail is small. Those are remaining obligations. The inherited coordinate theorem then applies to this proved projection gap.

## Obligation matrix

| Obligation | Result |
|---|---|
| Actual sorted singular values of A, not a variational surrogate | Passed |
| Gram eigenbasis and weighted norm identity | Passed |
| Zero modes lie in ker A; retained vectors have zero tail coefficients | Passed |
| Rank−1 index validity and positive least singular value for r>0 | Passed |
| Lower bound restricted to the actual kernel complement | Passed |
| Existing orthogonal pseudoinverse and actual range inverse | Passed |
| Upper norm estimates and explicit unit minimizer for sharpness | Passed |
| Full and restricted inverse norm equality | Passed |
| Noisy gap removes the supplied inverse/norm premises | Passed |
| Scalar and rank-deficient boundary examples | Passed |
| Perturbation/rank separation | Not addressed |
| Actual leading-left subspace and tail characterization | Not addressed |
| Orthonormal-basis decoder and minimum-singular-value formula | Not addressed |
| Independent referee / second proof assistant | Not performed |

Dependency graph: pinned singular-value definition and spectral eigenbasis → weighted norm expansion and zero-mode elimination → lower bound on (ker A)⊥ → existing Penrose identities → inverse upper bounds. Positive final Gram mode → unit minimizer → matching inverse lower bounds. Constructed range inverse + block12 residual/projection theorem → noisy gap under the supplied observed tail and dimension.

No circular full-gap or inverse-bound premise is used in the new endpoint. The source correspondence is to frozen P32 span hash `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`. Upstream mathematical leaves are the project-pinned Lean definitions and lemmas inspected locally; no unverified external theorem is invoked.

Proofreading self-review covered the four new modules and current release prose in P32 context. No mathematical-token corrections were made during proofreading. Outstanding spectral and decoder proofs are substantive gaps, not copyediting issues.
## Exact remaining P32 obligations

1. Prove sorted singular-value perturbation and rank separation for the actual finite table, including the maximal-rank tail-zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its observed tail bound. The current strongest gap theorem still takes the candidate subspace's dimension and observed tail as inputs.
3. Prove the orthonormal-basis matrix minimum-singular-value bound and the explicit decoder U(UhatᵀU)⁻¹.

The right inverse on the true range and its bound from σ_r(X) are now proved. The earlier one-sided-to-full projection argument and basis-free coordinate conditioning are already proved. None of these results certifies unseen process modes or the adequacy of a chosen finite table.

## Development record

8 compiler invocations: 4 successful and 4 failed. Source snapshots and diagnostics are retained in `verification/development_block13/`.

The failures were a missing unfolding/rewrite for the named eigenbasis in the inner-product identity; a continuous-map versus linear-map coercion blocking a norm rewrite; scalar examples needing explicit quotient arithmetic and inverse notation; and an attempted simplification with deprecated or unused arguments, rejected by warnings-as-errors. Direct typed equalities and the appropriate algebraic rewrites resolved them. No statement was weakened, and no proof placeholder was accepted.

Development used previously checked predecessor objects. The accepted cumulative runs rebuild all project objects. Inventoried sources are frozen during accepted runs.

## Preservation

All 85 predecessor proof files, 1,354 declaration records and 77 predecessor rejection-control files remain unchanged. The frozen manuscript and proof register are unchanged.

The package contains a compact 0.12.0 source snapshot made from the exact delivered ZIP. It preserves proof, control, declaration and report evidence while omitting redundant nested ZIP payloads; its original archive manifest is clearly renamed. The original delivered 0.12.0 ZIP remains saved separately, with its identity and hash recorded in SOURCE_LINEAGE.json. Existing earlier history is preserved. This prevents recursive archive duplication without representing the compact snapshot as the original ZIP.
