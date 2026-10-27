import Komorebi.HybridPosteriorSolver

noncomputable section
set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.QuadraticTransport
open scoped ENNReal
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Conditional soundness of the combined program is about the actual posterior law. -/
theorem hybrid_return_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β) (hr : hybridSolve M Q D ε B = some (p,c)) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have hc := hybridSolve_sound M Q D ε B p c hr
  exact checked_tolerance_bounds_posterior M Q D c ε hc.1 hc.2

/-- End-to-end hybrid closure: the executable exact solver creates slack, an explicit bit
bound makes outward evaluation pass, and the returned Joseph Gaussian meets the tolerance. -/
theorem hybrid_reaches_posterior_tolerance (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ p c, hybridSolve M Q D ε B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨p,c,hr,hcheck,htol⟩ := hybridSolve_terminates M hs Q D hQ hD ε hε B
  exact ⟨p,c,hr,hcheck,htol,hybrid_return_bounds_posterior M Q D ε B p c hr⟩

end Komorebi.RoundedPosterior
