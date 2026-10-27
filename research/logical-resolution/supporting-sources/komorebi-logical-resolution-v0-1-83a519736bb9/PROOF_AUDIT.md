# Mathematical self-review

Primary verdict: **proved as written**, for the explicit observational fragment
and exact hypotheses in the accepted Lean statements. This is an authoring-assistant
self-review of semantics, not independent external refereeing.

| Obligation | Verdict | Reason |
|---|---|---|
| Actual preceding semantic object retained | Passed | Two inherited modules match parent bytes and are rebuilt |
| Well-scoped bound/free variables | Passed | `Formula n` / `ValueTerm n`, `Fin n` probes, binder adds one variable |
| Word order | Passed | Probes use actual `behavior`; same left-to-right `run` |
| Atomic separation of output values | Passed under stated hypothesis | Every V value is a fixed literal; inverse type implication chooses one |
| No hidden state equality | Passed | Syntax only compares VALUE terms; counterexamples document extension failure |
| Existential reflection | Passed with surjectivity | Every target witness explicitly lifted; failed embedding counterexample included |
| Arbitrary Boolean nesting | Passed | Induction proves both truth directions, enabling negation |
| Arbitrary quantifier rank | Passed within fragment | Structural induction, no rank cutoff in theorem |
| Horizon and type comparison | Passed | Operational word-depth is tracked independently of quantifier nesting |
| No unjustified quantifier elimination | Passed | Separate two-model theorem proves uniform elimination can fail |
| Finite defining formula | Passed with closure certificate | Exact tests plus output/action closure imply all-word equivalence |
| Infinite nondefinability | Passed within fragment | Actual infinite streams, no finite truncation surrogate |
| Completeness/elementarity claims | Restricted correctly | No unrestricted first-order-type or elementary embedding theorem |
| Verification independence | Limited | Kernel check, independent finite reference routes, but no independent researcher |

## Dependency structure

Inherited System/run/ObsEq/Transport
  -> well-scoped observation syntax
  -> term transport and assignment binding
  -> all-formula surjective preservation
  -> actual behavioral quotient preservation.

Inherited horizon and distinguishing-word theorem
  -> bounded word agreement
  -> formula-depth invariance
  -> exact type/horizon equivalence and atomic failure witnesses.

Formula-depth invariance + actual stream shift
  -> arbitrarily late witnesses
  -> no one finite formula defines full stream behavior.

Inherited invariant relation soundness + finite-test conjunction
  -> certified finite definability
  -> actual 8-to-4 finite example.

## Corrections to the motivating brainstorm

1. The proposed equality with quantifier-free type equivalence is true for the
   observation-value fragment, not every quantifier-free formula of the full
   state-and-operation language. `T(x)=x` is a counterexample to the unrestricted
   version.
2. The proposed (h,q) grid does not automatically have a nontrivial q direction.
   Within one system and the initial fragment, every q gives exactly horizon h.
3. This collapse is NOT uniform quantifier elimination: witness availability in a
   different system changes existential truth even at corresponding qf-equivalent
   points.
4. An infinite family of observational equalities is not automatically one definable
   equivalence relation. The stream counterexample makes this failure explicit.
   General elimination of imaginaries therefore cannot simply be invoked.
