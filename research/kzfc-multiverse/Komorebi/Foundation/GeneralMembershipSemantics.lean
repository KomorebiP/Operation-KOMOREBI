import Komorebi.Foundation.GuardedTheory

/-!
# Membership-language semantics in arbitrary structures

No transitivity, external well-foundedness, powerset correctness, cardinal
absoluteness, or set-theoretic principle is assumed here.
-/

universe u v w

namespace Komorebi.GeneralMembershipSemantics

open FirstOrder FirstOrder.Language
open MembershipFormula

variable {M : Type u} [language.Structure M]

def member (x y : M) : Prop :=
  Structure.RelMap (L := language) MembershipSymbol.mem ![x, y]

def assign {α : Type v} (e : α → M) (x : M) : Option α → M
  | none => x
  | some a => e a

@[simp]
theorem memF_realize {α : Type v} (x y : α) (e : α → M) :
    (memF x y).Realize e ↔ member (e x) (e y) := by
  exact Formula.realize_rel₂

@[simp]
theorem eqF_realize {α : Type v} (x y : α) (e : α → M) :
    (eqF x y).Realize e ↔ e x = e y := by
  simp [eqF]

@[simp]
theorem allF_realize {α : Type v} (p : language.Formula (Option α)) (e : α → M) :
    (allF p).Realize e ↔ ∀ x : M, p.Realize (assign e x) := by
  simp only [allF, Formula.Realize, BoundedFormula.realize_all,
    BoundedFormula.realize_relabel]
  apply forall_congr'
  intro x
  apply Iff.of_eq
  congr 1
  · funext a
    cases a <;> simp [MembershipFormula.bind, assign, Function.comp_def, Fin.snoc]
  · funext i
    exact Fin.elim0 i

@[simp]
theorem exF_realize {α : Type v} (p : language.Formula (Option α)) (e : α → M) :
    (exF p).Realize e ↔ ∃ x : M, p.Realize (assign e x) := by
  simp only [exF, Formula.Realize, BoundedFormula.realize_ex,
    BoundedFormula.realize_relabel]
  apply exists_congr
  intro x
  apply Iff.of_eq
  congr 1
  · funext a
    cases a <;> simp [MembershipFormula.bind, assign, Function.comp_def, Fin.snoc]
  · funext i
    exact Fin.elim0 i

def subset (x y : M) : Prop := ∀ z, member z x → member z y

def IsEmpty (x : M) : Prop := ∀ z, ¬ member z x

def IsPair (p x y : M) : Prop := ∀ z, member z p ↔ z = x ∨ z = y

def IsUnion (r x : M) : Prop :=
  ∀ z, member z r ↔ ∃ y, member y x ∧ member z y

def IsPower (p x : M) : Prop := ∀ z, member z p ↔ subset z x

def IsSuccessor (r x : M) : Prop := ∀ z, member z r ↔ z = x ∨ member z x

def IsInductive (w : M) : Prop :=
  (∃ z, IsEmpty z ∧ member z w) ∧
    ∀ x, member x w → ∃ r, IsSuccessor r x ∧ member r w

@[simp]
theorem subsetF_realize {α : Type v} (x y : α) (e : α → M) :
    (subsetF x y).Realize e ↔ subset (e x) (e y) := by
  simp [subsetF, subset, assign]

@[simp]
theorem emptyF_realize {α : Type v} (x : α) (e : α → M) :
    (emptyF x).Realize e ↔ IsEmpty (e x) := by
  simp [emptyF, IsEmpty, assign]

@[simp]
theorem unorderedPairF_realize {α : Type v} (p x y : α) (e : α → M) :
    (unorderedPairF p x y).Realize e ↔ IsPair (e p) (e x) (e y) := by
  simp [unorderedPairF, IsPair, assign]

@[simp]
theorem successorF_realize {α : Type v} (r x : α) (e : α → M) :
    (successorF r x).Realize e ↔ IsSuccessor (e r) (e x) := by
  simp [successorF, IsSuccessor, assign]

@[simp]
theorem inductiveF_realize {α : Type v} (w : α) (e : α → M) :
    (inductiveF w).Realize e ↔ IsInductive (e w) := by
  simp [inductiveF, IsInductive, assign]

/-- The generic membership relation reduces to actual membership only for ZFSet. -/
@[simp]
theorem member_zfset (x y : ZFSet.{u}) : member x y ↔ x ∈ y := Iff.rfl

end Komorebi.GeneralMembershipSemantics
