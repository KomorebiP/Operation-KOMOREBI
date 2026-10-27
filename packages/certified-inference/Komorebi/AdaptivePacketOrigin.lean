import Komorebi.AdaptivePacketSolver

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.RoundoffSolver
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- The returned gain is one of the actual greedy packet iterates within the declared fuel. -/
theorem solveAdaptiveFuel_gain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (n : ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveAdaptiveFuel M Q D seed scan ε probes n B = some (p,c)) :
    ∃ k ≤ n, c.gain = greedyGain M Q seed scan B k := by
  induction n generalizing B with
  | zero =>
    have hc := (certifyGain_origin M Q D ε probes B p c hr).1
    exact ⟨0,le_rfl,by rw [hc]; rfl⟩
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | none =>
      have hh : solveAdaptiveFuel M Q D seed scan ε probes n (greedyStep M Q seed scan B) = some (p,c) := by
        simpa only [solveAdaptiveFuel,hc] using hr
      obtain ⟨k,hk,hgain⟩ := ih _ hh
      exact ⟨k+1,Nat.succ_le_succ hk,by simpa only [greedyGain_shift] using hgain⟩
    | some r =>
      have he : r = (p,c) := by simpa only [solveAdaptiveFuel,hc,Option.some.injEq] using hr
      rw [he] at hc
      have hgain := (certifyGain_origin M Q D ε probes B p c hc).1
      exact ⟨0,Nat.zero_le _,by rw [hgain]; rfl⟩

theorem adaptive_solver_gain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveAdaptive M Q D seed scan ε probes B = some (p,c)) :
    ∃ k ≤ adaptiveFuel M B ε (Fintype.card α), c.gain = greedyGain M Q seed scan B k := by
  unfold solveAdaptive at hr
  split at hr
  · exact solveAdaptiveFuel_gain_origin M Q D seed scan ε probes _ B p c hr
  · simp at hr

end Komorebi.AdaptivePosterior
