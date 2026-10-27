# Komorebi KZFC Residual Reflection v0.5.0

## Main result

An actual Mathlib first-order formula `extensionFormula`, in a language whose only nonlogical symbol is membership, now represents complete filter extension. At the initial-ordinal set code of any cardinal kappa, Lean proves its interpretation equivalent to the independently defined `CompleteFilterExtension kappa`. For regular kappa, it is also equivalent to the predecessor's `FixedDomainKRR kappa`.

    ZFSet satisfies Phi(initialOrdinal(kappa))
      <-> CompleteFilterExtension(kappa)
      <-> FixedDomainKRR(kappa)                 [last equivalence: regular kappa]

The symbols for filter, ultrafilter, function, injection and smallness are formula-building macros, not additional relation symbols or axioms. The syntax tree expands to membership, logical equality, Boolean connectives and first-order quantifiers. It is a one-free-parameter formula, not yet a closed regular-uncountable existence sentence.

## What changed

Five new mathematical modules provide exact set coding of subsets and families, relative intersections, proper filters, ultrafilters, extensions, cardinal-small families through set-coded injections, and a complete interpretation of the membership-language formula. Every small Lean type is equivalent to the carrier of a genuine ZFSet, so the all-set interpretation is not restricted to a convenient subcollection of carriers.

A regression theorem handles the empty-family convention. Intersections for a filter on X must be relative to X and send the empty family to X. Unbounded `ZFSet.sInter` sends the empty family to the empty set. Replacing the relative operation by that unbounded operation would make positive-cardinal completeness impossible for any proper set filter. This failure is formally proved, not merely documented.

The formula inherits the aleph0 baseline and the uniform failure at every infinite successor cardinal.

## Verification

Final status: PASS. A clean serial topological build, root build, separate source checks with warnings as errors, and all 173 named theorem axiom audits completed successfully. This block adds 76 declarations, including supporting lemmas and interpretation interfaces, not 76 independent discoveries. All 97 predecessor declarations and all 12 predecessor mathematical modules are preserved. The only observed axiom dependencies are `Classical.choice`, `Quot.sound`, and `propext`. No custom axiom or proof placeholder occurs in active source. False-proof and placeholder controls were rejected for the expected reasons.

The actual verifier exit was zero. Proof-input hashes were identical before and after execution. See `verification/RESULTS.json`, `verification/process_record.json`, and `verification/computation_manifest.json`.

A parallel clean-verification attempt timed out in the enclosing tool before producing a final verdict. Its partial logs remain under `verification/interrupted_parallel_clean`. The complete serial run supersedes that attempt. This scheduling repair did not change mathematical assumptions.

## Foundational boundary

This release proves semantic adequacy in the concrete ZFSet universe constructed in Lean's ambient type theory. It does not yet provide a first-order derivation from ZFC, an interpretation theorem for every arbitrary model of ZFC, or the closed sentence encoding the regular-uncountable existence guard. No uncountable compactness cardinal is proved to exist. No independence, relative-consistency, or new consistency-strength theorem is claimed.

The predecessor classification is a residual presentation of a known filter-extension form of strong compactness under its all-sets, regular-uncountable interpretation. The syntax and coding work does not create a new stronger axiom. The explicit integer cokernel remains separate from Mathlib's right-derived-functor implementation.

## Contents and reproduction

The new modules are `SetFilterCoding`, `SetCodingBridge`, `SetCardinalCoding`, `MembershipFormula`, and `FilterExtensionFormula`. Together with the 12 preserved modules they form the 17 mathematical modules under `Komorebi/Foundation`; `Audit.lean` is the audit driver. `THEORY.md`, `PROOF_BOUNDARY.md`, and `THEOREM_INDEX.md` give the exact statements and boundaries.

Run `python3 scripts/run_recorded.py --clean --sequential-build` in the pinned environment. See `REPRODUCE.md` for setup and evidence regeneration. The distribution excludes the compiler, dependency cache, build outputs and runtime archives. It includes project sources, pinned dependency manifests, predecessor provenance, final verification, and retained development failures.

Pinned environment: Lean 4.34.0-rc2, Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
