import Komorebi.RationalSolverSearch
import Komorebi.RationalPosteriorCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- The geometric iteration certificate controls actual posterior laws, not only a matrix residual. -/
theorem richardson_posterior_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    wasserstein2Sq M.posterior (M.approximation (M.solverGain B n)) ≤
      ENNReal.ofReal ((M.solverRate^n*M.residualScore B : ℚ) : ℝ) := by
  have hc := (checkCandidate_eq_true M Q D _).mpr
    (exactCandidate_valid M Q D (M.solverGain B n) hs hQ hD)
  have h := checked_score_bounds_posterior M Q D _ hc
  rw [exactCandidate_score M Q D hQ hD] at h
  apply h.trans
  apply ENNReal.ofReal_le_ofReal
  exact_mod_cast M.solver_score_geometric hs B n

/-- The explicit finite iteration budget yields the desired actual-posterior tolerance. -/
theorem richardson_posterior_at_fuel (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (B : Matrix ι κ ℚ) (ε : ℚ) (hε : 0 < ε) (n : ℕ) (hn : M.solverFuel B ε ≤ n) :
    wasserstein2 M.posterior (M.approximation (M.solverGain B n)) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := solver_iteration_checked_tolerance M hs Q D hQ hD B ε hε n hn
  exact checked_tolerance_bounds_posterior M Q D _ ε h.1 h.2

/-- Every executable solver return is accompanied by the actual Bayesian-posterior bound. -/
theorem solver_return_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (B : Matrix ι κ ℚ) (c : RationalCandidate ι κ α β)
    (hr : solveGain M Q D ε B = some c) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := solveGainFuel_sound M Q D ε _ B c hr
  exact checked_tolerance_bounds_posterior M Q D c ε h.1 h.2

/-- End-to-end total correctness: positive tolerance is reached by a finite executable solver. -/
theorem solver_reaches_posterior_tolerance (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ c, solveGain M Q D ε B = some c ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨c,hc,hcheck,htol⟩ := solveGain_terminates M hs Q D hQ hD ε hε B
  exact ⟨c,hc,hcheck,htol,solver_return_bounds_posterior M Q D ε B c hc⟩
end Komorebi.ExactPosterior
