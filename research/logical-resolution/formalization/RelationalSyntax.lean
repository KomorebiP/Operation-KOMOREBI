module
public import ObservationSyntax

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation
universe u v w z b

/-- A well-scoped state term is a variable followed by a finite operation word. -/
structure StateTerm (A : Type v) (n : Nat) where
  index : Fin n
  word : List A

/-- The old observational language enriched with named binary state relations.
    State equality is still not a constructor. -/
inductive RelFormula (A : Type v) (O : Type w) (V : Type z) (B : Type b) :
    Nat → Type (max v w z b) where
  | falsum {n} : RelFormula A O V B n
  | equal {n} : ValueTerm A O V n → ValueTerm A O V n → RelFormula A O V B n
  | related {n} : B → StateTerm A n → StateTerm A n → RelFormula A O V B n
  | neg {n} : RelFormula A O V B n → RelFormula A O V B n
  | conj {n} : RelFormula A O V B n → RelFormula A O V B n → RelFormula A O V B n
  | existsState {n} : RelFormula A O V B (n+1) → RelFormula A O V B n

variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z} {B : Type b} {n : Nat}

def StateTerm.eval (S : System X A O V) (ρ : Fin n → X) (t : StateTerm A n) : X :=
  run S t.word (ρ t.index)

def RelFormula.Holds (S : System X A O V) (K : B → X → X → Prop) :
    {n : Nat} → RelFormula A O V B n → (Fin n → X) → Prop
  | _, .falsum, _ => False
  | _, .equal t s, ρ => t.eval S ρ = s.eval S ρ
  | _, .related k t s, ρ => K k (t.eval S ρ) (s.eval S ρ)
  | _, .neg f, ρ => ¬ f.Holds S K ρ
  | _, .conj f g, ρ => f.Holds S K ρ ∧ g.Holds S K ρ
  | _, .existsState f, ρ => ∃ x, f.Holds S K (extend x ρ)

def RelFormula.qrank : {n : Nat} → RelFormula A O V B n → Nat
  | _, .falsum => 0
  | _, .equal _ _ => 0
  | _, .related _ _ _ => 0
  | _, .neg f => f.qrank
  | _, .conj f g => max f.qrank g.qrank
  | _, .existsState f => f.qrank + 1

def Formula.relational : {n : Nat} → Formula A O V n → RelFormula A O V B n
  | _, .falsum => .falsum
  | _, .equal t s => .equal t s
  | _, .neg f => .neg f.relational
  | _, .conj f g => .conj f.relational g.relational
  | _, .existsState f => .existsState f.relational

theorem observational_inclusion (S : System X A O V) (K : B → X → X → Prop)
    (f : Formula A O V n) (ρ : Fin n → X) :
    f.relational.Holds S K ρ ↔ f.Holds S ρ := by
  induction f with
  | falsum => rfl
  | equal => rfl
  | neg f ih => exact not_congr (ih ρ)
  | conj f g ihf ihg => exact and_congr (ihf ρ) (ihg ρ)
  | existsState f ih => exact exists_congr (fun x => ih (extend x ρ))

theorem stateTerm_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (t : StateTerm A n) (ρ : Fin n → X) :
    q.encode (t.eval S ρ) = t.eval T (fun i => q.encode (ρ i)) :=
  transport_run q t.word (ρ t.index)

/-- Exact relational transport requires reflection as well as preservation of atoms. -/
theorem relational_formula_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop)
    (hk : ∀ k x y, K k x y ↔ L k (q.encode x) (q.encode y))
    (f : RelFormula A O V B n) (ρ : Fin n → X) :
    f.Holds S K ρ ↔ f.Holds T L (fun i => q.encode (ρ i)) := by
  induction f with
  | falsum => rfl
  | equal t s =>
    change t.eval S ρ = s.eval S ρ ↔ _
    rw [valueTerm_transport q ρ t, valueTerm_transport q ρ s]
    rfl
  | related k t s =>
    change K k (t.eval S ρ) (s.eval S ρ) ↔ _
    rw [hk, stateTerm_transport, stateTerm_transport]
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

/-- A binary relation can be transported exactly through an encoder iff it is
    constant on both fibers. Surjectivity is not needed for this local criterion. -/
theorem relation_descends_iff (q : X → Y) (K : X → X → Prop) :
    (∃ L : Y → Y → Prop, ∀ x y, K x y ↔ L (q x) (q y)) ↔
      (∀ x x' y y', q x = q x' → q y = q y' → (K x y ↔ K x' y')) := by
  constructor
  · rintro ⟨L, hL⟩ x x' y y' hx hy
    rw [hL, hL, hx, hy]
  · intro h
    refine ⟨fun a b => ∃ x y, q x = a ∧ q y = b ∧ K x y, ?_⟩
    intro x y
    constructor
    · intro hk; exact ⟨x, y, rfl, rfl, hk⟩
    · rintro ⟨x', y', hx, hy, hk⟩
      exact (h x' x y' y hx hy).mp hk

theorem relation_descends_behavior_iff (S : System X A O V) (K : X → X → Prop) :
    (∃ L : BehaviorQuotient S → BehaviorQuotient S → Prop,
      ∀ x y, K x y ↔ L (Quotient.mk _ x) (Quotient.mk _ y)) ↔
    (∀ x x' y y', ObsEq S x x' → ObsEq S y y' → (K x y ↔ K x' y')) := by
  rw [relation_descends_iff]
  constructor
  · intro h x x' y y' hx hy
    exact h x x' y y' (Quotient.sound hx) (Quotient.sound hy)
  · intro h x x' y y' hx hy
    exact h x x' y y' (Quotient.exact hx) (Quotient.exact hy)

def quotientRelation (S : System X A O V) (K : B → X → X → Prop)
    (k : B) (a b : BehaviorQuotient S) : Prop :=
  ∃ x y, Quotient.mk _ x = a ∧ Quotient.mk _ y = b ∧ K k x y

theorem quotientRelation_correct (S : System X A O V) (K : B → X → X → Prop)
    (hc : ∀ k x x' y y', ObsEq S x x' → ObsEq S y y' → (K k x y ↔ K k x' y'))
    (k : B) (x y : X) :
    K k x y ↔ quotientRelation S K k (Quotient.mk _ x) (Quotient.mk _ y) := by
  constructor
  · intro hk; exact ⟨x,y,rfl,rfl,hk⟩
  · rintro ⟨x',y',hx,hy,hk⟩
    exact (hc k x' x y' y (Quotient.exact hx) (Quotient.exact hy)).mp hk

theorem relational_quotient_formula (S : System X A O V) (K : B → X → X → Prop)
    (hc : ∀ k x x' y y', ObsEq S x x' → ObsEq S y y' → (K k x y ↔ K k x' y'))
    (f : RelFormula A O V B n) (ρ : Fin n → X) :
    f.Holds S K ρ ↔ f.Holds (quotientSystem S) (quotientRelation S K)
      (fun i => Quotient.mk _ (ρ i)) := by
  apply relational_formula_transport (quotientTransport S) _ K (quotientRelation S K)
    (quotientRelation_correct S K hc) f ρ
  intro y
  induction y using Quotient.inductionOn with
  | h x => exact ⟨x,rfl⟩

end Komorebi.LogicalResolution
