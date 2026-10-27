# Certified observation discovery and exact representation change

## v0.2: the achieved scope

This release continues **Komorebi Representation Calculus v0.1**, SHA-256
`53ff5820e6a8446099e68ef38300040eb0432053c1b0d24dc8cb113ba1aa98b1`.
The frozen predecessor ZIP is included in `history/`. This is a representation-calculus
research branch, not p-adic Block 16. It neither updates nor re-verifies the p-adic corpus.

The new result is a working proof-carrying loop for a defined class of systems:

    complete source specification -> observation discovery -> exact encoding
      -> independent certificate -> generated Lean instance -> all-word theorem.

The generic semantic core is Lean-checked. The new linear row-module algorithm,
its prime-power Smith interpretation and its numerical linear-coordinate minimality
have written proofs and independently checked finite matrix certificates. They
are NOT newly connected to the generic Lean core by a universal matrix adapter.
One concrete, automatically exported 256-state source/8-state quotient has the
complete all-word and minimal-state injection chain checked in Lean.

No trained AI proposer, held-out structural benchmark, broad performance advantage,
independent-referee verdict or historical novelty is claimed. The basic ingredients
are observational equivalence, exact module closure, Smith theory and certificates.

## 1. The semantic problem, precisely

A system consists of a state type X, an operation alphabet A, observation indices O,
a common observation-value type V, maps T_a:X->X and observations o_j:X->V.
Operations are total, deterministic and unary. States and operations need not be
finite or linear for the generic Lean results. Multiple observations are allowed.
Words are read left to right:

    T_[a,b,c] x = T_c(T_b(T_a x)).

EVERY source state is an admissible initial state in this release. This is different
from minimizing the linear span reachable from one designated seed. An application
must declare that initial-state interface; the executable rejects `single_seed`.

Define behavior and equivalence by

    Beh(x)(w,j) = o_j(T_w x),
    x ~ y iff Beh(x)(w,j)=Beh(y)(w,j) for all finite w and all j.

The empty word is included. No fixed observation horizon stands in for all words.

### S1. Exact quotient and universal sufficiency [Lean]

The relation ~ is an equivalence preserved by every operation. It is the largest
operation-stable relation that respects the current observations. Thus the quotient
X/~ carries actual descended operations and observations.

For any surjective representation q:X->Y satisfying

    q T_a = U_a q,    o_j = o'_j q,

there is a unique map Y->X/~ factoring the quotient map. That map also preserves
the operations and observations. The proof constructs the quotient, its operations,
its observations and the sufficient factor rather than taking them as hypotheses.

Proof outline: equality of q-images implies equality of every future output by
induction. Therefore ker(q) is contained in ~. Map q(x) to the class of x; the kernel
inclusion makes this independent of the representative and surjectivity proves
uniqueness. Lean's standard quotient and classical choice mechanisms are explicit.

Endpoints: `behaviorSetoid`, `quotientSystem`, `quotientTransport`, `quotient_exact`,
`sufficientFactor_encode`, `sufficientFactor_unique`, `sufficientFactorTransport`.

### S2. Local correctness implies all-word correctness [Lean]

`Transport` is the exact one-step certificate above. The theorem `transport_run`
proves q(T_w x)=U_w(qx), and `transport_behavior` proves the output equality for
all words. `Transport.comp` constructs exact compositions.

`checkLocal` is an executable Boolean check of those two local equations for
explicit finite state, operation and observation types. `checkedTransport` proves
that a true check produces a valid transport. `checked_transport_all_words` is the
resulting universal word theorem. Concrete checks use kernel-reduced `decide`, not
`native_decide` or an assumed Boolean success flag.

### S3. Minimality via distinguishing continuations [Lean]

Suppose a surjective valid encoding q:X->Y has a distinguishing continuation for
every distinct pair y,z in Y. Then x~x' iff qx=qx'. Moreover Y injects into the
state space of ANY alternative encoding that preserves all-word behavior. That
alternative need not intertwine its internal states, be linear, or be finite.

Proof: choose a source representative of each y. Send y to the competitor's encoding
of that representative. If two images agree, all future observations agree. The
separation hypothesis forces the original y values equal.

For finite Y this is a state-cardinality lower bound. It is not the same quantity
as minimum free linear coordinates over a ring.

Endpoints: `separated_encoding_exact`, `minimal_word_encoding_injective`,
`distinguishing_word_excludes_merge`.

## 2. Finite horizons and invariants are certified, not guessed

Define H_0(x,y) by equality of current observations, and

    H_(n+1)(x,y) iff current observations agree and
                      H_n(T_a x,T_a y) for every a.

Lean proves that true all-word equivalence implies every H_n. If H_n is stable
under one more refinement, then H_n is ALREADY exact all-word equivalence. It also
proves that failure of H_n has a distinguishing word of length at most n. The latter
is an existence theorem; it does not formalize a particular breadth-first search.

For a bounded nondecreasing integer rank f(n)<=B, Lean proves some n<=B has
f(n)=f(n+1). Identifying a concrete rank with module length, and linking a particular
Python loop to that ranking argument, remain separate obligations. We do not
report this generic lemma as a verified implementation of row-module iteration.

The predicate layer proves invariant intersections, sound fixed-fiber cuts, actual
unreachability from a separating invariant, and equality of a witnessed invariant
set with its unary orbit. These are explicitly orbit-SET statements. Application
to a linear orbit SPAN requires the separate submodule closure hypotheses.

Endpoints include `stable_horizon_exact`, `horizon_counterexample`,
`fixed_fiber_excludes_state`, `witnessed_closed_exact`, `finite_rank_has_plateau`.

## 3. Move from state enumeration to discovery of sufficient tests

Now restrict the source to a complete linear system over R=Z/p^r Z, p prime,
r>=1, with source state module R^d. Let A_a be d-by-d column-action matrices and
let O_j be observation rows. Define the observable row module

    S = span_R { O_j A_w : all w,j } <= R^(1 by d).

The correct object to close is a MODULE, not a vector space over F_p. Nonunits
and nonzero torsion factors must survive.

### M1. Terminating exact row closure [written; implemented]

Start with the observation rows. Repeatedly test a row for membership in the
current span; when it is new, retain it together with its actual word and observation
index and queue its right-multiples by every action matrix. Right multiplication
by A_a prepends a to the recorded input word, because our words act left-to-right.

Every accepted generator lies in S. Every strict enlargement increases the finite
module length log_p |S_current| by at least one. That length is at most r*d.
Therefore there are at most r*d accepted generators. At termination, the final
span contains every observation and is closed under each right action, so it
contains every O_j A_w. It is consequently exactly S.

The search never enumerates R^d. Resource caps are reported as unresolved, never
as a certificate that a missing representation does not exist.

### M2. Every enlargement has a semantic counterexample [written; certified]

Let G be the current row matrix. Write its chain-ring Smith form as U G V=D.
If a proposed new row f does not belong to the row span, then fV either has a
nonzero coordinate beyond the Smith pivots or fails divisibility by pivot p^s.
In the first case take z=e_j. In the second take z=p^(r-s)e_j. Set delta=Vz.
Then

    G delta=0,    f delta != 0 in R.

Thus source states 0 and delta are indistinguishable by all tests retained so far,
but distinguished by the proposed new word. The checker verifies these equations
directly. It does not merely trust a Smith-engine 'not a member' response.

These are counterexamples to the CURRENT TEST FAMILY, not claims of all-word
equivalence or nonequivalence beyond what the new distinguishing word proves.

## 4. The independently checked matrix certificate

A certificate binds to the caller's complete source JSON, including p,r,d, operation
matrices, observations, word order and initial-state interface. The caller must
supply its intended source; a hash supplied by the certificate itself authenticates
nothing about the intended problem.

The certificate contains rows P (the proposed encoding), actual observation-word
witnesses G, coefficients W, target actions C_a, and output decoder D, satisfying

    P = W G,
    P A_a = C_a P for every a,
    O = D P.

It also contains invertible V and its verified inverse, with

    P V = [diag(p^s_1,...,p^s_t)  0],   0<=s_i<r.

All of these are finite exact equations. The independent checker imports neither
the discovery program nor the Smith constructor.

### M3. Exact observational quotient [written universal reduction]

Define q(x)=Px. The commuting equations imply equality of all future outputs
between the source and target. Conversely P is a linear combination of true
observation-word rows, so states equal under EVERY future observation have equal
P-images. Hence

    Px=Py iff x and y agree on all future observations.

The image of P is invariant under C_a. This image, NOT the whole possibly larger
free target R^t, is the exact quotient. Empty P is allowed: when every observation
is zero, the quotient has one element and zero free coordinates.

The generic Lean theorem proves the corresponding local-to-all-word and quotient
principles, but this release does NOT include the universal matrix-to-Transport
adapter proving the linear-algebra equations imply the generic hypotheses.

### M4. Exact resource counts [written; matrix-certified instances]

Since V is invertible, image(P) is isomorphic to product_i p^s_i R. Thus

    log_p |image(P)| = sum_i (r-s_i),
    minimum free linear coordinates = t.

For the upper bound use the t-row encoding and its certified target actions.
For the lower bound, any competing free linear machine with k coordinates and an
R-linear initial encoding has an initial-image submodule U<=R^k whose future-output
map surjects onto the intrinsic behavioral module. Every submodule of R^k over
Z/p^r Z has at most k generators: lift it to an integer submodule between p^r Z^k
and Z^k and reduce an integer basis. A quotient cannot require more generators.
The displayed product of t nonzero cyclic factors needs t generators, since its
quotient by p times itself is F_p^t. Hence k>=t. Local internal-state intertwining
is not required of the competitor, only all-word output correctness.

This is a model-relative linear-coordinate minimum. It is not a bit lower bound
for arbitrary programs, a neural-network size bound, or the state cardinality of
a single seeded automaton.

## 5. A real automatically generated Lean instance

`tools/export_lean.py` reads an expected source and an independently checked matrix
certificate. For bounded inputs it constructs the explicit finite source table,
its encoded image, target tables, representatives and distinguishing words.
It emits a Lean source file. The output is not trusted: Lean checks local equations,
representatives and all distinguishing witnesses by `decide`, then applies the
generic theorems to prove exactness for ALL words.

The retained input is a four-coordinate system over Z/4Z with a hidden invertible
coordinate change. The discovery program receives only the transformed actions
and observations, not the conjugating matrix or the expected answer. It produces
two free linear coordinates with valuations 0,1. Thus 256 possible source states
map onto 8 observable states.

`GeneratedProfile.lean` contains the actual tables and checked theorems
`all_words`, `exact_quotient` and `every_competitor_contains_target`. The last
constructs an injection of Fin 8 into every alternative all-word encoding's state
space. No fixed bound on word length replaces the universal quantifier.

Boundary: the exporter and JSON-to-table transcription are not verified programs.
The theorem concerns the actual explicit tables in the generated source. The
matrix/finite-table agreement is checked separately in the executable audit.
The exporter is capped at 256 source states and 32 target states. It is not how
the large symbolic instances are checked.

## 6. Large symbolic test, without state enumeration

A synthetic eight-coordinate source over Z/65536Z has 2^128 possible initial states.
Its operations and observation were conjugated by an invertible matrix not supplied
to the discoverer. The returned exact observation encoding has two rows, Smith
valuations (0,2), and therefore 2^30 possible observable states.

Only two independent tests were accepted and five queued candidates examined.
The independent certificate checks all source states and every input word through
the finite matrix identities, without enumerating either huge state set. This
is an all-state/all-word instance supported by the WRITTEN matrix-certificate
reduction, not a new Lean verification of that large source.

The example is deliberately synthetic and structurally constructed. It is a
mechanistic test of coordinate discovery, not an independently held-out discovery,
proof of speedup over competing methods, or invention of a new arithmetic theorem.

## 7. Why lowering precision does not commute with naive normalization

Consider x in Z/4Z, identity dynamics and observation 2x mod 4. The exact quotient
has two elements and one nonzero cyclic direction. Reduce the ORIGINAL system
modulo two: its observation becomes zero, so all states become indistinguishable.
The correct quotient now has one element.

Naively reducing the normalized two-element quotient as though its generator were
an ordinary free scalar would retain a distinction the lower profile cannot see.
The finite source/target statements are checked in `ConcreteExamples.lean`.

The general algebraic explanation is the exact sequence

    0 -> (M intersect pV)/pM -> M/pM -> (M+pV)/pV -> 0,

for a submodule M<=V. The last arrow sends a class of m to its ambient reduction.
Its kernel is exactly the middle intersection quotient. Surjectivity and the
kernel description prove exactness. For M=2(Z/4Z) in V=Z/4Z, the first term is all
of M and the last is zero. This sequence is a WRITTEN standard module argument,
not a new Lean module-exactness theorem in this branch.

The architecture must bind coefficients and precision into each contract. Updating
a hash alone is insufficient: the altered source's local equations must still pass.
The negative tests include both stale hashes and a falsely rebound source hash.

## 8. What this says about a machine-native calculus

The accepted artifact is not only a proposed answer. It has:

* a declared source semantic profile;
* a discovered representation with witnessed observable tests;
* a reason each newly introduced test was necessary;
* an exact bridge preserving every declared future operation and output;
* a stopping certificate establishing completeness;
* an explicit boundary between a symbolic checker and a kernel-checked instance.

A learned proposer could replace the deterministic search policy without changing
what the certificates authorize. The present release has no trained proposer.
A kernel can reject false candidate bridges, but cannot decide whether the input
matrices were a faithful encoding of the original human problem without a separate
semantic-translation theorem.

The finite-state and finite-linear strata are now concrete. Multi-input operations,
approximate semantics, stochastic probability preservation, global arithmetic
bridges, and universal representation invention have not been reduced to them.

## 9. Exact next obligation

Formalize the universal finite-ring MATRIX certificate adapter: from witnessed
row provenance, P A=C P and O=D P, construct the generic transport, prove the
exact behavioral quotient, and connect the explicit Smith image to the sharp
linear minimum. This would allow large symbolic certificates to produce Lean
all-state/all-word theorems without the finite-table exporter.

Then evaluate representation proposals on independently frozen, structurally
held-out inputs with matched model/prover/tool budgets. The current tests do not
establish empirical superiority or cross-domain generality.
