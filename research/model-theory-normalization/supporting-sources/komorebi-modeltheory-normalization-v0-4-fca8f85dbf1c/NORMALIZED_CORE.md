# Verified discovery of complete observational codes

Author: Komorebi P.

## Model-Theory Normalization v0.4 — actual target and lineage

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.3.zip`,
SHA-256 `e694d635ad8582b5f13b415825ee58821bec2c6e37854d7b8e6969903902c42d`.
It is preserved verbatim in `history/`. All 222 inherited library sources are
byte-identical. This block cold rebuilds only the 12 inherited dependencies of
its new proof, not the previous complete 222-module instance suite or the p-adic
corpus. The Representation Calculus and Logical Resolution parallel release
numbers are not advanced by this block.

The previous release certified finished matrix encodings. Its stopping loop and
its discovery-to-complete-test-list implication were outside executable Lean
coverage. This block supplies a total executable reference loop, a proved exact
membership implementation, and a universal theorem connecting its output to the
existing standard first-order defining formula. It separately lets a fast,
untrusted producer certify its actual branch-by-branch queue execution.

This is a specific finite-linear discovery theorem, not a universal mathematical
invention algorithm. The optimized Python Smith engine, parser and exporter are
not verified executable programs. The resulting test list is not asserted to
minimize number of tests, word horizon, logical formula size or linear coordinates.

## 1. The precise source and task

Fix a prime p, natural precision r and dimension d, k total linear operations,
and o linear observations. Write R = Z/(p^r), including r=0 (the trivial ring).
The source space is R^d. Every source state is admissible. Operations are column
matrices A_a and observations are rows O_j.

A word is read left to right. For w=[a,b], its observation row is O_j A_b A_a.
Thus extending a ROW on the right by A_a PREPENDS a to the recorded input word.
This convention is proved in `testValue_behavior`, not inferred from comments.

Define the full observable row module

    M = span_R { O_j A_w : every finite word w and observation j }.

For a finite list of genuine word/observation tests L let M(L) be their row span.
The desired successful output is a list L with M(L)=M. From that equality,

    all tests in L agree on x,y  iff  every future observation agrees on x,y.

The standard logical fragment and its state/value guards remain inherited from
v0.3. It is not unrestricted first-order truth with state equality.

## 2. The executable FIFO worklist

The loop maintains an accepted list L and a pending FIFO list Q. Initially L=[]
and Q contains every empty-word observation once in declared observation order.
At each iteration pop candidate t:

* if its row is in M(L), skip it;
* otherwise append t to L and append all k successor tests to the tail of Q.

A successful return occurs only when Q is empty. Exhausted fuel returns `none`,
even if that call also has an empty queue; the resource formula reserves one
extra call for the terminal check. Thus fuel exhaustion is not a successful
empty output and not proof of impossibility.

`SpanOracle` packages a Boolean test together with a proof that it is equivalent
to membership in the actual module M(L). Generic correctness and termination
are proved for every such exact oracle. This is not an assumed Smith solver.

A second definition `enumerationOracle` is an actual verified executable backend:

    v in M(L) iff exists c : Fin(length L) -> R,
                     sum_i c_i * testValue(L_i) = v.

R is finite, so the right side is decidable by enumerating scalar coefficient
tuples. Mathlib's finite linear-combination characterization proves correctness.
This backend does NOT enumerate source states, but its worst-case search includes
p^(r * length L) tuples and is intentionally impractical at high precision.

`finitePrimeDiscover` uses this concrete oracle. The rank used to prove its
termination is NOT computed by the executable program.

## 3. The queue invariant proves exactness at a successful stop

The invariant `Frontier` says:

1. every root observation is in M(L) or its test is still pending;
2. every one-step successor of every accepted test is in M(L) or still pending.

A skip removes only a test already accounted for by the span. An acceptance
extends the span and queues every required successor. Both updates preserve the
invariant. When Q becomes empty, all observations are spanned and the span is
closed under every row action. Linearity extends closure from generators to the
whole span, so induction on words puts every future observation in M(L).

Conversely every accepted entry is an actual word/observation test. No invented
row is inserted. Therefore M(L) is contained in M from the start. Together the
two inclusions give exact equality, not merely an invariant overapproximation.

Formal endpoints: `frontier_skip`, `frontier_accept`, `empty_frontier_closed`,
`empty_frontier_exact`, `worklist_exact`.

## 4. Universal termination and horizon bounds

Every submodule U of R^d has cardinality p^s for some s <= r*d. Lagrange's
subgroup-cardinality divisibility and the prime-power divisor characterization
prove this. Define the proof-only rank

    rank(U) = log_p |U|.

Strict submodule inclusion strictly increases this natural rank. Every accepted
candidate therefore increases rank by at least one. There can be at most r*d
accepted tests, including those of nonzero torsion. Field rank is not substituted.

A queue potential is

    length(Q) + k * (r*d - rank(M(L))).

It decreases after either update. A skip removes one pending element. An accept
removes one, adds k, and raises rank, compensating for those k additions. The
initial potential is o + k*r*d. Therefore

    fuel = o + k*r*d + 1

suffices for successful termination. It is a bound on queue iterations, NOT a
bound of that order on ring operations or bit complexity of the membership oracle.

An additional invariant shows every accepted word is shorter than the eventual
accepted-list length. Thus, when r*d>0, every returned test has word length <r*d.
For r*d=0 the returned list is empty. Empty actions, empty observations and d=0
are all covered by the universal statements.

The fully assembled theorem is:

    for every p prime, r,d,k,o and actual matrices A,O,
    finitePrimeDiscover p r d (rowRight A) O = some L for some L,
    span(L)=M, length(L)<=r*d, and every listed word has length<r*d.

Endpoints: `primeRank_strictMono`, `worklist_terminates`, `worklist_size`,
`worklist_horizon`, `prime_discover_total_exact`,
`finitePrimeDiscover_total_correct`.

## 5. Discovery itself now produces a standard defining formula

The row action is an actual Mathlib linear map. It agrees with the inherited
recursive matrix arithmetic, as proved by finite-sum identities. The semantics
lemma identifies dot(testValue(t),x) with the actual observation after word t.

Equality of the discovered tests propagates to all rows in M by linearity.
This constructs the inherited `FiniteCodeCertificate` (local observation equality
and operation stability), rather than requiring such a certificate as an input.
The standard compiler then constructs

    E_L(x,y) = State(x) and State(y) and
               AND_(w,j in L) [o_j(T_w x)=o_j(T_w y)].

Lean proves its actual Mathlib `IsQF` predicate and its satisfaction iff complete
behavioral equivalence on state-tagged pairs. A separate endpoint supplies the
actual `Set.Definable` result over the empty parameter set of the declared language.
That language already names the observation values. No predicate for the answer
or encoding matrix is added.

`prime_discovery_defines_behavior` assembles the concrete executable call, its
termination, length/horizon bounds, local certificate and standard formula semantics.
There is no completed matrix certificate or all-word equality hypothesis in its
input. This is not quantifier elimination or theory-wide elimination of imaginaries.

## 6. Fast search can certify its actual decisions

The reference oracle is slow. To use the existing fast Smith proposer without
trusting its implementation, `QueueTrace` certifies every popped candidate:

* a skip carries a coefficient tuple expressing that row in the preceding raw rows;
* an acceptance carries a linear functional vanishing on all previous rows but
  nonzero on the proposed row.

For matrix rows, the functional is dot product with an explicit state difference
delta. These are genuine distinguishing states for the accumulated observation
family, not merely a Smith engine's membership flag.

The inductive trace constructors enforce exact FIFO evolution and terminate
only in an empty pending list. Lean proves trace exactness and the same standard
first-order definition. It also proves that ANY two globally correct membership
oracles give the same literal returned list, with the same ordering. Finally,
`prime_trace_matches_reference` proves that a fully certified trace has exactly
the result of `finitePrimeDiscover`, without running its coefficient enumeration
on that instance. Extra fuel cannot change a successful output.

The fast producer is new Python code using the unchanged old Smith backend.
The independent trace checker imports neither that producer nor the Smith engine.
It rebuilds the FIFO queue, evaluates genuine tests, checks every witness directly,
and refuses an incomplete queue, missing/trailing events, wrong source or wrong word.
The separately supplied expected source is binding; the certificate cannot choose
its own mathematical task merely by supplying a hash.

Four complete traces are emitted as literal Lean files and kernel-checked:

* the inherited synthetic eight-coordinate source modulo 65536 (2^128 source states),
  with two accepted tests, three skips, and final horizon one;
* the eight-coordinate delay chain, requiring horizon seven;
* the hidden mod-four torsion example;
* the precision-one zero-output example with no accepted tests.

For the large source the generic bound is 128 accepted tests and 257 candidates,
with 258 fuel calls sufficient. Its actual certified trace has only five decisions.
The large reference algorithm is NOT evaluated exhaustively. Its output is proved
by the trace/reference theorem. Both state sets and coefficient tuples remain
symbolic in this proof; only finite matrix coordinates/witnesses are reduced.

## 7. Executed reference examples and audit boundary

The actual enumerative Lean program is also evaluated and its exact result proved
by kernel reduction on small fixtures: shear modulo four, two order-two torsion
rows, delay modulo two, ternary shear, no actions, no observations, d=0, r=0, and
insufficient fuel. Ordinary kernel `decide +kernel` is used, not `native_decide`.

All 202 frozen sources have newly regenerated complete Python traces: 643 justified
acceptances and 945 justified skips. Their final raw test lists are identical to
those retained in the predecessor certificates. Only four traces receive literal
instance proofs in this new Lean run; the universal trace verifier itself is formal.
The independent coefficient-enumeration reference exhausts all 64 dimension-two
binary one-action/one-observation systems and all 29 scalar systems at moduli 2,3,4.
These 93 finite cases audit implementation conventions, not universal termination.

The complete cold audit covers 23 local modules (12 inherited and 11 new), not
all 222 old generated case modules. The frozen parent Python audit is separately
replayed. Exact outcomes and non-successful attempts are recorded in RESULTS.md,
DEVELOPMENT_FAILURES.md, and version-2 evidence manifests.

## 8. Remaining work

The selected discovery-loop invariant, completeness, termination and source-to-
logical-definition theorem are closed at the exact formal endpoints stated above.
The efficient Smith membership algorithm is not itself verified. Its particular
accepted traces can now be validated in Lean, but not every Python run has such an
export. Efficient verified extraction, schema/parser correctness, learned search,
structurally held-out benchmarks, relational/multi-input discovery and general
logical-cost optimization remain separate work. No new minimum linear-coordinate
theorem is claimed here: the output is a sufficient raw test list and existing
minimal-encoding certificates remain a separate verified path.

The new abstract ingredients are standard finite algebra, invariant reasoning and
finite linear combinations. This release is an integration/formalization result,
not a historical-priority or independent-referee verdict.
