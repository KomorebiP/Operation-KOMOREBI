import PaperXI.HeisenbergGroup
import PaperXI.HeisenbergDimension
import Mathlib.RingTheory.Finiteness.Cardinality

/-! Finiteness and order of the actual Heisenberg group. -/

set_option autoImplicit false

namespace PaperXI.HeisenbergFinite

open PaperXI.Heisenberg

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- The underlying coordinate equivalence of the actual group. -/
def coordinates : Element K X ≃ (X × Module.Dual K X) × K where
  toFun a := ((a.position, a.frequency), a.central)
  invFun a := ⟨a.1.1, a.1.2, a.2⟩
  left_inv a := by cases a; rfl
  right_inv a := by rcases a with ⟨⟨x, ξ⟩, z⟩; rfl

instance instFinite [Finite K] [FiniteDimensional K X] : Finite (Element K X) := by
  let : Finite X := Module.finite_of_finite K
  let : Finite (Module.Dual K X) := Module.finite_of_finite K
  exact Finite.of_injective coordinates coordinates.injective

theorem natCard_eq [FiniteDimensional K X] :
    Nat.card (Element K X) = (Nat.card X) ^ 2 * Nat.card K := by
  rw [Nat.card_congr (coordinates (K := K) (X := X)), Nat.card_prod,
    PaperXI.HeisenbergDimension.natCard_symplectic]

end PaperXI.HeisenbergFinite
