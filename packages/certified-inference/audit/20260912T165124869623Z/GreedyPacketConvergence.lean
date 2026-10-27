import Komorebi.GreedyPacketSelection
import Komorebi.RationalRichardsonConvergence

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.GainSolver
variable {ι κ υ ω α : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α]

/-- Iteration updates the largest current output residual packet. -/
def greedyGain (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (seed : α) (scan : List α) (B : Matrix ι κ ℚ) : ℕ → Matrix ι κ ℚ
  | 0 => B
  | n+1 => greedyStep M Q seed scan (greedyGain M Q seed scan B n)

omit [Fintype α] [DecidableEq ι] [DecidableEq α] in
theorem greedyGain_shift (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (seed : α) (scan : List α) (B : Matrix ι κ ℚ) (n : ℕ) :
    greedyGain M Q seed scan (greedyStep M Q seed scan B) n = greedyGain M Q seed scan B (n+1) := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [greedyGain, ih]

/-- Packet selection is recomputed at each iterate; no fixed selection schedule is assumed. -/
theorem greedy_energy_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ) (n : ℕ) :
    rationalEnergy (M.residual (greedyGain M Q seed scan B n)) ≤
      (adaptiveRate M.solverRate (Fintype.card α))^n*rationalEnergy (M.residual B) := by
  have hr := adaptiveRate_bounds M.solverRate (Fintype.card α)
    (M.solverRate_bounds hs).1 (M.solverRate_bounds hs).2 (Fintype.card_pos_iff.mpr ⟨seed⟩)
  induction n with
  | zero => simp only [greedyGain, pow_zero, one_mul, le_refl]
  | succ n ih =>
    apply (greedy_energy_contract M hs Q hQ seed scan hscan _).trans
    have h := mul_le_mul_of_nonneg_left ih hr.1
    simpa only [pow_succ, mul_assoc, mul_left_comm, mul_comm] using h

theorem greedy_score_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (greedyGain M Q seed scan B n) ≤
      (adaptiveRate M.solverRate (Fintype.card α))^n*M.residualScore B := by
  have hf : 0 ≤ (M.noiseFloor+rationalVectorEnergy M.innovationVector)/M.noiseFloor^2 :=
    div_nonneg (add_nonneg hs.le (rationalVectorEnergy_nonneg _)) (sq_nonneg _)
  have h := mul_le_mul_of_nonneg_right (greedy_energy_geometric M hs Q hQ seed scan hscan B n) hf
  simpa only [RationalModel.residualScore, div_eq_mul_inv, mul_assoc] using h

/-- Computed finite update budget; verification receives three quarters of the target score as slack. -/
def adaptiveFuel (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (ε : ℚ) (count : ℕ) : ℕ :=
  toleranceFuel (adaptiveRate M.solverRate count) (M.residualScore B) (ε/2)

theorem greedy_score_at_fuel (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ)
    (ε : ℚ) (hε : 0 < ε) (n : ℕ) (hn : adaptiveFuel M B ε (Fintype.card α) ≤ n) :
    M.residualScore (greedyGain M Q seed scan B n) ≤ ε^2/4 := by
  have hr := adaptiveRate_bounds M.solverRate (Fintype.card α)
    (M.solverRate_bounds hs).1 (M.solverRate_bounds hs).2 (Fintype.card_pos_iff.mpr ⟨seed⟩)
  have h := (greedy_score_geometric M hs Q hQ seed scan hscan B n).trans
    (geometric_fuel_sufficient _ _ (ε/2) hr.1 hr.2 (by positivity) n hn)
  calc
    _ ≤ (ε/2)^2 := h
    _ = ε^2/4 := by ring

end Komorebi.AdaptivePosterior
