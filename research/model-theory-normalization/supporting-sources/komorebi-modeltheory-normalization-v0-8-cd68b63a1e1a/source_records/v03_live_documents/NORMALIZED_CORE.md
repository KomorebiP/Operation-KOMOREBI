# From discovered matrix representations to definable observation codes

Author: Komorebi P.

## M3 / Model-Theory Normalization v0.3

This release joins two existing, separately verified interfaces. The immutable
parents are Model-Theory Normalization v0.2 and Representation Calculus v0.4.
Their complete ZIPs and exact hashes are retained in `history/` and
`source_records/PREDECESSORS.json`. This is neither Representation Calculus v0.5
nor p-adic Block 16. It does not rerun the entire earlier mathematical corpus.

The new mathematical scope is the finite matrix-certificate-to-logical-code
bridge, in actual Mathlib first-order syntax. All source states are admissible.
The syntax describes deterministic unary operations and observations, excludes
state equality from the preserved fragment, and explicitly names the observation
values. The generated defining relation has no new predicate or function symbol
naming the encoding matrix. Its atoms use only the original observation tests.

The reference compiler and discovery program are not verified executables. Lean
checks the literal matrices, witnesses and formulas in its generated source. An
independent parser compares those literals with the separately supplied source
JSON. This is a tested transcription boundary, not formalization of an arbitrary
informal human problem. No trained proposer, independent held-out discovery,
performance advantage, external referee verdict or historical priority is claimed.

## 1. The two source interfaces

Fix a semiring R and finite dimensions d,t,k,o,l. The formal algebraic interface
uses `Lean.Grind.Semiring R`; no field or division assumption is required by the
new generic bridge. Generated instances use the standard modular semiring on
`Fin (p^r)`. States are column vectors x in R^d, action a is x -> A_a x, and
observation j is the j-th row of O applied to x. Words act left to right, so
[a,b] means first A_a and then A_b. The empty word is allowed.

A matrix certificate contains:

* encoding P : R^d -> R^t;
* target action matrices C_a and observation decoder D;
* finitely many actual tests (w_i,j_i), i in Fin l;
* their row matrix G, with row i = O_(j_i) A_(w_i);
* a matrix W expressing the proposed encoding in those tests.

Its finite exact obligations are

    P A_a = C_a P,       O = D P,       P = W G.

Word provenance is checked, not an uninterpreted assertion that a row is a test.
The inherited matrix theorem proves, for all x,y,

    P x = P y  iff  every future observation agrees on x,y.

That theorem comes from the three finite equations and the actual word rows. It
is not a new hypothesis supplied by our logical certificate.

The logical interface accepts a finite list of genuine observation tests. Its
certificate requires only that equality of test values implies equality of
immediate observations and is preserved by each operation. The model-theory
parent then produces a formula defining behavioral equivalence and proves
preservation of all translated observational formulas under surjective transport.

## 2. From matrix equations to a complete logical test list [Lean]

Define

    tau_i(x) = o_(j_i)(T_(w_i)(x)),
    code(x) = (tau_i(x))_(i<l).

Then the matrix equations imply

    code(x)=code(y)  iff  P x=P y.

Forward direction: Gx=Gy and P=WG imply Px=Py by matrix composition.
Reverse direction: the commuting equations and output decoder imply agreement
of every future observation, hence agreement of the selected tests.

Code equality therefore implies equality of current observations. It is stable
under source actions: equal P-images remain equal under C_a, and the reverse
implication returns equality of test codes. These two arguments construct the
actual `FiniteCodeCertificate`; no all-word equality axiom is inserted in it.

The initial code is a list of genuine tests, not arbitrary labels for classes.
Zero tests and a zero-row encoding are allowed when the valid certificate implies
that every source distinction is irrelevant to the declared observations.

Endpoints in `MatrixObservationCode`:

    matrix_code_encoding
    matrixFiniteCodeCertificate
    matrix_tests_behavior
    matrix_code_reconstruct
    matrix_code_from_encoding

The last two express the computational bridges: P x is reconstructed from the
actual test-value tuple using W; the same tests can be evaluated using the target
matrices after x has been encoded. Discovery may retain more tests than the final
row count of P. This theorem does not minimize test-list length.

## 3. A first-order formula for the discovered equivalence [Lean]

The existing tagged first-order universe is R^d + R. States and values remain
separate even when their underlying labels coincide. The language contains the
original action functions f_a, observation functions g_j, a predicate State, and
constants for observation values. Operations on value-tagged inputs are totalized
as in the parent. Guarded quantifiers range only over states.

Construct

    E_c(x,y) = State(x) and State(y) and
                 AND_(i<l) [g_(j_i)(f_(w_i)(x)) = g_(j_i)(f_(w_i)(y))].

This is a real Mathlib `FirstOrder.Language.Formula (Fin 2)`. Lean proves its
actual `IsQF` predicate. It also proves, for every assignment in the tagged
universe, that E_c holds exactly on pairs of state tags whose P-images are equal.
Wrong-sort inputs are excluded by the two State guards.

Thus the relation

    {(inl x,inl y) : P x=P y}

is `Set.Definable` over the empty parameter set in the declared language. The
proof supplies the displayed finite formula. It does not add a predicate for
P, choose arbitrary class labels, or introduce ring addition/multiplication as
extra logical primitives.

Every tau_i is itself an original-language term. The tuple of their value-tagged
outputs is a coordinatewise `Set.TermDefinable` encoding and has exactly the
same kernel as P. This is a concrete definable code for this certified quotient.
It is not elimination of imaginaries for every definable equivalence relation
of a theory. Parameter-free always refers to this stated language; the language
already contains names for every observation value.

Endpoints in `MatrixLogicalBridge`:

    matrixCodeFormula_isQF
    matrixCodeFormula_semantics
    matrix_encoding_definable
    matrixLogicalCode_term_definable
    matrixLogicalCode_exact

## 4. Quantified queries must use the actual image [Lean]

The correct compressed state domain is

    Y = {y in R^t : exists x, P x=y},

not automatically all of R^t. The inherited `imageSystem` is well-defined because
P A_a=C_a P makes Y invariant. The map R^d -> Y is surjective by construction.

Applying the standard-syntax transport theorem proves

    source |= compile(phi)[x_bar]
        iff image |= compile(phi)[P x_bar]

for every finite observational formula phi, including arbitrarily nested state
quantifiers. This is the same translated fragment as in M2. It does not preserve
arbitrary ordinary first-order state equality, establish elementarity, or perform
quantifier elimination.

A new exact counterexample prevents a dangerous replacement of Y by R^t. Over
R=Z/4Z, let source dynamics be identity, observation be 2x, P=2, C=1 and D=1.
All matrix certificate equations hold. The actual image is {0,2}.

The query `exists x, observe(x)=1` is false in the source and the image, but true
in the ambient target R, witnessed by 1. Both claims and the standard first-order
truth mismatch are Lean-checked in `MatrixImageBoundary`.

Endpoint: `matrix_image_preserves_formulas`.

## 5. Defining an individual encoded class without a source search [Lean]

For a compressed vector y, evaluate the certified tests in the target machine:

    b_i(y) = target_observation_(j_i)(target_run(w_i,y)).

Construct the source-language formula

    F_y(x) = State(x) and AND_(i<l) [tau_i(x)=b_i(y)].

Its constants are named observation values already allowed by the language.
The constructor does not enumerate source states or choose a representative of y.

For y belonging to the actual encoded image, Lean proves

    F_y(inl x)  iff  P x=y.

Proof: choose a preimage only inside the mathematical proof. Exact transport
identifies its selected test values with b_i(y). The code-kernel theorem then
identifies equality of those values with P x=y. This choice is not part of the
executable formula constructor.

Every image state therefore has a nonempty class formula, and different image
states have disjoint classes. The formula is quantifier-free. The Python
constructor checks image membership using the already certified Smith factors
and rejects out-of-image requests rather than pretending such a class is a
represented state.

Endpoints in `MatrixLogicalFibers`:

    matrix_fiber_exact
    matrixFiberFormula_isQF
    matrixFiberFormula_states
    matrixFiberFormula_nonempty
    matrixFiberFormula_disjoint

The Lean nonemptiness proof is existential, not a verified source-state inversion
algorithm. No claim of a jointly definable parameterized fiber map in a smaller
logical language is added.

## 6. Discovery failures produce genuine distinguishing formulas [Lean]

If P x != P y, at least one certified test tau_i differs; otherwise all code
coordinates would agree and force P x=P y. Choosing its observed value at x
produces a standard quantifier-free formula true at x and false at y.

Likewise every inherited growth witness delta_i, killed by all earlier rows but
not by the new actual test, gives the formula `tau_i(z)=0`, true at the zero state
and false at delta_i. The formal proof uses the checked word interpretation of
that row. It does not assert that the discovery order or final formula is optimal.

Endpoints: `matrix_distinguishing_test`, `matrix_distinguishing_formula`, and
`growth_formula_distinguishes`.

## 7. The executed discovery-to-definition path

The exporter accepts a separately supplied expected source JSON and a matrix
certificate. The frozen independent matrix checker first checks the source,
finite equations, word provenance, growth witnesses, and Smith data. The exporter
then writes:

1. Literal source/target matrices and the original certificate proof obligations.
2. Explicit genuine observation-word rows and their checked trace.
3. A literal logical test list, checked against the matrix certificate in Lean.
4. The guarded first-order formula and its IsQF, exactness and definability proofs.
5. Quantified preservation for the actual encoded image.
6. Individual-class, term-code and growth-formula theorems.

No finite source-state table is emitted. Matrix coordinate equalities are finite
kernel reductions (`decide`), followed by the generic universal proofs. No
`native_decide`, custom axiom, or successful untrusted Boolean flag is accepted.

All 202 previously frozen synthetic certificates are retained. The large fixture
has 2^128 source states (eight residues modulo 65536). Its test list has just the
current observation and the observation after action zero. Its defining formula
is exactly

    State(x) and State(y) and
      g_0(x)=g_0(y) and g_0(f_0(x))=g_0(f_0(y)).

This does not disclose a hidden scrambling matrix to the discoverer. Nevertheless,
it is an inherited, deliberately constructed synthetic example, not a held-out
scientific discovery. The delayed-observation example retains eight tests with
maximum word length seven. Zero-coordinate cases correctly yield a relation
containing all state-tagged pairs.

The formula term horizon is an exported measurement. There is no general theorem
that it or the number of atoms is minimum, and no claim that minimum arithmetic
coordinates imply minimum description length or quantifier complexity.

## 8. Evidence and remaining boundary

The generic proof does not depend on passing the finite experiments. Conversely,
the Python programs are not extracted from Lean; they are audited implementations.
The independent logical checker imports neither the discoverer nor exporter. It
constructs the expected original-language formula itself, checks profile metadata,
and reparses literal Lean matrices and tests against the caller's source.

The finite audit combines symbolic vector evaluation (which never enumerates the
large state sets), explicit equal-kernel state pairs, wrong-sort tests, formula
construction for classes, genuine growth witnesses, and exhaustive small-system
queries. Its source evaluator prepends bound variables and its independent
primitive target evaluator appends them. Quantified image preservation is audited
on the finite small systems. Universal quantified correctness is the Lean theorem.

Both immutable parent archives are preserved; fifteen relevant inherited modules
are cold rebuilt in this branch. This does not mean all 235 representation parent
modules or the entire p-adic corpus were rerun. Exact final outcomes, counts,
failures and replay scopes are recorded in RESULTS.md and the manifests.

The matrix-to-logical-code bridge selected by M2 is closed at the stated endpoints.
Remaining work includes verified execution/termination of the discovery loop,
logical-cost optimization, independently frozen structural benchmarks, and truly
relational/non-unary languages with additional preservation conditions. General
first-order types, compactness, saturation, QE, elimination of imaginaries,
probabilistic/approximate semantics, independent review and historical novelty
remain separate targets.
