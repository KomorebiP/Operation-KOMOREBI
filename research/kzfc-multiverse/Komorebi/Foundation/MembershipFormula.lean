import Komorebi.Foundation.SetCardinalCoding
import Mathlib.ModelTheory.Semantics

/-!
# Actual first-order formulas in the language containing only membership

These are Mathlib first-order syntax trees, not predicates inserted as relation
symbols. Quantifier helpers merely manage capture-free variable binding.
-/

universe u v

namespace Komorebi.MembershipFormula

open FirstOrder FirstOrder.Language
open SetFilterCoding

inductive MembershipSymbol : ℕ → Type
  | mem : MembershipSymbol 2

def language : Language := ⟨fun _ => Empty, MembershipSymbol⟩

instance membershipStructure : language.Structure ZFSet.{u} where
  funMap f := nomatch f
  RelMap | .mem => fun xs => xs 0 ∈ xs 1

def memF {α : Type v} (x y : α) : language.Formula α :=
  Relations.formula₂ (L := language) MembershipSymbol.mem (.var x) (.var y)

def eqF {α : Type v} (x y : α) : language.Formula α :=
  Term.equal (.var x) (.var y)

def bind {α : Type v} : Option α → α ⊕ Fin 1
  | none => .inr 0
  | some a => .inl a

def allF {α : Type v} (p : language.Formula (Option α)) : language.Formula α :=
  (BoundedFormula.relabel bind p).all

def exF {α : Type v} (p : language.Formula (Option α)) : language.Formula α :=
  (BoundedFormula.relabel bind p).ex

def extend {α : Type v} (e : α → ZFSet.{u}) (x : ZFSet.{u}) : Option α → ZFSet.{u}
  | none => x
  | some a => e a

@[simp]
theorem realize_memF {α : Type v} (x y : α) (e : α → ZFSet.{u}) :
    (memF x y).Realize e ↔ e x ∈ e y := by
  exact Formula.realize_rel₂

@[simp]
theorem realize_eqF {α : Type v} (x y : α) (e : α → ZFSet.{u}) :
    (eqF x y).Realize e ↔ e x = e y := by
  simp [eqF]

@[simp]
theorem realize_allF {α : Type v} (p : language.Formula (Option α))
    (e : α → ZFSet.{u}) :
    (allF p).Realize e ↔ ∀ x : ZFSet.{u}, p.Realize (extend e x) := by
  simp only [allF, Formula.Realize, BoundedFormula.realize_all,
    BoundedFormula.realize_relabel]
  apply forall_congr'
  intro x
  apply Iff.of_eq
  congr 1
  · funext a
    cases a <;> simp [bind, extend, Function.comp_def, Fin.snoc]
  · funext i
    exact Fin.elim0 i

@[simp]
theorem realize_exF {α : Type v} (p : language.Formula (Option α))
    (e : α → ZFSet.{u}) :
    (exF p).Realize e ↔ ∃ x : ZFSet.{u}, p.Realize (extend e x) := by
  simp only [exF, Formula.Realize, BoundedFormula.realize_ex,
    BoundedFormula.realize_relabel]
  apply exists_congr
  intro x
  apply Iff.of_eq
  congr 1
  · funext a
    cases a <;> simp [bind, extend, Function.comp_def, Fin.snoc]
  · funext i
    exact Fin.elim0 i

def subsetF {α : Type v} (x y : α) : language.Formula α :=
  allF ((memF none (some x)).imp (memF none (some y)))

def emptyF {α : Type v} (x : α) : language.Formula α :=
  allF (memF none (some x)).not

def interF {α : Type v} (r s t : α) : language.Formula α :=
  allF ((memF none (some r)).iff
    (memF none (some s) ⊓ memF none (some t)))

def diffF {α : Type v} (r x s : α) : language.Formula α :=
  allF ((memF none (some r)).iff
    (memF none (some x) ⊓ (memF none (some s)).not))

def relInterF {α : Type v} (r x s : α) : language.Formula α :=
  allF ((memF none (some r)).iff (memF none (some x) ⊓
    allF ((memF none (some (some s))).imp (memF (some none) none))))

@[simp]
theorem realize_subsetF {α : Type v} (x y : α) (e : α → ZFSet.{u}) :
    (subsetF x y).Realize e ↔ e x ⊆ e y := by
  simp [subsetF, extend, ZFSet.subset_def]

@[simp]
theorem realize_emptyF {α : Type v} (x : α) (e : α → ZFSet.{u}) :
    (emptyF x).Realize e ↔ e x = ∅ := by
  simp [emptyF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_interF {α : Type v} (r s t : α) (e : α → ZFSet.{u}) :
    (interF r s t).Realize e ↔ e r = e s ∩ e t := by
  simp [interF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_diffF {α : Type v} (r x s : α) (e : α → ZFSet.{u}) :
    (diffF r x s).Realize e ↔ e r = e x \ e s := by
  simp [diffF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_relInterF {α : Type v} (r x s : α) (e : α → ZFSet.{u}) :
    (relInterF r x s).Realize e ↔ e r = relInter (e x) (e s) := by
  simp [relInterF, extend, relInter, ZFSet.ext_iff]

end Komorebi.MembershipFormula
