module
public import ObservationalMathlibTranslation
public import FiniteObservationCode
public import Mathlib.ModelTheory.Complexity
public import Mathlib.ModelTheory.Definability

@[expose] public section
namespace Komorebi.ModelTheory.Standard
open Komorebi.Representation
open FirstOrder.Language
universe u v w
variable {A O V : Type u} {X Y : Type v} {α : Type w}

/-- Surjective behavioral transports preserve precisely the translated fragment. -/
theorem standard_observational_transport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (surj : ∀ y, ∃ x, q.encode x = y)
    {n : Nat} (f : ObsFO A O V n) (env : Fin n → X) :
    standardRealize S (toMathlib f) env ↔
      standardRealize T (toMathlib f) (fun i => q.encode (env i)) :=
  (toMathlib_correct S f env).trans
    ((observational_first_order_transport q surj f env).trans (toMathlib_correct T f _).symm)

theorem standard_quotient_preservation (S : System X A O V) {n : Nat}
    (f : ObsFO A O V n) (env : Fin n → X) :
    standardRealize S (toMathlib f) env ↔
      standardRealize (quotientSystem S) (toMathlib f)
        (fun i => (quotientTransport S).encode (env i)) :=
  standard_observational_transport (quotientTransport S) (quotient_encoding_surjective S) f env

/-- Agreement on all translated one-variable formulas, not on arbitrary FO formulas. -/
theorem standard_fragment_type_iff (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ f : ObsFO A O V 1,
      standardRealize S (toMathlib f) (fun _ => x) ↔
      standardRealize S (toMathlib f) (fun _ => y) := by
  simp only [toMathlib_correct]
  exact first_order_observation_type_iff S x y

/-- Quantifier-free source formulas compile to Mathlib's actual `IsQF` predicate. -/
theorem translateAux_isQF {n : Nat} (f : ObsFO A O V n) (h : f.quantifierRank = 0)
    {m : Nat} (σ : Fin n → α ⊕ Fin m) : (translateAux f σ).IsQF := by
  induction f generalizing m with
  | truth => exact BoundedFormula.IsQF.top
  | test t j c => exact (BoundedFormula.IsAtomic.equal _ _).isQF
  | compare t j s k => exact (BoundedFormula.IsAtomic.equal _ _).isQF
  | neg f ih => exact (ih h σ).not
  | conj f g ihf ihg =>
    have hs := Nat.max_eq_zero_iff.mp h
    exact (ihf hs.1 σ).inf (ihg hs.2 σ)
  | ex f _ => simp [ObsFO.quantifierRank] at h

theorem toMathlib_isQF {n : Nat} (f : ObsFO A O V n) (h : f.quantifierRank = 0) :
    (toMathlib f).IsQF := translateAux_isQF f h Sum.inl

theorem standard_finite_definition (S : System X A O V)
    (tests : List (ObservationTest A O)) (cert : FiniteCodeCertificate S tests)
    (env : Fin 2 → X) :
    standardRealize S (toMathlib (codeRelationFormula tests)) env ↔ ObsEq S (env 0) (env 1) :=
  (toMathlib_correct S _ env).trans (finite_observational_definition S tests cert env)

/-- State guards make the graph a relation on the state sort inside the tagged universe. -/
def guardedCodeFormula (tests : List (ObservationTest A O)) :
    (observationLanguage A O V).Formula (Fin 2) :=
  stateGuard (.var (.inl 0)) ⊓ stateGuard (.var (.inl 1)) ⊓
    toMathlib (codeRelationFormula tests)

def taggedRealize {n : Nat} (S : System X A O V)
    (f : (observationLanguage A O V).Formula (Fin n))
    (env : Fin n → TaggedCarrier X V) : Prop :=
  letI := taggedStructure S
  FirstOrder.Language.Formula.Realize f env

theorem tagged_guard_realize {n : Nat} (S : System X A O V)
    (i : Fin n) (env : Fin n → TaggedCarrier X V) :
    taggedRealize S (stateGuard (.var (.inl i))) env ↔ StateTag (env i) := Iff.rfl

def taggedBehaviorSet (S : System X A O V) : Set (Fin 2 → TaggedCarrier X V) :=
  {e | ∃ env : Fin 2 → X, e = (fun i => Sum.inl (env i)) ∧ ObsEq S (env 0) (env 1)}

theorem StateTag_iff_exists (z : TaggedCarrier X V) :
    StateTag z ↔ ∃ x, z = Sum.inl x := by
  cases z with
  | inl x => exact ⟨fun _ => ⟨x, rfl⟩, fun _ => trivial⟩
  | inr c => simp [StateTag]

theorem guardedCodeFormula_semantics (S : System X A O V)
    (tests : List (ObservationTest A O)) (cert : FiniteCodeCertificate S tests)
    (e : Fin 2 → TaggedCarrier X V) :
    taggedRealize S (guardedCodeFormula tests) e ↔ e ∈ taggedBehaviorSet S := by
  let _ := taggedStructure S
  change FirstOrder.Language.Formula.Realize
    ((stateGuard (.var (.inl 0)) ⊓ stateGuard (.var (.inl 1))) ⊓
      toMathlib (codeRelationFormula tests)) e ↔ _
  simp only [Formula.realize_inf]
  change (StateTag (e 0) ∧ StateTag (e 1)) ∧
    taggedRealize S (toMathlib (codeRelationFormula tests)) e ↔ _
  constructor
  · rintro ⟨⟨h0,h1⟩,hf⟩
    have hall : ∀ i : Fin 2, StateTag (e i) := by
      intro i
      exact Fin.cases h0 (fun j => Fin.cases h1 (fun k => Fin.elim0 k) j) i
    have hex : ∀ i, ∃ x, e i = Sum.inl x := fun i => (StateTag_iff_exists (e i)).mp (hall i)
    choose env henv using hex
    have heq : e = fun i => Sum.inl (env i) := funext henv
    refine ⟨env, heq, ?_⟩
    rw [heq] at hf
    exact (standard_finite_definition S tests cert env).mp hf
  · rintro ⟨env, rfl, h⟩
    exact ⟨⟨trivial,trivial⟩, (standard_finite_definition S tests cert env).mpr h⟩

theorem guardedCodeFormula_isQF (tests : List (ObservationTest A O)) :
    (guardedCodeFormula (V := V) tests).IsQF :=
  ((BoundedFormula.IsAtomic.rel _ _).isQF.inf (BoundedFormula.IsAtomic.rel _ _).isQF).inf
    (toMathlib_isQF (codeRelationFormula tests) (codeRelationFormula_quantifier_free tests))

/-- Parameter-free definability in the explicitly named observation language.
    This codes one certified relation; it is not theory-wide elimination of imaginaries. -/
theorem standard_behavior_definable (S : System X A O V)
    (tests : List (ObservationTest A O)) (cert : FiniteCodeCertificate S tests) :
    letI := taggedStructure S
    (∅ : Set (TaggedCarrier X V)).Definable (observationLanguage A O V) (taggedBehaviorSet S) := by
  let _ := taggedStructure S
  apply Set.empty_definable_iff.mpr
  refine ⟨guardedCodeFormula tests, ?_⟩
  ext e
  exact (guardedCodeFormula_semantics S tests cert e).symm

end Komorebi.ModelTheory.Standard
