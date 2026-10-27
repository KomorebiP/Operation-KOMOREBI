import PaperX.CyclotomicInertiaBridge

open PaperX.CyclotomicInertiaBridge

example : ∀ x y : PadicInt 2, x ^ 2 = 1 → y ^ 2 = 1 →
    IsLocalRing.residue (PadicInt 2) x = IsLocalRing.residue (PadicInt 2) y → x = y := by
  have hn : ¬ (∀ x y : PadicInt 2, x ^ 2 = 1 → y ^ 2 = 1 →
      IsLocalRing.residue (PadicInt 2) x = IsLocalRing.residue (PadicInt 2) y → x = y) := by
    intro h
    obtain ⟨x, y, hx, hy, hne, hres⟩ := twoAdic_distinct_roots_same_residue
    exact hne (h x y hx hy hres)
  rw [iff_false_intro hn]
