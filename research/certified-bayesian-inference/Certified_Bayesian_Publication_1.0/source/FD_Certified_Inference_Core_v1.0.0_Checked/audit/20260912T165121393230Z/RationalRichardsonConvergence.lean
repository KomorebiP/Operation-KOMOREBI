import Komorebi.RationalRichardsonGeometry
import Komorebi.RationalCandidateAcceptance

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.GainSolver Komorebi.PacketEnergy
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ]

/-- With exact local energies, complete packets account for the rational residual exactly. -/
theorem exactCandidate_total (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) (B : Matrix ι κ ℚ) :
    totalUpper (exactCandidate M Q D B) = rationalEnergy (M.residual B) := by
  have h := (matrixEnergy_eq_sum_blocks (realPackets Q hQ) (realPackets D hD)
    (realPackets_complete Q hQ) (realPackets_complete D hD) (realMatrix (M.residual B))).symm
  have hc : (∑ a, ∑ b, (rationalEnergy (Q a*M.residual B*D b) : ℝ)) =
      (rationalEnergy (M.residual B) : ℝ) := by
    simpa only [realPackets_proj, ← realMatrix_mul, ← rationalEnergy_cast] using h
  change (∑ a, ∑ b, rationalEnergy (Q a*M.residual B*D b)) = _
  exact_mod_cast hc

theorem exactCandidate_score (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) (B : Matrix ι κ ℚ) :
    candidateScore M (exactCandidate M Q D B) = M.residualScore B := by
  unfold candidateScore
  rw [exactCandidate_total M Q D hQ hD B]
  rfl

namespace RationalModel

omit [Fintype α] [Fintype β] [DecidableEq ι] in
/-- Geometric contraction applies to the actual rational solver iterates. -/
theorem solver_energy_succ (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    rationalEnergy (M.residual (M.solverGain B (n+1))) ≤
      M.solverRate * rationalEnergy (M.residual (M.solverGain B n)) := by
  rw [solver_residual_succ]
  exact M.residual_energy_transition hs _

omit [Fintype α] [Fintype β] [DecidableEq ι] in
theorem solver_energy_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    rationalEnergy (M.residual (M.solverGain B n)) ≤
      M.solverRate^n * rationalEnergy (M.residual B) := by
  induction n with
  | zero => simp
  | succ n ih =>
    apply (M.solver_energy_succ hs B n).trans
    have h := mul_le_mul_of_nonneg_left ih (M.solverRate_bounds hs).1
    simpa only [pow_succ, mul_assoc, mul_left_comm, mul_comm] using h

omit [Fintype α] [Fintype β] [DecidableEq ι] in
theorem residualScore_nonneg (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) : 0 ≤ M.residualScore B := by
  exact div_nonneg (mul_nonneg (rationalEnergy_nonneg _) (add_nonneg hs.le
    (rationalVectorEnergy_nonneg _))) (sq_nonneg _)

omit [Fintype α] [Fintype β] [DecidableEq ι] in
/-- A fixed model's exact score has the same geometric energy contraction. -/
theorem solver_score_succ (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (M.solverGain B (n+1)) ≤ M.solverRate*M.residualScore (M.solverGain B n) := by
  have hf : 0 ≤ (M.noiseFloor+rationalVectorEnergy M.innovationVector)/M.noiseFloor^2 :=
    div_nonneg (add_nonneg hs.le (rationalVectorEnergy_nonneg _)) (sq_nonneg _)
  have h := mul_le_mul_of_nonneg_right (M.solver_energy_succ hs B n) hf
  simpa only [residualScore, div_eq_mul_inv, mul_assoc] using h

omit [Fintype α] [Fintype β] [DecidableEq ι] in
theorem solver_score_geometric (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (M.solverGain B n) ≤ M.solverRate^n * M.residualScore B := by
  have hf : 0 ≤ (M.noiseFloor+rationalVectorEnergy M.innovationVector)/M.noiseFloor^2 :=
    div_nonneg (add_nonneg hs.le (rationalVectorEnergy_nonneg _)) (sq_nonneg _)
  have h := mul_le_mul_of_nonneg_right (M.solver_energy_geometric hs B n) hf
  simpa only [residualScore, div_eq_mul_inv, mul_assoc] using h

omit [Fintype α] [Fintype β] [DecidableEq ι] in
/-- Exact Richardson proposals do improve or preserve the score; arbitrary proposals need not. -/
theorem solver_score_nonincreasing (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residualScore (M.solverGain B (n+1)) ≤ M.residualScore (M.solverGain B n) := by
  apply (M.solver_score_succ hs B n).trans
  exact mul_le_of_le_one_left (M.residualScore_nonneg hs _) (M.solverRate_bounds hs).2.le

omit [Fintype α] [Fintype β] [DecidableEq ι] in
/-- The explicit fuel is a genuine uniform iteration-to-positive-tolerance bound. -/
theorem solver_score_at_fuel (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (B : Matrix ι κ ℚ) (ε : ℚ) (hε : 0 < ε) (n : ℕ) (hn : M.solverFuel B ε ≤ n) :
    M.residualScore (M.solverGain B n) ≤ ε^2 := by
  exact (M.solver_score_geometric hs B n).trans
    (geometric_fuel_sufficient _ _ _ (M.solverRate_bounds hs).1 (M.solverRate_bounds hs).2 hε n hn)
end RationalModel

/-- The finite iteration bound reaches the existing executable certificate's Boolean tolerance. -/
theorem solver_iteration_checked_tolerance [DecidableEq α] [DecidableEq β]
    (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (B : Matrix ι κ ℚ) (ε : ℚ) (hε : 0 < ε) (n : ℕ) (hn : M.solverFuel B ε ≤ n) :
    checkCandidate M Q D (exactCandidate M Q D (M.solverGain B n)) = true ∧
    checkTolerance M (exactCandidate M Q D (M.solverGain B n)) ε = true := by
  constructor
  · exact (checkCandidate_eq_true M Q D _).mpr (exactCandidate_valid M Q D _ hs hQ hD)
  · apply (checkTolerance_iff_score M _ ε hs).mpr
    rw [exactCandidate_score M Q D hQ hD]
    exact ⟨hε.le, M.solver_score_at_fuel hs B ε hε n hn⟩

/-- The retained acceptance rule accepts every exact solver step, not only hypothetical proposals. -/
theorem richardson_proposal_accepted [DecidableEq α] [DecidableEq β]
    (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    acceptCandidate M Q D (exactCandidate M Q D (M.solverGain B n))
      (exactCandidate M Q D (M.solverGain B (n+1))) =
      exactCandidate M Q D (M.solverGain B (n+1)) := by
  have hc := (checkCandidate_eq_true M Q D _).mpr
    (exactCandidate_valid M Q D (M.solverGain B (n+1)) hs hQ hD)
  have hle : candidateScore M (exactCandidate M Q D (M.solverGain B (n+1))) ≤
      candidateScore M (exactCandidate M Q D (M.solverGain B n)) := by
    rw [exactCandidate_score M Q D hQ hD, exactCandidate_score M Q D hQ hD]
    exact M.solver_score_nonincreasing hs B n
  simp only [acceptCandidate, hc, hle, and_self, ↓reduceIte]
end Komorebi.ExactPosterior
