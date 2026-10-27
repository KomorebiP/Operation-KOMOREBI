# Block 38 proof guide — binary measure and cube volume

## One dimension

1. Encode each finite prefix by `prefixCodeEquiv n : BitPrefix n ≃ Fin (2^n)`.
2. Prove the prefix grid index is uniform.
3. Identify the finite binary partial sum with `gridIndex/2^n`.
4. Bound the infinite tail by `2^{-n}`.
5. Sandwich the CDF between adjacent dyadic fractions.
6. Let `n→∞` to obtain `binaryCDF x=x`.
7. Use `Measure.ext_of_Iic` to identify the pushforward with interval volume.

## Three dimensions

1. Rewrite the uniform three-bit measure as a product of fair-bit measures.
2. Uncurry time-major arrays, swap `(time,axis)` to `(axis,time)`, and curry again.
3. Apply the one-dimensional measure-preserving map coordinatewise using `measurePreserving_pi`.
4. Compose with the Block 37 octree/bit equivalence.

## Hilbert layer

Apply `Lp.compMeasurePreservingₗᵢ` to obtain the norm-preserving pullback.
