import MachineTheory.HardSemantics
import Mathlib.Data.Nat.Log
import Mathlib.Data.Fintype.BigOperators

/-!
# Binary structure of the existing literal controllers

These are statistics of `HardInquiry.Tree`, not a replacement tree type. Optional
missing branches have no leaves and no records. Unary query nodes remain counted.
-/
namespace Komorebi.MachineTheory.BinaryDiagnosis
open HardInquiry Finset
variable {E C : Type}

/-- Number of stored terminal occurrences, even when labels repeat. -/
def leaves : (h : ℕ) → Tree E Bool C h → ℕ
  | 0, _ => 1
  | _+1, .inl _ => 1
  | h+1, .inr (_,k) => ((k false).map (leaves h)).getD 0 +
      ((k true).map (leaves h)).getD 0

/-- Actual query depth, rather than the horizon annotation. -/
def depth : (h : ℕ) → Tree E Bool C h → ℕ
  | 0, _ => 0
  | _+1, .inl _ => 0
  | h+1, .inr (_,k) => 1 + max (((k false).map (depth h)).getD 0)
      (((k true).map (depth h)).getD 0)

/-- Number of internal nodes having exactly one stored child. -/
def unary : (h : ℕ) → Tree E Bool C h → ℕ
  | 0, _ => 0
  | _+1, .inl _ => 0
  | h+1, .inr (_,k) =>
      (if (k false).isSome != (k true).isSome then 1 else 0) +
      ((k false).map (unary h)).getD 0 + ((k true).map (unary h)).getD 0

/-- A query with no possible child is not a successful controller. -/
def Live : (h : ℕ) → Tree E Bool C h → Prop
  | 0, _ => True
  | _+1, .inl _ => True
  | h+1, .inr (_,k) =>
      (k false ≠ none ∨ k true ≠ none) ∧
      (∀ o t, k o = some t → Live h t)

theorem depth_le_horizon (h : ℕ) (t : Tree E Bool C h) : depth h t ≤ h := by
  induction h with
  | zero => rfl
  | succ h ih =>
    cases t with
    | inl c => exact Nat.zero_le _
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have hf : ((k false).map (depth h)).getD 0 ≤ h := by
        cases he : k false with
        | none => simp
        | some s => simpa [he] using ih s
      have ht : ((k true).map (depth h)).getD 0 ≤ h := by
        cases he : k true with
        | none => simp
        | some s => simpa [he] using ih s
      change 1 + max _ _ ≤ h+1
      omega

theorem leaves_le_pow_depth (h : ℕ) (t : Tree E Bool C h) :
    leaves h t ≤ 2 ^ depth h t := by
  induction h with
  | zero => exact le_rfl
  | succ h ih =>
    cases t with
    | inl c => exact le_rfl
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have branch : ∀ o, ((k o).map (leaves h)).getD 0 ≤
          2 ^ (((k o).map (depth h)).getD 0) := by
        intro o
        cases he : k o with
        | none => simp
        | some s => simpa [he] using ih s
      have hf := (branch false).trans
        (Nat.pow_le_pow_right (by decide : 0 < 2) (le_max_left _ (((k true).map (depth h)).getD 0)))
      have ht := (branch true).trans
        (Nat.pow_le_pow_right (by decide : 0 < 2) (le_max_right (((k false).map (depth h)).getD 0) _))
      change _ + _ ≤ 2 ^ (1 + max _ _)
      rw [Nat.add_comm 1, pow_succ]
      omega

/-- Exact edge accounting includes the extra record of every unary node. -/
theorem records_identity (h : ℕ) (t : Tree E Bool C h) (ht : Live h t) :
    Model.records h t + 1 = 2 * leaves h t + unary h t := by
  induction h with
  | zero => rfl
  | succ h ih =>
    cases t with
    | inl c => rfl
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      cases hf : k false with
      | none =>
        cases hg : k true with
        | none =>
          have := ht.1
          simp only [hf,hg,ne_eq,not_true_eq_false,or_self] at this
        | some r =>
          have hr := ih r (ht.2 true r hg)
          simp [Model.records,leaves,unary,hf,hg]
          omega
      | some l =>
        have hl := ih l (ht.2 false l hf)
        cases hg : k true with
        | none =>
          simp [Model.records,leaves,unary,hf,hg]
          omega
        | some r =>
          have hr := ih r (ht.2 true r hg)
          simp [Model.records,leaves,unary,hf,hg]
          omega

/-- Every successful leaf contributes twice, less the root edge. -/
theorem records_lower (h : ℕ) (t : Tree E Bool C h) (ht : Live h t) :
    2 * leaves h t - 1 ≤ Model.records h t := by
  have := records_identity h t ht
  omega

end Komorebi.MachineTheory.BinaryDiagnosis
