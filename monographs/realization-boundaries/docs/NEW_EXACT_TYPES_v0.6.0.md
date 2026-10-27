# Exact elaborated interfaces — v0.6.0

Exported from the accepted production environment. Generated declarations are included and are not counted as independent results. No supplied cardinal, kernel size, or cyclicity certificate replaces the proofs.

## RootFibers

### `RealizationBoundaries.RootFiber`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) → ℕ → ↥(RealizationBoundaries.preimage W) → Type
```

### `RealizationBoundaries.coordinateExtension_annihilated`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ) (z : RealizationBoundaries.DivisorCoordinates m), m • RealizationBoundaries.coordinateExtension m z = 0
```

### `RealizationBoundaries.coordinateMap.eq_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ),
  RealizationBoundaries.coordinateMap W m = { toFun := fun x p => ↑x ↑p, map_zero' := ⋯, map_add' := ⋯ }
```

### `RealizationBoundaries.mem_rootKernel`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (y : ↥(RealizationBoundaries.preimage W)),
  y ∈ RealizationBoundaries.rootKernel W m ↔ m • y = 0
```

### `RealizationBoundaries.mem_rootKernel._simp_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (y : ↥(RealizationBoundaries.preimage W)),
  (y ∈ RealizationBoundaries.rootKernel W m) = (m • y = 0)
```

### `RealizationBoundaries.rootFiberEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m : ℕ} →
    0 < m →
      (x : ↥(RealizationBoundaries.preimage W)) →
        RealizationBoundaries.RootFiber W m x →
          RealizationBoundaries.RootFiber W m x ≃ RealizationBoundaries.DivisorCoordinates m
```

### `RealizationBoundaries.rootFiberEquiv_symm_apply`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (z : RealizationBoundaries.DivisorCoordinates m),
  ↑↑((RealizationBoundaries.rootFiberEquiv W hm x y).symm z) = ↑↑y + RealizationBoundaries.coordinateExtension m z
```

### `RealizationBoundaries.rootFiberTranslation`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  (m : ℕ) →
    (x : ↥(RealizationBoundaries.preimage W)) →
      RealizationBoundaries.RootFiber W m x →
        ↥(RealizationBoundaries.rootKernel W m) ≃ RealizationBoundaries.RootFiber W m x
```

### `RealizationBoundaries.rootFiberTranslation._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (k : ↥(RealizationBoundaries.rootKernel W m)), m • (↑y + ↑k) = x
```

### `RealizationBoundaries.rootFiberTranslation._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y z : RealizationBoundaries.RootFiber W m x), ↑z - ↑y ∈ RealizationBoundaries.rootKernel W m
```

### `RealizationBoundaries.rootFiberTranslation._proof_3`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (k : ↥(RealizationBoundaries.rootKernel W m)),
  ↑⟨↑y + ↑k, ⋯⟩ - ↑y ∈ RealizationBoundaries.rootKernel W m
```

### `RealizationBoundaries.rootFiberTranslation._proof_4`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (k : ↥(RealizationBoundaries.rootKernel W m)), ⟨↑⟨↑y + ↑k, ⋯⟩ - ↑y, ⋯⟩ = k
```

### `RealizationBoundaries.rootFiberTranslation._proof_5`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y z : RealizationBoundaries.RootFiber W m x), m • (↑y + ↑⟨↑z - ↑y, ⋯⟩) = x
```

### `RealizationBoundaries.rootFiberTranslation._proof_6`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y z : RealizationBoundaries.RootFiber W m x), ⟨↑y + ↑⟨↑z - ↑y, ⋯⟩, ⋯⟩ = z
```

### `RealizationBoundaries.rootFiberTranslation_apply`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (k : ↥(RealizationBoundaries.rootKernel W m)),
  ↑((RealizationBoundaries.rootFiberTranslation W m x y) k) = ↑y + ↑k
```

### `RealizationBoundaries.rootFiber_coset_iff`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (z : ↥(RealizationBoundaries.preimage W)),
  m • z = x ↔ z - ↑y ∈ RealizationBoundaries.rootKernel W m
```

### `RealizationBoundaries.rootFiber_finite`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m → ∀ (x : ↥(RealizationBoundaries.preimage W)), Finite (RealizationBoundaries.RootFiber W m x)
```

### `RealizationBoundaries.rootFiber_isEmpty`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (x : ↥(RealizationBoundaries.preimage W)),
  (¬∃ y, m • y = x) → IsEmpty (RealizationBoundaries.RootFiber W m x)
```

### `RealizationBoundaries.rootKernel`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) → ℕ → AddSubgroup ↥(RealizationBoundaries.preimage W)
```

### `RealizationBoundaries.rootKernel._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
AddSubmonoidClass (AddSubgroup RealizationBoundaries.Ambient) RealizationBoundaries.Ambient
```

### `RealizationBoundaries.rootKernelEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m : ℕ} → 0 < m → ↥(RealizationBoundaries.rootKernel W m) ≃+ RealizationBoundaries.DivisorCoordinates m
```

### `RealizationBoundaries.rootKernelEquiv._proof_1`

Kind: theorem. Axioms: `propext`.

```lean
∀ {m : ℕ} (i : RealizationBoundaries.DivisorPrime m), Fact (Nat.Prime ↑↑i)
```

### `RealizationBoundaries.rootKernelEquiv._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (z : RealizationBoundaries.DivisorCoordinates m),
      RealizationBoundaries.coordinateExtension m z ∈ RealizationBoundaries.preimage W
```

### `RealizationBoundaries.rootKernelEquiv._proof_3`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m)
  (z : RealizationBoundaries.DivisorCoordinates m),
  (RealizationBoundaries.integerMultiplication W m) ⟨RealizationBoundaries.coordinateExtension m z, ⋯⟩ = 0
```

### `RealizationBoundaries.rootKernelEquiv._proof_4`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (y : ↥(RealizationBoundaries.rootKernel W m)),
      RealizationBoundaries.coordinateExtension m ((RealizationBoundaries.coordinateMap W m) ↑y) ∈
        RealizationBoundaries.preimage W
```

### `RealizationBoundaries.rootKernelEquiv._proof_5`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (y : ↥(RealizationBoundaries.rootKernel W m)),
  (RealizationBoundaries.integerMultiplication W m)
      ⟨RealizationBoundaries.coordinateExtension m ((RealizationBoundaries.coordinateMap W m) ↑y), ⋯⟩ =
    0
```

### `RealizationBoundaries.rootKernelEquiv._proof_6`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (y : ↥(RealizationBoundaries.rootKernel W m)),
  ⟨⟨RealizationBoundaries.coordinateExtension m ((RealizationBoundaries.coordinateMap W m) ↑y), ⋯⟩, ⋯⟩ = y
```

### `RealizationBoundaries.rootKernelEquiv._proof_7`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m)
  (z : RealizationBoundaries.DivisorCoordinates m),
  (RealizationBoundaries.coordinateMap W m) ↑⟨⟨RealizationBoundaries.coordinateExtension m z, ⋯⟩, ⋯⟩ = z
```

### `RealizationBoundaries.rootKernelEquiv._proof_8`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (x x_1 : ↥(RealizationBoundaries.rootKernel W m)),
  (RealizationBoundaries.coordinateMap W m) ↑(x + x_1) = (RealizationBoundaries.coordinateMap W m) ↑(x + x_1)
```

### `RealizationBoundaries.rootKernelEquiv_apply`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (y : ↥(RealizationBoundaries.rootKernel W m))
  (p : RealizationBoundaries.DivisorPrime m), (RealizationBoundaries.rootKernelEquiv W hm) y p = ↑↑y ↑p
```

### `RealizationBoundaries.rootKernelEquiv_symm_apply`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m)
  (z : RealizationBoundaries.DivisorCoordinates m),
  ↑↑((RealizationBoundaries.rootKernelEquiv W hm).symm z) = RealizationBoundaries.coordinateExtension m z
```

### `RealizationBoundaries.rootKernel_coordinate_zero`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (m : ℕ) (y : ↥(RealizationBoundaries.rootKernel W m))
  (p : RealizationBoundaries.Prime), ¬↑p ∣ m → ↑↑y p = 0
```

### `RealizationBoundaries.rootKernel_finite`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ}, 0 < m → Finite ↥(RealizationBoundaries.rootKernel W m)
```

## RadicalCounts

### `RealizationBoundaries.divisorCoordinates_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ}, 0 < m → Nat.card (RealizationBoundaries.DivisorCoordinates m) = RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.divisorPrime_prod`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ},
  0 < m → ∀ [inst : Fintype (RealizationBoundaries.DivisorPrime m)], ∏ p, ↑↑p = RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.integerQuotient_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    Nat.card (↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W m) =
      RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.multiples_eq_radical`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m → RealizationBoundaries.multiples W m = RealizationBoundaries.multiples W (RealizationBoundaries.primeRadical m)
```

### `RealizationBoundaries.primeRadical`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
ℕ → ℕ
```

### `RealizationBoundaries.primeRadical.eq_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ), RealizationBoundaries.primeRadical m = ∏ p ∈ m.primeFactors, p
```

### `RealizationBoundaries.primeRadical_dvd`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ), RealizationBoundaries.primeRadical m ∣ m
```

### `RealizationBoundaries.primeRadical_dvd_of_dvd`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m n : ℕ}, 0 < n → m ∣ n → RealizationBoundaries.primeRadical m ∣ RealizationBoundaries.primeRadical n
```

### `RealizationBoundaries.primeRadical_one`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
RealizationBoundaries.primeRadical 1 = 1
```

### `RealizationBoundaries.primeRadical_pos`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ), 0 < RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.primeRadical_pow`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ) {k : ℕ}, k ≠ 0 → RealizationBoundaries.primeRadical (m ^ k) = RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.primeRadical_prime`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {p : ℕ}, Nat.Prime p → RealizationBoundaries.primeRadical p = p
```

### `RealizationBoundaries.primeRadical_prime_pow`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {p k : ℕ}, Nat.Prime p → k ≠ 0 → RealizationBoundaries.primeRadical (p ^ k) = p
```

### `RealizationBoundaries.prime_dvd_radical_iff`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ}, 0 < m → ∀ (p : RealizationBoundaries.Prime), ↑p ∣ RealizationBoundaries.primeRadical m ↔ ↑p ∣ m
```

### `RealizationBoundaries.rootFiber_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (x : ↥(RealizationBoundaries.preimage W)),
      Nat.card (RealizationBoundaries.RootFiber W m x) =
        if ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0 then RealizationBoundaries.primeRadical m else 0
```

### `RealizationBoundaries.rootFiber_card_of_obstruction`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (x : ↥(RealizationBoundaries.preimage W)) (p : RealizationBoundaries.Prime),
      ↑p ∣ m → ↑x p ≠ 0 → Nat.card (RealizationBoundaries.RootFiber W m x) = 0
```

### `RealizationBoundaries.rootFiber_card_of_root`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (x : ↥(RealizationBoundaries.preimage W)) (y : RealizationBoundaries.RootFiber W m x),
      Nat.card (RealizationBoundaries.RootFiber W m x) = RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.rootFiber_card_of_solvable`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (x : ↥(RealizationBoundaries.preimage W)),
      (∃ y, m • y = x) → Nat.card (RealizationBoundaries.RootFiber W m x) = RealizationBoundaries.primeRadical m
```

### `RealizationBoundaries.rootKernel_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m → Nat.card ↥(RealizationBoundaries.rootKernel W m) = RealizationBoundaries.primeRadical m
```

## CyclicQuotients

### `RealizationBoundaries.coordinateRestriction.congr_simp`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m n : ℕ} (hmn : m ∣ n),
  RealizationBoundaries.coordinateRestriction hmn = RealizationBoundaries.coordinateRestriction hmn
```

### `RealizationBoundaries.cyclicIntegerQuotientEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m : ℕ} →
    0 < m →
      ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W m ≃+
        ZMod (RealizationBoundaries.primeRadical m)
```

### `RealizationBoundaries.cyclicIntegerQuotientEquiv.eq_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m),
  RealizationBoundaries.cyclicIntegerQuotientEquiv W hm =
    (RealizationBoundaries.integerQuotientEquiv W hm).trans (RealizationBoundaries.divisorCrtEquiv hm).toAddEquiv.symm
```

### `RealizationBoundaries.cyclicIntegerQuotientEquiv_coordinates`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m)
  (x : ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W m),
  (RealizationBoundaries.divisorCrtEquiv hm) ((RealizationBoundaries.cyclicIntegerQuotientEquiv W hm) x) =
    (RealizationBoundaries.integerQuotientEquiv W hm) x
```

### `RealizationBoundaries.cyclicIntegerQuotientEquiv_mk`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W)),
  (RealizationBoundaries.divisorCrtEquiv hm) ((RealizationBoundaries.cyclicIntegerQuotientEquiv W hm) ↑x) =
    (RealizationBoundaries.coordinateMap W m) x
```

### `RealizationBoundaries.cyclicIntegerQuotientEquiv_restriction`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m n : ℕ} (hm : 0 < m) (hn : 0 < n) (hmn : m ∣ n)
  (x : ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W n),
  (RealizationBoundaries.cyclicIntegerQuotientEquiv W hm) ((RealizationBoundaries.quotientRestriction W hmn) x) =
    (ZMod.castHom ⋯ (ZMod (RealizationBoundaries.primeRadical m)))
      ((RealizationBoundaries.cyclicIntegerQuotientEquiv W hn) x)
```

### `RealizationBoundaries.cyclicRootFiberEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m : ℕ} →
    0 < m →
      (x : ↥(RealizationBoundaries.preimage W)) →
        RealizationBoundaries.RootFiber W m x →
          RealizationBoundaries.RootFiber W m x ≃ ZMod (RealizationBoundaries.primeRadical m)
```

### `RealizationBoundaries.cyclicRootFiberEquiv_symm_natCast`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (y : RealizationBoundaries.RootFiber W m x) (n : ℕ),
  ↑↑((RealizationBoundaries.cyclicRootFiberEquiv W hm x y).symm ↑n) =
    ↑↑y + RealizationBoundaries.coordinateExtension m fun p => ↑n
```

### `RealizationBoundaries.divisorCrtEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
{m : ℕ} → 0 < m → ZMod (RealizationBoundaries.primeRadical m) ≃+* RealizationBoundaries.DivisorCoordinates m
```

### `RealizationBoundaries.divisorCrtEquiv._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ} ⦃p q : RealizationBoundaries.DivisorPrime m⦄, p ≠ q → (↑↑p).Coprime ↑↑q
```

### `RealizationBoundaries.divisorCrtEquiv._proof_2`

Kind: theorem. Axioms: `propext`.

```lean
∀ {m : ℕ} (i : RealizationBoundaries.DivisorPrime m), Fact (Nat.Prime ↑↑i)
```

### `RealizationBoundaries.divisorCrtEquiv._proof_3`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ} (hm : 0 < m), RealizationBoundaries.primeRadical m = ∏ p, ↑↑p
```

### `RealizationBoundaries.divisorCrtEquiv.congr_simp`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ} (hm : 0 < m), RealizationBoundaries.divisorCrtEquiv hm = RealizationBoundaries.divisorCrtEquiv hm
```

### `RealizationBoundaries.divisorCrtEquiv_intCast`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ} (hm : 0 < m) (n : ℤ) (p : RealizationBoundaries.DivisorPrime m),
  (RealizationBoundaries.divisorCrtEquiv hm) (↑n) p = ↑n
```

### `RealizationBoundaries.divisorCrtEquiv_natCast`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ} (hm : 0 < m) (n : ℕ) (p : RealizationBoundaries.DivisorPrime m),
  (RealizationBoundaries.divisorCrtEquiv hm) (↑n) p = ↑n
```

### `RealizationBoundaries.divisorCrtEquiv_restriction`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m n : ℕ} (hm : 0 < m) (hn : 0 < n) (hmn : m ∣ n) (z : ZMod (RealizationBoundaries.primeRadical n)),
  (RealizationBoundaries.coordinateRestriction hmn) ((RealizationBoundaries.divisorCrtEquiv hn) z) =
    (RealizationBoundaries.divisorCrtEquiv hm) ((ZMod.castHom ⋯ (ZMod (RealizationBoundaries.primeRadical m))) z)
```

### `RealizationBoundaries.integerQuotientEquiv.congr_simp`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m),
  RealizationBoundaries.integerQuotientEquiv W hm = RealizationBoundaries.integerQuotientEquiv W hm
```

### `RealizationBoundaries.integerQuotientEquiv_restriction`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m n : ℕ} (hm : 0 < m) (hn : 0 < n) (hmn : m ∣ n)
  (x : ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W n),
  (RealizationBoundaries.integerQuotientEquiv W hm) ((RealizationBoundaries.quotientRestriction W hmn) x) =
    (RealizationBoundaries.coordinateRestriction hmn) ((RealizationBoundaries.integerQuotientEquiv W hn) x)
```

### `RealizationBoundaries.multiples_antitone`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m n : ℕ},
  m ∣ n → RealizationBoundaries.multiples W n ≤ RealizationBoundaries.multiples W m
```

### `RealizationBoundaries.quotientRestriction`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m n : ℕ} →
    m ∣ n →
      ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W n →+
        ↥(RealizationBoundaries.preimage W) ⧸ RealizationBoundaries.multiples W m
```

### `RealizationBoundaries.quotientRestriction._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {n : ℕ}, (RealizationBoundaries.multiples W n).Normal
```

### `RealizationBoundaries.quotientRestriction._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
AddSubmonoidClass (AddSubgroup RealizationBoundaries.Ambient) RealizationBoundaries.Ambient
```

### `RealizationBoundaries.quotientRestriction_mk`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m n : ℕ} (hmn : m ∣ n) (x : ↥(RealizationBoundaries.preimage W)),
  (RealizationBoundaries.quotientRestriction W hmn) ↑x = ↑x
```

### `ZMod.castHom.congr_simp`

Kind: theorem. Axioms: `propext`, `Quot.sound`.

```lean
∀ {n m m_1 : ℕ} (e_m : m = m_1) (h : m ∣ n) (R : Type u_2) [inst : Ring R] [inst_1 : CharP R m],
  ZMod.castHom h R = ZMod.castHom ⋯ R
```

## CyclicFiniteTargets

### `RealizationBoundaries.finiteTargetCyclicFactor`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  (F : Type u_1) →
    [inst : AddGroup F] →
      [Finite F] →
        (↥(RealizationBoundaries.preimage W) →+ F) → ZMod (RealizationBoundaries.primeRadical (Nat.card F)) →+ F
```

### `RealizationBoundaries.finiteTargetCyclicFactor._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
AddSubmonoidClass (AddSubgroup RealizationBoundaries.Ambient) RealizationBoundaries.Ambient
```

### `RealizationBoundaries.finiteTargetCyclicFactor._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (F : Type u_1) (i : RealizationBoundaries.DivisorPrime (Nat.card F)), Fact (Nat.Prime ↑↑i)
```

### `RealizationBoundaries.finiteTargetCyclicFactor._proof_3`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (F : Type u_1) [AddGroup F] [Finite F], 0 < Nat.card F
```

### `RealizationBoundaries.finiteTargetCyclicFactor_quotient`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [inst_1 : Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F) (x : ↥(RealizationBoundaries.preimage W)),
  (RealizationBoundaries.finiteTargetCyclicFactor W F f) ((RealizationBoundaries.cyclicIntegerQuotientEquiv W ⋯) ↑x) =
    f x
```

### `RealizationBoundaries.finiteTargetCyclicFactor_surjective`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [inst_1 : Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F),
  Function.Surjective ⇑f → Function.Surjective ⇑(RealizationBoundaries.finiteTargetCyclicFactor W F f)
```

### `RealizationBoundaries.finiteTargetFactor_bijective`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [inst_1 : Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F),
  Function.Surjective ⇑f → Function.Bijective ⇑(RealizationBoundaries.finiteTargetFactor W F f)
```

### `RealizationBoundaries.finite_quotient_cyclic`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F), Function.Surjective ⇑f → IsAddCyclic F
```

### `RealizationBoundaries.finite_quotient_exists_iff`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [Finite F],
  (∃ f, Function.Surjective ⇑f) ↔ IsAddCyclic F ∧ Squarefree (Nat.card F)
```

### `RealizationBoundaries.finite_quotient_radical_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F),
  Function.Surjective ⇑f → RealizationBoundaries.primeRadical (Nat.card F) = Nat.card F
```

### `RealizationBoundaries.finite_quotient_squarefree`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F), Function.Surjective ⇑f → Squarefree (Nat.card F)
```

### `RealizationBoundaries.finite_surjection_ker`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [Finite F]
  (f : ↥(RealizationBoundaries.preimage W) →+ F),
  Function.Surjective ⇑f → f.ker = RealizationBoundaries.multiples W (Nat.card F)
```

### `RealizationBoundaries.primeRadical_eq_of_squarefree`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ}, Squarefree m → RealizationBoundaries.primeRadical m = m
```

### `RealizationBoundaries.primeRadical_squarefree`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ), Squarefree (RealizationBoundaries.primeRadical m)
```

### `RealizationBoundaries.squarefreeCyclicQuotient`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  (F : Type u_1) →
    [inst : AddGroup F] →
      [Finite F] → IsAddCyclic F → Squarefree (Nat.card F) → ↥(RealizationBoundaries.preimage W) →+ F
```

### `RealizationBoundaries.squarefreeCyclicQuotient._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1),
  (RealizationBoundaries.multiples W (Nat.card F)).Normal
```

### `RealizationBoundaries.squarefreeCyclicQuotient._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (F : Type u_1), Squarefree (Nat.card F) → RealizationBoundaries.primeRadical (Nat.card F) = Nat.card F
```

### `RealizationBoundaries.squarefreeCyclicQuotient_surjective`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (F : Type u_1) [inst : AddGroup F] [inst_1 : Finite F]
  (hc : IsAddCyclic F) (hs : Squarefree (Nat.card F)),
  Function.Surjective ⇑(RealizationBoundaries.squarefreeCyclicQuotient W F hc hs)
```

## RootConsequences

### `RealizationBoundaries.coordinateDivide_root`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (m : ℕ) (x : RealizationBoundaries.Ambient),
  (∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → x p = 0) → m • RealizationBoundaries.coordinateDivide m x = x
```

### `RealizationBoundaries.normalizedRoot`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  {m : ℕ} →
    0 < m →
      (x : ↥(RealizationBoundaries.preimage W)) →
        (∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0) → RealizationBoundaries.RootFiber W m x
```

### `RealizationBoundaries.normalizedRoot._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m →
    ∀ (x : ↥(RealizationBoundaries.preimage W)),
      (∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0) →
        RealizationBoundaries.coordinateDivide m ↑x ∈ RealizationBoundaries.preimage W
```

### `RealizationBoundaries.normalizedRoot._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (h : ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0), m • ⟨RealizationBoundaries.coordinateDivide m ↑x, ⋯⟩ = x
```

### `RealizationBoundaries.normalizedRoot.congr_simp`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (h : ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0),
  RealizationBoundaries.normalizedRoot W hm x h = RealizationBoundaries.normalizedRoot W hm x h
```

### `RealizationBoundaries.normalizedRoot_coordinate`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (h : ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0) (p : RealizationBoundaries.Prime),
  ↑↑(RealizationBoundaries.normalizedRoot W hm x h) p = (↑m)⁻¹ * ↑x p
```

### `RealizationBoundaries.normalizedRoot_exceptional_zero`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (h : ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0) (p : RealizationBoundaries.Prime),
  ↑p ∣ m → ↑↑(RealizationBoundaries.normalizedRoot W hm x h) p = 0
```

### `RealizationBoundaries.normalizedRoot_unique`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ} (hm : 0 < m) (x : ↥(RealizationBoundaries.preimage W))
  (h : ∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑x p = 0) (y : RealizationBoundaries.RootFiber W m x),
  (∀ (p : RealizationBoundaries.Prime), ↑p ∣ m → ↑↑y p = 0) → y = RealizationBoundaries.normalizedRoot W hm x h
```

### `RealizationBoundaries.primeRadical_eq_one_iff`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ {m : ℕ}, 0 < m → (RealizationBoundaries.primeRadical m = 1 ↔ m = 1)
```

### `RealizationBoundaries.prime_power_root_count`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {p k : ℕ},
  Nat.Prime p →
    k ≠ 0 →
      ∀ (x : ↥(RealizationBoundaries.preimage W)),
        (∃ y, p ^ k • y = x) → Nat.card (RealizationBoundaries.RootFiber W (p ^ k) x) = p
```

### `RealizationBoundaries.unique_root_iff_one`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) {m : ℕ},
  0 < m → ∀ (x : ↥(RealizationBoundaries.preimage W)), (∃ y, m • y = x) → ((∃! y, m • y = x) ↔ m = 1)
```

### `RealizationBoundaries.zeroRootFiberEquiv`

Kind: definition. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
(W : Submodule ℚ RealizationBoundaries.TailSpace) →
  RealizationBoundaries.RootFiber W 0 0 ≃ ↥(RealizationBoundaries.preimage W)
```

### `RealizationBoundaries.zeroRootFiberEquiv._proof_1`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
AddSubmonoidClass (AddSubgroup RealizationBoundaries.Ambient) RealizationBoundaries.Ambient
```

### `RealizationBoundaries.zeroRootFiberEquiv._proof_2`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : ↥(RealizationBoundaries.preimage W)), 0 • x = 0
```

### `RealizationBoundaries.zeroRootFiberEquiv._proof_3`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : RealizationBoundaries.RootFiber W 0 0), 0 • ↑x = 0
```

### `RealizationBoundaries.zeroRootFiberEquiv._proof_4`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : RealizationBoundaries.RootFiber W 0 0), ⟨↑x, ⋯⟩ = ⟨↑x, ⋯⟩
```

### `RealizationBoundaries.zeroRootFiberEquiv._proof_5`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : ↥(RealizationBoundaries.preimage W)), ↑⟨x, ⋯⟩ = ↑⟨x, ⋯⟩
```

### `RealizationBoundaries.zeroRootFiber_card`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace), Nat.card (RealizationBoundaries.RootFiber W 0 0) = 0
```

### `RealizationBoundaries.zeroRootFiber_infinite`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace), Infinite (RealizationBoundaries.RootFiber W 0 0)
```

### `RealizationBoundaries.zeroRootFiber_isEmpty_of_ne_zero`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace) (x : ↥(RealizationBoundaries.preimage W)),
  x ≠ 0 → IsEmpty (RealizationBoundaries.RootFiber W 0 x)
```

### `RealizationBoundaries.zeroRootFiber_nonempty`

Kind: theorem. Axioms: `propext`, `Classical.choice`, `Quot.sound`.

```lean
∀ (W : Submodule ℚ RealizationBoundaries.TailSpace), Nonempty (RealizationBoundaries.RootFiber W 0 0)
```
