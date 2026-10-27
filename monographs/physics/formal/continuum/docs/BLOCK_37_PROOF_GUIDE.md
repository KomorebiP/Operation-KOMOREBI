# Block 37 proof guide — octree Cartesian binary quotient

## 1. Finite digit factorization

An octree digit `o : Fin 8` is decomposed into three bits by

```text
bitsOfOctant o i = (o / 2^i) mod 2,  i : Fin 3.
```

The inverse is

```text
octantOfBits b = b₀ + 2 b₁ + 4 b₂.
```

Lean proves both inverse laws, producing

```text
octantBitEquiv : Fin 8 ≃ (Fin 3 → Fin 2).
```

## 2. Measure preservation

Both finite spaces carry their uniform probability measures. Singleton calculations show that every point has mass `1/8`, and extensionality on singletons proves

```text
octantBit_measurePreserving.
```

Applying `Measure.infinitePi_map_pi` digitwise gives the full address theorem

```text
addressBit_measurePreserving.
```

The resulting product-space change of variables induces

```text
pullbackBitL2 : L²(bitCubeMeasure,E) →ₗᵢ[ℂ] L²(octreeMeasure,E).
```

## 3. Positional decoding

Each coordinate stream is decoded by Mathlib's base-two positional series

```text
Real.ofDigits : (ℕ → Fin 2) → ℝ.
```

The established range theorem places the value in `[0,1]`. Decoding the three coordinate streams gives

```text
cubeCode : BitCubeAddress → (Fin 3 → unitInterval).
```

Continuity follows from `Real.continuous_ofDigits` and product-coordinate continuity.

## 4. Dyadic prefix control

Mathlib's exact positional tail theorem yields

```text
|ofDigits x - ofDigits y| ≤ (2^n)⁻¹
```

whenever `x` and `y` agree before depth `n`. The block transfers this to each Cartesian coordinate of both the bit-vector address and original octree address representations.

## 5. Quotient realization

`Real.ofDigits_SurjOn` provides a binary expansion for every point of `[0,1]`. Coordinatewise choice gives cube surjectivity. Since the address space is compact and the cube is Hausdorff, a continuous surjection is a quotient map:

```text
cubeCode_isQuotientMap
octreeCubeCode_isQuotientMap
```

This is the precise topological form of the local-discrete/global-continuous bridge at this stage.

## 6. Ambiguity boundary

The streams

```text
0.1000…
0.0111…
```

are proved distinct but both decode to `1/2`. Therefore the decoder is not injective. A future measure equivalence must work almost everywhere or through a canonical expansion convention.

## 7. Nonclaims

No theorem in this block identifies the pushforward fair-bit measure with Lebesgue volume. The symbolic `L²` isometry is between octree addresses and interleaved bit addresses only.
