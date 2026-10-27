module
public import StandardObservationConsequences
public import LogicalBoundaries

@[expose] public section
namespace Komorebi.ModelTheory.Standard
open Komorebi.Representation
open FirstOrder.Language

/-- Ordinary first-order state equality is in the target language but outside the
    translated observational fragment. -/
def fixedPointFormula : (observationLanguage Unit Unit Unit).Formula (Fin 1) :=
  .equal (.func (.action ()) (fun _ => .var (.inl 0))) (.var (.inl 0))

theorem standard_fixedpoint_true :
    standardRealize constantCollapse fixedPointFormula (fun _ => false) := rfl

theorem standard_fixedpoint_false :
    ¬ standardRealize constantCollapse fixedPointFormula (fun _ => true) := by
  change ¬ (Sum.inl false : Bool ⊕ Unit) = Sum.inl true
  decide

theorem standard_full_qf_not_behavioral :
    ObsEq constantCollapse false true ∧
      (fixedPointFormula.IsQF ∧
        standardRealize constantCollapse fixedPointFormula (fun _ => false) ∧
        ¬ standardRealize constantCollapse fixedPointFormula (fun _ => true)) :=
  ⟨collapse_states_behaviorally_equal,
    (BoundedFormula.IsAtomic.equal _ _).isQF,
    standard_fixedpoint_true, standard_fixedpoint_false⟩

/-- The same existential test compiled without its required state guard. -/
def unguardedTrueObservation : (observationLanguage Unit Unit Bool).Formula (Fin 0) :=
  (BoundedFormula.equal
    (observedTerm [] () (.var (.inr 0)))
    (.func (.value true) Fin.elim0)).ex

theorem unguarded_value_is_spurious_witness :
    taggedRealize oneObservedState unguardedTrueObservation Fin.elim0 := by
  let _ := taggedStructure oneObservedState
  change FirstOrder.Language.Formula.Realize unguardedTrueObservation Fin.elim0
  rw [Formula.Realize, unguardedTrueObservation, BoundedFormula.realize_ex]
  exact ⟨Sum.inr true, rfl⟩

theorem guarded_formula_rejects_spurious_witness :
    ¬ standardRealize oneObservedState (toMathlib existsTrueObservation) Fin.elim0 :=
  fun h => source_has_no_true_witness ((toMathlib_correct oneObservedState _ _).mp h)

theorem erasing_state_guard_is_unsound :
    taggedRealize oneObservedState unguardedTrueObservation Fin.elim0 ∧
      ¬ standardRealize oneObservedState (toMathlib existsTrueObservation) Fin.elim0 :=
  ⟨unguarded_value_is_spurious_witness, guarded_formula_rejects_spurious_witness⟩

theorem nonsurjective_standard_formula_failure :
    ¬ standardRealize oneObservedState (toMathlib existsTrueObservation) Fin.elim0 ∧
      standardRealize twoObservedStates (toMathlib existsTrueObservation) Fin.elim0 :=
  ⟨guarded_formula_rejects_spurious_witness,
    (toMathlib_correct twoObservedStates _ _).mpr target_has_true_witness⟩

/-- The inner witness must not overwrite the outer state-variable binding. -/
def nestedRememberOuter : ObsFO Unit Unit Bool 0 :=
  .ex (.conj (.test (0,[]) () false)
    (.ex (.conj (.test (0,[]) () true) (.test (1,[]) () false))))

theorem nested_binder_translation :
    standardRealize twoObservedStates (toMathlib nestedRememberOuter) Fin.elim0 := by
  apply (toMathlib_correct twoObservedStates _ _).mpr
  exact ⟨false, rfl, true, rfl, rfl⟩

/-- The tagged universe can be nonempty even when its state sort is empty. -/
def emptyStateSystem : System Empty Unit Unit Bool where
  step := fun _ x => nomatch x
  observe := fun _ x => nomatch x

def someState : ObsFO Unit Unit Bool 0 := .ex .truth

theorem empty_state_sort_remains_empty :
    ¬ standardRealize emptyStateSystem (toMathlib someState) Fin.elim0 := by
  intro h
  obtain ⟨x, _⟩ := (toMathlib_correct emptyStateSystem someState Fin.elim0).mp h
  exact nomatch x

/-- Syntax compilation is not quantifier elimination. -/
theorem translated_existential_is_not_quantifier_free :
    ¬ (toMathlib someState).IsQF := BoundedFormula.not_ex_isQF _

/-- The value sort remains observable even though it is excluded from state binders. -/
theorem tagged_universe_of_empty_state_has_values :
    Nonempty (TaggedCarrier Empty Bool) := ⟨Sum.inr false⟩

end Komorebi.ModelTheory.Standard
