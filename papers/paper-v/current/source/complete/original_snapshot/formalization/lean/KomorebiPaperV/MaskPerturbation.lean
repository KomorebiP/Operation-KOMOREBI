import Mathlib.MeasureTheory.Function.LpSeminorm.Indicator
import Mathlib.MeasureTheory.Function.LpSeminorm.TriangleInequality
import Mathlib.Basic.Complex.Basic
import Mathlib.Tactic

/-! Author: Komorebi P. Measurable jump-mask perturbations, with extended Lp norms. -/
namespace KomorebiPaperV.MaskPerturbation
open MeasureTheory
open scoped ENNReal symmDiff
variable {Ω : Type*} [MeasurableSpace Ω]

noncomputable def jump (S : Set Ω) (a : ℂ) : Ω → ℂ := S.indicator (fun _ => a)

theorem jump_measurable (S : Set Ω) (hS : MeasurableSet S) (a : ℂ) (μ : Measure Ω) :
    AEStronglyMeasurable (jump S a) μ :=
  (stronglyMeasurable_const.indicator hS).aestronglyMeasurable

theorem symmetric_difference_norm (μ : Measure Ω) (S T : Set Ω)
    (hS : MeasurableSet S) (hT : MeasurableSet T) (p : ENNReal)
    (hp : p ≠ 0) (hpTop : p ≠ ∞) (a : ℂ) :
    eLpNorm (jump S a-jump T a) p μ = ‖a‖ₑ * μ (S ∆ T) ^ (1 / p.toReal) := by
  rw [jump, jump, eLpNorm_indicator_sub_indicator]
  exact eLpNorm_indicator_const (hS.symmDiff hT) hp hpTop

theorem indicator_difference_norm (μ : Measure Ω) (S T : Set Ω)
    (hS : MeasurableSet S) (hT : MeasurableSet T) (p : ENNReal)
    (hp : p ≠ 0) (hpTop : p ≠ ∞) :
    eLpNorm (jump S 1-jump T 1) p μ = μ (S ∆ T) ^ (1 / p.toReal) := by
  simpa using symmetric_difference_norm μ S T hS hT p hp hpTop 1

omit [MeasurableSpace Ω] in
theorem jump_sub_same_set (S : Set Ω) (a b : ℂ) : jump S a-jump S b = jump S (a-b) := by
  classical
  funext x
  by_cases hx : x ∈ S <;> simp [jump, hx]

omit [MeasurableSpace Ω] in
theorem jump_error_decomposition (S T : Set Ω) (a b : ℂ) :
    jump S a-jump T b = jump S (a-b)+(jump S b-jump T b) := by
  rw [← jump_sub_same_set]
  abel

theorem finite_p_perturbation (μ : Measure Ω) (S T : Set Ω)
    (hS : MeasurableSet S) (hT : MeasurableSet T) (p : ENNReal)
    (hp : 1 ≤ p) (hpTop : p ≠ ∞) (a b : ℂ) :
    eLpNorm (jump S a-jump T b) p μ ≤
      ‖a-b‖ₑ * μ S ^ (1 / p.toReal) + ‖b‖ₑ * μ (S ∆ T) ^ (1 / p.toReal) := by
  have hp0 : p ≠ 0 := ne_of_gt (lt_of_lt_of_le (by norm_num) hp)
  rw [jump_error_decomposition]
  calc
    _ ≤ eLpNorm (jump S (a-b)) p μ + eLpNorm (jump S b-jump T b) p μ :=
      eLpNorm_add_le (jump_measurable S hS (a-b) μ)
        ((jump_measurable S hS b μ).sub (jump_measurable T hT b μ)) hp
    _ = _ := by
      rw [symmetric_difference_norm μ S T hS hT p hp0 hpTop,
        jump, eLpNorm_indicator_const hS hp0 hpTop]

omit [MeasurableSpace Ω] in
theorem pointwise_sup_bound (S T : Set Ω) (a b : ℂ) (x : Ω) :
    ‖(jump S a-jump T b) x‖ ≤ ‖a-b‖ + if S ∆ T = ∅ then 0 else ‖b‖ := by
  classical
  rw [jump_error_decomposition]
  calc
    _ ≤ ‖jump S (a-b) x‖ + ‖(jump S b-jump T b) x‖ := norm_add_le _ _
    _ ≤ ‖a-b‖ + if S ∆ T = ∅ then 0 else ‖b‖ := by
      apply add_le_add
      · by_cases hx : x ∈ S <;> simp [jump, hx]
      · by_cases he : S ∆ T = ∅
        · have hST : S = T := symmDiff_eq_bot.mp he
          simp [hST]
        · by_cases hx : x ∈ S <;> by_cases hy : x ∈ T <;> simp [jump, hx, hy, he]

theorem infinity_perturbation (μ : Measure Ω) (S T : Set Ω) (a b : ℂ) :
    eLpNorm (jump S a-jump T b) ∞ μ ≤
      ENNReal.ofReal (‖a-b‖ + if S ∆ T = ∅ then 0 else ‖b‖) := by
  rw [eLpNorm_exponent_top]
  exact eLpNormEssSup_le_of_ae_bound (ae_of_all μ (pointwise_sup_bound S T a b))

theorem full_signal_perturbation (μ : Measure Ω) (S T : Set Ω)
    (hS : MeasurableSet S) (hT : MeasurableSet T) (p : ENNReal)
    (hp : 1 ≤ p) (hpTop : p ≠ ∞) (a b : ℂ) (s t : Ω → ℂ)
    (hs : AEStronglyMeasurable s μ) (ht : AEStronglyMeasurable t μ) :
    eLpNorm ((s+jump S a)-(t+jump T b)) p μ ≤ eLpNorm (s-t) p μ +
      (‖a-b‖ₑ * μ S ^ (1/p.toReal) + ‖b‖ₑ * μ (S ∆ T) ^ (1/p.toReal)) := by
  have he : (s+jump S a)-(t+jump T b) = (s-t)+(jump S a-jump T b) := by abel
  rw [he]
  exact (eLpNorm_add_le (hs.sub ht)
    ((jump_measurable S hS a μ).sub (jump_measurable T hT b μ)) hp).trans
      (add_le_add_right (finite_p_perturbation μ S T hS hT p hp hpTop a b) _)

end KomorebiPaperV.MaskPerturbation
