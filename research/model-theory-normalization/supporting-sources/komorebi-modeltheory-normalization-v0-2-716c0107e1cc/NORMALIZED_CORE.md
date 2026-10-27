# Observational logic in standard first-order syntax

Author: Komorebi P.

## M2 / Model-Theory Normalization v0.2

The sole predecessor is `Komorebi_ModelTheory_Normalization_v0.1.zip`, SHA-256
`e3250cda82983f5f531f640e880399bd60c07569db04c33e2e33631c3d5e4881`.
Its original archive is retained under `history/`. Its six mathematical source
modules are copied byte-for-byte and rebuilt. This is the model-theory branch,
not Representation Calculus v0.5 or p-adic Block 16.

The completed new scope is the actual translation from the inherited observational
syntax into Mathlib `FirstOrder.Language`, with a universal satisfaction theorem,
standard fragment-preservation corollaries, quantifier-free finite definitions,
and explicit counterexamples to erasing the hypotheses. No quantifier elimination,
theory-wide elimination of imaginaries, or historical novelty is asserted.

## 1. Source and target semantics

A source system has states X, operations A, observations O and values V, with
`step : A -> X -> X` and `observe : O -> X -> V`. All states are admissible.
A word `[a,b]` acts by applying a first and b second. The custom source grammar
`ObsFO A O V n` has n state variables. Its atoms compare observed values, either
with named values or with other observed values. It includes Boolean combinations
and existential state quantifiers, but excludes equality between states.

The first-order signature is independent of X and of the specific system:

* a constant `c_v` for every v in V;
* a unary function `f_a` for every a in A;
* a unary function `g_j` for every j in O;
* one unary predicate `State`.

The universe interpreting this language is the disjoint tagged sum `X + V`.
State inputs have the intended action and observation meanings. Functions on
value inputs are totalized as the identity. `State` is true exactly on the X
summand. The distinct tags matter even when X and V have identical underlying
labels. Observation constants name the V summand.

This is a genuine Mathlib language and structure. We use Mathlib's own `Term`,
`BoundedFormula`, `Formula.Realize`, `IsQF`, and `Set.Definable`. There is no second
custom target logic substituted for those definitions in the Lean theorem.

The complete family of value names is part of the language profile. With infinite
V, the language can be infinite, although each formula remains finite. The formal
proof works even for empty state types. When discussing ordinary nonempty models,
one specializes to a nonempty tagged universe. In particular a nonempty state
sort suffices. The guard also handles an empty state sort inside a nonempty tagged
universe without inventing witnesses.

## 2. The compiler and its binder discipline

The compiler sends a source observed term `(i,[a,b],j)` to

    g_j(f_b(f_a(x_i))).

Boolean connectives translate to standard first-order connectives. The crucial
quantifier clause is

    C(exists x, phi) = exists z, State(z) and C(phi),

with z installed as the newly bound source-state variable.

The source indexes its newest bound variable by zero. Mathlib uses bound-variable
levels and appends a new level. `extendVariables` maps source zero to `Fin.last m`
and shifts the type of old levels without changing their numeric values. Free
variables are unaffected. The generic theorem includes arbitrary ambient free
and bound variable assignments, not only closed sentences.

### Universal satisfaction theorem [Lean checked]

For every source system S, every finite source formula phi and every state
assignment e,

    Realize_(tagged S)(C(phi), inl o e) <-> Sat_S(phi,e).

The concrete endpoint is `toMathlib_correct`; `translateAux_correct` proves the
stronger open-bound-variable version. The compiler is structurally recursive and
its termination is checked by Lean.

Proof: the term theorem follows the actual word action. Atomic equality then uses
injectivity of the value tag. Boolean cases follow recursively. For an existential,
the State guard rules out every value-tagged witness. A state-tagged witness is
exactly a source witness, and `extendVariables_realize` proves the environment
alignment. This establishes both directions, including arbitrary nested binders.

The previous operation-prefix normalizer is composed with this translation via
`pathToObsFO`. `compileSource_correct` proves the full source-prefix-language to
Mathlib truth theorem. `compileSource_embed` retains the old normal-form retraction.

## 3. Exactly the preserved fragment [Lean checked]

For a surjective exact transport q between systems sharing A, O and V,

    q(step_S a x) = step_T a (q x),
    observe_S j x = observe_T j (q x),

standard satisfaction of translated formulas agrees on corresponding assignments.
This is `standard_observational_transport`. The actual behavioral quotient is
surjective, so `standard_quotient_preservation` follows.

Moreover, for source states x,y,

    ObsEq S x y
      iff every translated one-variable observational formula agrees at x and y.

This is `standard_fragment_type_iff`. It is agreement on the translated fragment,
not an assertion that unrestricted complete first-order types agree.

The translation has no input that asserts its semantic correctness. The transport
corollary does retain its necessary local commutation, observation and surjectivity
hypotheses. It does not construct those hypotheses for arbitrary encodings.

## 4. An actual first-order definition from a finite code [Lean checked]

A finite test list consists of genuine observation-word pairs `(w_i,j_i)`.
The inherited certificate requires only:

1. agreement on the selected tests implies agreement on immediate observations;
2. that agreement is preserved by each source operation.

These local conditions imply exact agreement on all future observations. Compile
its binary observation formula and add two outer state-sort guards:

    State(x) and State(y) and
      AND_i [g_ji(f_wi(x)) = g_ji(f_wi(y))].

The resulting `guardedCodeFormula` satisfies Mathlib's actual `IsQF` predicate.
Its satisfaction set in the tagged universe is exactly

    {(inl x,inl y) : ObsEq S x y}.

In particular, `standard_behavior_definable` proves `Set.Definable` over the empty
parameter set in the stated observation language. No arbitrary class labels or
new predicate naming the answer are introduced. This codes this particular
certified equivalence relation on the state sort. It is not elimination of
imaginaries for every equivalence relation of a first-order theory.

The unguarded relation is also proved correct on state assignments. Outer guards
are needed only when defining the relation throughout the tagged universe, where
we must exclude value-tagged inputs explicitly.

## 5. Counterexamples built using standard first-order syntax [Lean checked]

### State equality is stronger than behavioral equality

For a Boolean source whose action sends both states to false and whose observation
is constant, the two states are behaviorally equal. The ordinary quantifier-free
formula `f(x)=x` holds at false and fails at true. `standard_full_qf_not_behavioral`
checks this inside the actual target language and Mathlib satisfaction relation.

### Removing a state guard creates spurious witnesses

Take a one-state system with only the false observation and a Bool value sort.
The correct translation of `exists x, observe(x)=true` is false. The unguarded
formula is true: the tagged VALUE true is a witness, because the total observation
function is the identity on that wrong-sort input. `erasing_state_guard_is_unsound`
proves both facts. Thus the guard is a load-bearing semantic obligation.

### Surjectivity is needed for witness reflection

The one-state false-observing source embeds into the two-state identity system
with observations false and true. This exact nonsurjective transport does not
reflect the same existential query. The standard-syntax counterexample is
`nonsurjective_standard_formula_failure`.

### Empty state sorts and binder order are handled explicitly

`empty_state_sort_remains_empty` proves that an existential state query has no
witness in an empty state sort, even when the tagged universe contains Boolean
values. `nested_binder_translation` checks that an inner true witness does not
overwrite a preceding false witness. The independent executable audit also
rejects deliberately reversed action paths and a clobbered binder translation.

Finally, `translated_existential_is_not_quantifier_free` proves that this compiler
retains an actual quantifier. Semantic compilation must not be relabeled as QE.

## 6. Verification contract

The accepted cold build checks all eleven local modules and all named declarations
with warnings treated as errors. The compiled upstream cache is the pinned
Mathlib revision, not an asserted new rebuild of all of Mathlib. Pinned source
hashes are in `evidence/ENVIRONMENT_VERIFIED.json`. False and sorry controls must
fail, as must invalid guard/state-equality/quantifier transfers.

The separate Python interpreter has only primitive target connectives: falsum,
equality, the State predicate, implication, and universal quantification. Its bound
environment appends values, unlike the source evaluator's prepended state binder.
It compares 100 systems, exhaustively covering all 64 two-state systems with two
labelled actions and one Boolean observation. Formula families are sampled, not
exhaustive. Finite code definitions are checked on ALL pairs of tagged objects
in the declared finite structures, including wrong-sort inputs.

The reference program is tested, not extracted from or formally verified by Lean.
The unrestricted formula theorem is the structural Lean proof, not a conclusion
from sample count. Hashes prove artifact identity, not mathematics. Review is
self-review, not independent refereeing.

## 7. Remaining obligations

The planned v0.1-to-Mathlib satisfaction bridge is closed. Not yet supplied:

* a complete matrix-certificate-to-logical-code exporter and its integrated proof;
* theory-wide quantifier elimination or elimination of imaginaries;
* a full Mathlib complete-type or saturation development;
* automatic language discovery or a held-out machine-discovery benchmark;
* arbitrary non-unary, probabilistic, approximate or partial operation semantics;
* verified Python extraction or formalization of arbitrary informal source problems.

The next focused step is to derive finite logical test codes from accepted matrix
certificates, retaining the declared coefficient and observation languages. This
would connect the existing algebraic discovery pipeline to the now proved standard
first-order definability endpoint, rather than introducing ad hoc predicates that
simply name the answer.
