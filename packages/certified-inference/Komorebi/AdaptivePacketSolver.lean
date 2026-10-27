import Komorebi.GreedyPacketConvergence
import Komorebi.RoundedSolverOrigin

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.RoundoffSolver
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Each failed verification is followed by one exact selected-packet update. -/
def solveAdaptiveFuel (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) : ℕ → Matrix ι κ ℚ → Option (ℕ × RationalCandidate ι κ α β)
  | 0, B => certifyGain M Q D ε probes B
  | n+1, B =>
    match certifyGain M Q D ε probes B with
    | some r => some r
    | none => solveAdaptiveFuel M Q D seed scan ε probes n (greedyStep M Q seed scan B)

theorem solveAdaptiveFuel_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (n : ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveAdaptiveFuel M Q D seed scan ε probes n B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  induction n generalizing B with
  | zero => exact certifyGain_sound M Q D ε probes B p c hr
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | none =>
      exact ih _ (by simpa only [solveAdaptiveFuel,hc] using hr)
    | some r =>
      have he : r = (p,c) := by simpa only [solveAdaptiveFuel,hc,Option.some.injEq] using hr
      rw [he] at hc
      exact certifyGain_sound M Q D ε probes B p c hc

/-- A passing final permitted iterate guarantees successful early-stopping execution. -/
theorem solveAdaptiveFuel_complete (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (n : ℕ) (B : Matrix ι κ ℚ)
    (hp : ∃ p c, certifyGain M Q D ε probes (greedyGain M Q seed scan B n) = some (p,c)) :
    ∃ p c, solveAdaptiveFuel M Q D seed scan ε probes n B = some (p,c) := by
  induction n generalizing B with
  | zero => exact hp
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | some r => exact ⟨r.1,r.2,by simp only [solveAdaptiveFuel,hc]⟩
    | none =>
      have hp' : ∃ p c, certifyGain M Q D ε probes
          (greedyGain M Q seed scan (greedyStep M Q seed scan B) n) = some (p,c) := by
        simpa only [greedyGain_shift] using hp
      obtain ⟨p,c,hr⟩ := ih _ hp'
      exact ⟨p,c,by simpa only [solveAdaptiveFuel,hc] using hr⟩

/-- Greedy packet solver with checked geometry, scan coverage, and computed finite fuel. -/
def solveAdaptive (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (ℕ × RationalCandidate ι κ α β) :=
  if 0 < ε ∧ checkSetup M Q D = true ∧ ∀ a, a ∈ scan then
    solveAdaptiveFuel M Q D seed scan ε probes (adaptiveFuel M B ε (Fintype.card α)) B
  else none

theorem solveAdaptive_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveAdaptive M Q D seed scan ε probes B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold solveAdaptive at hr
  split at hr
  · exact solveAdaptiveFuel_sound M Q D seed scan ε probes _ B p c hr
  · simp at hr

/-- Success is guaranteed for every positive rational tolerance, not just asserted after a passing run. -/
theorem solveAdaptive_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveAdaptive M Q D seed scan ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  have hscore := greedy_score_at_fuel M hs Q hQ seed scan hscan B ε hε
    (adaptiveFuel M B ε (Fintype.card α)) le_rfl
  have hp := certifyGain_complete M hs Q D hQ hD ε hε probes _ hscore
  obtain ⟨p,c,hr⟩ := solveAdaptiveFuel_complete M Q D seed scan ε probes _ B hp
  have hs0 := (checkSetup_eq_true M Q D).mpr ⟨hs,hQ,hD⟩
  have hout : solveAdaptive M Q D seed scan ε probes B = some (p,c) := by
    rw [solveAdaptive, ite_eq_left ⟨hε,hs0,hscan⟩]
    exact hr
  exact ⟨p,c,hout,solveAdaptive_sound M Q D seed scan ε probes B p c hout⟩

end Komorebi.AdaptivePosterior
