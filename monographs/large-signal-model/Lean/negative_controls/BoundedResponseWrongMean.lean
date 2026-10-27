import KomorebiLSM.BoundedResponseNoise
open MeasureTheory ProbabilityTheory
open Komorebi.LSM.RegressionConfidence Komorebi.LSM.BoundedResponseNoise
noncomputable def response (_ : Unit) : ℝ := 1
/-- The actual centered noise does satisfy the claimed bounded-response scale. -/
theorem actual_centered : ConditionalSubgaussian (m := ⊥) bot_le
    (fun ω => response ω-((Measure.dirac ())[response|⊥]) ω) 1 (Measure.dirac ()) := by
  convert centered_interval (μ := Measure.dirac ()) (m := ⊥) bot_le response measurable_const
    (-1) 1 (by norm_num) (ae_of_all _ (fun _ => by norm_num [response])) using 1; norm_num
/- Replacing the actual conditional mean one by an incorrect prediction zero
makes the uncentered exponential fail its proposed sigma-one envelope. -/
example : (((Measure.dirac ())[fun ω => Real.exp (response ω)|⊥]) ())≤Real.exp (1/2) := by
  simp only [condExp_bot,response,integral_const,probReal_univ,one_smul]
  rw [Real.exp_le_exp]
  norm_num
