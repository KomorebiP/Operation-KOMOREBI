import MachineTheory.BinaryExecution
import Mathlib.Data.Fintype.Powerset

/-!
# Finite admission of the complete binary certificate

The guard checks actual model fields, including all finite support-dependent
terminal charges. It is not cheap by definition, and does not discover its table.
-/
namespace Komorebi.MachineTheory.BinaryDiagnosis
open HardInquiry Finset
variable {X E C : Type} [Fintype X] [DecidableEq X] [Fintype E] [Fintype C]

def checkScope (M : Model X E Bool C Unit) : Bool :=
  decide ((∀ e x, M.next e x = x) ∧
    (∀ c x y, M.accept x c = true → M.accept y c = true → x = y) ∧
    (∀ e, M.stepCost e () = 1) ∧
    (∀ c V, V.Nonempty → M.terminalCost c V () = 1))

theorem checkScope_iff (M : Model X E Bool C Unit) : checkScope M = true ↔ Scope M := by
  simp only [checkScope,decide_eq_true_eq]
  constructor
  · rintro ⟨hi,hs,hq,ht⟩; exact ⟨hi,hs,hq,ht⟩
  · intro s; exact ⟨s.immutable,s.singleton,s.query_cost,s.terminal_cost⟩

/-- Nothing in the returned certificate supplies the hidden state or performs exhaustive synthesis. -/
def admissionCheck (M : Model X E Bool C Unit) (h : ℕ) (V : Finset X) (t : Tree E Bool C h) : Bool :=
  checkScope M && checkCandidate M h V t

theorem admitted_scope_and_candidate (M : Model X E Bool C Unit) (h : ℕ)
    (V : Finset X) (t : Tree E Bool C h) (ha : admissionCheck M h V t = true) :
    Scope M ∧ M.Valid h V t ∧ M.profile h V t = lowerProfile V.card := by
  have hh := Bool.and_eq_true_iff.mp ha
  exact ⟨(checkScope_iff M).mp hh.1,(checkCandidate_iff M h V t).mp hh.2⟩

/-- A true complete gate certifies the entire computed frontier at the requested horizon. -/
theorem admitted_frontier (M : Model X E Bool C Unit) (h : ℕ)
    (V : Finset X) (t : Tree E Bool C h) (ha : admissionCheck M h V t = true) :
    M.compute h V = {lowerProfile V.card} := by
  have hh := Bool.and_eq_true_iff.mp ha
  exact checked_early_return M ((checkScope_iff M).mp hh.1) h V t hh.2

/-- The same certificate establishes the frontier at every larger finite horizon. -/
theorem admitted_all_horizons (M : Model X E Bool C Unit) (h : ℕ)
    (V : Finset X) (t : Tree E Bool C h) (ha : admissionCheck M h V t = true) (n : ℕ) :
    M.solve (h+n) V = {lowerProfile V.card} := by
  have hh := Bool.and_eq_true_iff.mp ha
  exact closed_frontier_all_larger_horizons M ((checkScope_iff M).mp hh.1) h V t hh.2 n

/-- Admission means that one same candidate satisfies every online/storage budget above it. -/
theorem admitted_budget (M : Model X E Bool C Unit) (h : ℕ)
    (V : Finset X) (t : Tree E Bool C h) (ha : admissionCheck M h V t = true) (b : Profile Unit) :
    (∃ u : Tree E Bool C h, M.Valid h V u ∧ M.profile h V u ≤ b) ↔
      lowerProfile V.card ≤ b := by
  rw [M.computed_budget_iff,admitted_frontier M h V t ha]
  simp only [mem_singleton,exists_eq_left]

end Komorebi.MachineTheory.BinaryDiagnosis
