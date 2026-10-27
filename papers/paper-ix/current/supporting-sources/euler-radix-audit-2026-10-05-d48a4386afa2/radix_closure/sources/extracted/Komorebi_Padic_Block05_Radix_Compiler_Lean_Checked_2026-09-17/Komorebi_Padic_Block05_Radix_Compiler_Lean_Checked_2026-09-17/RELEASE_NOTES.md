# Release notes: Block 05

## Added

- kernel-checked prime-base Kummer radix descent
- checked diagonal-index binomial symmetry
- exact radix quotient intervals
- exact maximal representative `min(Q,p(a+1))`
- checked representative cost-minimality theorem
- bounded radix-index compiler criterion
- finite representative-cost set and exact minimum
- executable Boolean `radixCompilerCrosses`
- kernel proof of Boolean compiler correctness
- 72 independent concrete Lean checks
- 1,562,433-check exact Python audit
- complete axiom, placeholder, and negative-control evidence

## Changed

Block 05 is checked under Lean 4.34.0-rc2 and its matching pinned mathlib,
rather than merely supplying uncompiled source.

## Not yet added

The suffix-window early-stop theorem remains in Python/prose and is the next
formal target.
