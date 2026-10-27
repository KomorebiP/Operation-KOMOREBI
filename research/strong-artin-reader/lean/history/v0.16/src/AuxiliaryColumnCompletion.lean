import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Finsupp.LinearCombination
import Mathlib.LinearAlgebra.Prod

namespace Komorebi.StrongArtin.AuxiliaryColumnCompletion

noncomputable section

variable {k U W ι : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- The linear combination of the selected auxiliary Jacobian columns. -/
def auxiliaryMap (column : ι → W) (Q : Finset ι) :
    (Q → k) →ₗ[k] W :=
  Fintype.linearCombination k (fun i : Q => column i.1)

@[simp]
theorem auxiliaryMap_apply
    (column : ι → W) (Q : Finset ι) (a : Q → k) :
    auxiliaryMap column Q a = ∑ i : Q, a i • column i.1 := rfl

/-- Adjoin finitely many auxiliary columns to a linearized deformation/Jacobian map. -/
def augmentedMap (J : U →ₗ[k] W) (column : ι → W) (Q : Finset ι) :
    (U × (Q → k)) →ₗ[k] W :=
  J.coprod (auxiliaryMap column Q)

@[simp]
theorem augmentedMap_apply
    (J : U →ₗ[k] W) (column : ι → W) (Q : Finset ι)
    (u : U) (a : Q → k) :
    augmentedMap J column Q (u, a) =
      J u + ∑ i : Q, a i • column i.1 := by
  rfl

/-- The dual obstruction space of `J`: linear functionals on the equation space
that kill every original Jacobian column. -/
def obstructionDual (J : U →ₗ[k] W) : Submodule k (Module.Dual k W) :=
  LinearMap.ker J.dualMap

@[simp]
theorem mem_obstructionDual (J : U →ₗ[k] W) (φ : Module.Dual k W) :
    φ ∈ obstructionDual J ↔ ∀ u : U, φ (J u) = 0 := by
  rw [obstructionDual, LinearMap.mem_ker]
  constructor
  · intro h u
    have hu := congrArg (fun f : Module.Dual k U => f u) h
    simpa using hu
  · intro h
    ext u
    simpa using h u

/-- Evaluation of one auxiliary column on the dual obstruction space. -/
def columnFunctional (J : U →ₗ[k] W) (column : ι → W) (i : ι) :
    Module.Dual k (obstructionDual J) where
  toFun φ := φ.1 (column i)
  map_add' φ ψ := by simp
  map_smul' a φ := by simp

@[simp]
theorem columnFunctional_apply
    (J : U →ₗ[k] W) (column : ι → W) (i : ι)
    (φ : obstructionDual J) :
    columnFunctional J column i φ = φ.1 (column i) := rfl

/-- If the selected auxiliary columns jointly separate the dual obstruction
space, then adjoining those columns makes the full linearized map surjective. -/
theorem augmentedMap_surjective_of_obstruction_detection
    (J : U →ₗ[k] W) (column : ι → W) (Q : Finset ι)
    (hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ i ∈ Q, columnFunctional J column i φ ≠ 0) :
    Function.Surjective (augmentedMap J column Q) := by
  classical
  rw [← LinearMap.dualMap_injective_iff]
  intro φ ψ hφψ
  let δ : Module.Dual k W := φ - ψ
  have hδJ : δ ∈ obstructionDual J := by
    rw [mem_obstructionDual]
    intro u
    have heq := congrArg
      (fun F : Module.Dual k (U × (Q → k)) => F (u, 0)) hφψ
    change φ (J u) - ψ (J u) = 0
    apply sub_eq_zero.mpr
    simpa [augmentedMap, auxiliaryMap] using heq
  have hδ0 : δ = 0 := by
    by_contra hne
    have hsubne : (⟨δ, hδJ⟩ : obstructionDual J) ≠ 0 := by
      intro hz
      apply hne
      exact Subtype.ext_iff.mp hz
    obtain ⟨i, hiQ, hi⟩ := hdetect ⟨δ, hδJ⟩ hsubne
    let qi : Q := ⟨i, hiQ⟩
    let ei : Q → k := Pi.single qi 1
    have hcol : augmentedMap J column Q (0, ei) = column i := by
      simp [augmentedMap, auxiliaryMap, ei, qi,
        Fintype.linearCombination_apply_single]
    have heq := congrArg
      (fun F : Module.Dual k (U × (Q → k)) => F (0, ei)) hφψ
    have hzero : δ (column i) = 0 := by
      change φ (column i) - ψ (column i) = 0
      apply sub_eq_zero.mpr
      simpa [hcol] using heq
    exact hi hzero
  exact sub_eq_zero.mp hδ0

end
end Komorebi.StrongArtin.AuxiliaryColumnCompletion

#print axioms Komorebi.StrongArtin.AuxiliaryColumnCompletion.augmentedMap_surjective_of_obstruction_detection
