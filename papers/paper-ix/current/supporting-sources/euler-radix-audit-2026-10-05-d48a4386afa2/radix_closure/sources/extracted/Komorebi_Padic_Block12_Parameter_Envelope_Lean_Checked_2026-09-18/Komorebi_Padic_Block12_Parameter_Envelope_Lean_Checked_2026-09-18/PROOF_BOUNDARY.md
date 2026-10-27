# Proof boundary

## Kernel-checked universal statements

Lean proves:

1. `quotientSearchBound p r h - 1 = coarseK r h / (p - 1)` for all naturals.
2. The final radix-block quotient at the search bound equals
   `coarseK r h / (p * (p - 1))` for all naturals.
3. The proposed Block 12 inequality therefore holds with equality.
4. The Block 11 prime envelope equals the direct `(p,r,h)` parameter envelope.
5. The core envelope is monotone in its visible-order cap.
6. `coarseK r h ≤ r - 1`.
7. For prime `p` and positive `r`, the exact compiler total is bounded by both
   the direct parameter envelope and the `h`-free raw-precision envelope.

## Finite computation

The Python and `native_decide` lanes test totalized boundary cases, dense finite
grids, monotonicity, concrete compiler outputs, and large integer stress cases.
They audit implementation and boundary behavior; they are not the universal
proof.

## Not claimed

- The envelopes are not generally exact operation counts.
- No asymptotic optimality theorem is claimed.
- No external novelty claim is made.
- The stable Lean `4.34.0` / mathlib `5ed296...` compatibility lane has not
  been executed.
