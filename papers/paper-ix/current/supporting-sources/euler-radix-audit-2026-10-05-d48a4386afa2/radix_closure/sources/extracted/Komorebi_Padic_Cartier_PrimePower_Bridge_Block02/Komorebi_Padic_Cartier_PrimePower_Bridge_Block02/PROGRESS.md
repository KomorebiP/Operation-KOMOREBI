# Progress — Prime-Power Cartier Bridge Block 02

## Closed in this block

- Proved the Block 01 layer bound is minimal among contiguous all-branch bounds.
- Proved the exact correction-branch p-adic content formula.
- Derived the defect-valuation layer bound `L_{r,h}`.
- Implemented exact binomial/valuation pruning.
- Identified the binomial valuation exactly with a Kummer base-p carry count and wired that criterion into branch pruning.
- Implemented least layer-specific degree propagation.
- Implemented sparse transition matrices over `Z/p^r Z`.
- Implemented exact coefficient queries from base-p digits.
- Implemented reachable finite-state enumeration with a hard resource cap.
- Implemented Moore minimization for reachable output automata.
- Proved the exact necessary-and-sufficient criterion for preserving the literal one-layer Cartier form.
- Isolated the successive obstruction packet `O_s(B)`.

## Verification status

- Sparse compiler: 22,987 exact coefficient comparisons, zero failures.
- Obstruction criterion: 1,575 exact checks, zero failures.
- Branch valuation: 9,389 exact checks, zero failures.
- Kummer/carry graph: 28,320 valuation checks + 33,471 edge checks, zero failures.
- Reachable/minimized automata: 2,505 coefficient checks, zero failures.

## Important correction to interpretation

The Frobenius-defect packet is an obstruction to **preserving the compressed one-layer normal form**. It is not an obstruction to existence of the formal-series lift itself; the series lift exists uniquely because `B(0)` is a unit.

This makes the special-case obstruction theorem rigorous without overclaiming Paper IX Conjecture 13.2.
