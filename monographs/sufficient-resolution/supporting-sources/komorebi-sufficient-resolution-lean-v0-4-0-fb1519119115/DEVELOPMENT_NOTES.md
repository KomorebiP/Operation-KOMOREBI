# Development and failure record — v0.3.0

## Restored baseline

The v0.2.0 archive passed CRC validation. No Lean installation was initially mounted.
The five preserved compact runtime parts were recovered from the user's Library.
A first extraction attempt failed because the destination directory had not been
created; after creating it, the multipart xz/tar restoration completed with exit 0.
The baseline source was then rebuilt and kernel-replayed: 125 theorems, 169 named
declarations, all 11 modules passed. No predecessor production proof source changed.

## Lean draft failures and corrections

The raw attempts are retained in verification/development_v0.3.0/.

- `FiniteHorizon_01`: `Mathlib.Tactic.Omega` is not a module at the pinned revision.
  Replaced it with the actual targeted import required for negation manipulation;
  `omega` itself was already available through the imported dependency closure.
- `FiniteHorizon_02`: outdated list-length theorem name, a dependent simplification
  that did not rewrite the submodule as intended, and deprecated `push_neg` syntax.
  Corrected the exact API name, used an explicit rewrite, and switched to `push Not`.
  The third attempt passed with warnings as errors.
- `BehavioralMinimality_01`: incorrect quotient-zero API, an inverse-equivalence
  simplification that needed an explicit inverse law, and proof-only hypotheses
  omitted from Lean's automatically inferred statement parameters. Corrected these,
  including explicitly including the required intertwining/readout hypotheses.
- `BehavioralMinimality_02`: a documentation comment was positioned before an
  `include` directive, and a finite-dimensional assumption was unnecessarily in
  scope for an algebraic equivalence. Moved the directive/comment and placed the
  dimension-free equivalence before the finite-dimensional section. The next
  attempt passed. No unused-assumption linter was disabled.
- `FiniteObservableModel_01`: an unused simp argument and a redundant automatically
  included finite-dimensional assumption. Removed/omitted them. The next run passed.
- `FiniteCertificate_01`: rewriting a composed-map evaluation did not match its
  function-application form. An explicitly typed pointwise equality fixed it.
- `ObservableExamples_01`: generic extensionality selected a product-linear-map
  rule rather than the intended pointwise rule, and the product equality lemma
  was applied with the wrong syntactic form. Used explicit `LinearMap.ext` and
  the product equality simplifier. The next run passed.

All five new production modules subsequently passed cumulative source compilation
and same-kernel replay. No production placeholder, extra axiom, unchecked evaluation
shortcut, or suppressed error was introduced to close a proof.

## Computation boundary

The exact-rational minimizer's first complete test run passed all 30 systems,
1,657 exact assertions and 10 negative controls. The Python source is not formally
verified. Its algebraic certificate specification is Lean-proved, and the shipped
noncommuting example is instantiated in Lean. Arbitrary JSON inputs do not thereby
receive an automatic Lean certificate.

## Preservation

Historical evidence is copied under explicitly inherited/history paths. Current
verification/release evidence comes from the present run. Round-trip checking
rebuilds extracted source and compares the complete execution-input hashes, rather
than merely checking a ZIP or reusing its compiled outputs.


## v0.4.0 corrections and execution notes

The first analytic draft used deprecated `ContinuousLinearMap.sub_apply` and
`add_apply` names. Warnings-as-errors rejected them. They were replaced by the
current general application lemmas; no warning checker was disabled.

An initial scalar geometric-identity proof asked `nlinarith` to multiply an
induction identity by a symbolic variable automatically. That failed. It was
replaced by an explicit ring rearrangement followed by the induction rewrite.

One monotonicity proof used the wrong-sided `add_le_add_left`; an explicit
`add_le_add le_rfl` solved the intended unchanged inequality. Scalar-map `ext x`
triggered an unused-pattern warning because a stronger scalar extensionality
lemma fired automatically. Explicit continuous-linear-map extensionality restored
the intended variable-wise proof.

The container rejected an interactive extraction session. Extraction was then
performed by a logged tar process and exited successfully. These were environment
and elaboration/tactic issues, not mathematical counterexamples. All failed draft
logs and corrected runs are retained in verification/development_v0.4.0.

The mathematical counterexample is deliberate: arbitrarily small positive
one-step error does not give a uniform all-time guarantee absent growth control.
It is kept in the production proof library, not treated as an implementation bug.
