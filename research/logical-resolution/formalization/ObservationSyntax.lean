module
public import RepresentationCore

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation
universe u v w z

/-- Terms of the fixed observation-value sort. State variables are well scoped. -/
inductive ValueTerm (A : Type v) (O : Type w) (V : Type z) (n : Nat) where
  | literal : V → ValueTerm A O V n
  | probe : Fin n → List A → O → ValueTerm A O V n

/-- First-order observational fragment: value equality is allowed, state equality is not. -/
inductive Formula (A : Type v) (O : Type w) (V : Type z) : Nat → Type (max v w z) where
  | falsum {n} : Formula A O V n
  | equal {n} : ValueTerm A O V n → ValueTerm A O V n → Formula A O V n
  | neg {n} : Formula A O V n → Formula A O V n
  | conj {n} : Formula A O V n → Formula A O V n → Formula A O V n
  | existsState {n} : Formula A O V (n+1) → Formula A O V n

variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z} {n : Nat}

def extend (x : X) (ρ : Fin n → X) : Fin (n+1) → X := Fin.cases x ρ

def ValueTerm.eval (S : System X A O V) (ρ : Fin n → X) : ValueTerm A O V n → V
  | .literal v => v
  | .probe i word j => behavior S (ρ i) word j

def Formula.Holds (S : System X A O V) : {n : Nat} → Formula A O V n → (Fin n → X) → Prop
  | _, .falsum, _ => False
  | _, .equal t s, ρ => t.eval S ρ = s.eval S ρ
  | _, .neg f, ρ => ¬ f.Holds S ρ
  | _, .conj f g, ρ => f.Holds S ρ ∧ g.Holds S ρ
  | _, .existsState f, ρ => ∃ x, f.Holds S (extend x ρ)

def ValueTerm.depth : ValueTerm A O V n → Nat
  | .literal _ => 0
  | .probe _ word _ => word.length

def Formula.depth : {n : Nat} → Formula A O V n → Nat
  | _, .falsum => 0
  | _, .equal t s => max t.depth s.depth
  | _, .neg f => f.depth
  | _, .conj f g => max f.depth g.depth
  | _, .existsState f => f.depth

def Formula.qrank : {n : Nat} → Formula A O V n → Nat
  | _, .falsum => 0
  | _, .equal _ _ => 0
  | _, .neg f => f.qrank
  | _, .conj f g => max f.qrank g.qrank
  | _, .existsState f => f.qrank + 1

def Formula.disj (f g : Formula A O V n) : Formula A O V n := .neg (.conj (.neg f) (.neg g))
def Formula.forallState (f : Formula A O V (n+1)) : Formula A O V n := .neg (.existsState (.neg f))

def observedValue (word : List A) (j : O) (v : V) : Formula A O V 1 :=
  .equal (.probe 0 word j) (.literal v)

theorem observedValue_holds (S : System X A O V) (x : X) (word : List A) (j : O) (v : V) :
    (observedValue word j v).Holds S (fun _ => x) ↔ behavior S x word j = v := Iff.rfl

theorem observedValue_depth (word : List A) (j : O) (v : V) :
    (observedValue word j v).depth = word.length := by
  simp [observedValue, Formula.depth, ValueTerm.depth]

theorem observedValue_qrank (word : List A) (j : O) (v : V) :
    (observedValue word j v).qrank = 0 := rfl

theorem extend_map (q : X → Y) (x : X) (ρ : Fin n → X) :
    (fun i => q (extend x ρ i)) = extend (q x) (fun i => q (ρ i)) := by
  funext i
  refine Fin.cases ?_ (fun j => ?_) i <;> rfl

theorem valueTerm_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (ρ : Fin n → X) (t : ValueTerm A O V n) :
    t.eval S ρ = t.eval T (fun i => q.encode (ρ i)) := by
  cases t with
  | literal v => rfl
  | probe i word j => exact transport_behavior q word j (ρ i)

/-- Surjectivity is essential to reflection of quantified witnesses. -/
theorem formula_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (f : Formula A O V n) (ρ : Fin n → X) :
    f.Holds S ρ ↔ f.Holds T (fun i => q.encode (ρ i)) := by
  induction f with
  | falsum => exact Iff.rfl
  | equal t s =>
    change t.eval S ρ = s.eval S ρ ↔ _
    rw [valueTerm_transport q ρ t, valueTerm_transport q ρ s]
    rfl
  | neg f ih => exact not_congr (ih ρ)
  | conj f g ihf ihg => exact and_congr (ihf ρ) (ihg ρ)
  | existsState f ih =>
    constructor
    · rintro ⟨x, hx⟩
      refine ⟨q.encode x, ?_⟩
      have h := (ih (extend x ρ)).mp hx
      simpa only [extend_map] using h
    · rintro ⟨y, hy⟩
      obtain ⟨x, rfl⟩ := hs y
      refine ⟨x, ?_⟩
      apply (ih (extend x ρ)).mpr
      simpa only [extend_map] using hy

theorem quotient_formula (S : System X A O V) (f : Formula A O V n) (ρ : Fin n → X) :
    f.Holds S ρ ↔ f.Holds (quotientSystem S) (fun i => Quotient.mk _ (ρ i)) := by
  apply formula_transport (quotientTransport S)
  intro y
  induction y using Quotient.inductionOn with
  | h x => exact ⟨x, rfl⟩

end Komorebi.LogicalResolution
