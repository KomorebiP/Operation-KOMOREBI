# Independent proof audit: shared affine corrections

Author: Komorebi P.  
Audit date: 8 September 2026  
Method: independent read-only review of the actual Lean definitions and proofs. The auditor did not edit the Lean implementation.

## Verdict and normalized claim

**Verdict: proved as written.** The mathematical statements have no identified gap. Fresh aggregate Lean verification passed, and the auditor independently matched every reported module and control source hash to the actual staged release files.

Let R be a commutative ring, U,V,W be arbitrary R-modules, and J:U→V and K:U→W be R-linear. Set

\[
C=U/(\ker J+\ker K).
\]

The formalization constructs surjective linear maps α:im J→C and β:im K→C with α(Ju)=[u]=β(Ku). It proves

\[
\operatorname{im}(J,K)\cong \operatorname{im}J\times_C\operatorname{im}K.
\]

The joint map is explicitly range-restricted, so the displayed identity is between submodules of im J×im K. It also proves finiteness of C when either V or W is finite. No field, finite-dimensionality, injectivity, or surjectivity onto V or W is assumed.

The quotient has both the ordinary quotient universal property and the paired pushout universal property: compatible linear maps h:im J→T and k:im K→T factor uniquely through C.

For the arithmetic application let q>0, L≥0, A:ℤᵈ→ℤᵉ and B:ℤᵈ→ℤᶠ be integer-linear, and suppose x solves Ax=b and Bx=c modulo qᴸ. The actual reduced maps are J=red_q∘A and K=red_q∘B. Residual vectors r,s with Ax−b=qᴸr and Bx−c=qᴸs are proved to exist. Then

\[
\begin{aligned}
&\exists y\equiv x\pmod{q^L}:
 Ay\equiv b\pmod{q^{L+1}},\quad By\equiv c\pmod{q^{L+1}}\\
&\quad\Longleftrightarrow\quad
\exists u,v:\ r+Au\equiv0\pmod q,\quad s+Bv\equiv0\pmod q,\quad [u]=[v]\text{ in }C.
\end{aligned}
\]

The quotient is finite and depends on q,A,B, without depending on L or the chosen solution. Given individual corrections, their classes are independent of those correction choices at the fixed residuals.

## Dependency graph

1. Mathlib module quotients and the first isomorphism theorem → well-defined labels and surjectivity.
2. Quotient equality ⇔ u−v∈ker J+ker K → explicit common correction → joint-image/fiber-product equality.
3. Quotient elimination and surjectivity → both uniqueness statements.
4. Finite target → finite range → finite surjective image C.
5. Integer coordinate divisibility → actual residuals and the representation y=x+qᴸt.
6. Linearity and cancellation of the nonzero integer qᴸ → next-level congruence ⇔ reduced residual equation.
7. A fixed individual correction identifies the full solution fiber of each reduced map.
8. Steps 2, 6, and 7 → exact joint-lift criterion. No common correction is assumed in the unconditional theorem.

All mathematical leaves are proved project declarations or mathlib declarations; no external-paper theorem or numerical experiment is needed.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Correct quotient | Passed | Definition uses the sum of kernels, not their intersection. |
| Labels independent of preimage | Passed | `liftQ` and `quotKerEquivRange` construct genuine linear maps. |
| Reverse fiber-product implication | Passed | From u−v=s+t with Js=0 and Kt=0, the proof takes w=u−s=v+t. |
| Universal properties | Passed | Existence uses `liftQ`; uniqueness uses actual quotient/label surjectivity. |
| Claimed finite scope | Passed | Either finite target suffices; the source module may be infinite. |
| Original arithmetic objects | Passed | `digitMap` is reduction composed with the actual integer-linear map. |
| Residual existence | Passed | Extracted coordinatewise from the stated lower-level solution. |
| Same lower residue | Passed | `HasJointLift` includes it and `same_residue_iff` supplies the correction vector. |
| Sign of correction | Passed | The exact equation is r+At≡0, matching y=x+qᴸt. |
| Individual solvability | Passed | Explicit in the unconditioned criterion; it is not silently inferred from compatibility. |
| Boundary q=1 | Passed | Included; reductions and the common quotient are trivial. |
| Boundary L=0 | Passed | Included; no nonlinear Taylor approximation is used. |
| Composite q | Passed | Included; cancellation only requires q>0, and modules are over ℤ. |
| Zero coordinate dimensions | Passed | Finite function types permit empty domains and targets. |
| Nonlinear/global/native claims | Out of scope | Neither unrestricted native conjecture follows from this block. |

## Decisive examples and controls

- J=K=id gives C=U and the diagonal fiber product. Individually attainable unequal targets do not glue.
- The two coordinate projections give C=0 and the full product. A zero left map likewise adds no compatibility restriction.
- With A=B=id on ℤ, q=2,L=1,x=0,b=0,c=2, both systems lift individually but a joint lift would require y≡0 and y≡2 modulo 4. The affine control proves this impossibility.
- A composite-modulus example at q=4,L=0 and the universal q=1 example check the stated boundary scope.
- The core controls include a finite common quotient with the infinite source (ℕ→ℤ/2ℤ).

The source controls test structural implications; no finite computation is being used as proof of an unrestricted theorem.

## Scope limits

The fiber product reconstructs the **joint image**, not U itself. The joint kernel is ker J∩ker K and may be nonzero. The common quotient C instead uses ker J+ker K; these have different roles.

Individual classes are independent of correction choice at fixed residuals. Changing the base representative can translate both classes by the same element; no absolute invariance of each class under that change is claimed.

This is a one-step affine lifting result. It does not establish indefinite lifting, a nonlinear Taylor bridge, arbitrary arithmetic seed invariance, or global reconstruction from unrelated local branches. Native Conjectures 13.2 and 13.3 remain open in their original generality. No novelty claim is made.

## Verification record

Read directly: `core/SharedCorrection.lean`, including the merged universal properties; `formalization/AffineObstructionCore.lean`, `AffinePairTransport.lean`, `AffineSharedCorrection.lean`, and `AffinePairControls.lean`; the core statement contract and positive/negative controls.

Aggregate record: `replay_01/shared_verification.json`, status **PASS**, elapsed 29.587 seconds, SHA256 `e985d2c3d9218de54f447411986794b8e8030cfaa7384aa12b6f0ed60a5f442a`.

- Six modules compiled afresh, with warnings treated as errors.
- Sixty explicit declaration axiom reports passed: 41 theorems, 11 definitions, and 8 abbreviations. This total includes the 13 previously checked affine-obstruction declarations rebuilt in `AffineObstructionCore`, positive control declarations, and one named statement-contract theorem. It is not a claim of 60 new mathematical results.
- Two statement-contract files passed. The second expands the actual original affine congruences, lower residue condition, and quotient by the two reduced-map kernels.
- Three intentionally invalid proofs were rejected with the expected diagnostics.
- All 13 recorded gates passed: compiler version, six module builds, two contracts, aggregate axiom audit, and three expected rejections.
- All 60 axiom closures contain only `propext`, `Classical.choice`, and `Quot.sound`.
- Every one of the 11 module/contract/negative-control source hashes matches both the local source and `release_staging/PRSC_IX_Shared_Correction_and_Checklist/shared_correction`. The reviewed core source also matches its formalization copy exactly.

Runtime: Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The project modules were rebuilt; mathlib was reused. No additional Lean rerun was performed by the auditor, because the fresh aggregate replay already supplied the necessary execution evidence.

Audit checks used read-only Python JSON parsing, SHA256 calculation, byte comparison of local and staged sources, declaration-count verification, and explicit inclusion checks against the three-axiom allowlist. No numerical experiment or empirical range was used to justify these universal statements.

There is no identified mathematical or verification implication left to fill in this block. The broader nonlinear and global obligations described above remain outside this proved result.
