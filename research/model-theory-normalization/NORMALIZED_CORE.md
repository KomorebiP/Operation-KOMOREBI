# Binary scalar arithmetic for certified observation discovery

Author: Komorebi P.

## Model-Theory Normalization v0.10: scope and lineage

The sole immediate predecessor is `Komorebi_ModelTheory_Normalization_v0.9.zip`,
SHA-256 `1dec07bad4136a5809059b0e3a0f014700909210d6c9f823627742fee07bba78`.
The exact archive is preserved in `history/`. Its 1,395 manifest payloads were
checked, and the 207 selected baseline payloads are byte-identical. This release
adds a scalar-bit backend; it does not replace the inherited discoveries or claim
a new full build of their historical Lean modules. Other Komorebi branches are
not advanced by this version number.

The broad outstanding target is an end-to-end implementation-level bit-cost
proof. This block closes its scalar-arithmetic subproblem: explicit bit routines,
correctness, length-sensitive metering and quadratic declared cost bounds. The
whole discovery-to-bit-program lowering, conversion costs and data-management
semantics remain unclosed. Exact execution status belongs in RESULTS.md and the
version-2 manifests, not merely in this exposition. Review is self-review.

## 1. Concrete representations, including their boundary cases

`Word = List Bool` is little-endian. Its value is defined by

    value [] = 0
    value (b :: tail) = bit(b) + 2 * value(tail).

Leading zero padding is permitted. It does not change the value. A word of length
B has value strictly below 2^B. The representation is not asserted canonical:
addition retains a final carry even when it is false, and division retains zero
padding in remainders. All complexity bounds use actual storage lengths, not an
incorrect assumption that every output is trimmed.

`SignedWord` consists of a sign Boolean and an unsigned magnitude. Negative zero
is allowed and has integer value zero. `ofNat`/`ofInt` and the decoders have proved
semantic correctness. These are boundary conversions using native arithmetic;
their implementation cost is NOT priced in the scalar circuit model.

The native integers appearing in correctness statements specify mathematical
meaning. They are not an unverified oracle substituted for the computed bit word.

## 2. Addition and subtraction from bit cells [Lean]

A full-adder column uses two XORs, two ANDs, and one OR. Its checked truth-table
identity is

    sumBit + 2*carryOut = aBit + bBit + carryIn.

Recursive ripple carry gives exact addition, including an input carry, at any
finite width and with zero padding of shorter inputs. Output length is
max(input lengths)+1. A full-subtractor uses seven Boolean gates and satisfies

    differenceBit + bBit + borrowIn = aBit + 2*borrowOut.

For equal-width inputs of length N, the whole subtractor satisfies

    value(out) + value(b) + borrowIn
      = value(a) + 2^N * borrowOut.

The equal-width premise is explicit. It is supplied by padding before signed
subtraction and every division stage. A final borrow is false exactly when the
subtrahend is at most the minuend (with initial borrow false). Failure to respect
that premise is not assigned the same subtraction theorem.

## 3. Multiplication and restoring long division [Lean]

Multiplication recursively computes the tail product, shifts it, and conditionally
adds the other operand. The bit-word value is exactly the integer product. The
untrimmed output length is bounded by 2*n+w for operand lengths n,w. This bound is
looser than a canonical binary product width but matches the actual representation.

Long division processes the input from most significant to least significant bit
by recursing on its little-endian tail first. At each stage it forms twice the old
remainder plus the next bit, pads it and the divisor to a common width, and uses
ripple borrow to choose subtraction or retention. The invariant is

    processedInput = quotient * divisor + remainder,
    0 <= remainder < divisor.

The universal correctness theorem requires a positive divisor. Quotient length is
the dividend length; remainder storage length is at most the sum of input lengths.
The safe signed wrapper checks all divisor bits and rejects zero, including padded
zero. The lower-level raw unsigned routine is total as Lean code, but its quotient
specification is NOT asserted at divisor zero.

Signed division has the positive-divisor interface used by the lattice solver.
If a negative magnitude divides exactly, negate the quotient. Otherwise increment
its magnitude and replace the remainder r by D-r. Thus

    -7 = (-3)*3 + 2,

not the truncation-toward-zero result. Lean proves agreement with its actual Int
Euclidean division and remainder. Negative divisors are outside this interface.
Addition, subtraction and multiplication are similarly proved for signed words.

## 4. An explicit gate/cell model, not native runtime [Lean]

The metered evaluators recursively compute both the bit results and declared
costs. Their erased values are proved equal to the unmetered bit algorithms.
They are not calls to the old scalar solver with an arbitrary estimate appended.

The model stipulates ten units per full-adder column (five gates and five bit-cell
accesses), twelve per subtractor column (seven gates and five accesses), and the
explicit padding/branch charges in COST_MODEL.md. It excludes native list-allocation,
index arithmetic, conversion, proof checking and the meter's own work. It therefore
does NOT purport to be an instruction count or a full Turing-machine bit cost.

For input word lengths n,w:

    addition cost = 10*max(n,w)+1
    equal-width subtraction cost = 12*n+1
    multiplication cost <= 1+n*(10*(2*n+w)+3)
    division cost <= 1+n*(14*(n+w)+4).

With every input length at most B:

    unsigned multiplication or division <= 32*(B+1)^2
    signed addition, multiplication or safe positive division <= 64*(B+1)^2
    signed subtraction <= 256*(B+1)^2
    modular multiplication or modular addition <= 256*(B+1)^2.

For modular multiplication, the full product is actually produced and then divided.
The proof allows its padded storage length to be as large as 3B. It never assumes
that the wider intermediate product fits back into the input width before reduction.
The analogous addition proof includes the carry bit before reduction.

The explicit unsigned request-trace interpreter has the conditional theorem

    number of requests <= A, every request width <= B
      ==> modeled trace cost <= 256*A*(B+1)^2.

It separately proves agreement with the native mathematical specifications when
all required divisors are positive. The trace is an actual input to this theorem.
It does not manufacture a lowering of the discovery implementation, infer input
width from its output width, or turn the predecessor's operation counter into a
full bit-runtime theorem. Signed routines have their own checked cost theorems;
the current `Request` datatype itself is the unsigned stratum.

## 5. Actual application to the inherited discovery workloads [finite audit]

The new `BitMeter` is substituted for the scalar interface of the unchanged v0.9
Python port. Each arithmetic result is produced by explicit bit arithmetic, then
decoded at that interface. The FIFO control, source-row reconstruction, integer
basis code and observations are otherwise unchanged. All 203 separately supplied
source profiles are rerun; their asserted answers are not inputs to the algorithm.

Every ordered test list, canonical basis, per-opcode event count and total event
count matches the frozen original. This includes the eight-coordinate source
modulo 65536, with 2^128 admissible initial states, and the descending-torsion case
modulo 2^24. There is no source-state or coefficient-tuple enumeration in discovery.

The port's gate/cell counter is a different quantity from v0.9's scalar event count.
It includes explicit adapter charges for extraction and Option tests. Those
particular Python adapter charges do not have a universal whole-program Lean
cost refinement yet. Conversion volume is reported separately, not silently
represented as free implementation work. Integer values are re-encoded at each
port call; a persistent bit-vector implementation remains to be built and proved.

The 203 reruns are finite executable evidence. They are NOT 203 Lean executions of
a universally proved bit-backed discovery program. The 27 concrete Lean examples
in this release exercise the scalar backend directly; the generic scalar semantics
and cost proofs cover arbitrary finite operands.

## 6. What is closed and what remains

CLOSED: scalar binary addition/subtraction/multiplication, restoring division,
positive-divisor signed Euclidean adjustment, boundary conversion correctness,
actual scalar metering, explicit width bounds and declared quadratic cost budgets.
An explicit unsigned trace has a correctness and conditional cost theorem.

NOT CLOSED: whole-loop refinement to persistent bit-vector states, memory access
and sharing, conversion costs, queue and index work, certified parsing/export,
proof-checking cost, and an end-to-end native-runtime/bit-machine polynomial bound.
The same finite-linear observational task and its inherited logical limits remain.
No arbitrary-program lower bound, new discovery benchmark or novelty claim is made.

The mathematical methods are standard binary arithmetic and exact refinement.
Their value here is the checked integration contract, not an assertion that binary
addition, long division or their polynomial costs are newly invented.
