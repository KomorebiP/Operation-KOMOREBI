module
public import LogicalHorizon

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation

/-- Both states have the same observations after every future word. -/
def constantSystem : System Bool Unit Unit Bool where
  step := fun _ _ => false
  observe := fun _ _ => false

def pointSystem : System Unit Unit Unit Bool where
  step := fun _ x => x
  observe := fun _ _ => false

def mergeStates : Transport constantSystem pointSystem where
  encode := fun _ => ()
  step_ok := by intros; rfl
  observe_ok := by intros; rfl

theorem constant_states_behavior_equal : ObsEq constantSystem false true := by
  intro word j
  rfl

/-- The full-language atomic formula f(x)=x separates the behaviorally equal states. -/
theorem state_equality_separates :
    constantSystem.step () false = false ∧ constantSystem.step () true ≠ true := by
  decide

/-- State identity cannot be reflected by a noninjective quotient map. -/
theorem merged_identity_not_reflected :
    mergeStates.encode false = mergeStates.encode true ∧ (false : Bool) ≠ true := by
  decide

/-- The sentence 'there are at least two states' is lost by this valid transport. -/
theorem state_cardinality_not_preserved :
    (∃ x y : Bool, x ≠ y) ∧ ¬ (∃ x y : Unit, x ≠ y) := by
  constructor
  · exact ⟨false, true, by decide⟩
  · rintro ⟨x,y,h⟩
    exact h (Subsingleton.elim _ _)

def visibleSystem : System Bool Unit Unit Bool where
  step := fun _ x => x
  observe := fun _ x => x

/-- A correct but nonsurjective transport. -/
def falseEmbedding : Transport pointSystem visibleSystem where
  encode := fun _ => false
  step_ok := by intros; rfl
  observe_ok := by intros; rfl

def existsTrue : Formula Unit Unit Bool 1 :=
  .existsState (.equal (.probe 0 [] ()) (.literal true))

theorem quantified_surjectivity_necessary :
    ¬ existsTrue.Holds pointSystem (fun _ => ()) ∧
    existsTrue.Holds visibleSystem (fun _ => false) := by
  constructor
  · rintro ⟨x,hx⟩
    change (false : Bool) = true at hx
    cases hx
  · exact ⟨true, rfl⟩

theorem falseEmbedding_not_surjective :
    ¬ (∀ y, ∃ x, falseEmbedding.encode x = y) := by
  intro h
  obtain ⟨x,hx⟩ := h true
  change (false : Bool) = true at hx
  cases hx

/-- Quantifier-free formulas alone do not require surjectivity. -/
theorem qf_formula_transport {X Y A O V : Type} {S : System X A O V}
    {T : System Y A O V} (q : Transport S T) {n : Nat}
    (f : Formula A O V n) (hq : f.qrank = 0) (ρ : Fin n → X) :
    f.Holds S ρ ↔ f.Holds T (fun i => q.encode (ρ i)) := by
  induction f with
  | falsum => exact Iff.rfl
  | equal t s =>
    change t.eval S ρ = s.eval S ρ ↔ _
    rw [valueTerm_transport q ρ t, valueTerm_transport q ρ s]
    rfl
  | neg f ih => exact not_congr (ih hq ρ)
  | conj f g ihf ihg =>
    have hf : f.qrank = 0 := by change max f.qrank g.qrank = 0 at hq; omega
    have hg : g.qrank = 0 := by change max f.qrank g.qrank = 0 at hq; omega
    exact and_congr (ihf hf ρ) (ihg hg ρ)
  | existsState f ih =>
    change f.qrank + 1 = 0 at hq
    omega

theorem false_points_same_qf_truth (f : Formula Unit Unit Bool 1) (hq : f.qrank = 0) :
    f.Holds pointSystem (fun _ => ()) ↔ f.Holds visibleSystem (fun _ => false) :=
  qf_formula_transport falseEmbedding f hq (fun _ => ())

/-- No one-variable quantifier-free formula uniformly eliminates this existential
query even over these two finite systems. This does not preclude theory-relative QE. -/
theorem no_uniform_qf_elimination :
    ¬ ∃ f : Formula Unit Unit Bool 1, f.qrank = 0 ∧
      (f.Holds pointSystem (fun _ => ()) ↔ existsTrue.Holds pointSystem (fun _ => ())) ∧
      (f.Holds visibleSystem (fun _ => false) ↔ existsTrue.Holds visibleSystem (fun _ => false)) := by
  rintro ⟨f,hq,hp,hv⟩
  have hf := hv.mpr quantified_surjectivity_necessary.2
  have hfalse := (false_points_same_qf_truth f hq).mpr hf
  exact quantified_surjectivity_necessary.1 (hp.mp hfalse)

end Komorebi.LogicalResolution
