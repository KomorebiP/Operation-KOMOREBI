import Komorebi.CachedPacketState

set_option autoImplicit false
namespace Komorebi.CachedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.AdaptivePosterior
variable {ι κ υ ω α : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α]

def chosen (seed : α) (scan : List α) (c : State ι κ α) : α := winner c.energies seed scan

def advance (K : Kernel κ) (seed : α) (scan : List α) (c : State ι κ α) : State ι κ α :=
  step K (chosen seed scan c) c

def trajectory (K : Kernel κ) (seed : α) (scan : List α) (c : State ι κ α) : ℕ → State ι κ α
  | 0 => c
  | n+1 => advance K seed scan (trajectory K seed scan c n)

omit [Fintype α] [Fintype υ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem trajectory_shift (K : Kernel κ) (seed : α) (scan : List α) (c : State ι κ α) (n : ℕ) :
    trajectory K seed scan (advance K seed scan c) n = trajectory K seed scan c (n+1) := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [trajectory,ih]

omit [DecidableEq ι] [DecidableEq α] in
theorem chosen_eq (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) :
    chosen seed scan c = selectPacket M Q seed scan c.gain := by
  have he : c.energies = fun a => rationalEnergy (Q a*M.residual c.gain) := by
    funext a; rw [hc.2.1 a,hc.1 a]
  simp only [chosen,selectPacket,he]

theorem advance_valid (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) :
    Valid M Q (advance (prepare M) seed scan c) := step_valid M Q hQ c hc _

omit [DecidableEq ι] in
theorem advance_gain (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) :
    (advance (prepare M) seed scan c).gain = greedyStep M Q seed scan c.gain := by
  rw [advance,step_gain M Q c hc,chosen_eq M Q c hc]
  rfl

theorem trajectory_valid (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) (n : ℕ) :
    Valid M Q (trajectory (prepare M) seed scan c n) := by
  induction n with
  | zero => exact hc
  | succ n ih => exact advance_valid M Q hQ _ ih seed scan

/-- Cached execution produces exactly the same gains as the fully recomputed greedy iteration. -/
theorem trajectory_gain (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) (n : ℕ) :
    (trajectory (prepare M) seed scan c n).gain = greedyGain M Q seed scan c.gain n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [trajectory,advance_gain M Q _ (trajectory_valid M Q hQ c hc seed scan n),ih]
    rfl

theorem trajectory_score_at_fuel (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (c : State ι κ α) (hc : Valid M Q c) (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε : ℚ) (hε : 0 < ε) (n : ℕ) (hn : adaptiveFuel M c.gain ε (Fintype.card α) ≤ n) :
    score (prepare M) (trajectory (prepare M) seed scan c n) ≤ ε^2/4 := by
  rw [score_eq M Q hQ _ (trajectory_valid M Q hQ c hc seed scan n),trajectory_gain M Q hQ c hc]
  exact greedy_score_at_fuel M hs Q hQ seed scan hscan c.gain ε hε n hn

end Komorebi.CachedPosterior
