import Komorebi.RoundedSolverSearch
import Komorebi.RationalPosteriorCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Every successful rounded-solver return has an actual Bayesian posterior guarantee. -/
theorem rounded_solver_return_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveRounded M Q D ε probes B = some (p,c)) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := solveRounded_sound M Q D ε probes B p c hr
  exact checked_tolerance_bounds_posterior M Q D c ε h.1 h.2

/-- End-to-end successful termination with rounded gain updates and rounded certification. -/
theorem rounded_solver_reaches_posterior_tolerance
    (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveRounded M Q D ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨p,c,hr,hc,ht⟩ := solveRounded_terminates M hs Q D hQ hD ε hε probes B
  exact ⟨p,c,hr,hc,ht,rounded_solver_return_bounds_posterior M Q D ε probes B p c hr⟩

end Komorebi.RoundoffSolver
