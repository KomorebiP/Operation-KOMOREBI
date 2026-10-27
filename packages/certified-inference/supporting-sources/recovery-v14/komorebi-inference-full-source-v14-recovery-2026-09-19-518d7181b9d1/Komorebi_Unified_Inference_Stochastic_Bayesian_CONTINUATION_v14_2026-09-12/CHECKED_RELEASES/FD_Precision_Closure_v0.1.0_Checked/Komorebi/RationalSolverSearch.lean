import Komorebi.RationalRichardsonConvergence

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Bounded executable search with early stopping. A return always passes both exact checks. -/
def solveGainFuel (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) :
    ℕ → Matrix ι κ ℚ → Option (RationalCandidate ι κ α β)
  | 0, B =>
    let c := exactCandidate M Q D B
    if checkCandidate M Q D c = true ∧ checkTolerance M c ε = true then some c else none
  | n+1, B =>
    let c := exactCandidate M Q D B
    if checkCandidate M Q D c = true ∧ checkTolerance M c ε = true then some c
    else solveGainFuel M Q D ε n (B+M.solverStep • M.residual B)

/-- A returned candidate is sound even without assuming the inputs valid in advance. -/
theorem solveGainFuel_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ)
    (n : ℕ) (B : Matrix ι κ ℚ) (c : RationalCandidate ι κ α β)
    (hr : solveGainFuel M Q D ε n B = some c) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  induction n generalizing B with
  | zero =>
    simp only [solveGainFuel] at hr
    split at hr
    · rename_i h
      cases hr
      exact h
    · cases hr
  | succ n ih =>
    simp only [solveGainFuel] at hr
    split at hr
    · rename_i h
      cases hr
      exact h
    · exact ih _ hr

/-- If the last permitted iterate passes, the early-stopping search cannot return failure. -/
theorem solveGainFuel_complete (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ)
    (n : ℕ) (B : Matrix ι κ ℚ)
    (hlast : checkCandidate M Q D (exactCandidate M Q D (M.solverGain B n)) = true ∧
      checkTolerance M (exactCandidate M Q D (M.solverGain B n)) ε = true) :
    ∃ c, solveGainFuel M Q D ε n B = some c := by
  induction n generalizing B with
  | zero =>
    have h0 : checkCandidate M Q D (exactCandidate M Q D B) = true ∧
        checkTolerance M (exactCandidate M Q D B) ε = true := hlast
    exact ⟨exactCandidate M Q D B, ite_eq_left h0⟩
  | succ n ih =>
    by_cases hnow : checkCandidate M Q D (exactCandidate M Q D B) = true ∧
      checkTolerance M (exactCandidate M Q D B) ε = true
    · exact ⟨exactCandidate M Q D B, ite_eq_left hnow⟩
    · have hn : checkCandidate M Q D (exactCandidate M Q D
          (M.solverGain (B+M.solverStep • M.residual B) n)) = true ∧
          checkTolerance M (exactCandidate M Q D
          (M.solverGain (B+M.solverStep • M.residual B) n)) ε = true := by
        rw [RationalModel.solverGain_shift]
        exact hlast
      obtain ⟨c,hc⟩ := ih _ hn
      exact ⟨c, (ite_eq_right hnow).trans hc⟩

/-- The solver uses the proved explicit finite budget, but checks for success at each earlier step. -/
def solveGain (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ) :
    Option (RationalCandidate ι κ α β) :=
  solveGainFuel M Q D ε (M.solverFuel B ε) B

/-- Uniform solver termination for every positive rational tolerance and valid factor-coded model. -/
theorem solveGain_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ c, solveGain M Q D ε B = some c ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  obtain ⟨c,hc⟩ := solveGainFuel_complete M Q D ε (M.solverFuel B ε) B
    (solver_iteration_checked_tolerance M hs Q D hQ hD B ε hε _ le_rfl)
  exact ⟨c,hc,solveGainFuel_sound M Q D ε _ B c hc⟩
end Komorebi.ExactPosterior
