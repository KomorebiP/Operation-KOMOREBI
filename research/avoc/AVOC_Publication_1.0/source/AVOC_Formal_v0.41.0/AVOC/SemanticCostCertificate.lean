import AVOC.BooleanProgram

namespace Komorebi.AVOC.CostCertificate

open Synthesis

/-- An interpretation of the fixed syntax. This interface need not be finite. -/
structure Algebra (D : Type) where
  literal : Bool → D
  atom : Variable → D
  neg : D → D
  conj : D → D → D
  disj : D → D → D
  excl : D → D → D

def interpret {D : Type} (a : Algebra D) : Program → D
  | .literal b => a.literal b
  | .variable v => a.atom v
  | .neg p => a.neg (interpret a p)
  | .conjunction p q => a.conj (interpret a p) (interpret a q)
  | .disjunction p q => a.disj (interpret a p) (interpret a q)
  | .exclusive p q => a.excl (interpret a p) (interpret a q)

/-- A subsolution to every syntax constructor is a universal cost lower bound. -/
structure LowerValid {D : Type} (a : Algebra D) (cost : D → Nat) : Prop where
  literal : ∀ b, cost (a.literal b) ≤ 1
  atom : ∀ v, cost (a.atom v) ≤ 1
  neg : ∀ s, cost (a.neg s) ≤ cost s + 1
  conj : ∀ s t, cost (a.conj s t) ≤ cost s + cost t + 1
  disj : ∀ s t, cost (a.disj s t) ≤ cost s + cost t + 1
  excl : ∀ s t, cost (a.excl s t) ≤ cost s + cost t + 1

/-- No grammar-height bound occurs in this induction. -/
theorem lower_bound {D : Type} (a : Algebra D) (cost : D → Nat)
    (h : LowerValid a cost) (p : Program) : cost (interpret a p) ≤ nodes p := by
  induction p with
  | literal b => exact h.literal b
  | «variable» v => exact h.atom v
  | neg p ih =>
    have hl := h.neg (interpret a p)
    simp only [interpret, nodes]; omega
  | conjunction p q ihp ihq =>
    have hl := h.conj (interpret a p) (interpret a q)
    simp only [interpret, nodes]; omega
  | disjunction p q ihp ihq =>
    have hl := h.disj (interpret a p) (interpret a q)
    simp only [interpret, nodes]; omega
  | exclusive p q ihp ihq =>
    have hl := h.excl (interpret a p) (interpret a q)
    simp only [interpret, nodes]; omega

/-- Witnesses turn independently certified lower bounds into attained optima. -/
def Realizes {D : Type} (a : Algebra D) (cost : D → Nat) (witness : D → Program) : Prop :=
  ∀ s, interpret a (witness s) = s ∧ nodes (witness s) = cost s

theorem witness_global_minimum {D : Type} (a : Algebra D) (cost : D → Nat)
    (w : D → Program) (hl : LowerValid a cost) (hw : Realizes a cost w)
    (s : D) (p : Program) (hp : interpret a p = s) : nodes (w s) ≤ nodes p := by
  have h := lower_bound a cost hl p
  rw [hp, ← (hw s).2] at h
  exact h

theorem cost_is_attained_minimum {D : Type} (a : Algebra D) (cost : D → Nat)
    (w : D → Program) (hl : LowerValid a cost) (hw : Realizes a cost w) (s : D) :
    (∃ p, interpret a p = s ∧ nodes p = cost s) ∧
    ∀ p, interpret a p = s → cost s ≤ nodes p := by
  refine ⟨⟨w s, (hw s).1, (hw s).2⟩, ?_⟩
  intro p hp
  simpa only [hp] using lower_bound a cost hl p

theorem exact_cost_unique {D : Type} (a : Algebra D) (c d : D → Nat)
    (w v : D → Program) (hc : LowerValid a c) (hd : LowerValid a d)
    (hw : Realizes a c w) (hv : Realizes a d v) : c = d := by
  funext s
  have hcd := lower_bound a c hc (v s)
  have hdc := lower_bound a d hd (w s)
  rw [(hv s).1, (hv s).2] at hcd
  rw [(hw s).1, (hw s).2] at hdc
  exact Nat.le_antisymm hcd hdc

/-- A lower certificate is still useful when a supplied upper witness is not optimal. -/
theorem lower_upper_sandwich {D : Type} (a : Algebra D) (cost : D → Nat)
    (hl : LowerValid a cost) (s : D) (p : Program) (hp : interpret a p = s) :
    cost s ≤ nodes p := by
  simpa only [hp] using lower_bound a cost hl p

/-- An optimal witness prevents positive node savings from deeper search. -/
theorem no_further_node_saving {D : Type} (a : Algebra D) (cost : D → Nat)
    (w : D → Program) (hl : LowerValid a cost) (hw : Realizes a cost w)
    (s : D) (p : Program) (hp : interpret a p = s) : nodes (w s) - nodes p = 0 := by
  exact Nat.sub_eq_zero_of_le (witness_global_minimum a cost w hl hw s p hp)

end Komorebi.AVOC.CostCertificate
