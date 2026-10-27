# WR01 bounded approximate realization continuation

The production source is `../../formal/KomorebiSpace/BoundedApproximateRealization.lean`.
Its five public declarations prove the full printed WR01 claim, including an exact
solution with the original norm budget, the bounded-sequence equivalence, and the
adjacent escape-to-infinity corollary.

The first theorem is slightly more general: for any nontrivial filter, a frequently
recurring uniform candidate bound together with convergence of the operator images
suffices to produce an exact solution within that bound. This gives the escape
corollary directly, without separately constructing a bounded subsequence.

The proof uses mathlib's Banach–Alaoglu compactness theorem for the weak-star dual
ball, the Riesz linear isometric equivalence, and evaluation against the adjoint.
No separability or closed-range hypothesis occurs. The production source introduces
no custom axiom and contains no `sorry`. All five declarations' reported axioms are
`propext`, `Classical.choice`, and `Quot.sound`.

This verifies the WR01 theorem by an alternative proof route. It does not add a
standalone formal declaration for the separately printed background lemma asserting
a weakly convergent subsequence of every bounded Hilbert sequence.

## Checks

`verification.json` binds the successful standalone check and axiom printout to the
source hash. `run_controls.py` compiles the source from scratch into a local control
build and checks one positive fixture with three scalar examples and two negative
fixtures. The positive cases are the zero operator with zero budget, the identity
operator saturating a nonzero budget, and the bounded-sequence equivalence for a
nonzero datum. The negatives reject (1) dropping the candidate bound while retaining
an arbitrary smaller solution budget and (2) shrinking the legitimate norm-two
solution budget to one. Both fail solely at the false real arithmetic obligation.
These scalar controls exercise preservation of the precise norm budget. They do
not independently instantiate an infinite-dimensional nonclosed-range counterexample.

## Recorded failed attempts

- `compile_01.log`: the first source check failed because a line break separated a
  parenthesized compactness proof from its dotted method. Corrected syntax yielded
  the clean `compile_02.log`.
- `controls_run01/`: the first control replay compiled production but its positive
  fixture failed the `unnecessarySimpa` linter under warnings-as-errors. The negative
  fixtures reached the intended false budget obligations but also emitted that
  incidental linter diagnostic. Replacing those fixture proofs with `simp` produced
  the accepted final run in `controls_verification.json`.

The library's frozen historical sources were not changed.
