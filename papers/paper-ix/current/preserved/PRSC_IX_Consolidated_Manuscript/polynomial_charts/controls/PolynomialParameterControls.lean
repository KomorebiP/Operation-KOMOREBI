module
public import PolynomialParameterSystem
public import Mathlib.NumberTheory.Padics.RingHoms

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialParameterControls
open MvPolynomial PolynomialDigitBridge PolynomialPadicLift PolynomialParameterSystem

/-- A smooth equation for which the specified first coordinate cannot be solved. -/
def squareMinusParameter : Fin 1 → MvPolynomial (Fin (1+1)) ℤ :=
  fun _ => X 0 ^ 2 - X 1

theorem full_jacobian_surjective :
    Function.Surjective (digitJacobian 2 squareMinusParameter (fun _ => 0)) := by
  intro t
  refine ⟨![0, -t 0], ?_⟩
  ext i
  simp [digitJacobian, squareMinusParameter, Fin.eq_zero i, Fin.sum_univ_two]

theorem solved_jacobian_zero :
    solvedJacobian 2 squareMinusParameter (fun _ => 0) = 0 := by
  ext u i
  simp [solvedJacobian, squareMinusParameter, Fin.eq_zero i]

theorem solved_jacobian_not_surjective :
    ¬ Function.Surjective (solvedJacobian 2 squareMinusParameter (fun _ => 0)) := by
  rw [solved_jacobian_zero]
  intro h
  obtain ⟨u, hu⟩ := h (fun _ => 1)
  have hi := congrFun hu 0
  norm_num at hi

/-- The proposed parameter is in the base residue ball modulo two. -/
theorem parameter_two_near_origin : (2 : ℤ_[2]) ∣ (2 : ℤ_[2]) - 0 := by simp

/-- Prescribing the second coordinate to two has no root, already modulo four. -/
theorem no_root_at_parameter_two :
    ¬ ∃ a : Fin (1+1) → ℤ_[2],
      padicEval 2 squareMinusParameter a = 0 ∧ a 1 = 2 := by
  rintro ⟨a, ha, ht⟩
  have hsq : a 0 ^ 2 = (2 : ℤ_[2]) := by
    have hi := congrFun ha 0
    simpa [padicEval, squareMinusParameter, ht, sub_eq_zero] using hi
  have hmod := congrArg (PadicInt.toZModPow 2) hsq
  have hnot : ∀ r : ZMod (2^2), r^2 ≠ 2 := by decide
  have htwo : (2 : ℤ_[2]) = 1 + 1 := by norm_num
  rw [map_pow, htwo, map_add, map_one] at hmod
  exact hnot _ (hmod.trans (by decide : (1 : ZMod (2^2)) + 1 = 2))

end Komorebi.PolynomialParameterControls
