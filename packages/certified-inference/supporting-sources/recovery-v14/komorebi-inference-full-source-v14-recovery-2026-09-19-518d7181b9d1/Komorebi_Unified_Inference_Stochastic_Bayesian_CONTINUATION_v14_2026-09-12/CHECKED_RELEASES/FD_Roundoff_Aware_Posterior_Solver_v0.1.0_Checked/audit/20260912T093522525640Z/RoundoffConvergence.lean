import Komorebi.RoundedGainEvaluation
import Komorebi.RoundoffTracking
import Komorebi.RationalRichardsonConvergence

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.GainSolver
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [DecidableEq κ]

/-- This iteration executes the rounded update, not the ideal specification. -/
def roundedGain (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) : ℕ → Matrix ι κ ℚ :=
  iterate (roundedGainStep M t) B

@[simp] theorem roundedGain_zero (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) :
    roundedGain M t B 0 = B := rfl
@[simp] theorem roundedGain_succ (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) (n : ℕ) :
    roundedGain M t B (n+1) = roundedGainStep M t (roundedGain M t B n) := rfl

/-- Exact residual identity with the whole-update rounding defect exposed. -/
theorem rounded_residual_step (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) :
    M.residual (roundedGainStep M t B) =
      M.residual B*(1-M.solverStep • M.innovation)-
        (roundedGainStep M t B-exactGainStep M B)*M.innovation := by
  have h := residual_forced_step (M.prior*M.observationMatrix.transpose) M.innovation
    M.solverStep B (roundedGainStep M t B-exactGainStep M B)
  have hid : gainStep (M.prior*M.observationMatrix.transpose) M.innovation M.solverStep B +
      (roundedGainStep M t B-exactGainStep M B) = roundedGainStep M t B := by
    change exactGainStep M B+(roundedGainStep M t B-exactGainStep M B) = _
    abel
  rw [hid] at h
  exact h

/-- Uniform error tube for actual rounded iterates, valid for every iteration number. -/
theorem roundedGain_tracking (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (t : ℕ) (B : Matrix ι κ ℚ) (n : ℕ) :
    rationalEnergy (roundedGain M t B n-M.solverGain B n) ≤
      6*(entryCount ι κ*(mesh t)^2)/(1-M.solverRate)^2 := by
  exact iterate_tracking_energy (M.prior*M.observationMatrix.transpose) M.innovation
    M.solverStep M.solverRate (entryCount ι κ*(mesh t)^2) (roundedGainStep M t) B
    (M.solverRate_bounds hs).1 (M.solverRate_bounds hs).2
    (mul_nonneg entryCount_nonneg (sq_nonneg _)) (M.residual_energy_transition hs)
    (rounded_step_energy_error M t) n

/-- Exact model-dependent conversion of residual energy to posterior certificate score. -/
def scoreWeight (M : RationalModel ι κ υ ω) : ℚ :=
  (M.noiseFloor+rationalVectorEnergy M.innovationVector)/M.noiseFloor^2

theorem scoreWeight_nonneg (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 ≤ scoreWeight M := by
  exact div_nonneg (add_nonneg hs.le (rationalVectorEnergy_nonneg _)) (sq_nonneg _)

theorem residualScore_eq_energy_weight (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    M.residualScore B = rationalEnergy (M.residual B)*scoreWeight M := by
  unfold RationalModel.residualScore scoreWeight
  ring

/-- An explicit coefficient for the update-induced squared-score floor. -/
def roundoffScoreCoeff (M : RationalModel ι κ υ ω) : ℚ :=
  12*entryCount ι κ*rationalEnergy M.innovation*scoreWeight M/(1-M.solverRate)^2

theorem roundoffScoreCoeff_nonneg (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 ≤ roundoffScoreCoeff M := by
  unfold roundoffScoreCoeff
  have := (entryCount_nonneg (ι := ι) (κ := κ))
  have := rationalEnergy_nonneg M.innovation
  have := scoreWeight_nonneg M hs
  positivity

/-- Certificate floor and ideal progress remain separate in the quantitative bound. -/
theorem rounded_score_compare (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (t : ℕ) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (roundedGain M t B n) ≤
      2*M.residualScore (M.solverGain B n)+roundoffScoreCoeff M*(mesh t)^2 := by
  have h := residual_energy_compare (M.prior*M.observationMatrix.transpose) M.innovation
    (roundedGain M t B n) (M.solverGain B n)
  have ht := roundedGain_tracking M hs t B n
  have hm := mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left ht (by norm_num : (0:ℚ)≤2))
    (rationalEnergy_nonneg M.innovation)
  have hb : rationalEnergy (M.residual (roundedGain M t B n)) ≤
      2*rationalEnergy (M.residual (M.solverGain B n))+
      2*(6*(entryCount ι κ*(mesh t)^2)/(1-M.solverRate)^2)*rationalEnergy M.innovation := by
    exact h.trans (add_le_add le_rfl hm)
  have hw := mul_le_mul_of_nonneg_right hb (scoreWeight_nonneg M hs)
  rw [residualScore_eq_energy_weight, residualScore_eq_energy_weight]
  calc
    _ ≤ (2*rationalEnergy (M.residual (M.solverGain B n))+
      2*(6*(entryCount ι κ*(mesh t)^2)/(1-M.solverRate)^2)*rationalEnergy M.innovation)*scoreWeight M := hw
    _ = _ := by unfold roundoffScoreCoeff; ring

theorem rounded_score_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (t : ℕ) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (roundedGain M t B n) ≤
      2*M.solverRate^n*M.residualScore B+roundoffScoreCoeff M*(mesh t)^2 := by
  apply (rounded_score_compare M hs t B n).trans
  have h := mul_le_mul_of_nonneg_left (M.solver_score_geometric hs B n)
    (by norm_num : (0:ℚ)≤2)
  nlinarith only [h]

/-- Global local-error precision: positivity of tolerance is required only by the proof. -/
def updateAccuracy (M : RationalModel ι κ υ ω) (ε : ℚ) : ℕ :=
  precisionFor (roundoffScoreCoeff M) (ε^2/8)

def roundedFuel (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (ε : ℚ) : ℕ :=
  M.solverFuel B (ε/4)

/-- Precision is selected so the update floor fits strictly inside the posterior tolerance. -/
theorem selected_update_floor (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (ε : ℚ) (hε : 0 < ε) (t : ℕ) (ht : updateAccuracy M ε ≤ t) :
    roundoffScoreCoeff M*(mesh t)^2 ≤ ε^2/8 := by
  have hm : (mesh t)^2 ≤ mesh t := by
    nlinarith only [(mesh_pos t).le, mesh_le_one t]
  exact (mul_le_mul_of_nonneg_left hm (roundoffScoreCoeff_nonneg M hs)).trans
    (coefficient_mesh_le _ _ (by positivity) t ht)

/-- At the computed horizon the genuinely rounded solver has exact-certificate slack. -/
theorem rounded_score_at_fuel (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (ε : ℚ) (hε : 0 < ε) (t : ℕ) (ht : updateAccuracy M ε ≤ t)
    (B : Matrix ι κ ℚ) (n : ℕ) (hn : roundedFuel M B ε ≤ n) :
    M.residualScore (roundedGain M t B n) ≤ ε^2/4 := by
  have he := M.solver_score_at_fuel hs B (ε/4) (by positivity) n hn
  have hf := selected_update_floor M hs ε hε t ht
  have hb := rounded_score_compare M hs t B n
  nlinarith only [he,hf,hb]

end Komorebi.RoundoffSolver
