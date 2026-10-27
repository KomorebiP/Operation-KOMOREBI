# Bounded temporary arithmetic for exact observation discovery

Author: Komorebi P.

## v0.8 — lineage and achieved scope

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.7.zip`,
SHA-256 `31a72f98d0ea22df07a90d09b8fbc5db66b8552cd7afcf5a14718219e317866c`.
It is retained verbatim under `history/`. All 645 inherited Lean sources and 42
Python sources are unchanged. Only 25 inherited Lean dependencies are cold rebuilt
here, not every historical generated suite. This advances Model-Theory
Normalization, not the p-adic or Representation Calculus release numbers.

v0.7 bounded the PERSISTENT canonical basis but explicitly did not bound its
insertion/reduction temporaries. This block proves a bounded-coefficient Euclidean
implementation, substitutes it into the exact integer insertion, and proves
explicit coefficient-arithmetic peak bounds through the entire FIFO discovery.
It also proves a logarithmic Euclidean recursion-depth bound.

These are verified algorithmic and arithmetic theorems. They are NOT a formal
runtime model of Lean, a proof of every intermediate allocation inside a machine
integer primitive, or a wall-time performance guarantee. A separately stated
written schoolbook-arithmetic cost analysis appears in COST_MODEL.md. Historical
novelty and external referee review are not claimed.

## 1. The unchanged mathematical problem

Let m>0, including m=1, and let g_i be rows over Z/m. The integer cache represents

    L = m Z^d + span_Z {canonical integer lifts of the accepted rows}.

The predecessor proves that L is the full preimage of the modular row module.
Its reduced upper-triangular basis B has positive pivots, each dividing m, and
all entries in [0,m]. Off-diagonal entries use the pivot in their COLUMN as their
reduction modulus. Coupled constraints and torsion are retained.

For a prime p and m=p^r, the discovery source has all states of (Z/m)^d,
k permitted linear operations and o linear observation rows. Right multiplication
of an observation row PREPENDS a digit to its operation word. The FIFO queue
accepts a new row only when it lies outside the accepted span, and enqueues its
successors only upon acceptance. At an empty queue the returned tests span every
future observation. This is not a single-seed orbit problem.

## 2. Executable bounded Bezout coefficients [Lean]

The new natural-input Euclidean coefficient routine is

    E(a,0)=(1,0),
    E(a,b)=(t,s-floor(a/b)t),  (s,t)=E(b,a mod b), b>0.

Lean proves, for every natural a,b,

    a*s+b*t=gcd(a,b),
    |s|<=max(1,b),  |t|<=max(1,a).

Signed integer candidates are handled by applying E to absolute values and
adjusting the second coefficient's sign. For an actual positive pivot q and
signed candidate head a, the resulting s,t satisfy sq+ta=gcd(q,a).

The auxiliary `euclidPeak` follows this SAME recursion. It includes input values,
quotients, individual products and subtraction results, not only returned
coefficients. If a,b<=M and M>=1, Lean proves euclidPeak(a,b)<=M.
The modulus/remainder result is no larger than the existing input bound. Primitive
integer division's internal machine representation is outside this model.

A separate counter `euclidSteps` counts nonterminal calls. The theorem

    b < 2^bits  ==>  euclidSteps(a,b) <= 2*bits

is proved by induction: after at most two divisions the second argument is below
the preceding power-of-two threshold. This covers zero arguments and zero bits.

Endpoints: `euclidCoeff_correct`, `euclidCoeff_bounds`, `smallBezout_correct`,
`euclidPeak_bound`, `euclidSteps_binary_bound`.

## 3. Exact insertion with the new coefficients [Lean]

At a leading pivot q and candidate head a, put

    g=gcd(q,a), Q=q/g, A=a/g, sq+ta=g.

Replace the current basis row b and candidate v by

    b'=s*b+t*v,
    v'=-A*b+Q*v.

The coefficient matrix has determinant sQ+tA=1 and the explicit integer inverse
has rows (Q,-t),(A,s). Both span inclusions are proved. Recursion on the tail gives

    lattice(boundedInsert B v) = lattice(B) + Z v.

The new normalized insertion and v0.7 normalized insertion are EQUAL AS BASIS DATA:

    boundedNormalizedInsert B v = normalizedInsert B v.

This uses the preceding canonicity theorem and equal lattices, not an assumption
that different extended-gcd routines return the same coefficients. Their raw
intermediates may differ; their canonical answers cannot.

Endpoints: `boundedInsert_correct`, `lattice_boundedInsert`,
`boundedNormalizedInsert_eq`.

## 4. Bounds on temporary coefficient arithmetic [Lean]

`Uniform m B` means every old positive pivot and absolute tail entry is at most m.
Let C>=m>=1 bound the absolute candidate coordinates.

At one insertion level the bounded Bezout estimates give

    |s|<=C, |t|<=m, |A|<=C, |Q|<=m.

Each of the four individual tail products has magnitude at most mC. Each resulting
sum has magnitude at most 2mC. Therefore, after d levels,

    raw basis entries and insertionPeak <= (2m)^d C.

The formal peak includes both products before addition, signed Bezout coefficients,
q,g,Q,A, each candidate vector, and the Euclidean routine's own peak. Thus cancellation
is not used to conceal a large multiplication operand or result.

For residue reduction through an m-bounded triangular basis, floor division by a
positive pivot q satisfies |a/q|<=|a|, including negative dividends. Subtracting a
multiple of a lower row increases a magnitude bound C by at most the factor m+1.
Consequently

    residuePeak(B,v) <= (m+1)^d C.

The triangular membership algorithm uses those same subtraction steps and stops
earlier when a pivot does not divide; `residuePeak` is a conservative trace for
that arithmetic. A separate theorem about instruction-by-instruction traces of
the compiled `coordinates` code is NOT supplied.

During bottom-up normalization the lower basis is ALREADY normalized and bounded
by m. This is crucial: reducing against the large raw tail would not justify the
same recurrence. For a raw C-bounded basis containing m Z^d,

    normalizationPeak(B) <= (m+1)^d C.

Starting with a reduced cache and a canonical residue lift (C=m), combine the
estimates to obtain

    updatePeak(B,v) <= K(m,d) := m * [2m(m+1)]^d.

Endpoints: `residuePeak_bound`, `boundedInsert_peak_bound`,
`normalizationPeak_bound`, `updatePeak_bound`.

## 5. The bound persists through the actual worklist [Lean]

`boundedRun` executes the same FIFO policy, using the new normalized insertion.
`runPeak` follows precisely its branch decisions and takes the maximum of the
membership/remainder and update traces along those decisions.

Because every completed insertion restores the canonical m-bounded cache, the
same K(m,d) applies at EVERY queue step. It is not repeatedly exponentiated with
the number of observations:

    StateCorrect B and Reduced B ==> runPeak <= K(m,d), for every fuel budget.

The initial cache has those properties. For the actual discovery invocation,

    discoveryPeak(p,r,d,A,O) <= K(p^r,d).

If m<=2^b, a further Lean theorem proves

    K(m,d) <= 2^[b+(2b+2)d].

Thus every tracked coefficient magnitude fits in at most b+(2b+2)d+1 binary digits.
An explicit sign representation can require one additional bit. For d>=1,m>=2
this is O(d log m), an elementary interpretation of the proved power bound.
It is not a bound on total memory, proof-term size, or all runtime objects.

`runPeak` does not include evaluating the source row from the original matrices,
queue indices, dimension constants, or transient data inside integer primitives.
Source row arithmetic uses residue operations and is separately accounted for in
the written cost model and instrumented Python audit. The Lean theorem's exact
meaning is the numeric inequality for the explicit arithmetic trace definitions.

Endpoints: `runPeak_bound`, `discoveryPeak_bound`, `coefficient_cap_power_two`,
`discoveryPeak_bit_budget`.

## 6. Semantics and the logical definition are unchanged [Lean]

The whole result, basis and ordered tests, agrees with the predecessor at every
fuel budget. The successful enough-fuel prime-power wrapper therefore agrees with
the verified reference implementation:

    boundedPrimeDiscover = normalizedPrimeDiscover = finitePrimeDiscover.

All earlier completeness, accepted-test and horizon bounds remain applicable:
at most rd accepted tests, returned word lengths below rd, enough fuel o+krd+1.
The output yields the same original-language guarded first-order formula defining
complete future observational equivalence. No predicate naming the answer is added.

Endpoints: `boundedRun_eq`, `boundedPrimeDiscover_eq_reference`,
`boundedPrimeDiscover_total_correct`, `boundedPrimeDiscover_defines_behavior`.

This does not minimize the raw test list, formula size, or runtime. Existing
minimum-linear-coordinate theorems remain distinct results. No unrestricted
first-order or relation-sensitive discovery theorem is added here.

## 7. Actual computation, not supplied traces

All 203 frozen systems are executed directly through the new Lean routine by
`decide +kernel`, followed by their all-word code theorem. The expected outputs
are propositions being tested, not inputs to discovery. No membership witness
list or exhaustive oracle is supplied.

The eight-coordinate system modulo 65536 has 2^128 admissible states and returns
two tests after five decisions. A one-coordinate system modulo 2^24 with descending
observations accepts 24 tests in 48 decisions. These are inherited synthetic
mechanism tests, not held-out theorem invention or evidence of empirical superiority.

A small checked example makes the distinction from v0.7 concrete. Starting from
4I in dimension two and inserting (3,3), the normalized basis is

    [[1,1],[0,4]],

but the actual updatePeak is 12. The persistent modulus bound four is therefore
false for the temporary trace. A negative control claiming otherwise is rejected.

## 8. Costs and remaining trust boundaries

COST_MODEL.md gives a separate written polynomial cost calculation for a dense
array implementation with ordinary schoolbook integer arithmetic. The Lean
formalization proves temporary coefficient bounds and Euclidean call counts,
not a costed big-integer machine semantics or compiler-correct performance theorem.

`bounded_echelon.py` is a separately tested port, not verified extraction. Its
instrumentation measures coefficient arithmetic and records modular row computation
separately. The parser/exporter is also not proved correct. Literal inputs and
expected outputs are independently compared with the Lean batch files.

The final cold audit and independent finite checks are recorded in RESULTS.md.
All proof interpretation is self-review. No historical-priority verdict is made.
