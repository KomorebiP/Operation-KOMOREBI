# Adversarial self-review

Primary verdict for the normalized M1 claims: **proved as written** in the custom
observational syntax, subject to the explicit signatures and transport premises.
This is self-review, not an independent actor/referee audit.

Dependency chain: inherited run/transport -> path-prefix semantics -> normalization
soundness -> atomic value-name separation -> fragment type equivalence. For
quantifiers: inherited transport -> term observation equality -> environment
lifting -> structural formula induction. For finite definition: true observable
term code + immediate-output preservation + successor-code preservation ->
invariant relation -> all-word equality -> formula for the code kernel.

| Obligation | Result |
|---|---|
| Operation word order and composition | Passed, both inherited theorem and noncommuting negative fixture. |
| Names/predicates separate actual values | Passed for the declared all-value-name syntax. General predicate families not assumed. |
| Equality on state terms | Out of fragment. Stronger preservation claim refuted by an actual fixed-point counterexample. |
| Quantifier witnesses in target | Surjectivity explicitly required. Removing it is refuted by an actual existential sentence. |
| Variable binding | Fin n indexed syntax and Fin.cases extension; environment-encoding equality proved. |
| Source of observational equivalence | Actual inherited all-word relation, not a bounded sample. |
| Finite-code exactness | All-word conclusion derived from local obligations, not supplied as a certificate field. |
| Unbounded domains | Generic Lean statements permit infinite states; stream theorem refutes uniform finite tests. |
| Nondefinability overstatement | Avoided: stream relation itself is definable by ordinary state equality in the larger language. |
| Canonical syntax claim | Only path-normal retraction claimed, not quotienting all Boolean/semantic equivalences. |
| Formal standard-logic translation | Not addressed in this block; explicitly next obligation. |
| Python identity/provenance | Exact-input manifests and separate implementation tests; not verified code extraction. |
| Historical novelty | Not addressed. Elementary semantic ingredients are not claimed new. |

No limiting, compactness, stability, saturation, forcing, or ultraproduct theorem
is used in this block. No full logical theory is asserted to have quantifier
elimination. The broad brainstorm remains a portfolio of proposed research,
not a theorem ledger.
