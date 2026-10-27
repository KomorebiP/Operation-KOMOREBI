# Block 06 progress record

## Scope

Block 06 develops the integral and prime-power layer of the fixed-radix regular theory. The input is an integer-valued sequence whose radix-section span is already finite dimensional over `Q`. The block does not assume that the actual integral sections form a saturated lattice.

## Closed in this block

1. The actual sections generate a canonical raw lattice `M_k(a)`.
2. The integer-valued part of the rational section space is a canonical maximal saturation `L_k(a)`.
3. Both lattices are finite free of rank equal to the rational regular rank, and `M_k(a)` has finite index in `L_k(a)`.
4. The finite quotient `C_k(a)=L_k(a)/M_k(a)` is the exact integral saturation defect.
5. Smith invariants and Fitting ideals provide canonical coordinates for that defect.
6. Tensoring with `Z/mZ` gives a digit-equivariant five-term exact sequence.
7. The ghost kernel is `C_k(a)[m]`, the missing quotient is `C_k(a)/mC_k(a)`, and the semantic image cardinality is explicit.
8. At modulus `p^r`, the semantic module has explicit cardinality and minimal generator number.
9. The semantic section orbit is the unique minimal LSD-first prime-power output automaton.
10. Raw and semantic reduction maps form compatible surjective towers.
11. Their inverse limits recover the embedded `p`-adic raw lattice.
12. Finite ghost coordinates vanish in the inverse limit, while the missing quotient survives as the `p`-primary saturation defect.
13. Raw section-orbit towers descend exactly to the `p`-adic orbit closure.
14. `p`-adic, profinite, ordinary integral, and actual-section effectivity are separated by explicit obstruction quotients.
15. The digit-sum sequence supplies strict examples at every effectivity level.
16. Profinite completion gives a local-global exact sequence with quotient `C_k(a)`.

## Exact computation

The Block 06 verifier records:

- 1,984 Smith divisibility chains of ranks one through four
- 45,632 chain-modulus cases for moduli 2 through 24
- 8,840 Fitting cases
- 39,680 prime-power profile cases over `p = 2,3,5,7`
- 320 exact digit-equivariant Smith-square systems
- digit-sum and doubled digit-sum state formulas over four primes
- 1,681 bounded ghost-contraction samples
- 697,958 exact checks total
- 0 failures

The cumulative Block 03-06 record is 838,209 exact checks with no failures.

## Deferred boundary

Block 06 does not provide:

- recognition of finite rational section rank from a finite prefix
- a minimal realization theorem over arbitrary coefficient rings
- semiring minimization
- a base-independent integral normal form
- cross-radix comparison
- an unrestricted semantic-orbit inverse-limit theorem without a raw-lift condition
- identification of the prime-power regular tower with Newton-Mahler analytic interpolation

## Final manuscript state

The final manuscript contains 114 letter-size pages and 100 outline entries. The clean source-package replay passed all four verifier suites, rebuilt the PDF without warnings, verified all 114 manifest entries, and produced 114 of 114 pixel-identical rendered pages. Full details are recorded in `VALIDATION_Block06.md`.
