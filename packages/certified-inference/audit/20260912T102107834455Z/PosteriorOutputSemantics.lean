import Komorebi.PosteriorOutputPrecision
import Komorebi.RationalModelSemantics

noncomputable section
set_option autoImplicit false
namespace Komorebi.PosteriorOutput
open Matrix MeasureTheory ProbabilityTheory
open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.FiniteDimensionalGaussianKalman
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq ι] [DecidableEq κ]

omit [Fintype υ] [Fintype ω] in
theorem outputMean_real (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    realVector (outputMean M B) = gainMean (realMatrix M.observationMatrix)
      (realVector M.mean) (realMatrix B) (realVector M.observation) := by
  ext i
  simp [outputMean, realVector, gainMean, RationalModel.innovationVector,
    matrixCLM_apply, rational_mulVec_cast]

theorem outputCovariance_real (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    realMatrix (outputCovariance M B) = gainJoseph (realMatrix M.observationMatrix)
      (realMatrix M.prior) (realMatrix M.noise) (realMatrix B) := by
  simp only [outputCovariance, outputOperator, gainJoseph, realMatrix_add,
    realMatrix_mul, realMatrix_transpose, realMatrix_sub, realMatrix_one]

theorem outputCovariance_posSemidef (M : RationalModel ι κ υ ω)
    (hs : 0 < M.noiseFloor) (B : Matrix ι κ ℚ) :
    (realMatrix (outputCovariance M B)).PosSemidef := by
  rw [outputCovariance_real]
  exact gainJoseph_posSemidef _ _ _ _ M.prior_real_posSemidef
    (M.noise_real_posDef hs).posSemidef

/-- The enclosed arrays are parameters of precisely the law certified by the solver. -/
theorem approximation_eq_output_gaussian (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    M.approximation B =
      multivariateGaussian (realVector (outputMean M B)) (realMatrix (outputCovariance M B)) := by
  rw [outputMean_real, outputCovariance_real]
  rfl

/-- Each stored interval is also an enclosure in the semantic real coordinate space. -/
theorem represented_real_errors (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (δ : ℚ) (hδ : 0 < δ) :
    (∀ i, |(realVector (outputMean M B)) i -
      (((represent M B δ).mean i).center : ℝ)| ≤ (δ : ℝ)) ∧
    (∀ i j, |realMatrix (outputCovariance M B) i j -
      (((represent M B δ).covariance i j).center : ℝ)| ≤ (δ : ℝ)) := by
  obtain ⟨he,hr⟩ := represent_spec M B δ hδ
  constructor
  · intro i
    change |(outputMean M B i : ℝ) - (((represent M B δ).mean i).center : ℝ)| ≤ (δ : ℝ)
    exact_mod_cast (he.1 i).trans (hr.1 i)
  · intro i j
    change |(outputCovariance M B i j : ℝ) -
      (((represent M B δ).covariance i j).center : ℝ)| ≤ (δ : ℝ)
    exact_mod_cast (he.2 i j).trans (hr.2 i j)

end Komorebi.PosteriorOutput
