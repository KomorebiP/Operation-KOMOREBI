# Exact cost-model contract — v0.9

## Meaning of one unit

The formal evaluator counts the following high-level arithmetic primitives:
integer addition, subtraction, multiplication, Euclidean division, remainder,
absolute value, negation and declared zero/sign comparisons; residue-ring addition
and multiplication; extraction of a residue coordinate to its integer lift; and
one test of the membership result's Option constructor per popped candidate.
Each costs ONE unit, independent of operand bit length.

The count is an instrumented arithmetic denotation under eager array sharing. The
formal value uses function-valued vectors; no theorem asserts that the actual Lean
kernel/native compiler executes each projection exactly once. This is not elapsed
time, CPU-instruction count, bit-operation count, memory allocation, or proof cost.
Scalar literal creation, list operations, queue/word copies, indices, parser/export,
modulus construction from p and r, and the metering counter's own overhead are not
included. Input matrices and the modulus are supplied data.

## Primitive recurrences (all formalized)

| Routine | Charged units |
|---|---|
| Natural extended Euclid | 5E+1 |
| Natural gcd, computed separately | 2E+1 |
| Signed extended Euclid | 5E+5 |
| Dot product, dimension d | 2d |
| Row-matrix product | 2d^2 |
| Actual word-row reconstruction, length h | 2d^2 h |
| Triangular membership | at most d^2+2d |
| Residue reduction | d(d+1) |
| Normalization | C(d), with 3C(d)+d=d^3 |
| Insertion | 3d^2+8d+7 sum E_i |
| Normalized insertion | insertion+C(d) |

The initial normalized diagonal cache costs C(d), even if no observations follow.
The initial diagonal is already normalized mathematically, but this evaluator calls
the inherited normalizer and charges its executed arithmetic. No dead-code
optimization is assumed. Membership failure may stop early but is not free.

## Composed bound (formal)

With m=p^r>0, m<=2^b, B=b+(2b+2)d+1, and F=o+k(rd)+1:

    cost <= d^3 + F(2d^2 F + d^3 + 4d^2 + 11d + 14Bd + 1).

The counter includes reconstructing each popped observation row from scratch. A
future verified row-value cache could lower that term but is not presumed here.
It charges every possible round as an acceptance, making the bound intentionally
coarse. The result holds for the modeled arithmetic, not all implementation work.

## Relation to v0.8

The old numeric temporary-size theorem now controls the actual Euclidean counts
used by the metered insertion, through E_i<=2B. Thus the cost proof has a checked
connection to those earlier operands rather than a new unproved bounded-gcd premise.
The value erasure theorem connects the metered algorithm to the original semantics.
This is stronger than reporting an isolated complexity expression in prose.

It is still weaker than a complete bit-level execution proof. Arithmetic units
could be priced by a suitable operand-sensitive backend, but the required cost
refinement, implementation of integer primitives, and non-arithmetic overhead have
not all been formalized. In particular, multiplying this entire count by a guessed
CPU or bit cost is not a proved runtime bound.

## Reproducible measurements

results/PYTHON_AUDIT.json contains per-primitive and per-phase counts for all 203
sources. Generated CostedComputed00--16 modules check the exact value/count pairs
in Lean. No source-state enumeration is part of the discovery computations.
The Python timings in audit receipts are test execution measurements, not a
comparison or prediction of the verified solver's performance.
