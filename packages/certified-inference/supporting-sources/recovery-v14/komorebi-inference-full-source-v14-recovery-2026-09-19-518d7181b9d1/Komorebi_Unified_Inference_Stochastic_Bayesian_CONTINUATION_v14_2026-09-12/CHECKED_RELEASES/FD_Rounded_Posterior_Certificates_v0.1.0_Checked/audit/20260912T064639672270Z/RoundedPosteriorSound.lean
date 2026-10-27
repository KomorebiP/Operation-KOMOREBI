import Komorebi.RoundedCandidate
import Komorebi.RationalPosteriorCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.QuadraticTransport
open scoped ENNReal
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Rounded arithmetic encloses the exact residual, and hence bounds the actual posterior. -/
theorem rounded_score_bounds_posterior (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) :
    wasserstein2Sq M.posterior (M.approximation B) ≤
      ENNReal.ofReal (candidateScore M (roundedCandidate p M Q D B) : ℝ) :=
  checked_score_bounds_posterior M Q D _
    (roundedCandidate_passes_exact_checker p M Q D B hs hQ hD)

/-- A rounded tolerance check implies an actual-distribution tolerance. -/
theorem rounded_tolerance_bounds_posterior (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ht : checkTolerance M (roundedCandidate p M Q D B) ε = true) :
    wasserstein2 M.posterior (M.approximation B) ≤ ENNReal.ofReal (ε : ℝ) :=
  checked_tolerance_bounds_posterior M Q D _ ε
    (roundedCandidate_passes_exact_checker p M Q D B hs hQ hD) ht

/-- No pre-assumed setup validity is required for soundness of a successful return. -/
theorem rounded_return_bounds_posterior (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (c : RationalCandidate ι κ α β) (h : certifyRounded p M Q D B ε = some c) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have hc := certifyRounded_sound p M Q D B ε c h
  exact checked_tolerance_bounds_posterior M Q D c ε hc.1 hc.2

end Komorebi.RoundedPosterior
