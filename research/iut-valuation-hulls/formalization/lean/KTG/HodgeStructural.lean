import KTG.HodgeAnchors

/-!
# Algebraic transport of full ring laws

Generic proofs, rather than brute-force tables, show that the field-law
requirements are preserved when an additive law is pulled back along a
multiplicative bijection.  This certifies the F17 example at the structural
level and avoids large exhaustive proof searches.
-/

namespace KTG
namespace HodgeBridge

universe u

theorem transported_add_associative
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x y z, A.add (A.add x y) z = A.add x (A.add y z)) :
    ∀ x y z, transportedAdd A L (transportedAdd A L x y) z =
      transportedAdd A L x (transportedAdd A L y z) := by
  intro x y z
  apply L.injective
  calc
    L.toFun (transportedAdd A L (transportedAdd A L x y) z) =
        A.add (L.toFun (transportedAdd A L x y)) (L.toFun z) := by
          exact transported_add_intertwines A L _ _
    _ = A.add (A.add (L.toFun x) (L.toFun y)) (L.toFun z) := by
        rw [transported_add_intertwines]
    _ = A.add (L.toFun x) (A.add (L.toFun y) (L.toFun z)) := h _ _ _
    _ = L.toFun (transportedAdd A L x (transportedAdd A L y z)) := by
      rw [transported_add_intertwines, transported_add_intertwines]

theorem transported_add_commutative
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x y, A.add x y = A.add y x) :
    ∀ x y, transportedAdd A L x y = transportedAdd A L y x := by
  intro x y
  apply L.injective
  rw [transported_add_intertwines, transported_add_intertwines]
  exact h _ _

theorem transported_add_right_zero
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x, A.add x A.zero = x) :
    ∀ x, transportedAdd A L x A.zero = x := by
  intro x
  apply L.injective
  rw [transported_add_intertwines, L.map_zero]
  exact h _

theorem transported_additive_inverse
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x, ∃ y, A.add x y = A.zero) :
    ∀ x, ∃ y, transportedAdd A L x y = A.zero := by
  intro x
  obtain ⟨y, hy⟩ := h (L.toFun x)
  refine ⟨L.invFun y, ?_⟩
  apply L.injective
  rw [transported_add_intertwines, L.right_inv, hy, L.map_zero]

theorem transported_left_distributive
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x y z, A.mul x (A.add y z) =
      A.add (A.mul x y) (A.mul x z)) :
    ∀ x y z, A.mul x (transportedAdd A L y z) =
      transportedAdd A L (A.mul x y) (A.mul x z) := by
  intro x y z
  apply L.injective
  calc
    L.toFun (A.mul x (transportedAdd A L y z)) =
        A.mul (L.toFun x) (L.toFun (transportedAdd A L y z)) := L.map_mul _ _
    _ = A.mul (L.toFun x) (A.add (L.toFun y) (L.toFun z)) := by
        rw [transported_add_intertwines]
    _ = A.add (A.mul (L.toFun x) (L.toFun y))
                (A.mul (L.toFun x) (L.toFun z)) := h _ _ _
    _ = L.toFun (transportedAdd A L (A.mul x y) (A.mul x z)) := by
      rw [transported_add_intertwines, L.map_mul, L.map_mul]

theorem transported_right_distributive
    {S : Type u} (A : ArithmeticLayer S)
    (L : MultiplicativeLink A A)
    (h : ∀ x y z, A.mul (A.add x y) z =
      A.add (A.mul x z) (A.mul y z)) :
    ∀ x y z, A.mul (transportedAdd A L x y) z =
      transportedAdd A L (A.mul x z) (A.mul y z) := by
  intro x y z
  apply L.injective
  calc
    L.toFun (A.mul (transportedAdd A L x y) z) =
        A.mul (L.toFun (transportedAdd A L x y)) (L.toFun z) := L.map_mul _ _
    _ = A.mul (A.add (L.toFun x) (L.toFun y)) (L.toFun z) := by
        rw [transported_add_intertwines]
    _ = A.add (A.mul (L.toFun x) (L.toFun z))
                (A.mul (L.toFun y) (L.toFun z)) := h _ _ _
    _ = L.toFun (transportedAdd A L (A.mul x z) (A.mul y z)) := by
      rw [transported_add_intertwines, L.map_mul, L.map_mul]

/-- F17 full additive associativity is proved by abstract transport. -/
theorem alien17_associative_verified :
    ∀ x y z : Fin 17,
      alien17.add (alien17.add x y) z = alien17.add x (alien17.add y z) := by
  exact transported_add_associative standard17 twistLink17 (by decide)

/-- F17 full distributivity follows from multiplicativity of x^9 and the
ordinary finite-field distributive law. -/
theorem alien17_distributive_verified :
    ∀ x y z : Fin 17,
      x * alien17.add y z = alien17.add (x * y) (x * z) := by
  exact transported_left_distributive standard17 twistLink17 (by decide)

theorem alien17_add_commutative_verified :
    ∀ x y : Fin 17, alien17.add x y = alien17.add y x := by
  exact transported_add_commutative standard17 twistLink17 (by decide)

theorem alien17_add_zero_verified :
    ∀ x : Fin 17, alien17.add x 0 = x := by
  exact transported_add_right_zero standard17 twistLink17 (by decide)

theorem alien17_right_distributive_verified :
    ∀ x y z : Fin 17,
      alien17.add x y * z = alien17.add (x * z) (y * z) := by
  exact transported_right_distributive standard17 twistLink17 (by decide)

/-- Multiplicative inverse witnesses are shared with the standard field. -/
theorem alien17_nonzero_multiplicative_inverse :
    ∀ x : Fin 17, x ≠ 0 → ∃ y : Fin 17, x * y = 1 := by decide

/-- Additive inverses exist in the transported field structure. -/
theorem alien17_additive_inverses_verified :
    ∀ x : Fin 17, ∃ y : Fin 17, alien17.add x y = 0 := by
  apply transported_additive_inverse standard17 twistLink17
  decide

end HodgeBridge
end KTG
