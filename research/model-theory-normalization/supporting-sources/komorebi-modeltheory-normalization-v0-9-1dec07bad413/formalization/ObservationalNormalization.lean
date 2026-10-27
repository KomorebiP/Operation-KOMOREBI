module
public import FiniteCertificates

@[expose] public section

namespace Komorebi.ModelTheory
open Komorebi.Representation
universe u v w z
variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z}

/-- One-state observational syntax. There is deliberately no equality on states. -/
inductive ObsFormula (A : Type v) (O : Type w) (V : Type z) where
  | truth : ObsFormula A O V
  | test : O → V → ObsFormula A O V
  | neg : ObsFormula A O V → ObsFormula A O V
  | conj : ObsFormula A O V → ObsFormula A O V → ObsFormula A O V
  | after : A → ObsFormula A O V → ObsFormula A O V

def ObsFormula.Sat (S : System X A O V) : ObsFormula A O V → X → Prop
  | .truth, _ => True
  | .test j c, x => S.observe j x = c
  | .neg f, x => ¬ f.Sat S x
  | .conj f g, x => f.Sat S x ∧ g.Sat S x
  | .after a f, x => f.Sat S (S.step a x)

/-- Normal form: Boolean structure is retained; every action path is attached to a test. -/
inductive PathFormula (A : Type v) (O : Type w) (V : Type z) where
  | truth : PathFormula A O V
  | atom : List A → O → V → PathFormula A O V
  | neg : PathFormula A O V → PathFormula A O V
  | conj : PathFormula A O V → PathFormula A O V → PathFormula A O V

def PathFormula.Sat (S : System X A O V) : PathFormula A O V → X → Prop
  | .truth, _ => True
  | .atom w j c, x => behavior S x w j = c
  | .neg f, x => ¬ f.Sat S x
  | .conj f g, x => f.Sat S x ∧ g.Sat S x

def PathFormula.prefix (w : List A) : PathFormula A O V → PathFormula A O V
  | .truth => .truth
  | .atom v j c => .atom (w ++ v) j c
  | .neg f => .neg (f.prefix w)
  | .conj f g => .conj (f.prefix w) (g.prefix w)

theorem prefix_nil (f : PathFormula A O V) : f.prefix [] = f := by
  induction f with
  | truth => rfl
  | atom w j c => rfl
  | neg f ih => simp only [PathFormula.prefix, ih]
  | conj f g ihf ihg => simp only [PathFormula.prefix, ihf, ihg]

theorem prefix_comp (f : PathFormula A O V) (w v : List A) :
    (f.prefix v).prefix w = f.prefix (w ++ v) := by
  induction f with
  | truth => rfl
  | atom l j c => simp only [PathFormula.prefix, List.append_assoc]
  | neg f ih => simp only [PathFormula.prefix, ih]
  | conj f g ihf ihg => simp only [PathFormula.prefix, ihf, ihg]

theorem prefix_sound (S : System X A O V) (f : PathFormula A O V)
    (w : List A) (x : X) : (f.prefix w).Sat S x ↔ f.Sat S (run S w x) := by
  induction f with
  | truth => rfl
  | atom v j c => simp only [PathFormula.prefix, PathFormula.Sat, behavior, run_append]
  | neg f ih => exact not_congr ih
  | conj f g ihf ihg => exact and_congr ihf ihg

def normalize : ObsFormula A O V → PathFormula A O V
  | .truth => .truth
  | .test j c => .atom [] j c
  | .neg f => .neg (normalize f)
  | .conj f g => .conj (normalize f) (normalize g)
  | .after a f => (normalize f).prefix [a]

theorem normalize_sound (S : System X A O V) (f : ObsFormula A O V) (x : X) :
    (normalize f).Sat S x ↔ f.Sat S x := by
  induction f generalizing x with
  | truth => rfl
  | test j c => rfl
  | neg f ih => exact not_congr (ih x)
  | conj f g ihf ihg => exact and_congr (ihf x) (ihg x)
  | after a f ih =>
    exact (prefix_sound S (normalize f) [a] x).trans (ih (S.step a x))

def afterWord : List A → ObsFormula A O V → ObsFormula A O V
  | [], f => f
  | a :: w, f => .after a (afterWord w f)

theorem normalize_afterWord (w : List A) (f : ObsFormula A O V) :
    normalize (afterWord w f) = (normalize f).prefix w := by
  induction w with
  | nil => exact (prefix_nil (normalize f)).symm
  | cons a w ih =>
    change (normalize (afterWord w f)).prefix [a] = (normalize f).prefix (a :: w)
    rw [ih, prefix_comp]
    rfl

def embed : PathFormula A O V → ObsFormula A O V
  | .truth => .truth
  | .atom w j c => afterWord w (.test j c)
  | .neg f => .neg (embed f)
  | .conj f g => .conj (embed f) (embed g)

theorem normalize_embed (f : PathFormula A O V) : normalize (embed f) = f := by
  induction f with
  | truth => rfl
  | atom w j c => simp [embed, normalize_afterWord, normalize, PathFormula.prefix]
  | neg f ih => simp only [embed, normalize, ih]
  | conj f g ihf ihg => simp only [embed, normalize, ihf, ihg]

theorem normalization_retraction (f : ObsFormula A O V) :
    normalize (embed (normalize f)) = normalize f := normalize_embed _

def PathFormula.horizon : PathFormula A O V → Nat
  | .truth => 0
  | .atom w _ _ => w.length
  | .neg f => f.horizon
  | .conj f g => max f.horizon g.horizon

/-- Operational depth, not first-order quantifier rank. -/
def operationalDepth (f : ObsFormula A O V) : Nat := (normalize f).horizon

def BoundedObsEq (S : System X A O V) (h : Nat) (x y : X) : Prop :=
  ∀ w : List A, w.length ≤ h → ∀ j, behavior S x w j = behavior S y w j

theorem bounded_mono (S : System X A O V) {h k : Nat} (hk : h ≤ k)
    {x y : X} (he : BoundedObsEq S k x y) : BoundedObsEq S h x y :=
  fun w hw j => he w (Nat.le_trans hw hk) j

theorem bounded_path_invariant (S : System X A O V) (f : PathFormula A O V)
    {x y : X} (he : BoundedObsEq S f.horizon x y) : f.Sat S x ↔ f.Sat S y := by
  induction f with
  | truth => rfl
  | atom w j c =>
    change (behavior S x w j = c) ↔ (behavior S y w j = c)
    rw [he w (Nat.le_refl _) j]
  | neg f ih => exact not_congr (ih he)
  | conj f g ihf ihg =>
    exact and_congr (ihf (bounded_mono S (Nat.le_max_left _ _) he))
      (ihg (bounded_mono S (Nat.le_max_right _ _) he))

theorem bounded_observation_type_iff (S : System X A O V) (h : Nat) (x y : X) :
    BoundedObsEq S h x y ↔
      ∀ f : PathFormula A O V, f.horizon ≤ h → (f.Sat S x ↔ f.Sat S y) := by
  constructor
  · intro he f hf
    exact bounded_path_invariant S f (bounded_mono S hf he)
  · intro he w hw j
    have hh := he (.atom w j (behavior S x w j)) hw
    have hy : behavior S y w j = behavior S x w j := hh.mp rfl
    exact hy.symm

theorem observation_type_iff (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ f : PathFormula A O V, f.Sat S x ↔ f.Sat S y := by
  constructor
  · intro he f
    exact bounded_path_invariant S f (fun w _ j => he w j)
  · intro he w j
    have hy : behavior S y w j = behavior S x w j :=
      (he (.atom w j (behavior S x w j))).mp rfl
    exact hy.symm

theorem original_observation_type_iff (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ f : ObsFormula A O V, f.Sat S x ↔ f.Sat S y := by
  constructor
  · intro he f
    exact (normalize_sound S f x).symm.trans
      (((observation_type_iff S x y).mp he (normalize f)).trans (normalize_sound S f y))
  · intro he
    apply (observation_type_iff S x y).mpr
    intro f
    have hx := normalize_sound S (embed f) x
    have hy := normalize_sound S (embed f) y
    rw [normalize_embed] at hx hy
    exact hx.trans ((he (embed f)).trans hy.symm)

theorem horizon_eq_bounded (S : System X A O V) (h : Nat) (x y : X) :
    Horizon S h x y ↔ BoundedObsEq S h x y := by
  induction h generalizing x y with
  | zero =>
    constructor
    · intro he w hw j
      have hw0 : w = [] := List.length_eq_zero_iff.mp (Nat.eq_zero_of_le_zero hw)
      subst w
      exact he j
    · intro he j
      exact he [] (Nat.le_refl 0) j
  | succ h ih =>
    constructor
    · intro he w hw j
      cases w with
      | nil => exact he.1 j
      | cons a w => exact (ih _ _).mp (he.2 a) w (Nat.le_of_succ_le_succ hw) j
    · intro he
      refine ⟨fun j => he [] (Nat.zero_le _) j, ?_⟩
      intro a
      apply (ih _ _).mpr
      intro w hw j
      exact he (a :: w) (Nat.succ_le_succ hw) j

theorem stable_logical_horizon (S : System X A O V) (h : Nat)
    (stable : ∀ x y, BoundedObsEq S h x y → BoundedObsEq S (h+1) x y)
    (x y : X) : BoundedObsEq S h x y ↔ ObsEq S x y := by
  rw [← horizon_eq_bounded]
  apply stable_horizon_exact
  intro x y he
  exact (horizon_eq_bounded S (h+1) x y).mpr
    (stable x y ((horizon_eq_bounded S h x y).mp he))

theorem path_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (f : PathFormula A O V) (x : X) :
    f.Sat S x ↔ f.Sat T (q.encode x) := by
  induction f with
  | truth => rfl
  | atom w j c =>
    change (behavior S x w j = c) ↔ (behavior T (q.encode x) w j = c)
    rw [transport_behavior q]
  | neg f ih => exact not_congr ih
  | conj f g ihf ihg => exact and_congr ihf ihg

end Komorebi.ModelTheory
