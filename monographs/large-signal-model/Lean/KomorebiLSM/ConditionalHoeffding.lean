import KomorebiLSM.PredictableResidual
import KomorebiLSM.ConditionalBernoulli
import Mathlib.MeasureTheory.Function.ConditionalExpectation.PullOut

/-! Sharp conditional Hoeffding bounds from ordinary conditional expectations.
No conditional-distribution kernel or Standard Borel sample space is used. -/
set_option autoImplicit false
namespace Komorebi.LSM.ConditionalHoeffding
open MeasureTheory ProbabilityTheory Real
open scoped BigOperators NNReal
variable {Ω : Type*} [mΩ : MeasurableSpace Ω]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- The bounded test's actual centered exponential is integrable. -/
theorem centered_exp_integrable {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (X : Ω → ℝ) (hX : @Measurable Ω ℝ mΩ _ X) (hb : ∀ᵐ ω∂μ,X ω∈Set.Icc (0:ℝ) 1)
    (θ : ℝ) : Integrable (fun ω => exp (θ*(X ω-(μ[X|m]) ω))) μ := by
  let : MeasurableSpace Ω := mΩ
  have hmean := PredictableResidual.conditional_mean_mem_Icc hm X hX hb
  have hres : ∀ᵐ ω∂μ,X ω-(μ[X|m]) ω∈Set.Icc (-1:ℝ) 1 := by
    filter_upwards [hb,hmean] with ω h h' using ⟨by linarith [h.1,h'.2],by linarith [h.2,h'.1]⟩
  exact integrable_exp_mul_of_mem_Icc
    ((hX.sub (stronglyMeasurable_condExp.measurable.mono hm le_rfl)).aemeasurable) hres

/-- The actual conditional centered MGF is bounded on an arbitrary probability
space. The real parameter is fixed before the almost-everywhere conclusion. -/
theorem centered_condExp_le {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (X : Ω → ℝ) (hX : @Measurable Ω ℝ mΩ _ X) (hb : ∀ᵐ ω∂μ,X ω∈Set.Icc (0:ℝ) 1)
    (θ : ℝ) :
    (μ[fun ω => exp (θ*(X ω-(μ[X|m]) ω))|m])≤ᵐ[μ] fun _ => exp (θ^2/8) := by
  let : MeasurableSpace Ω := mΩ
  let M : Ω → ℝ := μ[X|m]
  have hi : Integrable X μ := Integrable.of_mem_Icc (0:ℝ) 1 hX.aemeasurable hb
  have hmean : ∀ᵐ ω∂μ,M ω∈Set.Icc (0:ℝ) 1 :=
    PredictableResidual.conditional_mean_mem_Icc hm X hX hb
  have hexp : Integrable (fun ω => exp (θ*X ω)) μ :=
    integrable_exp_mul_of_mem_Icc hX.aemeasurable hb
  have haff : Integrable (fun ω => (exp θ-1)*X ω+1) μ :=
    (hi.const_mul (exp θ-1)).add (integrable_const 1)
  have hsec : (fun ω => exp (θ*X ω))≤ᵐ[μ] fun ω => (exp θ-1)*X ω+1 := by
    filter_upwards [hb] with ω hω
    have he := ConditionalBernoulli.exp_secant θ (X ω) hω
    nlinarith
  have hmono := condExp_mono (m := m) hexp haff hsec
  have haf : (fun ω => (exp θ-1)*M ω+1)=ᵐ[μ]
      μ[fun ω => (exp θ-1)*X ω+1|m] := by
    simpa only [smul_apply,ContinuousLinearMap.id_apply,smul_eq_mul] using
      (ContinuousLinearMap.comp_condExp_add_const_comm hm hi
        ((exp θ-1) • ContinuousLinearMap.id ℝ ℝ) (1:ℝ))
  have hsm : StronglyMeasurable[m] (fun ω => exp (-θ*M ω)) :=
    continuous_exp.comp_stronglyMeasurable (stronglyMeasurable_const.mul stronglyMeasurable_condExp)
  have hbound : ∀ᵐ ω∂μ,‖exp (-θ*M ω)‖≤exp |θ| := by
    filter_upwards [hmean] with ω hω
    rw [Real.norm_eq_abs,abs_of_pos (exp_pos _)]
    apply exp_le_exp.mpr
    calc
      -θ*M ω ≤ |-θ*M ω| := le_abs_self _
      _ = |θ| * |M ω| := by rw [abs_mul,abs_neg]
      _ ≤ |θ| *1 := mul_le_mul_of_nonneg_left (by simpa only [abs_of_nonneg hω.1] using hω.2) (abs_nonneg _)
      _ = _ := mul_one _
  have hpull := condExp_stronglyMeasurable_mul_of_bound hm hsm hexp (exp |θ|) hbound
  have heq : (fun ω => exp (θ*(X ω-M ω)))=
      (fun ω => exp (-θ*M ω))*(fun ω => exp (θ*X ω)) := by
    funext ω
    rw [Pi.mul_apply,← exp_add]
    congr 1
    ring
  change (μ[fun ω => exp (θ*(X ω-M ω))|m])≤ᵐ[μ] fun _ => exp (θ^2/8)
  rw [heq]
  filter_upwards [hpull,hmono,haf,hmean] with ω hp hm' ha hM
  simp only [Pi.mul_apply] at hp
  calc
    _ = exp (-θ*M ω)*(μ[fun ω => exp (θ*X ω)|m]) ω := hp
    _ ≤ exp (-θ*M ω)*((exp θ-1)*M ω+1) :=
      mul_le_mul_of_nonneg_left (hm'.trans_eq ha.symm) (exp_pos _).le
    _ = exp (-θ*M ω)*((1-M ω)+M ω*exp θ) := by ring
    _ ≤ _ := ConditionalBernoulli.centered_bernoulli_bound θ (M ω) hM

end Komorebi.LSM.ConditionalHoeffding
