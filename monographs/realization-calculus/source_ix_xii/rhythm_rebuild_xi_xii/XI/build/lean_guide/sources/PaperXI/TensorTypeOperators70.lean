import PaperXI.InducedTypeSpace68
import Mathlib.RingTheory.TensorProduct.Maps
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! Faithful first-factor operator realization in the literal inducing-type image.
The multiplicity space must be nonzero. Neither tensor amplification nor the
ambient induced space is silently identified with the first-factor carrier. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorTypeOperators70
open Representation
open scoped TensorProduct
variable {k W U G : Type*} [Field k] [AddCommGroup W] [Module k W]
  [AddCommGroup U] [Module k U] [Group G]

/-- First-factor amplification is an actual unital algebra homomorphism. -/
def amplify : Module.End k W →ₐ[k] Module.End k (W ⊗[k] U) :=
  Module.End.rTensorAlgHom k W U

@[simp] theorem amplify_tmul (B : Module.End k W) (w : W) (u : U) :
    amplify (U := U) B (w ⊗ₜ[k] u) = B w ⊗ₜ[k] u := rfl

/-- A nonzero multiplicity factor prevents loss of first-factor operators. -/
theorem amplify_injective [Nontrivial U] :
    Function.Injective (amplify (k := k) (W := W) (U := U)) := by
  obtain ⟨u, hu⟩ := exists_ne (0 : U)
  obtain ⟨φ, hφ⟩ := Module.Projective.exists_dual_eq_one k hu
  intro A B h
  ext w
  have he := congrArg (fun T : Module.End k (W ⊗[k] U) =>
    (TensorProduct.rid k W) (TensorProduct.map LinearMap.id φ (T (w ⊗ₜ[k] u)))) h
  simpa [hφ] using he

variable (H : Subgroup G) (Λ : Representation k H (W ⊗[k] U))

/-- The prescribed first-factor algebra inside the actual canonical type image. -/
def realize : Module.End k W →ₐ[k]
    Module.End k (InducedTypeSpace68.typeSpace H Λ) :=
  (InducedTypeSpace68.typeOperators H Λ).toAlgHom.comp amplify

@[simp] theorem realize_tmul (B : Module.End k W) (w : W) (u : U) :
    realize H Λ B (InducedTypeSpace68.typeEquiv H Λ (w ⊗ₜ[k] u)) =
      InducedTypeSpace68.typeEquiv H Λ (B w ⊗ₜ[k] u) := by
  change (InducedTypeSpace68.typeEquiv H Λ)
    (amplify B ((InducedTypeSpace68.typeEquiv H Λ).symm
      (InducedTypeSpace68.typeEquiv H Λ (w ⊗ₜ[k] u)))) = _
  rw [LinearEquiv.symm_apply_apply, amplify_tmul]

/-- The complete first-factor operator, not just its trace, is retained. -/
theorem realize_injective [Nontrivial U] : Function.Injective (realize H Λ) :=
  (InducedTypeSpace68.typeOperators H Λ).injective.comp amplify_injective

@[simp] theorem realize_eq_iff [Nontrivial U] (A B : Module.End k W) :
    realize H Λ A = realize H Λ B ↔ A = B := (realize_injective H Λ).eq_iff

@[simp] theorem realize_zero_iff [Nontrivial U] (A : Module.End k W) :
    realize H Λ A = 0 ↔ A = 0 := by
  rw [← map_zero (realize H Λ), realize_eq_iff]

/-- Full operator residuals are preserved and reflected. -/
theorem residual_zero_iff [Nontrivial U] (A B : Module.End k W) :
    realize H Λ A - realize H Λ B = 0 ↔ A - B = 0 := by
  rw [sub_eq_zero, sub_eq_zero, realize_eq_iff]

/-- Idempotence is not weakened to a scalar or character condition. -/
theorem projector_iff [Nontrivial U] (P : Module.End k W) :
    realize H Λ P * realize H Λ P = realize H Λ P ↔ P * P = P := by
  rw [← map_mul, realize_eq_iff]

/-- Both orders of composition are transported literally. -/
theorem intertwining_iff [Nontrivial U] (A B T : Module.End k W) :
    realize H Λ T * realize H Λ A = realize H Λ B * realize H Λ T ↔
      T * A = B * T := by
  rw [← map_mul, ← map_mul, realize_eq_iff]

/-- Any finite word of full packet operators has the same realized product. -/
theorem word_product (xs : List (Module.End k W)) :
    (xs.map (realize H Λ)).prod = realize H Λ xs.prod := by
  induction xs with
  | nil => simp
  | cons A xs ih => simp [ih]

/-- Zero holonomy is reflected as well as preserved, including the empty word. -/
theorem holonomy_iff [Nontrivial U] (xs : List (Module.End k W)) :
    (xs.map (realize H Λ)).prod = 1 ↔ xs.prod = 1 := by
  rw [word_product, ← map_one (realize H Λ), realize_eq_iff]

/-- Finite weighted projectors commute with the realization map. -/
theorem weighted_sum {I : Type*} (s : Finset I) (c : I → k)
    (A : I → Module.End k W) :
    realize H Λ (∑ i ∈ s, c i • A i) = ∑ i ∈ s, c i • realize H Λ (A i) := by
  simp only [map_sum, map_smul]

end PaperXI.TensorTypeOperators70
