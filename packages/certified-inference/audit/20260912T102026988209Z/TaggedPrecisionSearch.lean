import Komorebi.PrecisionCompleteness

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Retain the actual successful precision, trying a finite schedule in its supplied order. -/
def certifyTagged (ps : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ) :
    Option (ℕ × RationalCandidate ι κ α β) :=
  match ps with
  | [] => none
  | p :: rest =>
    match certifyRounded p M Q D B ε with
    | some c => some (p,c)
    | none => certifyTagged rest M Q D B ε

/-- A successful tagged search returns the exact rounded evaluator result at a listed precision. -/
theorem certifyTagged_origin (ps : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) (ε : ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : certifyTagged ps M Q D B ε = some (p,c)) :
    p ∈ ps ∧ certifyRounded p M Q D B ε = some c := by
  induction ps with
  | nil => simp [certifyTagged] at hr
  | cons a ps ih =>
    cases ha : certifyRounded a M Q D B ε with
    | none =>
      have hrest : certifyTagged ps M Q D B ε = some (p,c) := by
        simpa [certifyTagged,ha] using hr
      have h := ih hrest
      exact ⟨List.mem_cons_of_mem a h.1,h.2⟩
    | some d =>
      have he : a = p ∧ d = c := by simpa [certifyTagged,ha] using hr
      rcases he with ⟨rfl,rfl⟩
      exact ⟨List.mem_cons_self,ha⟩

/-- Containing one passing precision suffices, without monotonicity or sorting assumptions. -/
theorem certifyTagged_complete (ps : List ℕ) (p : ℕ) (hp : p ∈ ps)
    (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (B : Matrix ι κ ℚ) (ε : ℚ) (c : RationalCandidate ι κ α β)
    (hc : certifyRounded p M Q D B ε = some c) :
    ∃ q d, certifyTagged ps M Q D B ε = some (q,d) := by
  induction ps with
  | nil => simp at hp
  | cons a ps ih =>
    cases ha : certifyRounded a M Q D B ε with
    | some d => exact ⟨a,d,by simp [certifyTagged,ha]⟩
    | none =>
      have hp' : p ∈ ps := by
        rcases List.mem_cons.mp hp with he | he
        · subst p; rw [ha] at hc; cases hc
        · exact he
      obtain ⟨q,d,hd⟩ := ih hp'
      exact ⟨q,d,by simpa [certifyTagged,ha] using hd⟩

end Komorebi.RoundedPosterior
