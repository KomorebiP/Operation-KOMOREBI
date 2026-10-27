import Komorebi.RationalCertificateChecker

set_option autoImplicit false
namespace Komorebi.ExactPosterior

variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- An unchecked proposal replaces the incumbent only after exact checking and score comparison. -/
def acceptCandidate (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent proposal : RationalCandidate ι κ α β) : RationalCandidate ι κ α β :=
  if checkCandidate M Q D proposal = true ∧ candidateScore M proposal ≤ candidateScore M incumbent
  then proposal else incumbent

theorem acceptCandidate_valid (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent proposal : RationalCandidate ι κ α β) (h : ValidCandidate M Q D incumbent) :
    ValidCandidate M Q D (acceptCandidate M Q D incumbent proposal) := by
  unfold acceptCandidate
  split
  · rename_i hc
    exact (checkCandidate_eq_true M Q D proposal).mp hc.1
  · exact h

theorem acceptCandidate_score_le (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent proposal : RationalCandidate ι κ α β) :
    candidateScore M (acceptCandidate M Q D incumbent proposal) ≤ candidateScore M incumbent := by
  unfold acceptCandidate
  split
  · rename_i hc
    exact hc.2
  · exact le_rfl

theorem reject_invalid_candidate (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent proposal : RationalCandidate ι κ α β)
    (h : checkCandidate M Q D proposal = false) :
    acceptCandidate M Q D incumbent proposal = incumbent := by
  simp [acceptCandidate, h]

/-- A finite batch is evaluated without replacing the current incumbent by an invalid candidate. -/
def selectCandidates (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent : RationalCandidate ι κ α β) (proposals : List (RationalCandidate ι κ α β)) :=
  proposals.foldl (acceptCandidate M Q D) incumbent

theorem selectCandidates_valid (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent : RationalCandidate ι κ α β) (proposals : List (RationalCandidate ι κ α β))
    (h : ValidCandidate M Q D incumbent) :
    ValidCandidate M Q D (selectCandidates M Q D incumbent proposals) := by
  induction proposals generalizing incumbent with
  | nil => exact h
  | cons p ps ih =>
    exact ih _ (acceptCandidate_valid M Q D incumbent p h)

theorem selectCandidates_score_le (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent : RationalCandidate ι κ α β) (proposals : List (RationalCandidate ι κ α β)) :
    candidateScore M (selectCandidates M Q D incumbent proposals) ≤ candidateScore M incumbent := by
  induction proposals generalizing incumbent with
  | nil => exact le_rfl
  | cons p ps ih =>
    exact (ih (acceptCandidate M Q D incumbent p)).trans (acceptCandidate_score_le M Q D incumbent p)

omit [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β] in
/-- Squared-tolerance comparison has the same exact rational score interpretation. -/
theorem checkTolerance_iff_score (M : RationalModel ι κ υ ω)
    (c : RationalCandidate ι κ α β) (ε : ℚ) (hs : 0 < M.noiseFloor) :
    checkTolerance M c ε = true ↔ 0 ≤ ε ∧ candidateScore M c ≤ ε^2 := by
  rw [checkTolerance_eq_true]
  simp only [candidateScore, div_le_iff₀ (sq_pos_of_pos hs)]

/-- A valid incumbent's certified tolerance survives an arbitrary finite proposal batch. -/
theorem selectCandidates_preserves_tolerance (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (incumbent : RationalCandidate ι κ α β) (proposals : List (RationalCandidate ι κ α β))
    (h : ValidCandidate M Q D incumbent) (ε : ℚ) (ht : checkTolerance M incumbent ε = true) :
    checkTolerance M (selectCandidates M Q D incumbent proposals) ε = true := by
  have ht' := (checkTolerance_iff_score M incumbent ε h.1).mp ht
  exact (checkTolerance_iff_score M _ ε h.1).mpr
    ⟨ht'.1, (selectCandidates_score_le M Q D incumbent proposals).trans ht'.2⟩

end Komorebi.ExactPosterior
