# Block 05 computation contract

## Mathematical claim

The universal representative and finite-minimum compiler theorems are stated in
Lean. Their correctness is decided by kernel checking, not by the Python audit.

## Computational surrogate

`verification/verify_radix_compiler.py` checks, over declared finite ranges:

- base-`p` digit append identities;
- top and complementary digit decompositions;
- radix descent using factorial valuations;
- the same identity using Kummer carry counts;
- direct integer-binomial valuations on a smaller range;
- representative interval shape and descended carry;
- cost monotonicity within each block;
- equality of the original full minimum and compressed representative minimum;
- equality of crossing decisions around every observed threshold.

## Arithmetic domain

Python arbitrary-precision integers only. No floating point enters a
load-bearing calculation.

## Interpretation

- PASS means the implementations agree on the recorded finite domain.
- FAIL records an exact counterexample to at least one implemented assertion.
- TIMEOUT is inconclusive.
- A PASS is not a universal proof.
