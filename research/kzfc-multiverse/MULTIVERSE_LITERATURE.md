# Literature alignment for the multiverse-residual block

Checked 2026-09-26 against primary arXiv versions.

## Generic multiverse and amalgamation

Miha E. Habic, Joel David Hamkins, Lukas Daniel Klausner, Jonathan Verner, Kameryn J. Williams,
"Set-Theoretic Blockchains", arXiv:1808.01509.

Relevant exact points:

* Definition 1.1: the generic multiverse of a countable transitive M models ZFC is the smallest
  collection containing M and closed under forcing extensions and grounds.
* Definition 1.3: a family of forcing extensions is amalgamable when one forcing extension
  contains every member; finite amalgamability agrees with existence of an upper bound in the
  generic multiverse.
* Theorem 2.1 (Mostowski): for a finite index set, every subset-closed family containing all
  singletons is realizable by Cohen reals so that a subfamily is amalgamable exactly when its
  index set belongs to that family.
* The discussion after Theorem 2.1 states that finite posets embed while preserving
  nonexistence of upper bounds.

Translation to this project: `FiniteFaceComplex.Face` is the abstract allowed-family predicate,
and `WorldNetwork.JointAmalgamable` is the upper-bound predicate.  The Lean project does not yet
formalize the forcing construction, so this is an externally verified realization theorem, not a
kernel dependency.

## Nonamalgamable forcing extensions

Joel David Hamkins, "Upward closure and amalgamation in the generic multiverse of a countable
model of set theory", arXiv:1511.01074.

The paper proves, among other results, that every countable transitive model W has Cohen-real
extensions W[c] and W[d] that cannot be amalgamated into a further same-height ZFC extension.
This supports the interpretation of missing edges/faces as genuine generic-multiverse phenomena.

## Downward geometry

Toshimichi Usuba, "The downward directed grounds hypothesis and very large cardinals",
arXiv:1707.05132v2.

The abstract states that the grounds of V are downward set-directed.  This motivates separating
the upward amalgamation nerve from the dual/common-ground geometry rather than assuming the two
directions behave symmetrically.

## Novelty boundary

No claim is made here that the phrases "amalgamation nerve", "world residual", or the proposed
cohomological packaging are absent from all prior literature.  The checked sources establish the
underlying multiverse/amalgamation patterns.  A dedicated novelty search would be required before
claiming a new invariant or a new set-theoretic axiom.
