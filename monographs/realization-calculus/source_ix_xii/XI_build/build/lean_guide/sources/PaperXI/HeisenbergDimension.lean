import PaperXI.HeisenbergCardinality
import Mathlib.Basic.Complex.Basic
import Mathlib.Data.Nat.Sqrt

/-! Dimension and square-root cardinality in the finite Schrödinger model. -/

set_option autoImplicit false

namespace PaperXI.HeisenbergDimension

open Module

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]
variable [FiniteDimensional K X]

theorem natCard_dual : Nat.card (Module.Dual K X) = Nat.card X := by
  rw [Module.natCard_eq_pow_finrank (K := K) (V := Module.Dual K X),
    Subspace.dual_finrank_eq,
    Module.natCard_eq_pow_finrank (K := K) (V := X)]

theorem natCard_symplectic : Nat.card (X × Module.Dual K X) = (Nat.card X) ^ 2 := by
  rw [Nat.card_prod, natCard_dual, pow_two]

theorem sqrt_natCard_symplectic :
    Nat.sqrt (Nat.card (X × Module.Dual K X)) = Nat.card X := by
  rw [natCard_symplectic, Nat.sqrt_eq']

variable [Fintype X]

omit [AddCommGroup X] in
theorem finrank_function : finrank ℂ (X → ℂ) = Nat.card X := by
  rw [Module.finrank_fintype_fun_eq_card, Nat.card_eq_fintype_card]

theorem finrank_function_pow : finrank ℂ (X → ℂ) = Nat.card K ^ finrank K X := by
  rw [finrank_function, Module.natCard_eq_pow_finrank (K := K) (V := X)]

theorem finrank_function_sqrt :
    finrank ℂ (X → ℂ) = Nat.sqrt (Nat.card (X × Module.Dual K X)) := by
  rw [finrank_function, sqrt_natCard_symplectic]

end PaperXI.HeisenbergDimension
