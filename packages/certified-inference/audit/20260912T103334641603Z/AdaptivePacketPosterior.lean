import Komorebi.AdaptivePacketSolver
import Komorebi.RationalPosteriorCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Every successful selective-solver return has an actual Bayesian posterior guarantee. -/
theorem adaptive_solver_return_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveAdaptive M Q D seed scan ε probes B = some (p,c)) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := solveAdaptive_sound M Q D seed scan ε probes B p c hr
  exact checked_tolerance_bounds_posterior M Q D c ε h.1 h.2

/-- End-to-end successful termination with exact packet updates and rounded certification. -/
theorem adaptive_solver_reaches_posterior_tolerance
    (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveAdaptive M Q D seed scan ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨p,c,hr,hc,ht⟩ := solveAdaptive_terminates M hs Q D hQ hD seed scan hscan ε hε probes B
  exact ⟨p,c,hr,hc,ht,adaptive_solver_return_bounds_posterior M Q D seed scan ε probes B p c hr⟩

end Komorebi.AdaptivePosterior
