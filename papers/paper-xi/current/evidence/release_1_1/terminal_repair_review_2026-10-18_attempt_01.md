# Terminal repair source review — attempt 01

Reviewed: 2026-10-18T19:14:25.622058+00:00

## Outcome

No change to the intended mathematical conclusions or domain under the original explicitly declared standing section data was found in the reviewed delta. **This is an intermediate source review, not a release PASS.**

The separate bounded diagnostic status at review was **FAIL**.

## Exact revision

- Source: `paperxi_lean/evidence/terminal_repair/attempt_01_compatibility/ActualMonomialLocalGlobal.lean`
- Source SHA-256: `adf71a00e7445d6ad369b52ff55d2becb7ab6327509e1b1b8ebcaebd855392c7`
- Patch: `paperxi_lean/evidence/terminal_repair/attempt_01_compatibility/FROM_IMPORT_ONLY.patch`
- Patch SHA-256: `43f6206eec3bd169bafaf8f4d86f9e360de8dc2da85889119e7ea7c41520f208`
- Recovered original SHA-256: `fd37173d05fb42af98a4eae535e25975c63d90e532c18913f0aa132ca15736ea`
- Import-only intermediate SHA-256: `288c410b05d9a7c3c3d9364af47a5d7bf2ddaea7747308f005ea5e43fd875651`

## Essential comparison limit

The recovered original and its import-only revision do not successfully elaborate. There is no valid original kernel-declaration population with which to establish checked old-versus-new declaration equivalence. This review compares the intended mathematical reading of the original source under all explicitly declared standing section data.

## Reviewed changes

### Argument elaboration

Location: Local API applications throughout the file.

Positional n becomes (n := n) for locally declared APIs whose n is implicit. Imported APIs with explicit n retain positional n.

Selects the already intended parameter; no object or assumption changes.

### Standing hypotheses made explicit

Location: fixed_zero_eq_tame_invariants; standardArtin_eq_coordinates; packetArtin_eq_standardArtin; inertia_le_kernel_iff_label_zero; exists_unramified_descent_iff.

Adds include directives for hιrange and, at existence of descent, the already-declared hφ, hrel, hξ, hF as needed.

These are already standing data in the recovered section and are consumed in its intended proof. The exported binder list is affected; it would be incorrect to claim that all formal theorem signatures are textually unchanged.

### Comment syntax

Location: htame declaration.

Documentation comment becomes an ordinary block comment before variable.

No mathematical content changes.

### Equality direction in contradiction

Location: inertia_le_kernel_iff_label_zero.

Uses (NeZero.ne n) hdim instead of (NeZero.ne n) hdim.symm.

The retained dimension identities produce hdim : n = 0 in the nonzero-label contradiction. This applies the existing nonzero hypothesis in the required direction.

### Use of existing descent equality

Location: exists_unramified_descent_iff.

Rewrites by the already-assumed hσ when constructing hker, then supplies hker directly.

Moves the same equality to the point at which its representation type is required. No new descent existence or kernel assumption is supplied.

### Constructed local instances

Location: Two declarations before the unramified tower endpoint theorems.

Installs UnramifiedFieldTower.residueTowerAlgebra K s t and residueTowerFinite K s t as local instances.

Uses the retained constructions on the same field tower. These are constructed data, not arbitrary new algebra or finite-dimensionality assumptions. The analogous instances in ActualUnramifiedBaseChange were local and not exported.

## Mathematical scope

The actual representation is degree induction of the full inducing character on the degree-n subgroup of the literal residue-Frobenius pullback.

The original standing hypotheses are retained. In particular, the cyclic inertia range equals the degree kernel where actual inertia is identified; the geometric-Frobenius relation, character restriction, degree-one element, tame action hypothesis, and field-tower data remain explicit. The added `include` directives expose already-declared data in exported theorem binders; the new local instances use existing constructions. No arbitrary new arithmetic premise is introduced.

The conductor, invariant-space/Frobenius, zero-label descent, and actual field-tower conclusions remain within the declared tame monomial class. There is no new general realization, H5 or Conjecture 66 result.

## Execution boundary

{
  "role": "runtime-owned bounded diagnostic, separately reported",
  "status": "FAIL",
  "receipt_path": "paperxi_lean/evidence/terminal_repair/attempt_01_compatibility/DIAGNOSTIC_RESULT.json",
  "receipt_sha256_at_review": "387d25e71cf99b36420578470ff73b192a9a5976a4ace173af2cb1350dbb8bfc",
  "source_sha256": "adf71a00e7445d6ad369b52ff55d2becb7ab6327509e1b1b8ebcaebd855392c7",
  "exit_code": 1,
  "log_path": "evidence/terminal_repair/attempt_01_compatibility/DIAGNOSTIC.log",
  "log_sha256": "b58f6272863df725da0cb59862651bce303790be11b3841262448e78669a5c3e",
  "observed_failure": "packetArtin_eq_coordinates rewrite did not match the folded packetSwan after unfolding, with a semireducible subgroup-instance mismatch; maxErrors=1 then stopped further diagnosis. Candidate02 addresses this proof-presentation issue."
}

Successful final elaboration and the release axiom audit must be established by separately retained execution receipts against the final source hash. This review has not performed those gates.

## Provenance and open findings

Read-only collaborator-agent inspection of the recovered original, exact candidate diff, and relevant retained dependency definitions/theorem statements; this is not external peer review. Dependency hashes are listed in the paired JSON. No open actionable finding in mathematical meaning or hypotheses was identified in this delta. Further diagnostic or compiler issues remain with the runtime owner.
