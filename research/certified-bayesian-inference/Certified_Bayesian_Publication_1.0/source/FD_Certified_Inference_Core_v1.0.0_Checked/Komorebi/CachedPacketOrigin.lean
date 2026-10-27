import Komorebi.CachedPacketSolver

set_option autoImplicit false
namespace Komorebi.CachedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.AdaptivePosterior Komorebi.RoundedPosterior Komorebi.RoundoffSolver
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

theorem cached_solver_gain_origin (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β) (hr : solveCached M Q D seed scan ε probes B = some (p,c)) :
    ∃ k ≤ adaptiveFuel M B ε (Fintype.card α), c.gain = greedyGain M Q seed scan B k := by
  unfold solveCached at hr
  split at hr
  next hg =>
    dsimp only at hr
    cases hsearch : search (prepare M) seed scan ε (adaptiveFuel M B ε (Fintype.card α)) (initialState M Q B) with
    | none => simp only [hsearch] at hr; contradiction
    | some out =>
      simp only [hsearch] at hr
      have hQ := ((checkSetup_eq_true M Q D).mp hg.2.1).2.1
      obtain ⟨k,hk,he⟩ := search_origin (prepare M) seed scan ε _ (initialState M Q B) out hsearch
      have hc := (certifyGain_origin M Q D ε probes out.gain p c hr).1
      refine ⟨k,hk,?_⟩
      calc
        c.gain = out.gain := by rw [hc]; rfl
        _ = greedyGain M Q seed scan B k := by
          rw [he,trajectory_gain M Q hQ _ (initialState_valid M Q B)]
          rfl
  next => contradiction

end Komorebi.CachedPosterior
