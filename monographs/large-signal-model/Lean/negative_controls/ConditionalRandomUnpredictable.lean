import KomorebiLSM.ConditionalRandomMultiplier
import KomorebiLSM.ConditionalHoeffding
import Mathlib.Probability.Distributions.Bernoulli
/- Negative control: deterministic conditional bounds do not justify a
coefficient chosen after seeing the same noise. -/
set_option autoImplicit false
namespace ConditionalRandomUnpredictable
open MeasureTheory ProbabilityTheory Real
open Komorebi.LSM.RegressionConfidence Komorebi.LSM.ConditionalHoeffding
noncomputable def coin : Measure Bool := bernoulliMeasure true false ⟨1/2,by norm_num⟩
instance : IsProbabilityMeasure coin := by unfold coin; infer_instance
def observation (b : Bool) : ℝ := if b then 1 else 0
noncomputable def noise (b : Bool) : ℝ := observation b-1/2
theorem mean : (coin[observation|⊥])=(fun _ => (1/2:ℝ)) := by
  rw [condExp_bot]
  rw [show coin=bernoulliMeasure true false ⟨1/2,by norm_num⟩ from rfl,integral_bernoulliMeasure]
  norm_num [observation,smul_eq_mul]
/-- All deterministic coefficients satisfy the genuine conditional assumptions. -/
theorem actual_hypotheses : ConditionalSubgaussian (m := ⊥) bot_le noise (1/2) coin := by
  have hm : Measurable observation := measurable_of_countable _
  have hb : ∀ᵐ b∂coin,observation b∈Set.Icc (0:ℝ) 1 :=
    ae_of_all _ (fun b => by cases b <;> norm_num [observation])
  refine ⟨measurable_of_countable _,?_,?_⟩
  · intro h
    simpa only [mean,noise] using centered_exp_integrable (μ := coin) bot_le observation hm hb h
  · intro h
    have hc := centered_condExp_le (μ := coin) bot_le observation hm hb h
    have he : h^2*(1/2:ℝ)^2/2=h^2/8 := by ring
    simpa only [mean,noise,he] using hc
/-- Choosing a=4ξ after the noise makes the normalized factor e^(1/2)>1. -/
example : (∫ b,factor noise (1/2) (fun b => 4*noise b) b∂coin)≤1 := by
  have hf (b : Bool) : factor noise (1/2) (fun b => 4*noise b) b=exp (1/2) := by
    cases b <;> norm_num [factor,noise,observation]
  have hi : (∫ b,factor noise (1/2) (fun b => 4*noise b) b∂coin)=exp (1/2) := by
    calc (∫ b,factor noise (1/2) (fun b => 4*noise b) b∂coin)=∫ _ : Bool,exp (1/2:ℝ)∂coin :=
        integral_congr_ae (ae_of_all _ hf)
      _ = exp (1/2:ℝ) := by
        rw [integral_const,smul_eq_mul,measureReal_def,measure_univ,ENNReal.toReal_one,one_mul]
  rw [hi]
  have hn : ¬exp (1/2:ℝ)≤1 := not_le.mpr (one_lt_exp_iff.mpr (by norm_num))
  simp only [hn]
end ConditionalRandomUnpredictable
