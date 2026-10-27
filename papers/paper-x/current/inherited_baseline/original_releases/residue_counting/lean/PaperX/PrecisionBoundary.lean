import PaperX.PrecisionExamples

/-! Residual equality modulo two does not determine an integral C2 representation,
even for actual continuous representations on finite free Z_2 modules. -/
set_option autoImplicit false
namespace PaperX.PrecisionBoundary
open scoped Matrix
open PaperX.CompletionExamples PaperX.RepresentationLimits
open PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.PrecisionExamples

noncomputable def trivial : MatrixRep ℤ_[2] C2 (Fin 2) := 1

theorem sign_and_trivial_same_mod_two : changeCoefficients modTwo tau =
    changeCoefficients modTwo trivial := by
  apply MonoidHom.ext
  intro g
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [changeCoefficients, tau, trivial, signRep, signValue]
  all_goals split_ifs <;> simp

theorem sign_generator_det : (tau generator).det = -1 := by
  norm_num [tau, changeCoefficients, signRep, signValue, generator,
    Matrix.det_fin_two]

theorem sign_not_integrally_conjugate_trivial : ¬ Conjugate trivial tau := by
  rintro ⟨u, hu⟩
  have h := congrArg (fun ρ : MatrixRep ℤ_[2] C2 (Fin 2) => ρ generator) hu
  have htriv : trivial generator = 1 := rfl
  rw [conjugate_apply, htriv, mul_one, Units.mul_inv] at h
  have hd := congrArg Matrix.det h
  rw [Matrix.det_one, sign_generator_det] at hd
  norm_num at hd

theorem sign_continuous : AdicRepContinuous twoIdeal tau := by
  let : TopologicalSpace ℤ_[2] := twoIdeal.adicTopology
  exact continuous_of_discreteTopology

theorem trivial_continuous : AdicRepContinuous twoIdeal trivial := by
  let : TopologicalSpace ℤ_[2] := twoIdeal.adicTopology
  exact continuous_of_discreteTopology

/-- Modulo four already separates these two actual integral representations. -/
theorem sign_and_trivial_not_conjugate_mod_four :
    ¬ Conjugate (changeCoefficients modFour trivial) (changeCoefficients modFour tau) := by
  rintro ⟨u, hu⟩
  have h := congrArg (fun ρ : MatrixRep (ZMod 4) C2 (Fin 2) => ρ generator) hu
  rw [conjugate_apply] at h
  have htriv : (changeCoefficients modFour trivial) generator = 1 := by
    simp [changeCoefficients, trivial]
  rw [htriv, mul_one, Units.mul_inv] at h
  have hd := congrArg Matrix.det h
  rw [Matrix.det_one] at hd
  have hs : ((changeCoefficients modFour tau) generator).det = -1 := by
    change (modFour.mapMatrix (tau generator)).det = _
    rw [← RingHom.map_det, sign_generator_det]
    simp
  rw [hs] at hd
  exact (by decide : (1 : ZMod 4) ≠ -1) hd

end PaperX.PrecisionBoundary
