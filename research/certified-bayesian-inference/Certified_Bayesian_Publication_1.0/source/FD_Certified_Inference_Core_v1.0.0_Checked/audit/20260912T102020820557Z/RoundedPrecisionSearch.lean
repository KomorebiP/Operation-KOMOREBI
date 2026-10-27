import Komorebi.RoundedPosteriorSound

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.QuadraticTransport
open scoped ENNReal
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Try a finite precision schedule, returning only when the outward certificate succeeds. -/
def certifyPrecisions (ps : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ) :
    Option (RationalCandidate ι κ α β) :=
  match ps with
  | [] => none
  | p :: rest =>
    match certifyRounded p M Q D B ε with
    | some c => some c
    | none => certifyPrecisions rest M Q D B ε

theorem certifyPrecisions_sound (ps : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (c : RationalCandidate ι κ α β) (h : certifyPrecisions ps M Q D B ε = some c) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  induction ps with
  | nil => simp [certifyPrecisions] at h
  | cons p ps ih =>
    cases hr : certifyRounded p M Q D B ε with
    | none => exact ih (by simpa [certifyPrecisions, hr] using h)
    | some d =>
      have hd : d = c := by simpa [certifyPrecisions, hr] using h
      subst c
      exact certifyRounded_sound p M Q D B ε d hr

noncomputable section
/-- Every successful finite precision schedule has the same actual-law guarantee. -/
theorem precision_search_bounds_posterior (ps : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (c : RationalCandidate ι κ α β) (h : certifyPrecisions ps M Q D B ε = some c) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have hc := certifyPrecisions_sound ps M Q D B ε c h
  exact checked_tolerance_bounds_posterior M Q D c ε hc.1 hc.2
end
end Komorebi.RoundedPosterior
