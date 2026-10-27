import RelativeTaylorWilesFiniteSet
import AuxiliaryColumnCompletion

namespace Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone

open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.AuxiliaryColumnCompletion

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- The one-prime interface associated with auxiliary Jacobian columns. -/
def columnSelectionInterface
    (J : U →ₗ[k] W) (column : Aux → W) (admissible : Aux → Prop)
    (hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, admissible a ∧ columnFunctional J column a φ ≠ 0) :
    OnePrimeSelectionInterface k (obstructionDual J) Aux where
  admissible := admissible
  localFunctional := columnFunctional J column
  detects := hdetect

/-- **Relative Taylor--Wiles/Jacobian capstone.** If every nonzero dual
obstruction is detected by one admissible auxiliary column, then one can choose
exactly the dual-obstruction dimension many admissible columns and the resulting
augmented Jacobian is surjective. -/
theorem exists_exact_admissible_columns_making_augmentedMap_surjective
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W) (column : Aux → W) (admissible : Aux → Prop)
    (hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, admissible a ∧ columnFunctional J column a φ ≠ 0) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, admissible a) ∧
      Q.card = Module.finrank k (obstructionDual J) ∧
      Function.Surjective (augmentedMap J column Q) := by
  let I := columnSelectionInterface J column admissible hdetect
  obtain ⟨Q, hgood, hcard, hker, -⟩ :=
    exists_relative_TaylorWiles_set_exact I
  have hQdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ i ∈ Q, columnFunctional J column i φ ≠ 0 := by
    intro φ hφ
    by_contra hnone
    have hnone' : ∀ i ∈ Q, columnFunctional J column i φ = 0 := by
      intro i hi
      by_contra hne
      exact hnone ⟨i, hi, hne⟩
    have hmem : φ ∈ selectedKernel (columnFunctional J column) Q := by
      exact hnone'
    have hbotmem : φ ∈ (⊥ : Submodule k (obstructionDual J)) := by
      rwa [← hker]
    exact hφ (by simpa using hbotmem)
  exact ⟨Q, hgood, hcard,
    augmentedMap_surjective_of_obstruction_detection J column Q hQdetect⟩

end
end Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone

#print axioms Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone.exists_exact_admissible_columns_making_augmentedMap_surjective
