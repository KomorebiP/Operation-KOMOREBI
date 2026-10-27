# Standard logical semantics and relation-sensitive representation

## v0.2 — lineage and status

The sole logical predecessor is `Komorebi_Logical_Resolution_v0.1.zip`, SHA-256
`83a519736bb97f3cd888afbb81af9e92c4b99fd4592c804ae30bd96ca1c80abd`.
The original ZIP is unchanged under `history/`; all eight inherited Lean source
files are byte-identical. The parent Python audit is replayed separately. No
reverification of its embedded full Representation Calculus archive is claimed.

This release completes the preceding standard first-order translation target and
constructs a genuinely relational quantifier-rank distinction. The proofs are
kernel-checked under the pinned Lean/Mathlib environment. Semantic interpretation
is authoring-assistant self-review, not independent refereeing. No historical
novelty is claimed for quotient descent, formula induction or back-and-forth.

## 1. The source objects and preserved fragment

A deterministic unary system is S=(X,T_a,o_j), with o_j:X->V and a fixed external
observation-value type V. Words act left to right, so [a,b] means T_b(T_a(x)).
The state, operation, observation and value types need not be finite or nonempty.
An assignment at arity n is rho:Fin n -> X.

Retain the exact old observation-value terms:

    value term ::= literal(v) | o_j(T_w x_i).

Add state terms t=(i,w) and named binary predicates K_b:X->X->Prop. The new formulas
are falsum, value-term equality, K_b(t,u), negation, conjunction, and existential
state quantification. State equality is NOT a constructor. The newest bound
variable occupies index zero and previous variables shift by one. Universals are
abbreviated by negated existentials. Quantifier rank counts nesting; it is not an
operational word-depth bound.

`Formula.relational` embeds the original syntax without changing its meaning.
`observational_inclusion` proves that fact. Actual old operations and observations
are reused, not redefined through the new syntax.

## 2. A relation is representable exactly when it respects encoding fibers

For any map q:X->Y and predicate K:X->X->Prop, the following are equivalent:

    exists L:Y->Y->Prop, forall x y, K(x,y) iff L(qx,qy);

    forall x x' y y', qx=qx' -> qy=qy' -> (K(x,y) iff K(x',y')).

The forward implication substitutes the equal encoded values. For the reverse,
define L(a,b) by the existence of representatives x,y with qx=a, qy=b and K(x,y).
Fiber invariance makes this agree with K on every actual pair. Surjectivity is
unnecessary for this local existence theorem; off-image pairs can be false.

`relation_descends_iff` is the formal equivalence. Applying it to the actual
behavioral quotient proves `relation_descends_behavior_iff`:
K descends iff it is invariant under behavioral equivalence in BOTH arguments.
The predicate `quotientRelation` is explicitly constructed; its correctness is
proved from precisely that invariance, not from an assumed quotient structure.

This gives a necessary-and-sufficient obstruction test to adding a relation to a
fixed representation without refining that representation. It is not an algorithm
for deciding that invariant condition on arbitrary infinite structures.

## 3. Quantified relational transport

Suppose q is a surjective transport of deterministic systems:

    q(T_a x)=U_a(qx),    o_j(x)=o'_j(qx),

and every added binary predicate is preserved and reflected:

    K_b(x,y) iff L_b(qx,qy).

For every source formula phi at every arity and every assignment rho,

    Holds(S,K,phi,rho) iff Holds(T,L,phi,q o rho).

Proof: the inherited all-word equation preserves state terms, and observation
transport preserves value terms. The iff on relations gives the new atom case.
Boolean cases are direct. For an existential, map a source witness forward; lift
a target witness by surjectivity for the reverse implication. The binder assignment
square is checked rather than assumed. Arbitrary quantifier nesting follows by
formula induction.

Endpoint: `relational_formula_transport`. Applying it to the actual behavioral
quotient and the constructed descended predicates gives
`relational_quotient_formula`. Neither theorem preserves unrestricted state
equality through a noninjective map. One-way relation preservation is insufficient
because the language includes negation.

## 4. Translation into actual standard first-order syntax

The target is Mathlib's existing `FirstOrder.Language`, `Term`, `BoundedFormula`,
`Formula`, `Structure`, and `Realize`, not another custom evaluator called
first-order logic. A one-sorted RELATIONALIZATION is used on exactly the state
carrier X. The fixed value type V is represented by primitive relation symbols:

| Symbol | Arity | Interpretation |
|---|---:|---|
| step(a) | unary function | T_a |
| literals(v,u) | 0 | v=u in V |
| valueIs(j,v) | 1 | o_j(x)=v |
| agree(j,k) | 2 | o_j(x)=o_k(y) |
| link(b) | 2 | K_b(x,y) |

No state constants, dummy states, or value quantifiers are added. In particular
empty state carriers remain empty. This is not advertised as a native many-sorted
backend. There is not a primitive predicate for every whole formula; only the
fixed atomic families above are used.

`wordTerm` builds the genuine unary function compositions. `valueEquality`
translates the four combinations of literal and probe. In the literal/probe
orientation its correctness uses symmetry of value equality.

`translateAux` accepts an arbitrary map from the source's Fin k variables into
Mathlib free variables alpha plus bound levels Fin n. The custom syntax binds at
the front, whereas Mathlib quantifies the LAST bound level n. `pushMap` sends the
new source variable to Fin.last n and casts earlier bound levels with castSucc.
The theorem `binder_assignment` proves the exact semantic substitution identity.

The universal satisfaction theorem is

    Realize(model(S,K), translateAux(phi,sigma), v, xs)
      iff Holds(S,K,phi, i |-> Sum.elim(v,xs)(sigma(i))).

Induction handles arbitrary free/bound contexts and quantifier nesting. The main
specialization `translate_realize` gives the direct equivalence at all finite
arities; `original_formula_realize` connects the old observational language too.

The new function `Standard.rank` computes ordinary quantifier rank ON Mathlib's
actual syntax. `translate_rank` proves exact equality with source qrank.
`rank_zero_qf`, `qf_rank_zero` and `translate_qf_iff` connect this to Mathlib's
existing `IsQF`. This does not claim that the custom rank function was already a
named Mathlib API.

Finally `standard_relational_transport`, `standard_quotient_preservation` and
`standard_observational_transport` compose the actual translation with the
source transport theorems. The result preserves truth of the TRANSLATED fragment
in the explicit models, not all formulas in arbitrary target-language structures.
The target language has built-in state equality; the translator never emits it.

## 5. Back-and-forth as a quantified preservation certificate

For assignments rho, tau in potentially different structures, AtomicAgreement
means that every permitted value equality and every binary-relation test on
operation-word terms has the same truth value. State equality is not included.
Operational word depth is unbounded in this definition.

Define BF_0 to be AtomicAgreement. Define BF_(q+1) by AtomicAgreement together with

    for every source witness x, some target y gives BF_q of the extended tuples;
    for every target witness y, some source x gives BF_q of the extended tuples.

Reflexivity and symmetry are proved. Formula induction then proves

    BF_q(rho,tau) and qrank(phi)<=q ->
       (Holds(S,K,phi,rho) iff Holds(T,L,phi,tau)).

The existential case uses the first witness clause forward and the second clause
backward, consuming one rank. No global surjective map between the models is
assumed. Agreement at every rank gives agreement on every finite formula of the
fragment by choosing q=qrank(phi).

`backForth_preserves_formula` and `backForth_all_formulas` are the source endpoints;
`standard_backForth_preservation` transfers the theorem to standard Realize.
This is SOUNDNESS of the specified finite-rank condition. It does not prove that
formula agreement implies the existence of a matching strategy, construct a
finite algorithm for infinite atomic profiles, or identify arbitrary full
first-order Ehrenfeucht-Fraisse games.

## 6. A genuine rank-one distinction in one standard model

Take X=Fin 3, one identity operation, one constant Unit-valued observation, and
the single directed edge K(0,2). There are no other edges or state constants.
The old behavioral quotient has one class because every observed value is the same.

Every term in a constant variable assignment evaluates to that one assigned vertex.
Every self-loop is false. Therefore every parameter-free one-variable STANDARD
quantifier-free formula has the same truth value at every vertex. This theorem
quantifies over Mathlib's actual IsQF formulas, INCLUDING built-in state equality,
not just formulas emitted by our translator.

The formula phi(x)=exists y, K(x,y) has rank one and is true exactly at vertex 0.
It is false at vertex 1. Thus no parameter-free quantifier-free formula in this
fixed language can define phi uniformly over even this ONE model.

The proof uses `standard_qf_constant` and `standard_query_holds`, producing
`quantified_distinction` and `no_qf_replacement_in_this_model`. Parameter-freeness
is load-bearing: adding a constant naming vertex 2 supplies a new atomic query.
This does not refute quantifier elimination in a different expanded language or
a different theory.

There is also no exact relation on the old one-class behavioral quotient that
recovers K. The pairs (0,2) and (1,2) have equal quotient coordinates but different
K-truth. `relational_quotient_impossible` checks that instance of the general
fiber criterion.

This resolves the earlier collapsed rank axis in the intended sense: once actual
relations are permitted, a quantified query can distinguish states that EVERY
parameter-free QF formula in this model leaves indistinguishable. A whole strict
hierarchy at arbitrary ranks has not been proved.

## 7. Executable audit and proof boundary

`relational_logic.py` contains independent source and target finite evaluators.
The source binder prepends a value; the target evaluator appends a Mathlib-style
bound level and interprets falsum/imp/all. The translator's truth and exact rank
are audited under nested quantifiers and noncommuting operations. Mutation checks
intentionally replace the bound-level choice and reverse words; both are detected.

The finite audit covers 28 random/degenerate models, 16 surjective relational
pullback pairs, and all 512 directed relations on three vertices. Atomic and
rank-one back-and-forth checks are exhaustive on those graphs. Formula/assignment
sampling in other models is bounded and explicitly recorded in RESULTS.md.
The graph-specific Python partition has one rank-zero class and three rank-one
classes; the Lean theorem establishes the concrete rank-zero versus rank-one
separation above, not an additional universal classification of finite graphs.

The Python interpreter, parser and finite matching algorithm are NOT Lean-extracted
or formally verified programs. The universal conclusions are carried by the Lean
proofs. The standard syntax/semantics and basic back-and-forth ideas are classical
inputs and methods. The project-specific contribution here is a verified integration
with the declared Representation Calculus semantics, not a priority claim.

## 8. Next exact obligation

Build a finite relation-sensitive refinement/certificate algorithm over complete
finite profiles. It should return a sound preservation certificate or an actual
distinguishing formula and translate that result into the already checked standard
backend. Derive and certify its finite scope instead of equating bounded sampled
queries with all-word or all-rank behavior.

Separate later targets: equality-inclusive partial-isomorphism contracts,
finite-rank completeness under explicit finiteness hypotheses, native definability
and type-space interfaces, theory-relative quantifier elimination, imaginaries,
compactness, saturation, ultraproducts, forcing, general machine discovery,
independent review and historical novelty.
