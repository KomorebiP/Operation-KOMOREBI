import PaperX.ReconstructionExamples
import PaperX.UnipotentLogarithm

/-! Checked limits of the quadratic logarithm and of zero-parameter sampling. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionBoundary
open PaperX.AffineMonodromy PaperX.ReconstructionExamples
open PaperX.WeilSpecialChain PaperX.SpecialMonodromy
open PaperX.NilpotentExponential PaperX.UnipotentLogarithm
open PaperX.MonodromyReconstruction

def datum4 : PaperX.WeilData.Datum ν (Fin 4 → ℚ) := chain ℚ 4

theorem quartic_nilpotence : datum4.N ^ 3 ≠ 0 ∧ datum4.N ^ 4 = 0 :=
  ⟨shift_previous_power_nonzero 4 (by decide), shift_nilpotent 4⟩

theorem quartic_exponential_coordinates (s : ℚ) (x : Fin 4 → ℚ) :
    expN datum4.N s x =
      ![x 0 + s * x 1 + (s ^ 2 / 2) * x 2 + (s ^ 3 / 6) * x 3,
        x 1 + s * x 2 + (s ^ 2 / 2) * x 3, x 2 + s * x 3, x 3] := by
  rw [expN_sum quartic_nilpotence.2]
  funext j
  fin_cases j <;>
    simp [Finset.sum_range_succ, smul_pow, datum4, chain, chainDatum,
      shift_pow_apply, Nat.factorial] <;> ring

theorem quadratic_log_error :
    log₂ (expN datum4.N 1) ![0, 0, 0, 1] 0 = -(1/3 : ℚ) := by
  norm_num [log₂, pow_two, Module.End.mul_apply, LinearMap.sub_apply,
    quartic_exponential_coordinates, Matrix.cons_val_two, Matrix.cons_val_three]

theorem quadratic_log_fails_beyond_cube : log₂ (expN datum4.N 1) ≠ datum4.N := by
  intro h
  have he := congrArg (fun A : Module.End ℚ (Fin 4 → ℚ) => A ![0, 0, 0, 1] 0) h
  rw [quadratic_log_error] at he
  norm_num [datum4, chain, chainDatum, shift_apply] at he

theorem monodromy_nonzero : datum3.N ≠ 0 := by
  intro h
  have hn := nonzero_monodromy.1
  simp [h] at hn

theorem zero_sample_collision :
    expN datum3.N 0 = expN (0 : Module.End ℚ (Fin 3 → ℚ)) 0 ∧ datum3.N ≠ 0 := by
  exact ⟨by simp, monodromy_nonzero⟩

theorem zero_parameter_recovery_fails : recoverN 0 (expN datum3.N 0) ≠ datum3.N := by
  simpa [recoverN] using monodromy_nonzero.symm

theorem actual_translation_exponential : good3 u = expN datum3.N 1 := by
  ext x
  simp [good3, chosenCocycle, reconstruct_apply, unipotent,
    translation_value.1, translation_action]

theorem actual_monodromy_recovery : recoverN 1 (good3 u) = datum3.N := by
  rw [actual_translation_exponential]
  exact recoverN_expN nonzero_monodromy.2 (by norm_num)

theorem actual_fixed_vectors (x : Fin 3 → ℚ) : good3 u x = x ↔ datum3.N x = 0 := by
  rw [actual_translation_exponential]
  exact expN_fixed_iff nonzero_monodromy.2 (by norm_num) x

end PaperX.ReconstructionBoundary
