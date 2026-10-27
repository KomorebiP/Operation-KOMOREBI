import Komorebi.RationalModelSemantics
import Komorebi.RationalCandidateAcceptance
import Komorebi.PosteriorEnclosureBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix MeasureTheory Komorebi.PacketEnergy Komorebi.FiniteDimensionalGaussianKalman
open Komorebi.QuadraticTransport
open scoped ENNReal

variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

theorem valid_residual_energy_bound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) :
    frobeniusSq (gainResidual (realMatrix M.observationMatrix) (realMatrix M.prior)
      (realMatrix M.noise) (realMatrix c.gain)) ≤ (totalUpper c : ℝ) := by
  rw [← M.real_residual]
  have hb := frobeniusSq_le_packet_majorants
    (realPackets Q h.2.1) (realPackets D h.2.2.1)
    (realPackets_complete Q h.2.1) (realPackets_complete D h.2.2.1)
    (realMatrix (M.residual c.gain)) (fun a b => (c.packetUpper a b : ℝ))
    (rational_packet_majorant Q D h.2.1 h.2.2.1 _ _ h.2.2.2.1)
  simpa [totalUpper] using hb

theorem valid_innovation_energy_bound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) :
    ‖realVector M.observation - matrixCLM (realMatrix M.observationMatrix) (realVector M.mean)‖^2
      ≤ (c.innovationUpper : ℝ) := by
  rw [← M.real_innovationVector, ← rationalVectorEnergy_cast]
  exact_mod_cast h.2.2.2.2

/-- The exact finite checker implies an upper bound on actual posterior distribution error. -/
theorem checked_score_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (hc : checkCandidate M Q D c = true) :
    wasserstein2Sq M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (candidateScore M c : ℝ) := by
  have h := (checkCandidate_eq_true M Q D c).mp hc
  have hb := posterior_wasserstein2Sq_le_energy_majorants
    (realMatrix M.observationMatrix) (realVector M.mean) (realMatrix M.prior)
    (realMatrix M.noise) (realMatrix c.gain) (realVector M.observation)
    M.prior_real_posSemidef (M.noise_real_posDef h.1)
    (M.noiseFloor : ℝ) (by exact_mod_cast h.1) M.noise_real_floor
    (totalUpper c : ℝ) (c.innovationUpper : ℝ)
    (valid_residual_energy_bound M Q D c h) (valid_innovation_energy_bound M Q D c h)
  simpa [RationalModel.posterior, RationalModel.approximation, candidateScore, pow_two] using hb

/-- Kernel-checked rational accept and tolerance decisions imply the desired real-law tolerance. -/
theorem checked_tolerance_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (ε : ℚ) (hc : checkCandidate M Q D c = true) (ht : checkTolerance M c ε = true) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := (checkCandidate_eq_true M Q D c).mp hc
  have ht' := (checkTolerance_iff_score M c ε h.1).mp ht
  apply wasserstein2_le_of_sq_le _ _ (ε : ℝ) (by exact_mod_cast ht'.1)
  apply (checked_score_bounds_posterior M Q D c hc).trans
  apply ENNReal.ofReal_le_ofReal
  have hh : (candidateScore M c : ℝ) ≤ ((ε^2 : ℚ) : ℝ) := by exact_mod_cast ht'.2
  simpa [pow_two] using hh

/-- A checked incumbent remains sound under any finite batch of untrusted proposals. -/
theorem selected_batch_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (c : RationalCandidate ι κ α β) (ps : List (RationalCandidate ι κ α β))
    (hc : checkCandidate M Q D c = true) :
    wasserstein2Sq M.posterior (M.approximation (selectCandidates M Q D c ps).gain) ≤
      ENNReal.ofReal (candidateScore M c : ℝ) := by
  have hv := selectCandidates_valid M Q D c ps ((checkCandidate_eq_true M Q D c).mp hc)
  apply (checked_score_bounds_posterior M Q D _ ((checkCandidate_eq_true M Q D _).mpr hv)).trans
  apply ENNReal.ofReal_le_ofReal
  exact_mod_cast selectCandidates_score_le M Q D c ps

/-- A certified posterior tolerance survives the validity-preserving finite acceptance policy. -/
theorem selected_batch_preserves_posterior_tolerance (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (c : RationalCandidate ι κ α β) (ps : List (RationalCandidate ι κ α β))
    (ε : ℚ) (hc : checkCandidate M Q D c = true) (ht : checkTolerance M c ε = true) :
    wasserstein2 M.posterior (M.approximation (selectCandidates M Q D c ps).gain) ≤
      ENNReal.ofReal (ε : ℝ) := by
  have hv := (checkCandidate_eq_true M Q D c).mp hc
  exact checked_tolerance_bounds_posterior M Q D _ ε
    ((checkCandidate_eq_true M Q D _).mpr (selectCandidates_valid M Q D c ps hv))
    (selectCandidates_preserves_tolerance M Q D c ps hv ε ht)

end Komorebi.ExactPosterior
