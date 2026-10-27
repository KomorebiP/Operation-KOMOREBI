import PaperX.AffineMonodromy
import PaperX.NilpotentExponential
import PaperX.MonodromyReconstruction

set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionExamples
open PaperX.AffineMonodromy PaperX.WeilSpecialChain PaperX.SpecialMonodromy
open PaperX.MonodromyReconstruction

def chosenCocycle : TwistedCocycle ν := ⟨t, cocycle_identity⟩
def good3 : Representation ℚ G (Fin 3 → ℚ) := reconstruct datum3 chosenCocycle

theorem exponential_coordinates (s : ℚ) (x : Fin 3 → ℚ) :
    PaperX.NilpotentExponential.expN datum3.N s x =
      ![x 0 + s * x 1 + (s ^ 2 / 2) * x 2, x 1 + s * x 2, x 2] := by
  rw [PaperX.NilpotentExponential.expN_sum nonzero_monodromy.2]
  funext j
  fin_cases j <;>
    simp [Finset.sum_range_succ, smul_pow, datum3, chain, chainDatum,
      shift_pow_apply]
  ring

theorem translated_coordinates (x : Fin 3 → ℚ) :
    good3 u x = ![x 0 + x 1 + (1/2) * x 2, x 1 + x 2, x 2] := by
  simp [good3, chosenCocycle, reconstruct_apply, unipotent,
    translation_value.1, translation_action, exponential_coordinates]

theorem dilated_coordinates (x : Fin 3 → ℚ) :
    good3 d x = ![x 0, 3 * x 1, 9 * x 2] := by
  simp only [good3, reconstruct_apply, chosenCocycle, dilation_value.1,
    unipotent_zero, Module.End.one_apply]
  funext j
  fin_cases j <;> norm_num [dilation_action]
  rfl

theorem translation_is_nontrivial : good3 u ≠ 1 := by
  intro h
  have he := congrArg (fun A : Module.End ℚ (Fin 3 → ℚ) => A ![0, 1, 0] 0) h
  simp [translated_coordinates] at he

theorem dilation_translation_coordinates (x : Fin 3 → ℚ) :
    good3 (d * u) x = ![x 0 + x 1 + (1/2) * x 2, 3 * x 1 + 3 * x 2, 9 * x 2] := by
  rw [map_mul, Module.End.mul_apply, translated_coordinates, dilated_coordinates]
  ext j
  fin_cases j <;> simp
  ring

theorem translation_dilation_coordinates (x : Fin 3 → ℚ) :
    good3 (u * d) x = ![x 0 + 3 * x 1 + (9/2) * x 2, 3 * x 1 + 9 * x 2, 9 * x 2] := by
  rw [map_mul, Module.End.mul_apply, dilated_coordinates, translated_coordinates]
  ext j
  fin_cases j <;> simp
  ring

theorem exact_group_inverse (g : G) : good3 g * good3 g⁻¹ = 1 :=
  reconstruct_inverse datum3 chosenCocycle g

theorem quadratic_term_required : good3 u ≠ 1 + datum3.N := by
  intro h
  have he := congrArg (fun A : Module.End ℚ (Fin 3 → ℚ) => A ![0, 0, 1] 0) h
  simp [translated_coordinates, datum3, chain, chainDatum, shift_apply] at he

theorem ordinary_additivity_fails : t (d * u) ≠ t d + t u := by
  rw [product_values.1, dilation_value.1, translation_value.1]
  norm_num

def wrongOrder (g : G) : Module.End ℚ (Fin 3 → ℚ) :=
  datum3.r g * PaperX.NilpotentExponential.expN datum3.N (t g)

theorem wrong_order_fails : wrongOrder (u * d) ≠ wrongOrder u * wrongOrder d := by
  intro h
  have he := congrArg (fun A : Module.End ℚ (Fin 3 → ℚ) => A ![0, 1, 0] 0) h
  simp only [wrongOrder, map_mul, Module.End.mul_apply, product_values.2,
    translation_value.1, dilation_value.1, translation_action,
    PaperX.NilpotentExponential.expN_zero, Module.End.one_apply] at he
  simp [exponential_coordinates, dilation_action] at he


end PaperX.ReconstructionExamples
