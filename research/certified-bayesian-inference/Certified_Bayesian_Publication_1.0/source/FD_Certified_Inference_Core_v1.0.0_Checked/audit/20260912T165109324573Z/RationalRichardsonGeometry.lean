import Komorebi.RationalRichardsonDefs
import Komorebi.RationalModelSemantics
import Komorebi.RichardsonEnergy

noncomputable section
set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.GainSolver Komorebi.FiniteDimensionalGaussianKalman Komorebi.PacketEnergy
variable {ι κ υ ω : Type*} [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq κ]

omit [Fintype ι] [Fintype υ] [Fintype ω] [DecidableEq κ] in
/-- Trace is preserved by the exact rational embedding. -/
theorem realMatrix_trace (S : Matrix κ κ ℚ) : (S.trace : ℝ) = (realMatrix S).trace := by
  simp [Matrix.trace, realMatrix]

namespace RationalModel

/-- The existing Gram model witnesses supply innovation positivity. -/
theorem innovation_real_posSemidef (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    (realMatrix M.innovation).PosSemidef := by
  rw [M.real_innovation]
  exact (innovationMatrix_posDef _ _ _ M.prior_real_posSemidef (M.noise_real_posDef hs)).posSemidef

theorem innovation_real_floor (M : RationalModel ι κ υ ω) :
    QuadraticLowerBound (realMatrix M.innovation) (M.noiseFloor : ℝ) := by
  rw [M.real_innovation]
  exact innovation_quadraticLowerBound _ _ _ M.prior_real_posSemidef _ M.noise_real_floor

theorem innovation_trace_nonneg (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 ≤ M.innovation.trace := by
  have h := psd_trace_nonneg _ (M.innovation_real_posSemidef hs)
  rw [← realMatrix_trace] at h
  exact_mod_cast h

/-- The chosen cap is positive and at least the noise floor, without an eigenvalue oracle. -/
theorem spectralCap_bounds (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 < M.spectralCap ∧ M.noiseFloor ≤ M.spectralCap := by
  have ht := M.innovation_trace_nonneg hs
  dsimp [spectralCap]
  constructor <;> linarith

theorem solverRho_bounds (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 ≤ M.solverRho ∧ M.solverRho < 1 := by
  have hb := M.spectralCap_bounds hs
  dsimp [solverRho]
  constructor
  · exact sub_nonneg.mpr ((div_le_one hb.1).mpr hb.2)
  · have hp := div_pos hs hb.1
    linarith

/-- The energy contraction factor is strictly below one, including factor-zero cases. -/
theorem solverRate_bounds (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor) :
    0 ≤ M.solverRate ∧ M.solverRate < 1 := by
  have h := M.solverRho_bounds hs
  dsimp [solverRate]
  constructor
  · exact sq_nonneg _
  · nlinarith

/-- Certified spectral contraction transported to exact rational residual energies. -/
theorem residual_energy_transition (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (F : Matrix ι κ ℚ) :
    rationalEnergy (F*(1-M.solverStep • M.innovation)) ≤ M.solverRate*rationalEnergy F := by
  have h := trace_step_energy_contract (realMatrix M.innovation)
    (M.innovation_real_posSemidef hs) (M.noiseFloor : ℝ) (by exact_mod_cast hs)
    M.innovation_real_floor (realMatrix F)
  have hc : (M.spectralCap : ℝ) = (M.noiseFloor : ℝ)+(realMatrix M.innovation).trace := by
    simp only [spectralCap, Rat.cast_add, realMatrix_trace]
  have he : (rationalEnergy (F*(1-M.solverStep • M.innovation)) : ℝ) =
      matrixEnergy ((realMatrix F)*(1-((M.noiseFloor : ℝ)+
        (realMatrix M.innovation).trace)⁻¹ • realMatrix M.innovation)) := by
    rw [rationalEnergy_cast]
    simp only [realMatrix_mul, realMatrix_sub, realMatrix_one, realMatrix_smul,
      solverStep, Rat.cast_inv, hc]
  rw [← he, ← rationalEnergy_cast] at h
  have hr : (M.solverRate : ℝ) =
      (1-(M.noiseFloor : ℝ)/((M.noiseFloor : ℝ)+(realMatrix M.innovation).trace))^2 := by
    simp only [solverRate, solverRho, Rat.cast_pow, Rat.cast_sub, Rat.cast_one, Rat.cast_div, hc]
  rw [← hr] at h
  exact_mod_cast h
end RationalModel
end Komorebi.ExactPosterior
