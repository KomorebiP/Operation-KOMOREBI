# Proof boundary

## Kernel-checked in this archive

The active root imports all eight mathematical modules. Audit.lean prints axiom dependencies for all 65 named theorem declarations. See THEOREM_INDEX.md for the list.

The v0.2.0 mathematical source files ResidualReflection.lean, KappaResidualReflection.lean, and LogicalCompactness.lean are unchanged. Their copies are retained under predecessor_sources. Earlier audit output is historical and is not substituted for a current run.

The integer-tower proof applies to actual integer-valued sequences of arbitrary infinite length. The finite-prefix and finite-subset statements are universally quantified Lean theorems, not finite Python evidence.

The uniform multiplier classification applies to all natural m >= 2 and all integer c. The three small parameter controls do not supply its proof.

The ultrafilter bridge is conditional on an explicit fine kappa-complete ultrafilter. Completeness is Mathlib's CardinalInterFilter, not an assumption named after the desired conclusion. Scope locality and cardinal bounds remain explicit hypotheses.

## Not kernel-checked here

* Identification of the explicit cokernel with Mathlib's right-derived inverse-limit functor.
* A full syntax and semantics for L_{kappa,kappa}.
* Equivalence of the ultrafilter existence schema with an independently formalized strongly compact cardinal definition.
* New consistency strength, independence from ZFC, or relative consistency.
* Object-language coding of the candidate theory and a satisfaction theorem inside a set-theoretic model.
* A general classification of all admissible residual systems or all finite subdiagrams in arbitrary categories.

## Interpretation restrictions

The supportedSystem cardinal threshold applies only to its documented prefix-or-whole family of pieces. No large-cardinal strength is inferred from that single example. Finite-prefix invisibility is not the absence of a finite proof or a finite symbolic description of the global obstruction.

The degreePacked theorem preserves the old predicates by relabeling them. It proves neither an effective compiler nor a support-preserving translation into a fixed logical language.

A source scan is supplementary. The stronger checks are fresh elaboration and the axiom dependency audit. The trusted boundary still includes the Lean kernel, standard foundational axioms actually reported, the pinned Mathlib dependency, and the execution environment.
