# Block 26 restriction and coverage boundary

Production source: `lean/PaperX/SurjectivePullbackBoundary.lean`.

SHA256: `5e2d75f797f3f9a56c3380966bd7e02fd36ab2e84c1d34752cb991dc06461078`.

The first example uses actual one-dimensional rational representations of the
group `C2 = Multiplicative (ZMod 2)`. The sign action has generator value `-1`;
the trivial action has generator value `1`. Both are proved irreducible. An
equivariant equivalence would imply equality of their actual traces, giving
`-1 = 1` at the generator. Thus no such equivalence exists.

The homomorphism `collapsedMap : C2 →* C2` is constant at the identity and is
proved non-surjective. Restricting the two representations along this map makes
them equal. This equality constructs an actual `Representation.Equiv`. The
counterexample therefore concerns the representation equivalence relation, not
mere inequality of chosen matrices or additional system labels.

The second example takes `quotientSamples g = (g, 1)` in `C2 × C2`. Its projection
onto the first factor is surjective and satisfies the project's actual
`QuotientCoverage` predicate. The lifted family and all its conjugates miss
`(1, generator)`, so it is not conjugacy-dense and does not satisfy
`QuotientCoverage` in the product. Coverage in one quotient cannot establish
coverage in every larger quotient. This is a finite group counterexample, not
an assertion about the arithmetic samples constructed elsewhere in Block 26.

The module has 9 theorem declarations, 4 definitions, and 2 irreducibility
instances. It introduces no axiom, placeholder proof, or native decision.

Checks run with the pinned Lean 4.34.0-rc2 kit and `warningAsError=true`:

- Production compile: passed (`pullback_boundary_attempt2.log`, empty output).
- Positive control: passed (`pullback_boundary_positive.log`, empty output).
- False unrestricted-descent control: rejected at the intended goal `False`
  (`pullback_boundary_negative.log`).

The first compile failed from an incorrect Mathlib units API name, the tactic
presentation of the irreducibility class, and a field-notation ambiguity after
composition. These were repaired directly; `pullback_boundary_attempt1.log`
retains the failed compiler output. No predecessor source was modified.

The root release workflow owns the transitive axiom audit and fresh archive
replay. The results above are individual compiler checks, not claims that those
later release gates have already run.
