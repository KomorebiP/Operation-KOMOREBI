import Komorebi.PrecisionScore
import Komorebi.PrecisionSelection
import Komorebi.RoundedPrecisionSearch

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Precision planning uses magnitude/radius budgets, not exact residual evaluation. -/
def sufficientPrecision (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (δ : ℚ) : ℕ :=
  precisionFor (scoreRoundCoeff M Q D B) δ

omit [DecidableEq ι] [DecidableEq α] [DecidableEq β] in
/-- Every precision above the computed bound has at most the requested score inflation. -/
theorem rounded_score_le_with_slack (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (δ : ℚ) (hδ : 0 < δ) (p : ℕ)
    (hp : sufficientPrecision M Q D B δ ≤ p) :
    candidateScore M (roundedCandidate p M Q D B) ≤
      candidateScore M (exactCandidate M Q D B)+δ := by
  have hc := coefficient_mesh_le (scoreRoundCoeff M Q D B) δ hδ p hp
  exact (rounded_score_inflation p M Q D B hs).trans (add_le_add le_rfl hc)

/-- Strict exact-certificate slack plus the computed precision forces rounded certification. -/
theorem certifyRounded_of_slack (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε δ : ℚ) (hε : 0 ≤ ε) (hδ : 0 < δ)
    (hmargin : candidateScore M (exactCandidate M Q D B)+δ ≤ ε^2)
    (p : ℕ) (hp : sufficientPrecision M Q D B δ ≤ p) :
    certifyRounded p M Q D B ε = some (roundedCandidate p M Q D B) := by
  have hsetup : checkSetup M Q D = true := (checkSetup_eq_true M Q D).mpr ⟨hs,hQ,hD⟩
  have ht : checkTolerance M (roundedCandidate p M Q D B) ε = true :=
    (checkTolerance_iff_score M _ ε hs).mpr
      ⟨hε,(rounded_score_le_with_slack M Q D B hs δ hδ p hp).trans hmargin⟩
  simp only [certifyRounded,hsetup,ht,ite_true]

/-- A fixed candidate with strict score slack is certified at an explicitly defined precision. -/
theorem exists_precision_of_strict_score (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 ≤ ε) (hm : candidateScore M (exactCandidate M Q D B) < ε^2) :
    ∃ p, certifyRounded p M Q D B ε = some (roundedCandidate p M Q D B) := by
  let δ := ε^2-candidateScore M (exactCandidate M Q D B)
  have hd : 0 < δ := sub_pos.mpr hm
  exact ⟨sufficientPrecision M Q D B δ,
    certifyRounded_of_slack M Q D B hs hQ hD ε δ hε hd (by dsimp [δ]; linarith) _ le_rfl⟩

/-- A finite precision schedule succeeds whenever it contains a successful precision. -/
theorem certifyPrecisions_complete_of_mem (ps : List ℕ) (p : ℕ) (hp : p ∈ ps)
    (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (B : Matrix ι κ ℚ) (ε : ℚ) (c : RationalCandidate ι κ α β)
    (hc : certifyRounded p M Q D B ε = some c) :
    ∃ d, certifyPrecisions ps M Q D B ε = some d := by
  induction ps with
  | nil => simp at hp
  | cons a ps ih =>
    cases ha : certifyRounded a M Q D B ε with
    | some d => exact ⟨d,by simp [certifyPrecisions,ha]⟩
    | none =>
      have hp' : p ∈ ps := by
        rcases List.mem_cons.mp hp with he | he
        · subst p; rw [ha] at hc; cases hc
        · exact he
      obtain ⟨d,hd⟩ := ih hp'
      exact ⟨d,by simpa [certifyPrecisions,ha] using hd⟩

/-- A finite schedule containing the computed sufficient precision is complete under strict slack. -/
theorem precision_schedule_of_slack (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε δ : ℚ) (hε : 0 ≤ ε) (hδ : 0 < δ)
    (hm : candidateScore M (exactCandidate M Q D B)+δ ≤ ε^2)
    (ps : List ℕ) (hp : sufficientPrecision M Q D B δ ∈ ps) :
    ∃ c, certifyPrecisions ps M Q D B ε = some c :=
  certifyPrecisions_complete_of_mem ps _ hp M Q D B ε _
    (certifyRounded_of_slack M Q D B hs hQ hD ε δ hε hδ hm _ le_rfl)

end Komorebi.RoundedPosterior
