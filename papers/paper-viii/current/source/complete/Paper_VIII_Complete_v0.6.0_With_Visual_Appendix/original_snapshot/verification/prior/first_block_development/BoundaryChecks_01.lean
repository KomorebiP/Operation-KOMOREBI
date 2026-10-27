module
public import TransferSupport
import all TransferSupport
import all PacketIR
import all QuantumPacketCore
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.Linarith

/-!
Author: Komorebi P.
Boundary checks for the strengthened Paper VIII.
A support path need not survive cancellation.
A nonempty positive allocation requires a strictly positive total budget (item 8.4).
These are not proofs of the full continuous precision optimization theorem.
-/

public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

/-- A rational, nonzero matrix with exact square zero. -/
def cancellationMatrix : Matrix (Fin 2) (Fin 2) ℚ := fun i _ => if i = 0 then 1 else -1

theorem cancellation_square_zero : cancellationMatrix ^ 2 = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [pow_two, cancellationMatrix, Matrix.mul_apply, Fin.sum_univ_two]

theorem cancellation_block_nonzero :
    (coordinatePackets (K := ℚ) (fun i : Fin 2 => i)).block cancellationMatrix 0 0 ≠ 0 := by
  intro h
  have he := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℚ => M 0 0) h
  norm_num [coordinatePackets, PacketFamily.block, cancellationMatrix,
    Matrix.mul_apply, Fin.sum_univ_two, Matrix.diagonal_apply] at he

/-- Exact counterexample to replacing the support inclusion by equality. -/
theorem paths_can_cancel :
    let P := coordinatePackets (K := ℚ) (fun i : Fin 2 => i)
    TransferPath P cancellationMatrix 2 0 0 ∧ P.block (cancellationMatrix ^ 2) 0 0 = 0 := by
  dsimp
  constructor
  · exact ⟨0, cancellation_block_nonzero, 0, cancellation_block_nonzero, rfl⟩
  · rw [cancellation_square_zero]
    simp [PacketFamily.block]

/-- Positive sensitivities and tolerances force the equality budget to be positive. -/
theorem positive_allocation_budget {E : Type*} [Fintype E] [Nonempty E]
    (s ε : E → ℝ) (hs : ∀ e, 0 < s e) (hε : ∀ e, 0 < ε e) :
    0 < ∑ e, s e * ε e := by
  exact Finset.sum_pos (fun e _ => mul_pos (hs e) (hε e)) Finset.univ_nonempty

/-- Theorem 8.4 cannot assert a minimizer at a nonpositive budget on a nonempty edge set. -/
theorem no_positive_allocation_nonpositive_budget {E : Type*} [Fintype E] [Nonempty E]
    (s : E → ℝ) (hs : ∀ e, 0 < s e) (τ : ℝ) (hτ : τ ≤ 0) :
    ¬ ∃ ε : E → ℝ, (∀ e, 0 < ε e) ∧ (∑ e, s e * ε e) = τ := by
  rintro ⟨ε, hε, hbudget⟩
  have h := positive_allocation_budget s ε hs hε
  linarith

/-- One positive-sensitivity edge at budget zero is already infeasible. -/
theorem one_edge_zero_budget_infeasible :
    ¬ ∃ ε : Fin 1 → ℝ, (∀ e, 0 < ε e) ∧ (∑ e, (1 : ℝ) * ε e) = 0 := by
  exact no_positive_allocation_nonpositive_budget (fun _ => 1) (by intro e; norm_num) 0 le_rfl

end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.cancellation_square_zero
#print axioms KomorebiPaperVIII.cancellation_block_nonzero
#print axioms KomorebiPaperVIII.paths_can_cancel
#print axioms KomorebiPaperVIII.positive_allocation_budget
#print axioms KomorebiPaperVIII.no_positive_allocation_nonpositive_budget
#print axioms KomorebiPaperVIII.one_edge_zero_budget_infeasible
