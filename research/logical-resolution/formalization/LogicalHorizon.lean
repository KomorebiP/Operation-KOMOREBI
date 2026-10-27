module
public import ObservationSyntax
public import FiniteCertificates

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation
universe u v w z
variable {X : Type u} {A : Type v} {O : Type w} {V : Type z} {n : Nat}

def AgreesTo (S : System X A O V) (h : Nat) (x y : X) : Prop :=
  ∀ word : List A, word.length ≤ h → ∀ j, behavior S x word j = behavior S y word j

theorem agreesTo_refl (S : System X A O V) (h : Nat) (x : X) : AgreesTo S h x x :=
  fun _ _ _ => rfl

theorem agreesTo_mono (S : System X A O V) {h k : Nat} (hk : h ≤ k)
    {x y : X} (hxy : AgreesTo S k x y) : AgreesTo S h x y :=
  fun word hw j => hxy word (Nat.le_trans hw hk) j

theorem horizon_iff_agreesTo (S : System X A O V) (h : Nat) (x y : X) :
    Horizon S h x y ↔ AgreesTo S h x y := by
  induction h generalizing x y with
  | zero =>
    constructor
    · intro ho word hw j
      cases word with
      | nil => exact ho j
      | cons a word => simp only [List.length_cons] at hw; omega
    · intro ho j
      exact ho [] (Nat.le_refl 0) j
  | succ h ih =>
    constructor
    · intro ho word hw j
      cases word with
      | nil => exact ho.1 j
      | cons a word =>
        exact (ih _ _).mp (ho.2 a) word (Nat.le_of_succ_le_succ hw) j
    · intro ho
      refine ⟨fun j => ho [] (Nat.zero_le _) j, ?_⟩
      intro a
      apply (ih _ _).mpr
      intro word hw j
      exact ho (a::word) (Nat.succ_le_succ hw) j

theorem valueTerm_agrees (S : System X A O V) (h : Nat) (ρ τ : Fin n → X)
    (he : ∀ i, AgreesTo S h (ρ i) (τ i)) (t : ValueTerm A O V n) (ht : t.depth ≤ h) :
    t.eval S ρ = t.eval S τ := by
  cases t with
  | literal v => rfl
  | probe i word j => exact he i word ht j

theorem extend_agrees (S : System X A O V) (h : Nat) (x : X) (ρ τ : Fin n → X)
    (he : ∀ i, AgreesTo S h (ρ i) (τ i)) :
    ∀ i, AgreesTo S h (extend x ρ i) (extend x τ i) := by
  intro i
  refine Fin.cases ?_ (fun j => ?_) i
  · exact agreesTo_refl S h x
  · exact he j

/-- Quantifiers add no new distinctions between finite-horizon-equivalent
assignments INSIDE a fixed system in this deliberately restricted language. -/
theorem formula_depth_congr (S : System X A O V) (h : Nat)
    (f : Formula A O V n) (ρ τ : Fin n → X)
    (he : ∀ i, AgreesTo S h (ρ i) (τ i)) (hf : f.depth ≤ h) :
    f.Holds S ρ ↔ f.Holds S τ := by
  induction f with
  | falsum => exact Iff.rfl
  | equal t s =>
    change t.eval S ρ = s.eval S ρ ↔ t.eval S τ = s.eval S τ
    have ht : t.depth ≤ h := Nat.le_trans (Nat.le_max_left _ _) hf
    have hs : s.depth ≤ h := Nat.le_trans (Nat.le_max_right _ _) hf
    rw [valueTerm_agrees S h ρ τ he t ht, valueTerm_agrees S h ρ τ he s hs]
  | neg f ih => exact not_congr (ih ρ τ he hf)
  | conj f g ihf ihg =>
    exact and_congr
      (ihf ρ τ he (Nat.le_trans (Nat.le_max_left _ _) hf))
      (ihg ρ τ he (Nat.le_trans (Nat.le_max_right _ _) hf))
  | existsState f ih =>
    constructor
    · rintro ⟨x,hx⟩
      exact ⟨x,(ih (extend x ρ) (extend x τ) (extend_agrees S h x ρ τ he) hf).mp hx⟩
    · rintro ⟨x,hx⟩
      exact ⟨x,(ih (extend x ρ) (extend x τ) (extend_agrees S h x ρ τ he) hf).mpr hx⟩

def SameType (S : System X A O V) (x y : X) : Prop :=
  ∀ f : Formula A O V 1, f.Holds S (fun _ => x) ↔ f.Holds S (fun _ => y)

def SameQFType (S : System X A O V) (x y : X) : Prop :=
  ∀ f : Formula A O V 1, f.qrank = 0 →
    (f.Holds S (fun _ => x) ↔ f.Holds S (fun _ => y))

def SameBoundedType (S : System X A O V) (h q : Nat) (x y : X) : Prop :=
  ∀ f : Formula A O V 1, f.depth ≤ h → f.qrank ≤ q →
    (f.Holds S (fun _ => x) ↔ f.Holds S (fun _ => y))

theorem behavior_implies_type (S : System X A O V) {x y : X} (hxy : ObsEq S x y) :
    SameType S x y := by
  intro f
  exact formula_depth_congr S f.depth f (fun _ => x) (fun _ => y)
    (fun _ word _ j => hxy word j) (Nat.le_refl _)

theorem qf_type_implies_behavior (S : System X A O V) {x y : X}
    (hxy : SameQFType S x y) : ObsEq S x y := by
  intro word j
  have he := hxy (observedValue word j (behavior S x word j)) rfl
  exact (he.mp rfl).symm

theorem behavior_iff_observation_qf_type (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ SameQFType S x y := by
  constructor
  · intro h f _; exact behavior_implies_type S h f
  · exact qf_type_implies_behavior S

theorem behavior_iff_observation_type (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ SameType S x y := by
  constructor
  · exact behavior_implies_type S
  · intro h; exact qf_type_implies_behavior S (fun f _ => h f)

theorem bounded_type_iff_horizon (S : System X A O V) (h q : Nat) (x y : X) :
    SameBoundedType S h q x y ↔ Horizon S h x y := by
  rw [horizon_iff_agreesTo]
  constructor
  · intro he word hw j
    have hh := he (observedValue word j (behavior S x word j))
      (by simpa only [observedValue_depth] using hw) (Nat.zero_le q)
    exact (hh.mp rfl).symm
  · intro he f hf _
    exact formula_depth_congr S h f (fun _ => x) (fun _ => y) (fun _ => he) hf

theorem bounded_type_rank_independent (S : System X A O V) (h q k : Nat) (x y : X) :
    SameBoundedType S h q x y ↔ SameBoundedType S h k x y :=
  (bounded_type_iff_horizon S h q x y).trans (bounded_type_iff_horizon S h k x y).symm

theorem distinguishing_observation_formula (S : System X A O V) (h : Nat) (x y : X)
    (hne : ¬ Horizon S h x y) :
    ∃ f : Formula A O V 1, f.depth ≤ h ∧ f.qrank = 0 ∧
      f.Holds S (fun _ => x) ∧ ¬ f.Holds S (fun _ => y) := by
  obtain ⟨word,hw,j,hj⟩ := horizon_counterexample S h x y hne
  refine ⟨observedValue word j (behavior S x word j), ?_, rfl, rfl, ?_⟩
  · simpa only [observedValue_depth] using hw
  · intro he
    exact hj he.symm

end Komorebi.LogicalResolution
