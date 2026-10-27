import SyzygyCorrectedAuxiliarySelection
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! Direct composition with the actual v0.23 presentation theorem. Extend the
selected raw evaluation off the kernel by a vector-space splitting. The transpose
of the combined relation map has image exactly the syzygy-annihilating equation
space. No intrinsic Selmer comparison is manufactured here. -/

namespace Komorebi.StrongArtin.IntrinsicCompatibleTarget

open Module
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.SelmerPresentationComparison
open Komorebi.StrongArtin.SyzygyCorrectedAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

noncomputable section

variable {R S I T H Aux : Type*} [CommRing R] [Field S] [Algebra R S]
  [AddCommGroup H] [Module S H]

/-- The syzygy submodule embedded back into the displayed relation space. -/
def ambientRelationSyzygies (P : Algebra.Presentation R S I T) :
    Submodule S (T →₀ S) :=
  (relationSyzygies P).map (LinearMap.ker (relationDifferentialMap P)).subtype

/-- Extend selected raw evaluations from the relation kernel to all relation
vectors. The extension uses a noncanonical vector-space splitting. -/
def extendedRawEvaluation
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux) :
    (T →₀ S) →ₗ[S] (Q → S) :=
  LinearMap.pi (fun a : Q =>
    Subspace.dualLift (K := S) (LinearMap.ker (relationDifferentialMap P))
      (pullbackLocalFunctional D iface a.1))

@[simp] theorem extendedRawEvaluation_coe
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (x : presentationObstructionDual P) :
    extendedRawEvaluation D iface Q (x : T →₀ S) = rawEvaluationMap D iface Q x := by
  funext a
  change Subspace.dualLift (K := S) (LinearMap.ker (relationDifferentialMap P))
    (pullbackLocalFunctional D iface a.1) (x : T →₀ S) =
    pullbackLocalFunctional D iface a.1 x
  exact Subspace.dualLift_of_subtype x

/-- Its transpose is the original Jacobian with the selected dual auxiliary
coordinates adjoined. -/
def relationMapWithAuxiliaries
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux) :
    (T →₀ S) →ₗ[S] ((I →₀ S) × (Q → S)) :=
  (relationDifferentialMap P).prod (extendedRawEvaluation D iface Q)

/-- v0.23's exact selected kernel determines the kernel of the full relation map. -/
theorem ker_relationMapWithAuxiliaries
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hker : LinearMap.ker (rawEvaluationMap D iface Q) = relationSyzygies P) :
    LinearMap.ker (relationMapWithAuxiliaries D iface Q) = ambientRelationSyzygies P := by
  ext x
  constructor
  · intro hx
    have hpair := LinearMap.mem_ker.mp hx
    have hL : relationDifferentialMap P x = 0 := congrArg Prod.fst hpair
    let y : presentationObstructionDual P := ⟨x, hL⟩
    have hE : rawEvaluationMap D iface Q y = 0 := by
      have h := congrArg Prod.snd hpair
      change extendedRawEvaluation D iface Q x = 0 at h
      simpa only [← extendedRawEvaluation_coe D iface Q y] using h
    have hy : y ∈ relationSyzygies P := by
      rw [← hker]
      exact LinearMap.mem_ker.mpr hE
    exact ⟨y, hy, rfl⟩
  · rintro ⟨y, hy, rfl⟩
    apply LinearMap.mem_ker.mpr
    apply Prod.ext
    · exact y.property
    · change extendedRawEvaluation D iface Q (y : T →₀ S) = 0
      rw [extendedRawEvaluation_coe]
      have hy' : y ∈ LinearMap.ker (rawEvaluationMap D iface Q) := by
        rw [hker]
        exact hy
      exact LinearMap.mem_ker.mp hy'

/-- Intrinsic selected auxiliaries reach exactly the compatible equation dual. -/
theorem range_augmentedTranspose_eq_compatible
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) (Q : Finset Aux)
    (hker : LinearMap.ker (rawEvaluationMap D iface Q) = relationSyzygies P) :
    LinearMap.range (relationMapWithAuxiliaries D iface Q).dualMap =
      (ambientRelationSyzygies P).dualAnnihilator := by
  rw [LinearMap.range_dualMap_eq_dualAnnihilator_ker,
    ker_relationMapWithAuxiliaries D iface Q hker]

/-- Direct v0.23-to-compatible-image capstone. The Selmer comparison and the
arithmetic one-prime interface remain explicit inputs. -/
theorem exists_intrinsic_auxiliaries_with_exact_compatible_image
    [DecidableEq Aux] [FiniteDimensional S H]
    {P : Algebra.Presentation R S I T} (D : Datum P H)
    (iface : OnePrimeSelectionInterface S H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, iface.admissible a) ∧
      Q.card = Module.finrank S H ∧
      LinearMap.ker (relationMapWithAuxiliaries D iface Q) = ambientRelationSyzygies P ∧
      LinearMap.range (relationMapWithAuxiliaries D iface Q).dualMap =
        (ambientRelationSyzygies P).dualAnnihilator := by
  obtain ⟨Q, hgood, hcard, hker, -, -⟩ := exists_syzygy_corrected_TaylorWiles_set D iface
  exact ⟨Q, hgood, hcard,
    ker_relationMapWithAuxiliaries D iface Q hker,
    range_augmentedTranspose_eq_compatible D iface Q hker⟩

end
end Komorebi.StrongArtin.IntrinsicCompatibleTarget

#print axioms Komorebi.StrongArtin.IntrinsicCompatibleTarget.ker_relationMapWithAuxiliaries
#print axioms Komorebi.StrongArtin.IntrinsicCompatibleTarget.range_augmentedTranspose_eq_compatible
#print axioms Komorebi.StrongArtin.IntrinsicCompatibleTarget.exists_intrinsic_auxiliaries_with_exact_compatible_image
