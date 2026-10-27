module
public import MatrixPrimeMinimality
public import GeneratedLarge

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
namespace Komorebi.Representation.Symbolic.Large
open Komorebi.Representation Komorebi.Representation.Matrix

theorem nonzero_weights : ∀ i, smith.weights i ≠ 0 := by decide

theorem sharp_linear_budget (budget : Nat) :
    (∃ n ≤ budget,
      ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) (R))
        (e : (Fin 8 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  prime_certificate_minimum_iff (p:=2) (r:=16) (by decide) (by decide)
    data valid smith (by exact of_decide_eq_true smith_checked) nonzero_weights budget

end Komorebi.Representation.Symbolic.Large
