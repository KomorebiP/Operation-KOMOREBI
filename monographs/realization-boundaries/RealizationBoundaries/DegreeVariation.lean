import RealizationBoundaries.ComputableNormalCodes
import RealizationBoundaries.ObservationSystems
import RealizationBoundaries.OracleCopyOperations
import RealizationBoundaries.ComputableFiniteObservations

/-! # Least presentation degrees over one observation system

The usual degrees of sets are the native Mathlib Turing degrees represented by
total binary membership oracles. Mathlib also permits partial-function oracle
degrees; no totalization theorem about that broader carrier is assumed here.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

def selectorTuringDegree (a : ℕ → Bool) : TuringDegree :=
  toAntisymmetrization TuringReducible (selectorOracle a)

theorem selectorTuringDegree_le_iff (a X : ℕ → Bool) :
    selectorTuringDegree a ≤ selectorTuringDegree X ↔ SelectorReducible a X := Iff.rfl

/-- Degrees of sets, using the official native degree carrier and membership oracles. -/
def SetTuringDegree := {d : TuringDegree // ∃ a : ℕ → Bool, selectorTuringDegree a = d}

def HasLeastPresentationDegree (H : Type*) [AddGroup H] (d : TuringDegree) : Prop :=
  (∃ a : ℕ → Bool, selectorTuringDegree a = d ∧ Nonempty (OracleGroupCopy a H)) ∧
    ∀ X : ℕ → Bool, Nonempty (OracleGroupCopy X H) → d ≤ selectorTuringDegree X

/-- The degree is attained by an actual copy and bounds every other copy below. -/
theorem paired_least_presentation_degree (a : ℕ → Bool) :
    HasLeastPresentationDegree (pairedGroup a) (selectorTuringDegree a) := by
  constructor
  · exact ⟨a, rfl, (paired_oracle_copy_iff a a).mpr (TuringReducible.refl _)⟩
  · intro X hX
    exact (selectorTuringDegree_le_iff a X).mpr ((paired_oracle_copy_iff a X).mp hX)

/-- Every ordinary degree of a set occurs among the actual countable paired groups,
while their complete source-free finite quotient observations remain identical. -/
theorem every_set_degree_with_common_observations (d : SetTuringDegree) :
    ∃ a : ℕ → Bool,
      selectorTuringDegree a = d.val ∧
      HasLeastPresentationDegree (pairedGroup a) d.val ∧
      Countable (pairedGroup a) ∧ Infinite (pairedGroup a) ∧
      AddGroup.ResiduallyFinite (pairedGroup a) ∧
      Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+ Ambient) ∧
      ∀ b : ℕ → Bool, CommonCofinalObservation
        (allFiniteObservation (selectorLine (pairedSelector a)))
        (allFiniteObservation (selectorLine (pairedSelector b))) := by
  obtain ⟨a, ha⟩ := d.property
  refine ⟨a, ha, ha ▸ paired_least_presentation_degree a,
    (paired_countably_infinite a).1, (paired_countably_infinite a).2,
    preimage_residuallyFinite _, ⟨pairedCompletionEquiv a⟩, ?_⟩
  intro b
  exact allFiniteObservation_common _ _

/-- Reducedness is retained for every degree: no nontrivial divisible group embeds. -/
theorem paired_degree_reduced (a : ℕ → Bool) (E : Type*) [AddGroup E] [Nontrivial E]
    (hdiv : ∀ m : ℕ, 0 < m → ∀ x : E, ∃ y : E, m • y = x)
    (f : E →+ pairedGroup a) : ¬ Function.Injective f := by
  intro hf
  exact not_injective_hom_of_divisible E hdiv ((pairedGroup a).subtype.comp f)
    (Subtype.val_injective.comp hf)

def IsReducedAddGroup (H : Type*) [AddGroup H] : Prop :=
  ∀ (E : Type) [AddGroup E] [Nontrivial E],
    (∀ m : ℕ, 0 < m → ∀ x : E, ∃ y : E, m • y = x) →
      ∀ f : E →+ H, ¬ Function.Injective f

theorem paired_isReduced (a : ℕ → Bool) : IsReducedAddGroup (pairedGroup a) := by
  intro E _ _ hdiv f
  exact paired_degree_reduced a E hdiv f

/-- Monograph 8.4 with the literal fixed, natively computable finite-group diagram. -/
theorem every_set_degree_with_fixed_computable_observation (d : SetTuringDegree) :
    ∃ a : ℕ → Bool,
      selectorTuringDegree a = d.val ∧
      HasLeastPresentationDegree (pairedGroup a) d.val ∧
      Countable (pairedGroup a) ∧ Infinite (pairedGroup a) ∧
      IsReducedAddGroup (pairedGroup a) ∧
      AddGroup.ResiduallyFinite (pairedGroup a) ∧
      Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+ Ambient) ∧
      CommonCofinalObservation
        (allFiniteObservation (selectorLine (pairedSelector a))) fixedComputableObservation := by
  obtain ⟨a, ha, hd, hc, hi, hr, he, _⟩ := every_set_degree_with_common_observations d
  exact ⟨a, ha, hd, hc, hi, paired_isReduced a, hr, he, allFiniteObservation_fixed_computable _⟩

end RealizationBoundaries
