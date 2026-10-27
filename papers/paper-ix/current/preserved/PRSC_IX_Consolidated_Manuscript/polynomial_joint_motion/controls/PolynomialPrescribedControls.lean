module
public import PolynomialPrescribedLifts

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedControls

open MvPolynomial PolynomialDigitBridge PolynomialPrescribedSystem
open PolynomialPrescribedLifts PolynomialParameterSystem
open PolynomialObstruction NativeAffine FiniteFiberCounts

/-- The equation only sees the parameter coordinate. -/
def parameterOnly : Fin 1 → MvPolynomial (Fin (1 + 1)) ℤ := fun _ => X 1

/-- Full Jacobian surjectivity does not imply freedom to prescribe parameters. -/
theorem full_jacobian_surjective :
    Function.Surjective (digitJacobian 2 parameterOnly (fun _ => 0)) := by
  intro t
  refine ⟨![0, t 0], ?_⟩
  ext i
  simp [digitJacobian, parameterOnly, Fin.eq_zero i, Fin.sum_univ_two]

theorem solved_jacobian_zero :
    PolynomialPrescribedSystem.solvedJacobian 2 parameterOnly (fun _ => 0) = 0 := by
  ext u i
  simp [PolynomialPrescribedSystem.solvedJacobian, parameterOnly, Fin.eq_zero i]

/-- The nonzero prescribed parameter digit obstructs lifting already modulo four. -/
theorem digit_one_empty :
    ¬ Nonempty (PrescribedDigits 2 parameterOnly (fun _ => 0) (fun _ => 0) (fun _ => 1)) := by
  rintro ⟨u, hu⟩
  have hi := congrFun hu 0
  norm_num [parameterResidual, reduction, parameterJacobian,
    PolynomialPrescribedSystem.solvedJacobian, parameterOnly, Pi.single_apply, Fin.ext_iff] at hi

/-- A zero parameter digit leaves precisely the solved-coordinate digit free. -/
def zeroDigitEquiv :
    PrescribedDigits 2 parameterOnly (fun _ => 0) (fun _ => 0) (fun _ => 0) ≃
      (Fin 1 → ZMod 2) where
  toFun := Subtype.val
  invFun u := ⟨u, by
    ext i
    simp [parameterResidual, reduction, parameterJacobian,
      PolynomialPrescribedSystem.solvedJacobian, parameterOnly, Fin.eq_zero i]⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem zero_digit_card :
    Nat.card (PrescribedDigits 2 parameterOnly (fun _ => 0) (fun _ => 0) (fun _ => 0)) = 2 := by
  rw [Nat.card_congr zeroDigitEquiv]
  simp [Nat.card_eq_fintype_card]

theorem zero_residual : evalSystem parameterOnly (fun _ => 0) = (2 : ℤ)^1 • (fun _ => 0) := by
  ext i
  simp [evalSystem, parameterOnly]

/-- The obstructed digit has no actual next-level polynomial residue lift. -/
theorem prescribed_one_no_actual_lift :
    ¬ Nonempty (PrescribedLifts 2 1 parameterOnly (fun _ => 0) (fun _ => 1)) := by
  rintro ⟨y⟩
  exact digit_one_empty ⟨(prescribedDigitEquivLifts 2 1 (by decide) (by decide)
    parameterOnly (fun _ => 0) (fun _ => 0) zero_residual (fun _ => 1)).symm y⟩

/-- The unobstructed digit has exactly two actual residue lifts modulo four. -/
theorem prescribed_zero_actual_card :
    Nat.card (PrescribedLifts 2 1 parameterOnly (fun _ => 0) (fun _ => 0)) = 2 := by
  rw [← Nat.card_congr (prescribedDigitEquivLifts 2 1 (by decide) (by decide)
    parameterOnly (fun _ => 0) (fun _ => 0) zero_residual (fun _ => 0))]
  exact zero_digit_card

/-- An odd-prime control distinguishes the required plus sign from a minus sign. -/
def parameterPlusThree : Fin 1 → MvPolynomial (Fin (1 + 1)) ℤ := fun _ => X 1 + 1 + 1 + 1

theorem three_residual :
    evalSystem parameterPlusThree (fun _ => 0) = (3 : ℤ)^1 • (fun _ => 1) := by
  ext i
  norm_num [evalSystem, parameterPlusThree]

theorem digit_one_for_three_empty :
    ¬ Nonempty (PrescribedDigits 3 parameterPlusThree (fun _ => 0) (fun _ => 1)
      (fun _ => 1)) := by
  rintro ⟨u, hu⟩
  have hi := congrFun hu 0
  norm_num [parameterResidual, reduction, parameterJacobian,
    PolynomialPrescribedSystem.solvedJacobian, parameterPlusThree,
    Pi.single_apply, Fin.ext_iff, MvPolynomial.pderiv_one] at hi
  exact (by decide : (2 : ZMod 3) ≠ 0) hi

theorem digit_two_for_three_exists :
    Nonempty (PrescribedDigits 3 parameterPlusThree (fun _ => 0) (fun _ => 1)
      (fun _ => 2)) := by
  refine ⟨⟨fun _ => 0, ?_⟩⟩
  ext i
  norm_num [parameterResidual, reduction, parameterJacobian,
    PolynomialPrescribedSystem.solvedJacobian, parameterPlusThree,
    Pi.single_apply, Fin.ext_iff, Fin.eq_zero i, MvPolynomial.pderiv_one]
  exact (by decide : (3 : ZMod 3) = 0)

theorem prescribed_one_for_three_no_actual_lift :
    ¬ Nonempty (PrescribedLifts 3 1 parameterPlusThree (fun _ => 0) (fun _ => 1)) := by
  rintro ⟨y⟩
  exact digit_one_for_three_empty ⟨(prescribedDigitEquivLifts 3 1 (by decide) (by decide)
    parameterPlusThree (fun _ => 0) (fun _ => 1) three_residual (fun _ => 1)).symm y⟩

theorem prescribed_two_for_three_actual_lift :
    Nonempty (PrescribedLifts 3 1 parameterPlusThree (fun _ => 0) (fun _ => 2)) := by
  obtain ⟨u⟩ := digit_two_for_three_exists
  exact ⟨prescribedDigitEquivLifts 3 1 (by decide) (by decide)
    parameterPlusThree (fun _ => 0) (fun _ => 1) three_residual (fun _ => 2) u⟩

end Komorebi.PolynomialPrescribedControls
