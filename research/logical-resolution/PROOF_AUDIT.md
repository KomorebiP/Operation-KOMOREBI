# Mathematical self-audit

## Verdict: proved as written, within the contracts stated below

This is authoring-assistant self-review, not a separate referee or fresh-agent audit.

Dependency chain:

    preserved operational core -> state/value semantics -> relation-aware syntax
    -> exact atom contracts + binder square -> standard satisfaction
    -> standard quantified transport and finite-rank back-and-forth
    -> concrete standard QF/rank-one separation.

| Obligation | Status | Evidence |
|---|---|---|
| Source variables scoped at every binder | Passed | Fin-indexed syntax and translateAux |
| Bound-variable order reconciled | Passed | binder_assignment for arbitrary sigma/free/bound contexts |
| Noncommuting operation order | Passed | wordTerm_realize; independent mutation control |
| Literal/probe equality orientation | Passed | valueEquality_realize uses eq_comm where required |
| Actual standard semantics, not renamed custom evaluator | Passed | FirstOrder.Language.Structure, Term, BoundedFormula.Realize and Formula.Realize |
| Relation preservation AND reflection | Passed | iff premise; both directions used under negation |
| Witness lifting for quantifiers | Passed | explicit surjectivity; both back-and-forth directions |
| Fiber criterion sufficient and necessary | Passed | explicit existential target predicate and converse |
| Concrete quotient, not assumed isomorphic object | Passed | quotientRelation and standard_quotient_preservation |
| Standard quantifier rank and IsQF | Passed | rank equations and both zero/QF implications |
| Relational example is within one model | Passed | Fin3, edge(0,2), parameter-free language |
| QF counterexample covers full standard QF syntax | Passed | induction on IsQF including state equality |
| Empty carrier is not accidentally enlarged | Passed | target carrier exactly X, no state constants; finite empty controls |
| Generic full FO truth preservation | Out of scope | state equality excluded from translated fragment |
| Back-and-forth converse/completeness | Not established | soundness only |
| Strict quantifier hierarchy at every rank | Not established | rank0 versus rank1 example only |
| Verified Python program | Not established | separate exact finite audit |
| Historical novelty | Not assessed | classical techniques and upstream APIs attributed |

The counterexample is parameter-free. Adding named vertices can change QF
definability. The source language's value literals are not named STATE constants.
This distinction is checked in the interpretation and documentation.

The previous observation-only within-model rank collapse remains valid. The new
example does not contradict it: the added binary relation is not constant on the
old behavioral fibers and thus is not an admissible atom of that earlier profile.
