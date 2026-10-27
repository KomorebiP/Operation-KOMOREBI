import KomorebiLSM.PredictableResidualAffine
import Mathlib.Probability.Distributions.Bernoulli

open MeasureTheory ProbabilityTheory
private noncomputable def fair : Measure Bool :=
  bernoulliMeasure true false ⟨(1/2:ℝ),by constructor <;> norm_num⟩
private def unitTest (b : Bool) : ℝ := if b then 1 else 0
private def wideTest (b : Bool) : ℝ := 1+2*unitTest b

/- The affine interval has width two. Deleting that factor does not preserve
the actual conditional centered residual, even for the first fair observation. -/
example : wideTest true-(fair[wideTest | ⊥]) true=
    unitTest true-(fair[unitTest | ⊥]) true := by
  let : IsProbabilityMeasure fair := by unfold fair;infer_instance
  rw [condExp_bot,condExp_bot]
  change wideTest true-(∫ b,wideTest b∂bernoulliMeasure true false ⟨(1/2:ℝ),by constructor <;> norm_num⟩)=
    unitTest true-(∫ b,unitTest b∂bernoulliMeasure true false ⟨(1/2:ℝ),by constructor <;> norm_num⟩)
  rw [integral_bernoulliMeasure,integral_bernoulliMeasure]
  norm_num [wideTest,unitTest,smul_eq_mul]
