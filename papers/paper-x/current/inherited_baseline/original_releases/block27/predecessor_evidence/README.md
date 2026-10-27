# Paper X — Block 19

This cumulative release proves simultaneous lifting and labeled conjugacy for complete finite orthogonal projector families inside a supplied integral finite-group carrier. The full arithmetic ledger remains **15 checked claims and 5 partial claims**.

## Checked existence theorem

Let R be a commutative integral domain complete for the (π)-adic filtration. Let Γ be finite and ρ an actual integral matrix representation. Assume |Γ| is nonzero in R and divides π^e. For k>0, let (Q_i) be a finite labeled family of equivariant idempotents over R/(π)^(e+k), pairwise orthogonal in both orders and summing to the identity.

There is a complete labeled family (E_i) of actual integral equivariant projectors with every E_i retaining Q_i modulo (π)^k. The precision loss is at most e, independent of the matrix rank and number of labels. No local-ring or finite-residue-field assumption is needed for this existence theorem. Empty label sets are handled uniformly when the input completeness equation is possible. The carrier and the deep quotient family remain supplied inputs.

Every input matrix is averaged once to make it exactly equivariant. Finite induction then corrects inside the complementary corner to the already lifted projectors. Each correction retains depth k. After all labels are lifted, the remaining complementary idempotent reduces to zero at positive depth; adic separatedness forces it to vanish. This proves the exact sum-to-identity equation.

## Actual decomposition and rigidity

The release constructs an actual equivariant linear isomorphism between R^n and the finite product of im(E_i). Its maps are v ↦ (E_i v)_i and (v_i)_i ↦ sum_i v_i. The images are genuine invariant submodules. The existing image-reduction theorem applies to each component, giving surjectivity onto the corresponding reduced projector image. No basis, freeness assertion, or intrinsic quotient-module isomorphism is assumed for the components.

If R is local, π is a nonunit and two exact complete families E,F agree label by label modulo (π)^k with k>0, then

    U = sum_i F_i E_i

is an actual integral unit, commutes with ρ, reduces to the identity modulo (π)^k, and satisfies U E_i U⁻¹ = F_i for every label. It induces equivariant linear isomorphisms of the actual images. Rigidity itself does not require a finite group, a domain, or completeness. More generally, a unit-reflecting coefficient map suffices. The combined theorem proves existence and uniqueness up to this precise labeled conjugacy; exact uniqueness of projector matrices is false.

## Examples and boundaries

A continuous rank-three C₂ carrier diag(1,−1,1) over Z₂ has a complete three-projector family modulo 4 obtained using the shear I+2e₀₁. The general lifting theorem constructs three nonzero integral summands retaining that family modulo 2. Lean proves that no exact equivariant family retains the whole prescribed family modulo 4.

Other checked examples show that independent exact equivariant idempotent lifts can fail orthogonality and the sum-to-identity equation, and that two complete families with the same reduction can be distinct while related by the required identity-congruent conjugacy.

## Verification and contents

The release contains nine new production modules alongside all 112 predecessor modules. Final build counts, source and proof-object hashes, axiom results, compiler controls and archive replay are recorded in verification.json, axioms.json, archive_replay.json and the release audit. The predecessor sources and rebuilt proof objects are required to remain byte-identical. Only Lean's standard propext, Classical.choice and Quot.sound axioms are permitted by the audit.

Independent source review is in FAMILY_PROOF_AUDIT.md. Exact finite checks are in checks/exact_families.py, exact_families.json, EXACT_FAMILIES_AUDIT.md and EXACT_FAMILIES_REVIEW.md. They cover 98 constructed family lifts with 370 projectors, 49 conjugacy comparisons, 8 exhaustive small pairs and 128 vector decompositions. The larger cases are deterministic constructed examples, not an exhaustive census or proof of convergence. The finite implementation corrects all but the final projector and fills the complement; the Lean induction lifts every label and proves the remaining complement zero.

The updated ledger, status report, amended LaTeX and patch are included. No new PDF was typeset. Block 18's frozen cumulative archive and reports are retained under references/ and predecessor_evidence/.

## Reproduction

Use the external matching portable Lean 4.34.0-rc2 kit. The verifier checks the compiler hash and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

```bash
python3 checks/verify_release.py /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/exact_families.py
```

All project proof objects are rebuilt from production sources for the cumulative check. Deliberately false statements and the placeholder control remain under checks/, outside production.

## Arithmetic boundary

This completes the simultaneous finite-group projector-family step relevant to Claim 9.2. It does not identify the intended arithmetic packets, construct Galois-to-Weil–Deligne attachment or period objects, establish coefficient/Hodge–Tate comparisons, or prove arithmetic Frobenius coverage. Universal positive occupancy remains conjectural. None of the five full arithmetic claims is promoted.
