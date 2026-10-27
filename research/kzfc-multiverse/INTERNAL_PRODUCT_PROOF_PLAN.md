# Resolved arithmetic target in v0.10.0

The target below is now proved by a different, shorter internal route using the existing regular-cardinal guard. See BLOCK_10_REPORT.md, THEORY.md and InternalProductArithmetic.lean. The full cardinal-square/order-type machinery suggested below was not needed. The original outline is retained here as historical provenance, not a live gap.

---

# Internal cardinal-product proof plan

Status: mathematical proof outline and explicit formalization obligations, not a completed Lean derivation inside arbitrary encoded ZFC models.

The remaining target is products of internally small sets being internally small at a guarded cardinal. The ambient cardinal theorem is already formalized in Mathlib and used only in the concrete ZFSet discharge. Moving its conclusion into an arbitrary model requires internally coded witnesses and a proof using that model's axioms.

## Standard mathematical reduction

In ZFC, suppose there were a least infinite cardinal lambda with |lambda times lambda| greater than lambda. Well-order pairs (alpha,beta) lexicographically by (max(alpha,beta),alpha,beta). Every strict predecessor segment of a pair is contained in gamma times gamma for gamma=max(alpha,beta)+1<lambda. The cardinal of gamma is below lambda. Minimality of lambda (and elementary finite arithmetic when gamma is finite) therefore bounds each such segment strictly below lambda.

If the order type of the whole pair order were greater than lambda, its element at ordinal position lambda would have a predecessor segment of cardinality lambda, a contradiction. Hence the order type is at most lambda, so |lambda times lambda| is at most lambda. The diagonal embedding gives the reverse inequality. Thus every infinite cardinal is equipotent with its square.

For an uncountable cardinal kappa and cardinals mu,nu<kappa, put lambda=max(aleph0,mu,nu). Then lambda<kappa and mu times nu <= lambda times lambda=lambda<kappa. The finite threshold case is handled separately. Regularity is not required for this binary product bound.

## What must be encoded internally

The proof needs internal ordinal/cardinal representatives and comparison, a set-coded well-order of the product, its internal ordinal order type, the initial-segment cardinal comparison and the well-founded induction/minimal-counterexample step. The full function graphs witnessing the resulting injections must exist internally.

An external ordering of the elements of M is not an internal well-order witness. Likewise, external transfinite induction on the model's externally viewed ordinals is not justified for an arbitrary, potentially externally ill-founded model. All order constructions and the induction argument must be derived from the existing first-order ZFC schemas.

## Already checked consumers

No new cone-filter machinery is required after this arithmetic step. InternalSupportEquivalence.fine_iff_productClosed_of_extension and InternalConeFormula.model_zfc_extensionCompactness_of_arithmetic are compiled consumers with explicit types that expose exactly this remaining premise.

This outline does not claim novelty or that the target is mathematically open. It records the ordinary argument that remains to be internalized in this particular Lean development.
