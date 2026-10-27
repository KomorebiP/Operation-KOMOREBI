# Proof boundary

## Kernel-checked universal statements

The compiled source proves:

1. low-digit base-`p` digit-sum decomposition;
2. top and complementary barrier decompositions;
3. prime-base Kummer radix descent;
4. symmetry between diagonal and low binomial indices;
5. constancy of carry cost on each radix block;
6. exact maximal representative for every nonempty block;
7. representative cost minimality inside each block;
8. equivalence between barrier crossing and a bounded representative scan;
9. equivalence between barrier crossing and a finite exact minimum;
10. correctness of the executable Boolean compiler.

## Finite computation evidence

The Python audit checks the implementation on explicit bounded ranges using
exact integers and independent formulas. It is evidence about the executable
path, not a substitute for the universal Lean proof.

## Still open in Lean

- suffix-window early termination and its executable scan
- exact stable Lean 4.34.0 rebuild
- final quotient search as a complete end-to-end executable returning
  `M_{p,r,h}` from `(p,r,h)`
- proof-level integration of the final-fiber maximization
- broader Paper IX obstruction-packet conjecture
- literature novelty and priority

## Inherited narrow obstruction statement

The Block 02 obstruction concerns persistence of one specific one-layer Cartier
normal form. It does not rule out every possible lift of the rational-mask
formal series.
