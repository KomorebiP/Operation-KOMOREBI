# Block 05 progress record

## Scope

Block 05 expands the verified automatic and regular layer while remaining fixed-radix and field-valued. It removes the scalar rational-mask restriction from Block 04 and uses the full radix-section module as the common semantic object.

## Closed in this block

1. A field-valued sequence is fixed-radix regular exactly when the span of its radix sections is finite dimensional.
2. The canonical section module is reachable and observable.
3. Its dimension equals the rank of the fixed-radix word-Hankel matrix and the minimal dimension of any digit-linear realization.
4. Minimal reachable-observable realizations are unique up to the unique pointed output-preserving similarity.
5. A deterministic shortlex greedy basis of kernel states yields a literal coordinate normal form.
6. Semantic, canonical section-module, minimal digit-linear, strict shortlex, and word-Hankel charts form an effective normalized atlas with contractible fibers.
7. Automaticity is exactly finiteness of the section orbit inside the canonical module.
8. On the finite-orbit locus, the orbit automaton is reachable, behaviorally reduced, and the unique minimal DFAO.
9. Over a finite field `F_q`, every fixed-radix regular sequence is automatic and satisfies `r <= kappa <= q^r`.
10. Over characteristic zero, polynomial sequences have rank `m+1` and digit sum has rank two, while their kernel orbits are infinite.

## Exact computation

The verifier enumerates bounded deterministic automata in three regimes:

- base 2 over `F_2`, through three raw states
- base 2 over `F_3`, through three raw states
- base 3 over `F_2`, through two raw states

It records:

- 25,986 raw automata
- 417 distinct minimized automata
- 83 minimized automata with strict state-to-rank compression
- 86,207 automatic-to-linear checks
- 2,438 exact polynomial and digit-sum checks
- 89,055 checks total
- 0 failures

The cumulative Block 03-05 record is 140,251 exact checks with no failures.

## Deferred boundary

Block 05 does not identify one canonical object over arbitrary rings or semirings. Integral saturation, Smith/Fitting data, prime-power reduction towers, local completion, all-moduli compatibility, and all-radix comparison remain later blocks.

## Final manuscript state

- manuscript growth: 93 to 103 pages
- PDF outline entries: 92
- clean LaTeX warnings in the final log: none
- source-package manifest before replay: 102 files
- clean replay: PASS
- rendered replay comparison: 103 of 103 pages pixel-identical at 96 dpi
