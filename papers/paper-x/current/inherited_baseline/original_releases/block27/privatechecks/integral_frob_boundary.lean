import PaperX.CyclotomicIntegralFrobenius

/- The nonzero residue-order hypothesis is necessary: distinct square roots
of unity over the integers coincide on reduction modulo two. -/
example : (1 : ℤ) ^ 2 = 1 ∧ (-1 : ℤ) ^ 2 = 1 ∧
    Int.castRingHom (ZMod 2) (1 : ℤ) = Int.castRingHom (ZMod 2) (-1 : ℤ) ∧
    (1 : ℤ) ≠ -1 := by norm_num; decide

/- The injectivity lemma applies at a good residue characteristic, even though
its ambient ring homomorphism has nontrivial kernel. -/
example {x y : ℤ} (hx : x ^ 2 = 1) (hy : y ^ 2 = 1)
    (h : Int.castRingHom (ZMod 3) x = Int.castRingHom (ZMod 3) y) : x = y := by
  exact PaperX.CyclotomicIntegralFrobenius.map_injective_on_roots
    (Int.castRingHom (ZMod 3)) 2 (by decide) hx hy h
