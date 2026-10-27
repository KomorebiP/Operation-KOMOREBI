# Failure ledger — Strong Artin Lean v0.14.0

Failures below are retained because they distinguish proof-engineering problems from mathematical obstructions. A failed or timed-out command is never counted as a theorem check.

## 1. Full portable-suite timeout

The portable kit’s broad verification command emitted several successful module results but exceeded the outer execution limit before returning an aggregate exit code.

**Classification:** operational timeout.  
**Promotion decision:** not counted as aggregate proof evidence. Narrow module builds with explicit return codes were used instead.

## 2. Wrong working directory

An early integration invocation ran `lake env` outside the portable workspace, so Mathlib was absent from the import path.

**Classification:** environment/path error.  
**Mathematical implication:** none.

## 3. Initial `Rep.of` universe mismatch

The first pre-Chebotarev scratch theorem constructed a categorical `Rep` from field, group, and module objects living in incompatible universes for Mathlib’s low-degree cohomology API.

**Resolution:** state the theorem directly for an existing `Rep`, and use Mathlib’s native single-universe interface only in the `H¹` capstones.

## 4. Residual inverse action was not automatic

Lean did not infer `rho sigma⁻¹ = 1` from `rho sigma = 1` while proving triviality of conjugation.

**Resolution:** prove it pointwise with `Representation.inv_self_apply`.

## 5. Provisional ambient cohomological capstone elaboration failure

Repeating the adjoint `Rep` expression in the `H1π` binder caused an elaboration mismatch across universes.

**Resolution:** restrict the capstone to Mathlib’s native same-universe interface. The corrected theorem compiled.

## 6. First quotient-adjoint invariance attempt

The first proof left scalar multiplication undistributed through conjugation, and the quotient action proof used `ext` before unfolding the quotient representation, causing the bound variable to receive the ambient type.

**Resolution:** prove scalar invariance pointwise; unfold `Representation.quotient`, use quotient surjectivity, and apply `Submodule.mapQ_apply` explicitly.

## 7. First quotient fixed-vector averaging attempt

The first calculation did not normalize the constant finite sum and mixed natural-number scalar multiplication with field scalar multiplication.

**Resolution:** use `Finset.sum_const`, `Finset.card_univ`, `Nat.cast_smul_eq_nsmul`, and `smul_smul` explicitly. The corrected averaging theorem compiled.

## 8. Schur membership orientation mismatch

The span-singleton witness expected `a • 1 = X`, while the intermediate Schur equality was oriented as `X = a • id`.

**Resolution:** give an explicit equality chain through the bundled intertwining map.

## 9. Unproved arithmetic leaves

The following were not attempted as if they were formal consequences of the finite algebra:

- centrality/linear disjointness for a concrete cyclotomic field tower;
- Chebotarev realization of the selected finite quotient element;
- identification with the local Taylor–Wiles Tate-duality functional;
- relative patching and packet occurrence.

**Classification:** genuine external/arithmetic research boundary, not Lean engineering failure.

## 10. First packaged verifier root mismatch

The first packaged replay compiled the four v0.12 modules, then failed when a v0.13 source was passed with the v0.12 directory as Lean's `-R` root. Lean requires each source to lie beneath the declared root.

**Classification:** verifier-path bug; the theorem source did not fail.  
**Resolution:** stage the exact v0.12/v0.13/v0.14 dependency closure into one flat source root before compilation. Existing successful object files remain reusable only when their source hashes match.
