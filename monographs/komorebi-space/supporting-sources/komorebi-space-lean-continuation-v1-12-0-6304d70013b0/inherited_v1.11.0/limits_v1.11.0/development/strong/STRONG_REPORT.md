# WR08 attained-case strong limit implementation

Status: the complete attained-case target compiles under Lean 4.34.0-rc2 with `-j1 -DwarningAsError=true -DautoImplicit=false`. Seven explicit theorem statements were added. This is a development result; independent statement review and full-project replay remain root-owned acceptance gates.

## Exact scope

For arbitrary real Hilbert spaces H and Y, a continuous linear map T, and datum r, let b be the orthogonal projection of r onto the closure of the actual range of T. If b belongs to the actual range, `exists_unique_minimum_and_limit` constructs the unique minimum norm preimage and proves that the actual regularized correction path converges to it as all positive real parameters tend to zero. The path uses the accepted regularized correction at every positive parameter. No closed range, finite dimension, separability, injectivity, or positivity of the residual floor is assumed. The conclusion uses the full right-hand neighborhood filter and norm topology.

## Proof route

1. Apply the accepted closed convex minimum theorem to the nonempty closed convex fiber T⁻¹({b}); reuse its uniqueness theorem.
2. Prove a generic filter norm limit. If the norms of approximate preimages are frequently at most c below the minimum norm, the accepted frequently bounded WR01 theorem supplies an exact preimage with norm at most c, a contradiction. The regularized energy identity supplies the matching eventual upper bound.
3. Cancel the orthogonal residual floor in the accepted exact regularized energy identity. This yields `‖a_α−a†‖² ≤ ‖a†‖²−‖a_α‖²`. The right-hand side tends to zero, giving norm convergence.
4. Combine construction, uniqueness, and the full positive-parameter limit in one existential uniqueness theorem.

This route avoids selecting subsequences or introducing a new weak convergence API. It is mathematically equivalent to the printed attained-case conclusion; it uses a different proof organization.

## Immutable attempts

- `strong_001`: the mathematical proofs elaborated, but strict warning handling rejected an unused codomain completeness section variable in the fiber existence theorem. Fixed by locally omitting that assumption.
- `strong_002`: rejected because `omit` followed a declaration doc comment, and the generic norm-energy convergence proof needed an explicit constant function type. Moved `omit` before the doc comment and supplied the type. No theorem was weakened.
- `strong_003`: the complete seven-theorem module compiled successfully with the full path and constructed-minimum conclusion.
- `audit_001`: explicit type checks and axiom closures for all seven theorems compiled successfully. Every reported axiom closure is contained in `propext`, `Classical.choice`, and `Quot.sound`.

Every attempt has an immutable source snapshot, exact compiler command, dependency object hashes, selected environment, complete compiler output, exit code, and timestamp. Successful receipts include output object hashes. The development build contains symlinks to accepted dependency objects and a copied new basic-limit module; accepted artifacts were never modified.

## Self-review under proofread-math

Proofread scope: the changed module only, against the accepted theorem APIs and printed WR08 attained-case statement.

- Routine edits: doc comment and local `omit` placement during strict elaboration.
- Mathematical-token changes: none made as proofreading corrections. The new mathematical statements and proofs belong to this authorized formalization task.
- Unresolved issues: none in the local statement/prose correspondence.
- Validation: strict module compile and explicit type/axiom audit passed.
- Coverage limit: this self-review does not replace independent audit or the clean integrated replay.
