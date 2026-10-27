# Observation, logical resolution, and the boundary of definability

## Status and provenance

This first logical-resolution block imports the exact `RepresentationCore.lean` and
`FiniteCertificates.lean` bytes from Representation Calculus v0.4, whose archive
SHA-256 is `d847c5b678bd2a632b3f14fb8ae089ca3352c14071fbcba8c8a03a3995a0fbd2`.
Those two modules are rebuilt. No new verification of the rest of v0.4 or the
p-adic corpus is asserted. Six new modules have completed a cold Lean build and
axiom audit. Semantic interpretation is authoring-assistant self-review, not an
external referee review. No historical novelty claim is made.

The motivating model-theory proposal needed two qualifications. First, a behavioral
quotient does not preserve arbitrary state-equality formulas. Second, quantifier
rank need not produce a new resolution axis inside an observation-only language.
Both boundaries are now mathematical theorems in the release.

## 1. The specified language

A system is the inherited deterministic unary structure

    S = (X, (T_a)_(a in A), (o_j)_(j in O)),  o_j : X -> V.

The state type X, operation alphabet A, observation indices O, and fixed value type
V are arbitrary. They need not be finite, linear, or nonempty. A word is executed
left to right, so `[a,b]` acts by `T_b(T_a x)`. Let

    Beh_S(x)(w,j) = o_j(T_w x).

The language at arity n has observation-value terms

    t ::= literal(v) | o_j(T_w x_i),    i < n,

and formulas

    phi ::= false | (t=u) | not phi | (phi and psi) | exists x phi.

Terms return values in V. **State equality is not an atom.** Every value in V has
its own fixed literal. Existential quantification ranges over X, and universal
quantification is the derived abbreviation `not exists not`. The constructor
`Formula.existsState` binds variable zero and shifts the other variable indices.
Lean's indexed datatype ensures all variables remain in scope.

Words normalize all compositions of the available unary state operations. The
language contains no additional binary state relations, state constants, value
operations, value quantifiers, or observation predicates with unspecified separating
power. Adding any of these requires a new contract and proof.

Define operational term depth h(phi) as the maximum length of a word occurring in
a probe, including probes beneath quantifiers. Define quantifier rank q(phi) by
the usual nesting count. These are distinct syntactic measures; calling a deep
word quantifier-free does not bound its operational depth.

This is an independent, small, well-scoped syntax and semantics in Lean/Std. An
embedding into Mathlib's `FirstOrder.Language` has NOT been implemented in this
block. Its intended mathematical interpretation is a fragment of a two-sorted
language, with states and fixed observation values kept distinct.

## 2. M1: behavior is exactly observational type agreement

Define behavioral equivalence by

    x ~_S y  iff  for all w,j, Beh_S(x)(w,j)=Beh_S(y)(w,j).

For x,y in the SAME structure S, the following conditions are equivalent:

1. x ~_S y;
2. x and y satisfy the same quantifier-free formulas of the specified
   one-free-variable observational language;
3. x and y satisfy the same formulas of that language, even with state quantifiers.

**Proof.** Equality of every probe value preserves each atomic equality and then
Boolean combinations. When quantifying, use the same witness in the same structure;
its behavior agrees with itself. Induction on the formula gives (1) implies (3),
and (3) implies (2) is immediate. For (2) implies (1), choose w,j and the literal
v=Beh_S(x)(w,j). The atomic formula `o_j(T_w x)=v` holds at x, so it holds at y.

The availability of literals separating every value is load-bearing. This theorem
is not a statement that unlabelled equality patterns among outputs distinguish
the actual output values. It is also not equality of unrestricted first-order types.

Checked endpoints:

    behavior_iff_observation_qf_type
    behavior_iff_observation_type

## 3. Quantified preservation across structures

Let q:X->Y be an exact transport between S and T, with the SAME value domain:

    q(T_a x)=U_a(qx),    o_j(x)=o'_j(qx).

If q is surjective, then for every finite observational formula phi, every arity n,
and every assignment rho of its free variables,

    S |= phi[rho]  iff  T |= phi[q o rho].

**Proof.** A probe is preserved by the inherited all-word transport theorem. Value
literals are unchanged. Atomic and Boolean cases follow. For an existential, a
source witness maps forward under q. In the reverse direction, surjectivity lifts
every target witness to a source witness. The binding/assignment square is proved
in `extend_map`. This proves both directions through arbitrary quantifier nesting.

Applying this to the ACTUAL inherited behavioral quotient proves preservation by
its specific quotient map, not by an arbitrary newly postulated isomorphism.

    formula_transport
    quotient_formula

Without surjectivity, the quantifier-free theorem still holds. Quantified truth can
fail: embed a one-state, false-observing identity system into the two-state identity
system on Bool with observation equal to the state. All quantifier-free formulas
agree at the false state, but `exists y, observe(y)=true` is false in the former and
true in the latter. Therefore that existential query has no uniform quantifier-free
elimination across even these two systems. This does not deny quantifier elimination
relative to a suitable fixed theory.

    qf_formula_transport
    quantified_surjectivity_necessary
    no_uniform_qf_elimination

## 4. What happens to the proposed (h,q) resolution grid

Let x ~_h y mean equality of all observations after words of length at most h.
Let x ==_(h,q) y mean agreement on every one-variable observational formula with
operational depth at most h and quantifier rank at most q.

For every fixed S and all natural h,q,

    x ==_(h,q) y  iff  x ~_h y.

This is also proved equal to the inherited recursive `Horizon S h` relation.

**Proof.** Under pointwise finite-horizon agreement of assignments, every term
in a depth-h formula has equal value. In a quantified case, use the same bound
witness on both sides; the extended assignments still agree at depth h. Formula
induction gives the forward invariance. Conversely, rank-zero labelled atoms
already test every word of length at most h.

Thus the q-axis adds no distinctions in THIS fragment within a fixed structure.
It does not follow that quantifiers are uniformly eliminable across structures:
the preceding two-model example proves otherwise. Nor is this a statement about
languages with binary relations or state equality.

    formula_depth_congr
    bounded_type_iff_horizon
    bounded_type_rank_independent

Failure of the horizon relation has a certificate: a rank-zero labelled atomic
formula of depth at most h that is true at the first state and false at the second.
The witness comes from the inherited actual distinguishing word.

    distinguishing_observation_formula

## 5. Why unrestricted quantifier-free types are different

Take state space Bool, T(x)=false, and a constant false observation. The two states
have identical future observations. But the atomic state-equality formula

    T(x)=x

holds at false and fails at true. The valid map collapsing both states to one also
loses the sentence `there exist two distinct states`.

These are actual finite counterexamples, checked in Lean. They show that a
noninjective behavioral quotient must not be called an elementary map of the
unrestricted first-order language. Its exact preservation class must be named.

    constant_states_behavior_equal
    state_equality_separates
    merged_identity_not_reflected
    state_cardinality_not_preserved

## 6. Finite tests compile into a defining formula

For a finite list T of word/observation pairs, define the code

    code_T(x) = [Beh_S(x)(w,j) : (w,j) in T].

The compiler constructs the quantifier-free formula

    E_T(x,y) = AND_((w,j) in T) o_j(T_w x)=o_j(T_w y).

Lean proves that this formula is true exactly when the codes agree. Its quantifier
rank is zero and its operational depth is exactly the maximum listed word length.

Suppose equality of codes implies equality of current observations and is preserved
by every state operation. Then the formula defines COMPLETE behavioral equivalence:

    S |= E_T[x,y]  iff  x ~_S y.

The certificate is the two local closure conditions, not the mere existence of a
list of tests or its success on sampled words. The inherited invariant-relation
soundness theorem propagates the local conditions to all finite words.

    certified_finite_definability
    finiteCode_equal_iff

A concrete verified example uses bit states (a,b,c), operation
`(a,b,c) -> (a xor b,b,c)`, and observation a. The map to (a,b) is an exact,
surjective 8-state to 4-state transport. Its equality is defined by just

    observe(x)=observe(y) AND observe(Tx)=observe(Ty).

Lean proves this finite formula defines full behavior and proves preservation of
EVERY formula of our fragment by the quotient, at every arity and quantifier rank.

    Small.all_observational_formulas
    Small.finite_formula_defines_all_behavior

No minimum-formula-size theorem or quantifier-elimination algorithm is claimed.

## 7. Infinite observational equality need not be finitely definable

Let X be all streams Nat -> Bool, with head observation and left shift. Then

    Beh(s)(w,head)=s(length(w)),
    s ~ t iff s=t.

For every horizon h, the all-zero stream and the stream with a single one at
position h+1 agree through h and disagree after h+1 shifts. Therefore no uniform
finite observation horizon determines behavior on this system.

The stronger checked statement is that NO ONE FINITE FORMULA of our observational
fragment defines behavioral equivalence on all pairs of streams, even when arbitrary
state-quantifier nesting is allowed.

**Proof.** Suppose phi(x,y) defines the relation, and let h=depth(phi). The assignments
(0,0) and (0,spike_(h+1)) agree on every observation through h. The bounded-depth
formula theorem makes their phi truths identical. The first pair is behaviorally
equal and the second is not, a contradiction.

    no_uniform_stream_horizon
    stream_behavior_not_finitely_definable

Nevertheless, the INFINITE FAMILY of pair-observation formulas does define the
relation by intersection. The release proves this pair-atom schema directly:

    behavior_iff_all_pair_formulas

This is the essential distinction between an equivalence specified by an infinite
family of formulas and one defined by a single formula. It prevents a premature
appeal to elimination of imaginaries, which concerns definable equivalence relations.
The nondefinability statement is language-relative: adding state equality gives an
immediate formula for stream identity. It is not a theorem of nondefinability in
all richer languages.

## 8. What has and has not been achieved

The M1 observational bridge is formalized for its precise fragment, including
quantified transport, bounded logical resolution, finite definability certificates,
and explicit obstructions to stronger interpretations. This is a first logical
layer of Representation Calculus, not a full model-theory development.

Still separate: a verified translation to Mathlib's standard first-order syntax;
additional state relations/equality and appropriate back-and-forth interfaces;
complete types over parameter sets, compactness, saturation, elimination of
imaginaries, theory-specific quantifier elimination, ultraproducts, forcing,
independent refereeing, and historical novelty. The Python finite-model evaluator
and test search are not verified programs or a learned AI policy.
