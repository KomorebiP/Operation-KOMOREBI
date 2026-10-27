module
public import RelationalSyntax
public import Mathlib.ModelTheory.Semantics
public import Mathlib.ModelTheory.Complexity

@[expose] public section
namespace Komorebi.LogicalResolution.Standard
open Komorebi.Representation
open FirstOrder
universe u v w z b t

inductive OpSymbol (A : Type v) : Nat → Type v where
  | step : A → OpSymbol A 1

/-- A one-sorted relationalization: observations still return values in the fixed
    external V, but equality of their values is represented by primitive predicates. -/
inductive RelSymbol (O : Type w) (V : Type z) (B : Type b) : Nat → Type (max w z b) where
  | literals : V → V → RelSymbol O V B 0
  | valueIs : O → V → RelSymbol O V B 1
  | agree : O → O → RelSymbol O V B 2
  | link : B → RelSymbol O V B 2

def language (A : Type v) (O : Type w) (V : Type z) (B : Type b) : FirstOrder.Language :=
  ⟨OpSymbol A, RelSymbol O V B⟩

variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z} {B : Type b}
  {α : Type t}

/-- The model is defined on exactly X, so empty states require no dummy element. -/
@[instance_reducible] def model (S : System X A O V) (K : B → X → X → Prop) :
    (language A O V B).Structure X where
  funMap := fun {n} f xs => match f with
    | .step a => S.step a (xs 0)
  RelMap := fun {n} f xs => match f with
    | .literals v w => v = w
    | .valueIs j v => S.observe j (xs 0) = v
    | .agree j k => S.observe j (xs 0) = S.observe k (xs 1)
    | .link k => K k (xs 0) (xs 1)

def wordTerm (w : List A) (t : (language A O V B).Term α) :
    (language A O V B).Term α :=
  match w with
  | [] => t
  | a :: rest => wordTerm rest (.func (.step a) (fun _ => t))

def stateTerm {k n : Nat} (σ : Fin k → α ⊕ Fin n) (t : StateTerm A k) :
    (language A O V B).Term (α ⊕ Fin n) := wordTerm t.word (.var (σ t.index))

def valueEquality {k n : Nat} (σ : Fin k → α ⊕ Fin n)
    (t s : ValueTerm A O V k) : (language A O V B).BoundedFormula α n :=
  match t, s with
  | .literal v, .literal u => .rel (.literals v u) Fin.elim0
  | .probe i w j, .literal v =>
    .rel (.valueIs j v) (fun _ => stateTerm σ ⟨i,w⟩)
  | .literal v, .probe i w j =>
    .rel (.valueIs j v) (fun _ => stateTerm σ ⟨i,w⟩)
  | .probe i w j, .probe i' w' j' =>
    .rel (.agree j j') ![stateTerm σ ⟨i,w⟩, stateTerm σ ⟨i',w'⟩]

/-- Our syntax binds at the front. Mathlib binds at the last de Bruijn level. -/
def pushMap {k n : Nat} (σ : Fin k → α ⊕ Fin n) : Fin (k+1) → α ⊕ Fin (n+1) :=
  Fin.cases (Sum.inr (Fin.last n)) (fun i => Sum.map id Fin.castSucc (σ i))

def translateAux : {k n : Nat} → RelFormula A O V B k → (Fin k → α ⊕ Fin n) →
    (language A O V B).BoundedFormula α n
  | _, _, .falsum, _ => .falsum
  | _, _, .equal t s, σ => valueEquality σ t s
  | _, _, .related k t s, σ => .rel (.link k) ![stateTerm σ t, stateTerm σ s]
  | _, _, .neg f, σ => (translateAux f σ).not
  | _, _, .conj f g, σ => translateAux f σ ⊓ translateAux g σ
  | _, _, .existsState f, σ => (translateAux f (pushMap σ)).ex

def translate {k : Nat} (f : RelFormula A O V B k) :
    (language A O V B).Formula (Fin k) := translateAux f Sum.inl

section Semantics
variable (S : System X A O V) (K : B → X → X → Prop)

theorem wordTerm_realize (w : List A) (t : (language A O V B).Term α) (ρ : α → X) :
    let _inst : (language A O V B).Structure X := model S K
    (wordTerm w t).realize ρ = run S w (t.realize ρ) := by
  let _inst : (language A O V B).Structure X := model S K
  induction w generalizing t with
  | nil => rfl
  | cons a w ih => exact ih (.func (.step a) (fun _ => t))

theorem stateTerm_realize {k n : Nat} (σ : Fin k → α ⊕ Fin n)
    (t : StateTerm A k) (v : α → X) (xs : Fin n → X) :
    let _inst : (language A O V B).Structure X := model S K
    (stateTerm (O:=O) (V:=V) (B:=B) σ t).realize (Sum.elim v xs) =
      t.eval S (fun i => Sum.elim v xs (σ i)) := by
  let _inst : (language A O V B).Structure X := model S K
  exact wordTerm_realize S K t.word (.var (σ t.index)) (Sum.elim v xs)

theorem valueEquality_realize {k n : Nat} (σ : Fin k → α ⊕ Fin n)
    (t s : ValueTerm A O V k) (v : α → X) (xs : Fin n → X) :
    let _inst : (language A O V B).Structure X := model S K
    (valueEquality (B:=B) σ t s).Realize v xs ↔
      t.eval S (fun i => Sum.elim v xs (σ i)) =
      s.eval S (fun i => Sum.elim v xs (σ i)) := by
  let _inst : (language A O V B).Structure X := model S K
  cases t with
  | literal a =>
    cases s with
    | literal b => rfl
    | probe i w j =>
      change S.observe j ((stateTerm (O:=O) (V:=V) (B:=B) σ ⟨i,w⟩).realize
        (Sum.elim v xs)) = a ↔ a = behavior S (Sum.elim v xs (σ i)) w j
      rw [stateTerm_realize]
      exact eq_comm
  | probe i w j =>
    cases s with
    | literal a =>
      change S.observe j ((stateTerm (O:=O) (V:=V) (B:=B) σ ⟨i,w⟩).realize
        (Sum.elim v xs)) = a ↔ behavior S (Sum.elim v xs (σ i)) w j = a
      rw [stateTerm_realize]
      rfl
    | probe i' w' j' =>
      change S.observe j ((stateTerm (O:=O) (V:=V) (B:=B) σ ⟨i,w⟩).realize
        (Sum.elim v xs)) = S.observe j' ((stateTerm (O:=O) (V:=V) (B:=B) σ ⟨i',w'⟩).realize
        (Sum.elim v xs)) ↔ _
      simp only [stateTerm_realize]
      rfl

theorem binder_assignment {k n : Nat} (σ : Fin k → α ⊕ Fin n)
    (v : α → X) (xs : Fin n → X) (x : X) :
    (fun i => Sum.elim v (Fin.snoc xs x) (pushMap σ i)) =
      extend x (fun i => Sum.elim v xs (σ i)) := by
  funext i
  refine Fin.cases ?_ (fun j => ?_) i
  · simp [pushMap, extend]
  · cases h : σ j <;> simp [pushMap, extend, h]

/-- Satisfaction preservation holds at arbitrary free/bound contexts and nesting. -/
theorem translateAux_realize {k n : Nat} (f : RelFormula A O V B k)
    (σ : Fin k → α ⊕ Fin n) (v : α → X) (xs : Fin n → X) :
    let _inst : (language A O V B).Structure X := model S K
    (translateAux f σ).Realize v xs ↔
      f.Holds S K (fun i => Sum.elim v xs (σ i)) := by
  let _inst : (language A O V B).Structure X := model S K
  induction f generalizing n with
  | falsum => rfl
  | equal t s => exact valueEquality_realize S K σ t s v xs
  | related k t s =>
    change K k ((stateTerm (O:=O) (V:=V) (B:=B) σ t).realize (Sum.elim v xs))
      ((stateTerm (O:=O) (V:=V) (B:=B) σ s).realize (Sum.elim v xs)) ↔ _
    simp only [stateTerm_realize]
    rfl
  | neg f ih =>
    simpa only [translateAux, FirstOrder.Language.BoundedFormula.realize_not,
      RelFormula.Holds] using not_congr (ih σ xs)
  | conj f g ihf ihg =>
    simpa only [translateAux, FirstOrder.Language.BoundedFormula.realize_inf,
      RelFormula.Holds] using and_congr (ihf σ xs) (ihg σ xs)
  | existsState f ih =>
    simp only [translateAux, FirstOrder.Language.BoundedFormula.realize_ex,
      RelFormula.Holds]
    apply exists_congr
    intro x
    have h := ih (pushMap σ) (Fin.snoc xs x)
    simpa only [binder_assignment] using h

theorem translate_realize {k : Nat} (f : RelFormula A O V B k) (ρ : Fin k → X) :
    let _inst : (language A O V B).Structure X := model S K
    (translate f).Realize ρ ↔ f.Holds S K ρ :=
  translateAux_realize S K f Sum.inl ρ Fin.elim0

theorem original_formula_realize {k : Nat} (f : Formula A O V k) (ρ : Fin k → X) :
    let _inst : (language A O V B).Structure X := model S K
    (translate (B:=B) f.relational).Realize ρ ↔ f.Holds S ρ :=
  (translate_realize S K f.relational ρ).trans (observational_inclusion S K f ρ)

end Semantics

/-- Formula rank on Mathlib's actual locally nameless syntax. -/
def rank {L : FirstOrder.Language} {α : Type t} : {n : Nat} → L.BoundedFormula α n → Nat
  | _, .falsum => 0
  | _, .equal _ _ => 0
  | _, .rel _ _ => 0
  | _, .imp f g => max (rank f) (rank g)
  | _, .all f => rank f + 1

theorem translateAux_rank {k n : Nat} (f : RelFormula A O V B k) (σ : Fin k → α ⊕ Fin n) :
    rank (translateAux f σ) = f.qrank := by
  induction f generalizing n with
  | falsum => rfl
  | equal t s => cases t <;> cases s <;> rfl
  | related => rfl
  | neg f ih => simp [translateAux, FirstOrder.Language.BoundedFormula.not, rank, ih, RelFormula.qrank]
  | conj f g ihf ihg =>
    simp [translateAux, Min.min, FirstOrder.Language.BoundedFormula.not, rank, ihf, ihg, RelFormula.qrank]
  | existsState f ih =>
    simp [translateAux, FirstOrder.Language.BoundedFormula.ex,
      FirstOrder.Language.BoundedFormula.not, rank, ih, RelFormula.qrank]

theorem translate_rank {k : Nat} (f : RelFormula A O V B k) : rank (translate f) = f.qrank :=
  translateAux_rank f Sum.inl

theorem rank_zero_qf {L : FirstOrder.Language} {α : Type t} {n : Nat}
    (f : L.BoundedFormula α n) (h : rank f = 0) : f.IsQF := by
  induction f with
  | falsum => exact .falsum
  | equal t s => exact (FirstOrder.Language.BoundedFormula.IsAtomic.equal t s).isQF
  | rel r ts => exact (FirstOrder.Language.BoundedFormula.IsAtomic.rel r ts).isQF
  | imp f g ihf ihg =>
    have hf : rank f = 0 := Nat.max_eq_zero_iff.mp h |>.1
    have hg : rank g = 0 := Nat.max_eq_zero_iff.mp h |>.2
    exact .imp (ihf hf) (ihg hg)
  | all f ih => simp [rank] at h

theorem qf_rank_zero {L : FirstOrder.Language} {α : Type t} {n : Nat}
    (f : L.BoundedFormula α n) (h : f.IsQF) : rank f = 0 := by
  induction h with
  | falsum => rfl
  | of_isAtomic ha => cases ha <;> rfl
  | imp hf hg ihf ihg => simp [rank, ihf, ihg]

theorem translate_qf_iff {k : Nat} (f : RelFormula A O V B k) :
    (translate f).IsQF ↔ f.qrank = 0 := by
  constructor
  · intro h; rw [← translate_rank]; exact qf_rank_zero _ h
  · intro h; apply rank_zero_qf; rw [translate_rank,h]

theorem standard_relational_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop)
    (hk : ∀ k x y, K k x y ↔ L k (q.encode x) (q.encode y))
    {n : Nat} (f : RelFormula A O V B n) (ρ : Fin n → X) :
    (let _inst : (language A O V B).Structure X := model S K
     (translate f).Realize ρ) ↔
    (let _inst : (language A O V B).Structure Y := model T L
     (translate f).Realize (fun i => q.encode (ρ i))) :=
  (translate_realize S K f ρ).trans
    ((relational_formula_transport q hs K L hk f ρ).trans
      (translate_realize T L f (fun i => q.encode (ρ i))).symm)

theorem standard_observational_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop)
    {n : Nat} (f : Formula A O V n) (ρ : Fin n → X) :
    (let _inst : (language A O V B).Structure X := model S K
     (translate (B:=B) f.relational).Realize ρ) ↔
    (let _inst : (language A O V B).Structure Y := model T L
     (translate (B:=B) f.relational).Realize (fun i => q.encode (ρ i))) :=
  (original_formula_realize S K f ρ).trans
    ((formula_transport q hs f ρ).trans
      (original_formula_realize T L f (fun i => q.encode (ρ i))).symm)

end Komorebi.LogicalResolution.Standard
