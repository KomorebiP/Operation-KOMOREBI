import PaperX.CompletionExamples
import PaperX.RepresentationClasses
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-! A common residual representation is insufficient when the group order is
not a unit in the coefficient ring. This uses actual representations of C2. -/
set_option autoImplicit false
namespace PaperX.AveragingBoundary
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.CompletionExamples
open scoped Matrix

noncomputable def signFour : MatrixRep (ZMod 4) C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom (ZMod 4)) signRep

def trivialFour : MatrixRep (ZMod 4) C2 (Fin 2) := 1

noncomputable def toTwo : ZMod 4 →+* ZMod 2 := ZMod.castHom (by decide) (ZMod 2)

theorem same_residual : changeCoefficients toTwo signFour =
    changeCoefficients toTwo trivialFour := by
  apply MonoidHom.ext
  intro g
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [changeCoefficients, signFour, trivialFour, signRep, signValue, toTwo]
  all_goals split_ifs <;> decide +kernel

theorem group_order_not_unit : ¬ IsUnit (Fintype.card C2 : ZMod 4) := by
  decide +kernel

theorem signFour_det : (signFour generator).det = -1 := by
  norm_num [signFour, changeCoefficients, signRep, signValue, generator,
    Matrix.det_fin_two]

theorem not_integrally_conjugate : ¬ Conjugate trivialFour signFour := by
  rintro ⟨u, hu⟩
  have h := congrArg (fun ρ : MatrixRep (ZMod 4) C2 (Fin 2) => ρ generator) hu
  have htriv : trivialFour generator = 1 := rfl
  rw [conjugate_apply, htriv, mul_one, Units.mul_inv] at h
  have hd := congrArg Matrix.det h
  rw [Matrix.det_one, signFour_det] at hd
  exact (by decide : (1 : ZMod 4) ≠ -1) hd

end PaperX.AveragingBoundary
