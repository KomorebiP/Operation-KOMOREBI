# Proof boundary v0.6.0

## Completed in Lean

All 17 predecessor mathematical modules and 173 theorem declarations are preserved. Three new modules add 37 named declarations, for 210 in total.

The new checked content is: the independent set-level regular-uncountable initial-cardinal guard; the characterization of every guarded set witness as an initial ordinal; the exact small-subset boundedness equivalence with regularity; actual membership-only guard formulas; the closed sentence Theta; its ZFSet realization equivalence with both independently defined existence assertions; the true unguarded baseline and guarded witness exclusions; and the generic base-theory insertion interface.

The guard itself is proved satisfiable at infinite successors. Its satisfaction does not imply the filter-extension property, which is separately refuted at those successors.

## Not proved or assumed

* No regular uncountable compactness cardinal is asserted to exist.
* No custom Lean axiom is introduced.
* No derivation of the classification from a coded first-order ZFC axiom theory, nor its internally interpreted analogue in every arbitrary ZFC model, is supplied.
* No external/internal cardinal or completeness absoluteness is assumed.
* No independence, relative consistency, new large-cardinal strength or first-formalization claim is made.
* No classification of arbitrary higher-derived systems or identification with Mathlib derived functors is added.

## Arbitrary-model logical interface versus set-theoretic interpretation

`model_extension_iff` is valid for every membership structure but is just the model rule for inserting one sentence into a theory. `guardedSentence_of_elementarilyEquivalent` transports a sentence across an explicitly given elementary equivalence. Neither theorem supplies the missing arbitrary-model set-theoretic classification.

The guard and sentence interpretation theorems use the concrete ZFSet structure in Lean's ambient type theory. These are not automatically proofs from ZFC.

## Trust and evidence

The kernel axiom audit covers all 210 named theorem declarations in the project's explicit namespace format. Supporting and interface lemmas count toward this total. The expected dependencies are Classical.choice, Quot.sound and propext. The active verdict, the 47 recorded compiler-command exits, and the final staged-session completion status must all be read before claiming verification. This was not one uninterrupted subprocess.

The clean build removes project build products, not the pinned Mathlib dependency cache. Compiler/kernel binaries, dependency source and cache, and the surrounding platform remain trusted. Hashes establish provenance and record integrity, not an independent proof of Lean soundness. Historical incomplete attempts are retained but are not active PASS evidence.
