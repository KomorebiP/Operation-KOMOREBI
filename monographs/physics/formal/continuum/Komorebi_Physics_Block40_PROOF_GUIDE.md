# Block 40 proof guide — concrete Euclidean dyadic boxes

## 1. Geometry of one prefix

1. Split each octree digit into its three Cartesian bits.
2. Encode the first `n` coordinate bits by an integer `k_i < 2^n`.
3. Define the closed coordinate interval
   `[`k_i/2^n`, (`k_i+1`)/2^n`]`.
4. Take the Cartesian product over `Fin 3`.
5. Prove each side has length `2⁻ⁿ` and the product measure is `8⁻ⁿ`.

## 2. Cylinder–box relation

1. A stream in prefix cylinder `C_{n,a}` has the prescribed first `n` coordinate bits.
2. The binary partial sum is the lower endpoint of the corresponding interval.
3. The unresolved tail lies in `[0,2⁻ⁿ]`.
4. Hence `C_{n,a}` is contained in the decoder preimage of the closed box.
5. Measure preservation and equal volume imply the inclusion is an almost-everywhere equality.

The equality is deliberately almost everywhere: adjacent closed boxes share dyadic boundary faces.

## 3. Indicator transport

1. Define the octree prefix indicator and the Euclidean box indicator in `L²`.
2. Use the a.e. set equality to prove exact equality of their `L²` representatives under pullback.
3. Apply the checked adjoint identity `U†U = I` to transport prefix indicators back to box indicators.

## 4. Level identification

1. Convert between the `range (d+1)` and `Iic d` prefix index conventions.
2. Decompose every finite-prefix cylinder indicator into the finite sum of its singleton prefix indicators.
3. Prove the Block 36 initial-level span equals the singleton-prefix span.
4. Map that span through the Block 39 adjoint.
5. Identify its image with the span of concrete dyadic-box indicators.
6. Take closures to obtain exact equality of closed levels.

## 5. Density and projection convergence

1. Transport Block 39 nesting through the level equality.
2. Identify the algebraic union of concrete levels with the already dense transported union.
3. Reuse the orthogonal projection through the proved level equality.
4. Conclude strong convergence to every cube `L²` field.
