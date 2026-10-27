# Komorebi p-adic compiler — Block 12

This directory is the authoritative focused release for Block 12.

Block 12 eliminates the auxiliary quotient-bound variables from the displayed
compiler complexity envelope.  The key identity is exact in Lean's totalized
natural-number arithmetic:

```text
lastRadixBlockQuotient p (quotientSearchBound p r h)
  = coarseK r h / (p * (p - 1)).
```

Consequently the Block 11 envelope is exactly equal to a direct `(p,r,h)`
expression.  A monotonicity theorem also gives an `h`-free bound by replacing
`coarseK r h` with `r - 1`.

Read `PROOF_BOUNDARY.md`, `BLOCK12_THEOREM_INDEX.md`, and `CONTINUE_HERE.md`
before extending the project.
