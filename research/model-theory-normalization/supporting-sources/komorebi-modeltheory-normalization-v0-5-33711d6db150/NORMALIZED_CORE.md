# Checked membership evidence and bounded-width observation discovery

Author: Komorebi P.

## v0.5: lineage and exact target

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.4.zip`,
SHA-256 `fca8f85dbf1cff576e4461fc8a1f68e9933770c65c95b8b747ba9338d967243b`.
The frozen ZIP is retained verbatim under `history/`. All inherited Lean sources
are preserved unchanged. This release advances the Model-Theory Normalization
branch, not the parallel Logical Resolution or p-adic release numbers.

v0.4 proved a reference discovery algorithm whose span-membership oracle enumerates
coefficient tuples. It also formalized a propositional QueueTrace and checked four
explicit traces, each with separately authored branch proofs. This release adds a
verified executable validator for untrusted witness DATA, a guarded oracle that
cannot return a wrong decision even when its proposer is wrong, and a small-width
Smith producer whose complete traces are independently checked. All 202 frozen
sources and one new stress source have emitted Lean data-replay applications.

Execution status and counts are in RESULTS.md and FORMALIZATION_COVERAGE.md. This
note is not itself an execution receipt. The proofs are self-reviewed, not externally
refereed. The ingredients are standard linear algebra, exact certificates and
simulation invariants; no historical novelty is asserted.

## 1. The unchanged task

For a prime p, precision r and dimension d, source states are all of
R^d, R=Z/(p^r). Column-action matrices A_a and observation rows O_j are supplied.
Words are read left to right. Right multiplication of an observation row by A_a
PREPENDS a to its recorded word. The target is the complete observable row module

    M = span_R { O_j A_w : every finite word w and observation j }.

The FIFO algorithm retains genuine tests, appends successors only when a new row
is outside the old span, and stops only when the pending queue is empty. Existing
Lean theorems prove that exact decisions give the complete span, at most r*d
accepted tests, horizon strictly below r*d, and sufficient fuel o+k*r*d+1.
These are iteration bounds, not bounds on the cost of membership decisions.

The resulting logical definition is the original guarded observation-test formula.
No predicate naming the answer is inserted. The fragment includes observation-value
equality, Boolean connectives and state quantification with the appropriate target
image/guard contracts. It is not unrestricted first-order elementarity.

## 2. Executable evidence checker [Lean]

For accepted tests L, let g_i be their actual observation rows and v the next row.
An `Evidence R d` is one of:

* `combination c`, with an untrusted LIST of scalar coefficients;
* `separation delta`, with a candidate state difference delta in R^d.

The checker returns `Option Bool` with three distinct meanings:

    some true  : span membership has been certified;
    some false : span nonmembership has been certified;
    none       : the supplied evidence is invalid.

A combination is accepted only when its length is exactly |L| and

    sum_i c_i * g_i = v.

A separator is accepted only when

    g_i dot delta = 0 for all i,       v dot delta != 0.

These are finite sums, products and equality tests. The checker performs no Smith
elimination, scalar inversion, source-state enumeration or enumeration of possible
coefficient tuples. It does reconstruct genuine test rows from the source; this
cost depends on their word lengths.

`checked_member` and `checked_nonmember` prove the meanings against actual Mathlib
submodule membership. The first uses the finite linear-combination characterization.
The second uses the linear functional u -> u dot delta: if v were in the span,
linearity would force its value to vanish. `checked_decision` combines them, and
`accepted_decisions_unique` proves that two valid witnesses cannot certify opposite
answers for the same source, list and row.

These soundness theorems hold over any decidable commutative ring. They DO NOT
assert that every nonmember over every ring has such a scalar separating witness.
The prime-power setting supplies the familiar Smith construction; universal
completeness of the untrusted Python implementation is not assumed.

### Torsion example

Over Z/4, the row 1 is outside the span of row 2. Delta=2 certifies this because
2*2=0 but 1*2=2 != 0. Conversely coefficients [2] fail to reconstruct row 1.
The accepted and rejected calculations are kernel-checked. Nonunit pivots are not
treated as invertible field elements.

## 3. Verified replay of a whole data trace [Lean]

`replay` recursively consumes the evidence list and reconstructs its own FIFO queue.
The data cannot substitute a different candidate row or omit a required successor.
A successful terminal state requires BOTH the evidence list and pending queue to
be empty. Too few events, trailing events, and invalid local evidence return none.

The proof `replay_sound` constructs the inherited `QueueTrace` by induction on the
actual evidence data. The existing queue invariant then gives:

    replaySource A O data = some L  ==>  span(L) = M.

Further endpoints prove:

    CodeEqual L x y  iff  complete future behavior agrees on x,y;
    the standard first-order formula generated from L defines that relation;
    finitePrimeDiscover p r d A O = some L.

The last identity is with the literal result of the verified enumerative reference,
including its ordering, not merely an isomorphic span. `replaySource_unique` proves
that independent accepted traces for the same prime-power source cannot disagree
on that result.

This advances the old propositional trace interface: a single kernel-reduced
check of an ordinary data list now supplies all branch proof obligations.

## 4. A universally safe guarded membership backend [Lean]

Let `propose` be ANY total function from an accepted test list and candidate row
to optional evidence. It is not required to satisfy a correctness hypothesis.

`guardedOracle` first validates the proposal. It uses a certified Boolean when
one is available. Missing or invalid evidence falls back to the proved finite
coefficient-enumeration oracle.

The result is a genuine `SpanOracle` whose correctness is constructed, not assumed.
The central theorem is

    guardedPrimeDiscover(..., propose) = finitePrimeDiscover(...)

for every such proposer. With p prime, the inherited termination and exactness
proofs supply successful return, the size/horizon bounds, and the original-language
first-order definition. The proposition quantifies over all source states and
all finite future words.

A concrete proposer that always supplies the zero separator is checked both by
the universal theorem and kernel computation. It still returns the correct list,
because its invalid advice is rejected and the reference is used.

This is NOT an unconditional speed theorem. A slow proposer or expensive fallback
can still make execution slow. An external process that hangs is not a total Lean
function completing a call. In operational use a resource cap is unresolved.
The fail-closed replay interface never falls back; it is the interface used by the
large exported instances.

## 5. Small-width Smith producer [implemented; certified runs]

The new Python producer keeps a minimal working family B while retaining exact
coefficients expressing B in ALL accepted raw tests G:

    B = C G.

When v is accepted, it diagonalizes only [B;v], not [G;v]. If the preceding basis
has t<=d rows, that Smith calculation has at most d+1 rows. From

    U [B;v] V = diagonal(p^s_i)

it extracts a new family from the rows p^s_i V_inverse[i] and updates its coefficient
matrix relative to the enlarged raw list. The new diagonal coordinate description
then answers membership queries; a positive answer is converted BACK to coefficients
in G, not emitted in an undocumented changing basis.

Every acceptance emits a separating delta and every skip emits raw reconstruction
coefficients. The independent predecessor checker verifies all witnesses and queue
evolution without importing the producer or Smith code. Thus a wrong internal
basis calculation cannot by itself make an invalid trace acceptable.

The producer and its Python program are NOT verified executables. The width
argument is a written algorithmic invariant, its explicit bound is checked in
every retained run, and the accepted traces have separate Lean certificates.

### Stress case

The source is one coordinate modulo 2^24 with identity dynamics and 24 observations
2^23 x, 2^22 x, ..., x, queued in that order. All 24 are accepted in turn, though
the final row module has one generator. There are 48 queue decisions.

The previous raw-row strategy reaches a 24-row Smith input. The new producer never
uses more than two rows, while its final witnesses still refer to all 24 raw tests.
This is a demonstrated reduction in matrix size, not a comparative wall-time claim.
It also shows why the accepted-test bound is not the minimum coordinate count.

## 6. Data export and model-theory endpoint

The exporter writes source matrices, an evidence list, a result list, and one theorem

    replaySource A O evidence = some result := by decide +kernel.

No per-event proof scripts are generated. Four consequences per case cover checked
replay, the exact reference output, all-word equivalence and standard defining-formula
semantics. Only finite matrix/witness arithmetic is reduced by the kernel; source
states and future words remain universally quantified.

The 202 inherited profiles plus the one-coordinate stress case are emitted in 17
batches. The large source still has 2^128 possible initial states, two accepted tests
and three skips. Its trace is checked without enumerating either source states or
coefficient tuples. These are synthetic mechanism/regression tests, not a held-out
mathematical-discovery benchmark.

The source specification is supplied separately to the independent checker. The
audit also reparses all emitted action, observation, modulus, evidence and returned-
list literals. Those are tests of transcription, not a formal proof of the Python
parser or fidelity to an informal human problem.

## 7. Audit and limitations

The cold Lean audit recompiles the selected 18 inherited dependencies and every
new generic, concrete and generated module. All named declarations are axiom-audited;
false assertions and sorry controls must reject. Upstream Mathlib is reused from
the pinned cache rather than rebuilt. The archive preserves the entire immediate
predecessor and all its proof-source bytes, but does not claim a fresh build of all
historical modules.

The finite Python audit checks all complete traces and literal exports, exhausts
membership on all generating lists of length 0,1,2 for five small ring/dimension
configurations, validates positive/negative witnesses and basis provenance, and
rejects malformed, truncated, trailing and misbound traces. Exhaustive ranges and
actual counts are recorded in RESULTS.md.

Still separate: formally verifying the efficient Smith producer itself, proving
an asymptotic bit-complexity bound for the implementation, minimizing raw test or
formula counts, multi-input/relational discovery, verified parser/extraction,
learned proposals, structural holdouts, and independent refereeing.

**Completed target:** a verified fast-witness checking path, universal protection
against bad total proposals, and systematic data-to-Lean certification of complete
optimized search runs. **Not claimed:** an unconditionally efficient verified Smith
solver or a universal mathematical invention algorithm.
