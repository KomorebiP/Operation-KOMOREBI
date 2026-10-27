import Komorebi.RoundedModel

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Finite-precision enclosure producer. All scalar centers and radii are rounded outward. -/
def roundedCandidate (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    RationalCandidate ι κ α β where
  gain := B
  packetUpper a b := matrixEnergyUpper (packetBall p M B (Q a) (D b))
  innovationUpper := vectorEnergyUpper (innovationVectorBall p M)

omit [DecidableEq α] [DecidableEq β] in
/-- The local upper bounds include every propagated arithmetic radius. -/
theorem roundedCandidate_valid (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) :
    ValidCandidate M Q D (roundedCandidate p M Q D B) := by
  refine ⟨hs, hQ, hD, ?_, ?_⟩
  · intro a b
    exact matrixEnergyUpper_sound (packetBall_encloses p M B (Q a) (D b))
  · exact vectorEnergyUpper_sound (innovationVectorBall_encloses p M)

theorem roundedCandidate_passes_exact_checker (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) :
    checkCandidate M Q D (roundedCandidate p M Q D B) = true :=
  (checkCandidate_eq_true M Q D _).mpr (roundedCandidate_valid p M Q D B hs hQ hD)

/-- Only model floor and exact packet geometry are checked here; no exact residual recomputation. -/
def checkSetup (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) : Bool :=
  decide (0 < M.noiseFloor ∧ RationalPacketsValid Q ∧ RationalPacketsValid D)

@[simp] theorem checkSetup_eq_true (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) :
    checkSetup M Q D = true ↔ 0 < M.noiseFloor ∧ RationalPacketsValid Q ∧ RationalPacketsValid D := by
  simp [checkSetup]

/-- A sound rounded-arithmetic acceptance test. Failure is not evidence of excessive true error. -/
def certifyRounded (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ) :
    Option (RationalCandidate ι κ α β) :=
  if checkSetup M Q D then
    let c := roundedCandidate p M Q D B
    if checkTolerance M c ε then some c else none
  else none

theorem certifyRounded_sound (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (c : RationalCandidate ι κ α β) (h : certifyRounded p M Q D B ε = some c) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold certifyRounded at h
  split at h
  · rename_i hs
    have hvalid := (checkSetup_eq_true M Q D).mp hs
    split at h
    · rename_i ht
      have hc : roundedCandidate p M Q D B = c := Option.some.inj h
      rw [← hc]
      exact ⟨roundedCandidate_passes_exact_checker p M Q D B hvalid.1 hvalid.2.1 hvalid.2.2, ht⟩
    · simp at h
  · simp at h

end Komorebi.RoundedPosterior
