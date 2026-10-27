import Komorebi.RoundedSolverSearch

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

theorem certifyGain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : certifyGain M Q D ε probes B = some (p,c)) :
    c = roundedCandidate p M Q D B ∧
      p ∈ probes++[sufficientPrecision M Q D B (ε^2/4)] := by
  have h := certifyTagged_origin _ M Q D B ε p c hr
  have hc := h.2
  unfold certifyRounded at hc
  split at hc
  · dsimp only at hc
    split at hc
    · exact ⟨(Option.some.inj hc).symm,h.1⟩
    · simp at hc
  · simp at hc

/-- The returned gain is one of the actual rounded iterates within the declared fuel. -/
theorem solveRoundedFuel_gain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (t n : ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveRoundedFuel M Q D ε probes t n B = some (p,c)) :
    ∃ k ≤ n, c.gain = roundedGain M t B k := by
  induction n generalizing B with
  | zero =>
    have hc := (certifyGain_origin M Q D ε probes B p c hr).1
    exact ⟨0,le_rfl,by rw [hc]; rfl⟩
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | none =>
      have hh : solveRoundedFuel M Q D ε probes t n (roundedGainStep M t B) = some (p,c) := by
        simpa only [solveRoundedFuel,hc] using hr
      obtain ⟨k,hk,hgain⟩ := ih _ hh
      exact ⟨k+1,Nat.succ_le_succ hk,by simpa only [roundedGain_shift] using hgain⟩
    | some r =>
      have he : r = (p,c) := by simpa only [solveRoundedFuel,hc,Option.some.injEq] using hr
      rw [he] at hc
      have hgain := (certifyGain_origin M Q D ε probes B p c hc).1
      exact ⟨0,Nat.zero_le _,by rw [hgain]; rfl⟩

theorem rounded_solver_gain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveRounded M Q D ε probes B = some (p,c)) :
    ∃ k ≤ roundedFuel M B ε, c.gain = roundedGain M (updateAccuracy M ε) B k := by
  unfold solveRounded at hr
  split at hr
  · exact solveRoundedFuel_gain_origin M Q D ε probes _ _ B p c hr
  · simp at hr

end Komorebi.RoundoffSolver
