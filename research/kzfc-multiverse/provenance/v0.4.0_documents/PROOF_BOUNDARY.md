# Proof boundary v0.4.0

## Kernel-checked in the current pinned environment

* The complete equivalence cycle in THEORY.md for the explicitly defined class and regular infinite kappa.
* Construction of a genuine complete ultrafilter from Boolean constraint compactness.
* Construction, properness and completeness of the fine cone filter.
* Ordinary baseline at aleph0.
* Uniform distinct-value counterexample at each successor of an infinite cardinal.
* Equivalence of the two candidate uncountable existence assertions, not either assertion itself.
* Every predecessor theorem, with all eight predecessor mathematical modules unchanged.

## Interpretation supported externally, not a substituted formal proof

The all-sets filter-extension/fine-ultrafilter formulations at a regular uncountable cardinal are standard strong-compactness formulations. LITERATURE.md identifies the exact primary source and the notation translation. The theorem proofs in this project construct the relevant objects directly, rather than importing the paper's conclusions as Lean axioms.

## Not established

1. Existence of any regular uncountable cardinal satisfying the classified principles.
2. An object-language encoding and derivation in ZFC, or a model/consistency/independence theorem.
3. A new cardinal notion or new consistency strength, or priority as the first formalization.
4. Classification of all derived residual systems, finite-rank systems, or bounded algebraic fragments.
5. A Mathlib derived-functor comparison for the explicit integer cokernel.
6. Full infinitary logical syntax/semantics or local lambda-bounded versions of strong compactness.
7. Any polynomial-time, finite-certificate-size or computational-efficiency guarantee.

## Trusted base and audit limits

Lean 4.34.0-rc2 and the pinned Mathlib dependencies are the trusted proof environment. All 97 project theorem declarations were re-elaborated/audited. The observed axiom dependencies are only propext, Classical.choice, and Quot.sound. No custom axioms or placeholders occur in active project sources. This is not a reimplementation of the Lean kernel or an audit of the entire compiler supply chain.

The distributed dependency cache is external. The release records exact revisions and restoration hashes, but does not rebuild Lean or all Mathlib from source. The source inventory parser is deliberately scoped to this project's explicit namespace-only declaration style. Its inventory is checked against the exact set and number of kernel axiom-print outputs.

The execution checks prove only what the Lean statements say. The mathematical interpretation and scope require the statement audit documented in THEORY.md.
