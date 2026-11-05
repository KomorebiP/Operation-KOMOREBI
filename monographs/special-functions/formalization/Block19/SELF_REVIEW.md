# SF-LEAN-B19 focused self-review

Primary verdict for the pinned Python source: **conditional on the named
parser, closed-fragment binder/template and primitive semantics** below.
The operational-model equivalence and enclosure theorems themselves are
proved as written in Lean; final execution evidence is in `evidence/receipt.json`.
Review provenance is author self-review, not an independent review.

## Exact normalized claim

For every rational scale tuple `p`, rational `x`, optional natural last index,
optional rational outer radius, and modeled outcome `out`,
`EvaluationRun p x last outer out` holds if and only if `out` is the exact
dictionary encoding, or modeled error, of `certifiedEvaluationSpec`.
Execution exists and is deterministic for every such input. Every normal
return has exactly the seven specified keys and uniquely represents a typed
result enclosing both canonical functions and bounding the complex disk error.

The raw front end is quantified over arbitrary input type `α`, conversion
failure type `ε`, and a conversion primitive `α -> Except ε ℚ`. It distinguishes
exact integer index tags from booleans and other types, performs conversions
and validations in source order, and propagates conversion failures. Every
successful raw execution has both real and complex enclosure theorems at its
converted rational point. This does not certify a user object's intended
mathematical meaning independently of the Fraction conversion contract.

## Dependency graph and trust leaves

Pinned source bytes -> Python AST parser and closed-fragment binder/template
-> generated `CoupledPythonSource.lean` -> `CoupledPythonRefinement.lean`
-> Block18 typed specification -> Block15-17 analytic/normalization/majorant
theorems -> canonical actual functions.

The first arrow is a trusted, source-checked translation boundary, not a
verified-compiler theorem. Every selected function's non-docstring syntax is
checked against the complete masked AST; every arithmetic/default/dictionary
hole is translated. Changes outside the selected functions are still caught
by the pinned whole-file hashes. The selected call closure comprises `_index`,
`scales`, `coupled_odd_derivatives`, `ordinary_taylor_coefficients`,
`disk_majorant`, and `certified_evaluation`.

Other trusted leaves are standard sequential Python/container semantics,
exact integer and Fraction operations/conversions, idempotent reconstruction
of an already normalized Fraction, exact `comb`/`factorial`/binary widths,
the type-tag projection, and absence of concurrent mutation or monkeypatching.
The binder, template, AST parser, CPython and stdlib internals are not proved
correct in Lean. They are not smuggled into the Lean axiom audit as proved facts.

## Obligation matrix

| Obligation | Assessment |
| --- | --- |
| Distinct old arrays and materialized products | Passed for the model: `products` is computed from the old pair before appends; each row uses the same terms with its own scales. The AST pattern excludes replacement by a shared lazy iterator. |
| Inclusive loop/index coverage | Passed: Python range 1 through N corresponds to a fold over N indices shifted by one; source-derived coefficient terms agree at every index. |
| Safe subscripts and integer subtraction | Passed: `source_array_bounds` and `source_integer_index_safe` justify the total-list representation on every reachable array access and exclude negative Python indices. |
| Ordinary normalization | Passed: generated factorial division and enumerated partial sum agree with the proved ordinary arrays and `arrayPolynomial`. Odd factorials are nonzero. |
| While-loop state and step cap | Passed: the accumulator appends in original order, the length guard precedes append, and the remaining-budget invariant proves agreement with `buildLadder`. |
| Reverse fold and bit guards | Passed: the actual reverse iteration and post-update checks agree with `guardedFold`. The unchecked seed behavior is retained. |
| Division safety | Passed on reachable analytic inputs: the ladder terminal lies strictly between 0 and 1; its seed denominator is positive. Successful evaluation has S>x>=0, so S is nonzero. |
| Empty/zero boundaries | Passed: N=0 retains one coefficient; small-radius loops may be empty; zero radius precedes resource checks in the majorant; x=0 in evaluation defaults to S=1. |
| Dictionary keys, values and recovery | Passed: exact encoding has seven keys; component order, endpoint additions and metadata are preserved; the encoding is injective. |
| Failure propagation | Passed for modeled validation, conversion and resource outcomes; no error yields a dictionary. Exact Python validation-exception object identity is outside the theorem. |
| Bool/int distinction and conversion order | Passed for explicit type tags and the parameterized conversion front end; faithful projection of actual Python types remains a named primitive assumption. |
| Non-vacuity | Passed: operational execution is total and deterministic in the mathematical model; the equivalence theorem is bidirectional. |
| Actual-source link | Conditional: complete source shape/byte binding is executed, with 24 adversarial controls; the binder/template interpretation is trusted and self-reviewed, not a verified Python compiler. |
| Machine resources | Outside the totality theorem: unexpected allocation failure, interruption and hostile object side effects are not successful mathematical primitive steps. Model totality is not a wall-clock/memory guarantee. |
| Proof leaves | Internal Lean proofs and inherited foundations; no new external theorem or numerical approximation is a proof leaf. |

## Adversarial interpretation

Mutation checks deliberately bypass the whole-file hash so they test structural
and arithmetic discrimination. They reject altered loop endpoints, binomials,
subscripts, exponents, normalization, scale rows, seed/update signs, fold order,
step/bit guards, defaults, dictionary keys/values, index guards and lazy shared
products. These are finite binder tests, not a proof of compiler correctness.
The five Lean rejection controls separately challenge missing execution,
boolean acceptance, a six-field result, forward folding and placeholder proofs.

No source/spec equality is assumed to prove itself. Array, ladder and fold
invariants are proved independently from their operational definitions before
the top-level refinement theorem is used. Historical finite calculator tests
remain inherited evidence for unchanged source hashes; they are not substituted
for the universal Lean statements.

The strongest safe conclusion is a source-bound, universal operational-model
refinement and an actual-Python soundness claim conditional on the explicit
translation/primitive trust boundary. An unconditional claim that CPython or
the binder has itself been verified would be unsupported. Removing that
boundary requires a separate compiler/interpreter or library-verification
project; it is not inferred from the present theorem count or passing controls.
