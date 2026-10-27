# WR15 independent mathematical and semantic audit

## Claim and current verdict

**Primary verdict: proved as written.** The raw WR15 proposition is correct over the real finite-dimensional spaces and whole-kernel basis stipulated immediately before it, and the current compiled Lean sources cover every clause. This mathematical signoff is tied to the exact source hashes, successful compiler/type evidence, and terminal clean replay/postflight identities recorded below. Release packaging remains outside this audit.

Reviewer: isolated `wr15_math_audit` agent. The raw target and accepted base definitions were read before any proposed implementation or author narrative. The checklist below was frozen and sent to the implementation/verifier agents before source review. This is an independent semantic derivation, not evidence that independent reviewers cannot share mathematical errors.

Authoritative raw target: `recovery/v1.11.0/Komorebi_Space_Lean_Continuation_v1.11.0/limits_v1.11.0/records/targets/05k_stopping_rules.tex`, proposition `WR15`, its preceding setup, and entire proof. SHA-256: `c808f84874650d1c08fb5ddee1e42bc6c59b82f3a7449a316135edf0442af85f`.

## Normalized claim card

Let E and Y be finite-dimensional real Hilbert spaces in orthonormal ambient coordinates, let p be the protected linear map, and let H = ker p with its inherited Hilbert metric. Let V = R^n with the Euclidean coefficient metric, including n = 0. Let B: V -> H be a linear isomorphism, followed by the subtype inclusion when viewed in E. Thus the columns are independent and span the **entire** permitted space H. Put T = D restricted to H, S = T B, G = B* B. For arbitrary c in V, datum r in Y, and real alpha, define a = Bc, q = (S* S + alpha G)c - S* r and the actual normal residual g = T*(Ta-r) + alpha a. Here * means the Hilbert adjoint and, in the stipulated orthonormal coordinates, is ordinary matrix transpose.

The claim is g = B G^-1 q and ||g||^2 = <q,G^-1 q>. For every invertible C: V -> V, put B' = BC and c' = C^-1 c. Then B'c' = Bc, S' = SC, G' = C*GC, q' = C*q, and <q',(G')^-1 q'> = <q,G^-1 q>. All formulas include n = 0. The algebraic identities require no sign condition on alpha; any positive-parameter hypothesis inherited from the regularization setting is harmless for that narrower intended use, but no optimizer existence or convergence theorem is needed here.

## Independent derivation and dependency graph

1. B is injective, so <v,Gv> = ||Bv||^2 > 0 for nonzero v. Because B is onto H, both B and B* are invertible between V and H; G is invertible and self-adjoint.
2. S* = B*T*, hence q = B*[T*(T(Bc)-r)+alpha Bc] = B*g. This identifies q with pairings of the actual residual, rather than defining a substitute residual using q.
3. G^-1 B* = B^-1 as maps H -> V. Therefore B G^-1 B* = id_H, giving g = B G^-1 q. In ambient E, the same operator is the orthogonal projection P_H because B spans all H.
4. Write z = G^-1q. Then ||Bz||^2 = <z,Gz> = <z,q> = <q,G^-1q> over R. This supplies the actual Hilbert norm equality.
5. B'C^-1c = Bc. The adjoint composition law gives G' = (BC)*(BC) = C*GC. Direct substitution into the independently defined primed normal equation gives q' = C*q. Neither conclusion requires C orthogonal.
6. (G')^-1 = C^-1 G^-1 (C*)^-1, with the displayed order. Thus the transformed quadratic form is <C*q,C^-1G^-1(C*)^-1C*q> = <q,G^-1q>. Equivalently both sides equal the squared norm of the same g.
7. For n = 0 the coefficient space and H are zero, all vectors are zero, the unique endomorphism is also its inverse, and both scalar forms are zero. No nonzero-vector witness or nonempty-index hypothesis is admissible as a prerequisite for the universal result.

Leaves are real inner-product/adjoint algebra and inverse laws, discharged by the checked Lean/mathlib proofs, plus the accepted project definition of the restricted operator. There is no external literature or numerical-computation leaf. The dependency path must run from accepted `ProtectedHilbertRepair.restricted` and `RegularizedHilbertRepair.gradient` to the coordinate residual; it must not run only from a newly declared metric norm or a newly named gradient surrogate to itself.

## Frozen obligation matrix

| ID | Required content | Verdict | Checked Lean evidence |
| --- | --- | --- | --- |
| O1 | Real Euclidean coefficient metric; inherited protected-kernel metric | passed | `dotProduct_eq_euclidean_inner`; `protected_gradient_norm_sq_eq_normalResidual` uses the ambient E norm |
| O2 | B independent and onto entire ker p, with no orthonormality assumption | passed | `Basis ι ℝ p.ker` in protected theorem types; `changedBasis` returns a full Basis of the same H |
| O3 | G is actual B*B and invertible; inverse laws hold | passed | `gram_posDef`, `gram_isUnit`, `protected_gram_eq_transpose_mul`, `inverse_gram_pairings` |
| O4 | S is actual D B | passed | `protected_operatorMatrix_eq_mul`; literal S=dm*Bm in `protected_coordinate_certificate` |
| O5 | q is actual (S*S+alpha G)c-S*r, not an assumed equality | passed | `normalResidual` definition; literal q in `protected_coordinate_certificate` |
| O6 | q = B*g for accepted `RegularizedHilbertRepair.gradient` | passed | `normalResidual_eq_pairings`; `pairings` is the actual inner-product pairing |
| O7 | g = B G^-1q, with full protected/ambient projection bridge | passed | `protected_gradient_eq_projected`, `protected_gradient_eq_synthesis_inverse_normalResidual`, `protected_coordinate_certificate` |
| O8 | Actual squared Hilbert norm equals the inverse-Gram quadratic form, without redefining the norm | passed | `gradient_norm_sq_eq_normalResidual`, protected ambient-norm specialization, consolidated certificate |
| O9 | Every invertible C, including nonorthogonal scaling/shear | passed | The full types require exactly `IsUnit C` in addition to finite real matrix structure; no isometry premise |
| O10 | c'=C^-1c represents same correction under B'=BC | passed | `changedBasis_apply`, `changedBasis_same_vector`, `changedBasis_coordinates`, `correction_basis_change` |
| O11 | S'=SC and G'=C*GC for actual changed bases | passed | `operatorMatrix_changedBasis`, `gram_changedBasis`; rectangular ambient matrix laws also exported |
| O12 | Independently defined primed equation gives q'=C*q | passed | `normalResidual_basis_change` and actual-basis `computed_normalResidual_changedBasis` |
| O13 | Inverse-Gram quadratic form invariant | passed | `inverse_gram_basis_change`, `inverse_gram_quadratic_basis_change`, `computed_certificate_changedBasis` |
| O14 | Zero-dimensional kernel admitted, scalar norm zero | passed | No Nonempty/Nontrivial premise in universal signatures; `norm_sq_eq_zero_of_empty_basis` and `zero_dimensional_certificate` |
| O15 | Full exported types have no hidden conclusion-strength assumptions | passed | All 51 public signatures inspected and matched exactly to final clean exports; all 15 generated helper signatures also reviewed |
| O16 | Current compiled exports use no sorry/custom axiom | passed | Both sources strict-compiled; all 66 final new declaration reports contain only propext, Classical.choice, Quot.sound |

## Adverse controls fixed before implementation review

* **Proper subspace:** E = R^2, p = 0, T = id, alpha = 1, r = e2, proposed a = 0. The full residual is g = -e2. Taking the single column B = e1 yields q = 0 and a zero metric certificate. Thus injectivity/kernel membership without spanning is insufficient. An equivalence onto the actual subtype `p.ker` excludes this failure structurally.
* **Nonorthogonal change:** B = I, T = 0, alpha = 1, c = e1, C = [[2,1],[0,1]]. Then q = e1, c' = (1/2,0), q' = (2,1), G' = [[4,2],[2,2]], (G')^-1 = [[1/2,-1/2],[-1/2,1]], and the metric quadratic form is 1 on both sides, while raw covector squared norms are 1 and 5. This detects a transpose/inverse confusion and an accidental isometry-only restriction.
* **Rank deficiency:** Redundant columns B = [1 1] into R give singular G = [[1,1],[1,1]]. No ordinary inverse theorem may accept this as a basis. Lean's totalized inverse notation alone is not evidence of invertibility.
* **Dimension zero:** V = Fin 0 -> R (with Euclidean norm), H = {0}. All corrections, coordinate covectors, and normal residuals vanish. The empty matrix inverse is the unique map and the scalar is zero. A theorem demanding a nontrivial coefficient space misses this clause.
* **Parameter sign:** alpha = 0 and negative alpha still satisfy the identities; positivity belongs to optimizer bounds elsewhere. A test must not confuse these identities with invertibility of S*S+alpha G.
* **Same-proposal requirement:** Transforming B while keeping c unchanged changes a in general. Invariance must explicitly use C^-1c or otherwise prove same a, not compare arbitrary unrelated proposals.

## Accepted semantic anchors inspected

`ProtectedHilbertRepair.restricted D p = D.comp p.ker.subtypeL`; its domain is the actual protected kernel. `ProtectedRegularizedRepair.restricted_adjoint` identifies the restricted adjoint with `p.ker.orthogonalProjectionOnto (D.adjoint r)`. `RegularizedHilbertRepair.gradient` is `normal T alpha a - T.adjoint r`, and `normal` is `T.adjoint.comp T + alpha • id`. `ExactCoordinates.Space n` is `EuclideanSpace R (Fin n)`, with the real Euclidean inner product and squared norm, so the Pi maximum norm is not substituted.

## Exact compiled source and type evidence

All paths below are relative to `wr15_v1.12.0` unless stated otherwise.

| Artifact | SHA-256 / evidence |
| --- | --- |
| `formal/KomorebiSpace/CoordinateCovector.lean` | `151661fac5f9ef5e2212ef41d76bf179299b5da4c5df10bf07844f18e04decfe` |
| `formal/KomorebiSpace/CoordinateBasisChange.lean` | `964ed871bf33db57c854b653125b9bf92416eefb5bc5df40877cd909ef366c07` |
| Strict core compile | `development/coordinates/attempt_011/report.json`: exit 0; source hash matches above |
| Strict basis compile | `development/basis_change/attempt_005/result.json`: exit 0; source hash matches above |
| Full core types/axioms | `development/coordinates/attempt_013/compile.log` and `report.json`: exit 0; 34 declarations |
| Reviewer full basis types/axioms | `reviews/math/BasisTypes.lean`, `basis_types.log`, `basis_types_command.json`, `basis_types_result.json`: exit 0; 17 declarations |
| Basis imported object provenance | Reviewer-resolved `.olean` hash `c8d951385d04c698020b5b833833b510418260cb9a81ee15532a0154b54e0d39`, exactly equal to strict basis attempt 005 output hash |

Source compilation and type exports use Lean 4.34.0-rc2 with `-j1 -DwarningAsError=true -DautoImplicit=false`. Exact commands and LEAN_PATH/LD_PRELOAD settings are preserved in the corresponding command/environment JSON. The reviewer type export imports the final compiled basis module and prints `#check @...` with universes/full names plus `#print axioms` for every declaration. No production source was modified by the reviewer.

Core type export attempt 012 was preserved as a failed development attempt because `pp.width` is not a supported option in this Lean version. Attempt 013 removed that presentation option and succeeded. The reviewer checked that its entire type/axiom output is byte-for-byte equal to attempt 012 after removing the single option error line; the successful run, not the failed run, is the cited evidence. The production proof source did not change in that correction.

## Semantic coverage of the consolidated result

`protected_coordinate_certificate` explicitly binds Bm to ambient orthonormal coordinates of the supplied full kernel basis, dm to the ambient-to-residual matrix of D, S to dm*Bm, G to Bm-transpose times Bm, q to the literal coordinate equation, and g to the already accepted restricted `gradient`. Its conclusions are the projected ambient residual identity, invertibility of this G, the ambient-coordinate equality g = Bm G^-1q, and the original ambient Hilbert norm identity. There is no hypothesis asserting any of those conclusions.

`changedBasis` is produced by mapping the original full Basis through the linear equivalence of an arbitrary invertible real matrix C. Its column equation is B'=BC, its same-vector equation uses inverse coordinates, and the core transport lemmas compute the Gram, observation matrix, coordinate residual, and quadratic certificate of that actual changed Basis. Consequently the invariance theorem specializes to H=ker p and the very same proposed correction; it is not merely an unrelated matrix identity or a comparison of changed optimization problems.

The coordinate carrier is a finite function type, but its default Pi norm is never used as the certificate. `dotProduct_eq_euclidean_inner` explicitly identifies the scalar product with EuclideanSpace's inner product. Completeness assumptions are satisfied by the finite-dimensional ambient/residual spaces in the raw statement. Decidable equality on the finite coefficient index imposes no mathematical restriction. The theorem is stronger concerning alpha (arbitrary real) and some ambient-space hypotheses, while covering the full stated case.

## Decisive evidence and exact remaining gap

The independent derivation and all O1-O16 checks pass. The proper-subspace and nonorthogonal-change adverse examples above were checked directly by exact hand algebra and used to assess the theorem types; they are not offered as numerical proof of the universal result. The universal result is proved by the compiled Lean declarations, with only the standard logical axioms listed above. There is no external-source or unproved computational dependency and no mathematical gap remaining for WR15.

A filesystem search found no applicable `AGENTS.md` in the inspected workspace/root scope. The raw target and accepted semantic anchors were read before implementation narrative. The original checklist was saved while source/type verification was still pending; this final revision replaces that pending status only after current-source compiler and full-type evidence became available. No production source, progress ledger, or acceptance record was edited by this reviewer.

The strongest safe statement is that WR15's real finite-dimensional coordinate-certificate identities, all invertible basis changes, actual protected residual/norm, and zero-dimensional boundary are formally covered by the named source revisions. The clean replay and adverse-control execution have now passed the separate terminal/postflight gates bound below. Release packaging remains a separate responsibility. If either production hash changes, this mathematical signoff must be reconsidered for the changed source.

## Proofreading self-review

Proofread: this audit report only. Routine edits: corrected a Markdown-table delimiter collision and updated one pending-tense phrase. Mathematical-token changes: none; the affected table label was reworded without altering its norm-equality obligation. Unresolved issues: none. Validation: reread the full report against the raw proposition, named Lean declarations, source hashes, and successful type logs; confirmed every Markdown table has four or two columns as intended. Production proofs were not copyedited.

## Terminal clean replay binding

The mathematical verdict is now bound to `integration/runs/clean_wr15_01`. Both the replay receipt and independent postflight have terminal **PASS**. The run strictly compiled all 156 targets, completed the prescribed 44 controls, and recorded the exact 238-command inventory. Its cumulative axiom catalogue has 5,048 declarations: all 4,982 inherited declaration identities are preserved, and 66 declarations belong to the two new modules. The latter comprise 43 source theorems, eight source definitions, and 15 compiler-generated theorem helpers.

| Terminal artifact | SHA-256 |
| --- | --- |
| `integration/runs/clean_wr15_01/axioms.json` | `9ad15c9fb3139088dc1e1afab28e137a8ae8d70b4a1eb6ba8bc40fb21271256b` |
| `integration/runs/clean_wr15_01/declarations_sorted.json` | `2154d10de1afa16c0bf95635a9f65b386360d7be2d72b2568e89ea3ba3097d95` |
| `integration/runs/clean_wr15_01/new_declarations.json` | `6222bd6e4b8b4e9a5e754201c14895128e0581a9ec2bd6f850c00b92d55cb2fd` |
| `integration/runs/clean_wr15_01/postflight.json` | `262fd925eb8ad139bebfcfc7627545da04ad7b3de6f0b0d3e32e0de67b3e90af` |
| `integration/runs/clean_wr15_01/receipt.json` | `2de09e2bdae21cd53e0b3ff294d706dbf1582446ef5a0e1b8bc875023a4737cb` |
| `reviews/math/clean_wr15_01/new_full_type_hashes.json` | `32588a50a24f86826f55c31e77ac8c3f50b8ac03083105f067230f5544ed25dd` |
| `reviews/math/clean_wr15_01/binding.json` | `d06d34f5780de7ef5fe47c7403d5b7ea8c337c8f2e42a8c72781e27efdd796af` |

`reviews/math/bind_clean_review.py` required terminal receipt/postflight PASS, checked both production and clean-snapshot source hashes against this audit's approved revisions, and checked the postflight's receipt/axiom bindings. It then imported the final clean object directory without writing any compiled object into it and reran the same public-type/axiom exports used for the source-specific review. The basis module's 17 declaration outputs and the core module's 34 declaration outputs are each **byte-identical** to the previously inspected logs. `public_type_comparison.json` records this comparison. `new_full_type_hashes.json` records a hash of every one of the 66 complete type strings in the terminal catalogue.

Every generated helper was inspected from a compiler-produced readable rendering of its final type; the final readable signatures are identical to those already read while controls completed. The original full, untruncated type strings remain in the bound `new_declarations.json`; the reading aid does not replace them. `generated_helpers_manifest.json` records each helper's originating module, kind, axiom list, safety flag, complete-type length, and complete-type hash, and `generated_helper_reviews.json` records each individual verdict and its mathematical meaning.

The 15 helper signatures are seven definitional equation lemmas; four matrix simplifier lemmas (transpose/inverse and three matrix-vector associativity variants); the determinant-unit proof used to construct `changedBasis`; one additive rearrangement in the actual protected-kernel subtype; and two congruence lemmas. The last two are named `KomorebiSpace.RegularizedHilbertRepair.gradient.congr_simp` and `Matrix.toLinearEquiv.congr_simp`: they were correctly included by originating module even though their namespace is not `CoordinateCovector`. No helper introduces an additional mathematical premise into a public WR15 statement. All 66 new declarations are safe and have axioms drawn only from `propext`, `Classical.choice`, and `Quot.sound`.

The additive rearrangement helper has a roughly 12-million-character fully explicit type because its inherited subtype and instance terms are printed in full. Its readable signature is precisely `(x+y)-z=(x-z)+y` with `x=T*(Ta)`, `y=alpha a`, and `z=T*r` in `ker p`. The large raw type was neither shortened nor removed from the terminal evidence; its full hash is included in the per-declaration hash catalogue.

The five new control sources were also read in the exact clean snapshot. The two positive fixtures use the production theorems for a nonorthogonal shear-and-scale change, a full scalar Hilbert basis with vector 2 and negative alpha, and an actual empty-basis Euclidean Hilbert space. The three negative fixtures reject the exact false scalar or invertibility consequences of the raw-covector-norm, proper-subspace, and singular-Gram adverse examples. Those negative fixtures are not described as a universal formalization of all malformed inputs. The universal spanning and norm guarantees come from the audited theorem types.

Terminal proofreading self-review: all newly added identities, counts, file references, helper classifications, and table delimiters were checked against the final JSON evidence. No production proof or mathematical claim was edited in this binding pass. This review's owned artifacts will be frozen by `reviews/math/FROZEN.json`; that manifest binds the final audit report and every other file in the reviewer's math subtree.
