# Gate/cell cost contract — v0.10

## Meaning and exclusions

This is a stipulated scalar-bit computation model. It is neither the v0.9 scalar
unit model nor a measured CPU runtime. Bits are LSB-first Boolean lists. Costs are
natural counters, excluded from their own accounting. Inputs are already encoded.
Native integer/bit-word conversion, allocating/traversing Lean or Python lists,
length/index arithmetic, queue/word management, exception handling, serialization,
input parsing, proof terms and native big-integer internals are NOT priced.

The model prices the indicated circuit cells with specified padding and local
control work. It does not prove that native compiler evaluation follows that exact
sharing strategy. Recursive tail results are explicitly let-bound in the metered
definitions, but an execution-model refinement is still required.

## Exact recurrence conventions

* Full adder: 2 XOR + 2 AND + 1 OR, 3 input reads and 2 outputs = 10 units.
  A final carry cell costs 1; shorter inputs are logically zero padded.
* Full subtractor: 2 XOR + 2 NOT + 2 AND + 1 OR, 3 reads and 2 outputs = 12 units.
  Terminal borrow output costs 1. Only equal-width semantics is used by clients.
* Multiplication: empty input costs 1; each processed multiplier bit costs 2
  for control/shift plus the actual recursive adder cost when that bit is one.
  The shifted tail is shared as an immutable list, not copied under this model.
* Division: empty input costs 1; a stage at width W copies two W-cell paddings,
  runs the subtractor, and charges 3 local control/output units. Total stage
  charge is 14W+4, in addition to its recursive tail computation.
* Zero test: a full scan, 4 units per stored bit plus terminal 1. Leading zeros
  are not ignored for cost. This also guards the safe division interface.
* Signed difference: two padding copies, subtract, branch and a second subtraction
  only if the magnitudes occur in the opposite order. Signed addition adds 2
  sign-selection units. Signed multiplication adds one XOR. Subtraction adds a
  sign negation to the signed addition cost.
* Signed division: first guard the divisor; perform unsigned division and a sign
  branch. A negative input scans the remainder. In the inexact branch it really
  increments the quotient and subtracts the remainder from the positive divisor.
* Modular multiplication/addition: actually compute the full product/sum and pay
  for its entire restoring-division reduction. No constant-cost remainder oracle.

## Formal bounds

For maximum encoded operand width B:

    ordinary multiply/divide <= 32(B+1)^2
    signed add/multiply/safe positive-divide <= 64(B+1)^2
    signed subtraction and modular add/multiply <= 256(B+1)^2.

Actual output words may contain redundant high zeros. Multiplication storage is
bounded by 2*n+w; division remainder storage is bounded by n+w. The modular bound
uses the wider intermediate, not a fictitious B-bit product.

`evaluateTrace_budget` prices an explicitly supplied UNSIGNED Request trace with
at most A events and maximum operand width B by 256*A*(B+1)^2. It does not assert
that every discovery execution has already been translated into that trace.
Positive-divisor validity is needed for the semantic theorem, not manufactured by
the cost theorem. The separate signed primitive budgets are also universal.

## Python whole-workload instrumentation

The port's `BitMeter` routes arithmetic values through the bit routines. The old
295,173 scalar-event count is retained as a different counter. It additionally
charges extraction/Option interfaces by an explicit copy-width convention, and
records conversion input/output volume. These adapter prices and conversions have
not been assembled into a universal Lean implementation-cost theorem.

The measured gate/cell total is 270,165,476 for 203 fixtures. It is not seconds,
CPU instructions, proof cost, a hardware benchmark, or a lower bound on any other
implementation. Comparing it numerically with scalar units is not a speedup test.
The persistent bit-vector lowering needed to eliminate re-encoding remains open.

## Next required implication

Construct an explicit source instruction trace or persistent bit-state evaluator,
prove its erasure equals the v0.9 discovery evaluator, and prove operand-width and
trace-length bounds for THAT execution. Account for conversion and data-management
work with a stated memory model. Only then combine scalar backend costs with the
proved source budget to make a full implementation-level bit-cost claim.
