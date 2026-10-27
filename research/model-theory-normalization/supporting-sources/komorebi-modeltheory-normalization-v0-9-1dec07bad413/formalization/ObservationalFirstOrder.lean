module
public import ObservationalNormalization

@[expose] public section

namespace Komorebi.ModelTheory
open Komorebi.Representation
universe u v w z
variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z}

/-- State terms are already flattened into a variable and its operation word. -/
abbrev StateTerm (A : Type v) (n : Nat) := Fin n × List A

/-- A first-order observational fragment: quantifiers range over states, but
    equality compares observable VALUES, never states or state terms. -/
inductive ObsFO (A : Type v) (O : Type w) (V : Type z) : Nat → Type (max v w z) where
  | truth {n} : ObsFO A O V n
  | test {n} : StateTerm A n → O → V → ObsFO A O V n
  | compare {n} : StateTerm A n → O → StateTerm A n → O → ObsFO A O V n
  | neg {n} : ObsFO A O V n → ObsFO A O V n
  | conj {n} : ObsFO A O V n → ObsFO A O V n → ObsFO A O V n
  | ex {n} : ObsFO A O V (n+1) → ObsFO A O V n

/-- Variable zero is the most recently bound variable. -/
def extendEnv {n : Nat} (x : X) (e : Fin n → X) : Fin (n+1) → X :=
  Fin.cases x e

def termObservation {n : Nat} (S : System X A O V) (e : Fin n → X)
    (t : StateTerm A n) (j : O) : V := behavior S (e t.1) t.2 j

def ObsFO.Sat (S : System X A O V) : {n : Nat} → ObsFO A O V n → (Fin n → X) → Prop
  | _, .truth, _ => True
  | _, .test t j c, e => termObservation S e t j = c
  | _, .compare t j u k, e => termObservation S e t j = termObservation S e u k
  | _, .neg f, e => ¬ f.Sat S e
  | _, .conj f g, e => f.Sat S e ∧ g.Sat S e
  | _, .ex f, e => ∃ x, f.Sat S (extendEnv x e)

def ObsFO.quantifierRank : {n : Nat} → ObsFO A O V n → Nat
  | _, .truth => 0
  | _, .test _ _ _ => 0
  | _, .compare _ _ _ _ => 0
  | _, .neg f => f.quantifierRank
  | _, .conj f g => max f.quantifierRank g.quantifierRank
  | _, .ex f => f.quantifierRank + 1

def ObsFO.termHorizon : {n : Nat} → ObsFO A O V n → Nat
  | _, .truth => 0
  | _, .test t _ _ => t.2.length
  | _, .compare t _ u _ => max t.2.length u.2.length
  | _, .neg f => f.termHorizon
  | _, .conj f g => max f.termHorizon g.termHorizon
  | _, .ex f => f.termHorizon

theorem encode_extend (q : X → Y) {n : Nat} (x : X) (e : Fin n → X) :
    (fun i => q (extendEnv x e i)) = extendEnv (q x) (fun i => q (e i)) := by
  funext i
  refine Fin.cases ?_ (fun j => ?_) i <;> rfl

theorem term_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) {n : Nat} (e : Fin n → X) (t : StateTerm A n) (j : O) :
    termObservation S e t j = termObservation T (fun i => q.encode (e i)) t j :=
  transport_behavior q _ _ _

/-- Surjectivity is required: target quantifier witnesses must lift to source states. -/
theorem observational_first_order_transport
    {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (surj : ∀ y, ∃ x, q.encode x = y)
    {n : Nat} (f : ObsFO A O V n) (e : Fin n → X) :
    f.Sat S e ↔ f.Sat T (fun i => q.encode (e i)) := by
  induction f with
  | truth => rfl
  | test t j c =>
    change (termObservation S e t j = c) ↔
      (termObservation T (fun i => q.encode (e i)) t j = c)
    rw [term_transport q]
  | compare t j u k =>
    change (termObservation S e t j = termObservation S e u k) ↔
      (termObservation T (fun i => q.encode (e i)) t j =
       termObservation T (fun i => q.encode (e i)) u k)
    rw [term_transport q, term_transport q]
  | neg f ih => exact not_congr (ih e)
  | conj f g ihf ihg => exact and_congr (ihf e) (ihg e)
  | ex f ih =>
    change (∃ x, f.Sat S (extendEnv x e)) ↔
      (∃ y, f.Sat T (extendEnv y (fun i => q.encode (e i))))
    constructor
    · rintro ⟨x, hx⟩
      refine ⟨q.encode x, ?_⟩
      have h := (ih (extendEnv x e)).mp hx
      rw [encode_extend] at h
      exact h
    · rintro ⟨y, hy⟩
      obtain ⟨x, hx⟩ := surj y
      refine ⟨x, (ih (extendEnv x e)).mpr ?_⟩
      rw [encode_extend, hx]
      exact hy

theorem quotient_encoding_surjective (S : System X A O V) :
    ∀ y, ∃ x, (quotientTransport S).encode x = y := by
  intro y
  refine Quotient.inductionOn y ?_
  intro x
  exact ⟨x, rfl⟩

theorem quotient_preserves_observational_first_order
    (S : System X A O V) {n : Nat} (f : ObsFO A O V n) (e : Fin n → X) :
    f.Sat S e ↔ f.Sat (quotientSystem S) (fun i => (quotientTransport S).encode (e i)) :=
  observational_first_order_transport (quotientTransport S) (quotient_encoding_surjective S) f e

/-- Same-model tuple invariance, including nested state quantifiers. -/
theorem first_order_tuple_invariance (S : System X A O V) {n : Nat}
    (f : ObsFO A O V n) (e e' : Fin n → X)
    (he : ∀ i, ObsEq S (e i) (e' i)) : f.Sat S e ↔ f.Sat S e' := by
  have heq : (fun i => (quotientTransport S).encode (e i)) =
      (fun i => (quotientTransport S).encode (e' i)) := by
    funext i
    exact (quotient_exact S _ _).mpr (he i)
  have hx := quotient_preserves_observational_first_order S f e
  have hy := quotient_preserves_observational_first_order S f e'
  apply hx.trans
  rw [heq]
  exact hy.symm

/-- This fragment's full one-variable type agrees with behavior; this is NOT
    a claim about ordinary first-order types with equality on states. -/
theorem first_order_observation_type_iff (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ f : ObsFO A O V 1,
      f.Sat S (fun _ => x) ↔ f.Sat S (fun _ => y) := by
  constructor
  · intro h f
    exact first_order_tuple_invariance S f _ _ (fun _ => h)
  · intro h w j
    have hy := (h (.test (0, w) j (behavior S x w j))).mp rfl
    exact hy.symm

theorem quantified_terms_need_separate_horizon (w : List A) (j : O) (c : V) :
    (ObsFO.test (A := A) (n := 1) (0,w) j c).quantifierRank = 0 ∧
    (ObsFO.test (A := A) (n := 1) (0,w) j c).termHorizon = w.length := ⟨rfl,rfl⟩

end Komorebi.ModelTheory
