# Observational logic and representation normalization

## M1 / v0.1 — normalized model-theory entry point

Author: Komorebi P.

This is a new branch continuing the semantic core of Komorebi Representation
Calculus v0.4. It is not Representation Calculus v0.5, p-adic Block 16, or a
replacement for Resolution Logic. The complete v0.4 archive is frozen under
`history/`. Two of its modules are copied byte-for-byte and rebuilt. No full
replay of the 235-module predecessor is claimed.

**Achieved scope:** a total, meaning-preserving path normalizer; exact agreement
between behavior and a specified observational logical fragment; quantified
preservation under surjective exact transports; finite test codes with local
certificates; and explicit failures of stronger unqualified claims. Four new
Lean modules and a separate Python reference implementation are provided.

The definitions and theorems are elementary structural semantics. No literature
novelty, quantifier-elimination theorem, elimination-of-imaginaries theorem,
automatic scientific discovery, or foundation for arbitrary model theory is
claimed. Proof interpretation is self-review.

## 1. The profile comes before the language

Fix sets/types X of states, A of unary operation symbols, O of observation
symbols, and V of observation values, with total deterministic maps

    T_a : X -> X,       o_j : X -> V.

Every source state is an admissible initial state. Words are read left to right:
`run [a,b] x = T_b(T_a(x))`. Let

    Beh(x)(w,j) = o_j(run w x).

The inherited relation is

    x E y  iff  Beh(x)(w,j)=Beh(y)(w,j) for every finite word w and every j.

The new syntax has a value-name test for **every** c in the fixed value sort V.
This is a genuine richness assumption on the observation language. With infinite
V it is an infinite signature, though each formula is finite. It is not a claim
that all possible values have finite encodings in an arbitrary executable.

One may replace value names by a declared family of predicates separating values,
but the present formal theorem uses the complete family of value-name tests.
Without separation, logical agreement can be strictly coarser than behavior.

The Lean definitions allow empty types. The reference finite implementation uses
nonempty state sets. Interpreting the grammar in conventional many-sorted
first-order logic additionally requires its usual nonempty-sort conventions.

## 2. Observational syntax and path normal form

The source grammar is

    phi ::= true | test(j,c) | not phi | phi and psi | after(a,phi).

Semantics:

    test(j,c)(x)             means o_j(x)=c,
    after(a,phi)(x)          means phi(T_a(x)).

The normal grammar is

    F ::= true | atom(w,j,c) | not F | F and G,

where `atom(w,j,c)(x)` means Beh(x)(w,j)=c.

A prefix operation attaches w before every atom path. For example,

    after(a, after(b, test(j,c)) and not test(k,d))

normalizes to

    atom([a,b],j,c) and not atom([a],k,d).

The order [a,b] is intentional: a is applied first. Reversing this order can fail
when the transitions do not commute.

### N1. Normalization soundness [Lean]

For every profile, state x, and source formula phi,

    Sat(normalize(phi),x) iff Sat(phi,x).

The proof uses the inherited word-composition identity and structural induction.
All definitions are total recursive functions checked by Lean's termination
checker. This is not a normalizer whose correctness is merely sampled in Python.

### N2. Retraction [Lean]

Embedding a path-normal formula into source syntax and normalizing it returns
exactly that formula:

    normalize(embed(F)) = F.

Consequently normalize(embed(normalize(phi)))=normalize(phi).

This is **path normalization**, not a unique normal form modulo every Boolean
identity or every equation of a theory. For example p and q is not automatically
identified with q and p. No quantifiers are eliminated by this normalizer.

## 3. Exactly the right logical-equivalence theorem

### L1. Observational type equivalence [Lean]

    x E y iff x and y satisfy the same path-normal observation formulas.

Equivalently, they satisfy the same source observation formulas.

Forward proof: equal behavior gives equal atomic truth values and induction
handles Boolean connectives. Reverse proof: if an observation at word w differs,
choose the named value c=Beh(x)(w,j). The atom atom(w,j,c) is true at x and false
at y. The availability of this name is why Section 1 states language richness.

This is a **fragment type**, not an ordinary unrestricted complete or
quantifier-free type. Ordinary first-order syntax also permits equality between
state terms, which this language does not contain.

### Counterexample: full quantifier-free preservation is false [Lean]

Take X={false,true}, a transition sending both states to false, and constant
observations. Both states have identical complete behavior. Yet T(x)=x is true
at false and false at true. No predicate on the one-point behavioral quotient can
represent this fixed-point property.

Even the sentence `exists x exists y, x != y` is true in the source and false in
its quotient. Thus the quotient is not in general elementarily equivalent to,
nor an elementary image of, the full source structure with state equality.

## 4. Logical resources must be separated

For h>=0, let E_h mean equality of observations on words of length at most h.
The horizon of a path-normal formula is its longest atom path. Lean proves

    x E_h y iff all observation formulas of horizon <=h agree at x,y.

It also identifies E_h with the inherited recursive finite-horizon relation and
proves: if E_h implies E_(h+1) for all state pairs, then E_h already equals E.
The stability premise cannot be dropped.

Quantifier rank and term depth are different resources. An atom

    o_j(T_a^h(x))=c

has first-order quantifier rank zero for every h. Thus bounding quantifier rank
alone does not bound the length of the experiment. Any later logical resolution
profile must fix the signature and separately track term horizon, quantifier
rank, and (when relevant) formula size and parameter budget.

### Infinite boundary [Lean]

On Boolean streams f:N->Bool, use shift as the sole operation and f(0) as the
observation. For every h, the zero stream and the stream with its first one at
h+1 agree through horizon h but differ at the next step. Therefore there is no
uniform finite horizon, and no finite list of observation tests, complete for
all states in this system.

This does **not** prove absence of a full first-order definition. Indeed, with
ordinary equality on streams, the entire behavioral relation in this particular
example is just x=y. The proved negative result concerns finite observational
test codes, not all possible first-order formulas.

## 5. A precisely scoped quantified extension

We also implement a state-variable-indexed first-order observational syntax.
An n-variable state term is `(i,w)` with i in Fin n. Its observed value is

    o_j(run w (environment(i))).

The atoms are either equality to a named output value or equality between two
observed values. Boolean connectives and state existential quantifiers are
allowed. Universal quantifiers and disjunction can be defined from those.
Binder variable zero is the most recently bound state. Equality between STATES
or STATE TERMS, additional arbitrary state relations, and state constants are
not part of this fragment.

### L2. Surjective observational first-order preservation [Lean]

Let q:X->Y satisfy

    q(T_a(x)) = U_a(q(x)),        o_j(x)=o'_j(q(x)),

and suppose q is surjective. Then every formula phi of the specified fragment
satisfies

    S |= phi[env] iff T |= phi[q o env].

The proof handles atoms through word transport, Boolean connectives by induction,
and existential witnesses by mapping source witnesses forward and lifting target
witnesses using surjectivity.

The actual behavioral quotient map has the required surjectivity, so its formula
preservation is a formal corollary. Replacing each free state by a behaviorally
equivalent state in the same structure preserves every fragment formula, even
with nested quantifiers. For one free variable, fragment-type equivalence is
exactly behavioral equivalence.

This is **not quantifier elimination**. It is preservation/reflection of truth
through a particular surjective transport for a language with specified atoms.
No quantifier-free replacement formula for an arbitrary quantified query is
constructed.

### Counterexample: surjectivity cannot be omitted [Lean]

A one-state identity system observes false. It embeds by exact transport into a
two-state identity system whose observations are false and true. All observations
of the embedded state are preserved. Nevertheless `exists y, o(y)=true` is false
in the source and true in the target. The extra witness is outside the image.

## 6. When the equivalence has one finite defining formula

Let tests be a finite list (w_i,j_i). Define the actual tuple code

    code(x) = (Beh(x)(w_i,j_i))_i.

A finite-code certificate supplies TWO LOCAL obligations:

1. equal codes imply equal immediate observations;
2. equal codes imply equal codes after every permitted operation.

It does not include all-word exactness as an assumed field.

### L3. Finite-code exactness and definition [Lean]

Those obligations imply

    code(x)=code(y) iff x E y.

The reverse implication holds because every selected coordinate is an actual
behavioral test; the forward implication follows from the inherited invariant-
relation theorem. Construct the two-variable formula

    E_tests(x,y) = AND_i [ o_ji(T_wi(x)) = o_ji(T_wi(y)) ].

Lean proves that this finite formula has quantifier rank zero and defines E
exactly whenever the local certificate holds. The tuple code itself is made of
existing observed terms, not arbitrary class labels.

In a conventional many-sorted language containing these operations/observations,
this supplies an explicit definable code for **this particular equivalence
relation**, under the stated completeness certificate. It is not elimination of
imaginaries for the entire theory. The embedding into Mathlib's general
`FirstOrder.Language` syntax remains the next separate formal bridge.

Without a finite certificate, the construction initially supplies an infinite
family of pair-observation equations, i.e. a partial-type description in the
corresponding language. A single defining formula does not follow automatically.
Nor does the failure of a finite test list by itself rule out every possible
first-order definition in a larger language.

## 7. Normalization ledger for the earlier brainstorm

| Earlier informal arrow | Normalized statement/status |
|---|---|
| behavior = quantifier-free type | True for the declared observation-only Boolean fragment. False for unrestricted state equality. |
| increasing quantifier rank = longer observation | False. Track term horizon separately; atomic formulas can have arbitrary term depth. |
| behavioral quotient preserves first-order truth | True for the specified observational fragment under a surjective exact transport. False for unrestricted first-order equality. |
| quotient exists -> definable quotient code | Invalid without a finite definability/code certificate or another explicit definability theorem. |
| quantifier elimination = effective compiler | Only after an effective procedure and complexity/output obligations are supplied. Not proved here. |
| stability/NIP -> cheap representation | Research question requiring a named definable family and resource model. Not a consequence established here. |
| compactness -> realization in a chosen structure | Not automatic. Existence of a model and realization in a specified model are different obligations. |
| forcing extension = coordinate change | Incorrect general identification; it belongs to a separate semantics-changing class of maps. |
| arbitrary new predicates reduce definability cost | Vacuous unless the language is fixed or definitions/expansion costs are charged. |

The forcing, Fraisse, stability, NIP and ultraproduct proposals remain research
ideas, not accepted bridges in this block.

## 8. Proof and execution boundary

Four new Lean modules, 44 new theorem declarations. Two inherited modules are
rebuilt byte-for-byte. Total library scope: six modules and 119 named declarations.
The final cold build, full named-declaration axiom audit, and controls are in
`results/LEAN_AUDIT.json`. The only observed foundations are `propext`,
`Classical.choice`, and `Quot.sound`. No custom project axiom, `sorryAx`, or
`Lean.ofReduceBool` is admitted in accepted library proofs.

The reference Python audit checks normalization, encoded quotients, quantified
preservation, and finite-code semantics over 100 declared finite systems. It
exhausts all 64 two-state systems with two labelled deterministic actions and one
binary observation. The other 36 are deterministic-seeded/boundary systems of
sizes 1..6. Random formula families are sampled, not exhaustive. An independent
pair-search algorithm checks all-word observational equivalence on each finite
system; it is separate from partition refinement. The finite loops do not prove
the universal Lean theorems, and the Python program is not extracted from Lean.

The formal syntax is intentionally self-contained over Lean/Std, using the actual
inherited System/run/ObsEq/Transport definitions. It is not yet an imported
Mathlib FirstOrder-language development, a translation of arbitrary informal
mathematics, or a global model-theoretic normal form.

## 9. Next exact target

Construct an explicit translation of the observational fragment into conventional
many-sorted or tagged single-sorted first-order syntax and prove satisfaction
commutes with the translation. Then connect finite matrix-derived test sets to
finite defining formulas using the existing certificate pipeline. Only after
those bridges should the project attempt theory-level quantifier elimination or
quantitative coding of more general definable equivalence relations.
