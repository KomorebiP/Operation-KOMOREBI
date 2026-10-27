# WR15 target contract

Base: `KS-v1.11.0-WR08-WR09-WR16-complete`, bound by `BASE_CHECKPOINT.json`. The recovered predecessor is immutable. This is an additive Lean continuation. WR10–WR12 and publication synchronization remain outside this block.

The frozen printed target is WR15 in `targets/05k_stopping_rules.tex`. Work over real finite-dimensional Hilbert spaces with their actual inner products. The columns of B form an arbitrary basis of the entire permitted correction space H = ker p. Ambient matrix coordinates are orthonormal, but B need not be orthonormal. For a proposed correction a = Bc, S = dB, G = BᵀB, and real parameter α, define the coordinate equation residual q = (SᵀS + αG)c − Sᵀr.

## Required conclusions

1. Derive invertibility of G from the full-basis hypothesis, including the empty basis. Connect B and its coordinates to the actual correction Hilbert space.
2. Identify the restricted Hilbert normal residual g = T*(Ta − r) + αa, where T = d restricted to H, with B G⁻¹ q. A premise assuming this identity does not prove the target.
3. Prove ‖g‖² = qᵀG⁻¹q in the actual Hilbert norm.
4. For every invertible C, with B′ = BC and the same correction, derive c′ = C⁻¹c, S′ = SC, G′ = CᵀGC and q′ = Cᵀq from the coordinate definitions.
5. Prove (q′)ᵀ(G′)⁻¹q′ = qᵀG⁻¹q. An abstract adjoint theorem is supporting evidence only until its finite matrix interpretation and protected-space identification are supplied.

No reduction to a selected rescaling, orthonormal basis, positive-dimensional space, proper subspace of the kernel, or an assumed invertible Gram matrix can replace the complete target. Useful intermediate results are retained and labeled partial until all named obligations pass.

## Evidence required for promotion

Strict Lean compilation, no placeholders or extra axioms, full exported new declaration types, preserved inherited declaration identities, fresh cumulative project replay, intended positive and rejection controls, independent mathematical statement review, separately checked terminal evidence, and package integrity verification. External dependency caches and Lean's compiler/kernel remain trusted and that boundary must remain explicit.

## Ownership and routes

- `wr15_coordinates`: Gram metric, normal-residual identification and norm formula; `CoordinateCovector.lean` and its numbered attempts.
- `wr15_basis_change`: arbitrary finite matrix basis transport; `CoordinateBasisChange.lean` and its numbered attempts.
- `wr15_math_audit`: raw-target derivation followed by independent source and compiler-type review.
- `wr15_runtime`: recover pinned toolchain and dependency cache with provenance.
- `wr15_verifier`: additive source assembly, cumulative replay, full axiom/type export and terminal validation infrastructure.
- Coordinator: target and state journal, controls, reconciliation, release and saved-file checks.

Structural route: use a basis isomorphism to identify the Riesz representative and its Gram matrix. Matrix route: derive transport from arbitrary two-sided inverse equations and specialize to genuine invertibility. Adverse controls: wrong raw covector norm, omitted spanning/invertibility, and zero-dimensional handling. The routes support different clauses of the same theorem rather than independent substitutes for the complete target.

## Recovery observations

Workspace maintenance removed earlier scratch files. The saved v1.11 archive was recovered and its accepted archive digest, CRC, every payload digest and all 5,863 paths checked. An initial materialization request failed because it used a Library identifier in the file-identifier field. Listing the saved item resolved its exact identifiers; the corrected transfer succeeded. This was a retrieval error and did not affect accepted mathematical evidence.
