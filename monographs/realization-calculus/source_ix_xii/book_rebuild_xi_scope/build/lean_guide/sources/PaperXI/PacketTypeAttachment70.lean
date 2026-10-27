import PaperXI.TensorTypeOperators70

/-! The finite packet action is the restriction of the SAME actual induced
representation on its literal type image. Full operator relations and graph
edge residuals are preserved and reflected. No arithmetic factor theory is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketTypeAttachment70
open Representation
open scoped TensorProduct
open PaperXI.InductionIrreducibility PaperXI.InducedTypeSpace68
variable {k G W U : Type*} [Field k] [Group G]
  [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]
variable (H : Subgroup G) (Λ : Representation k H (W ⊗[k] U))

/-- The conjugated action on the literal identity-coset type image. -/
def typeAction : Representation k H (typeSpace H Λ) :=
  (typeOperators H Λ).toAlgHom.toMonoidHom.comp Λ

/-- The conjugated action really is the restriction of the ambient induction. -/
theorem ambient_action (h : H) (x : typeSpace H Λ) :
    ((typeAction H Λ h x : typeSpace H Λ) : IndV H.subtype Λ) =
      ind H.subtype Λ (h : G) (x : IndV H.subtype Λ) := by
  obtain ⟨v, rfl⟩ := (typeEquiv H Λ).surjective x
  change ((typeEquiv H Λ)
    (Λ h ((typeEquiv H Λ).symm ((typeEquiv H Λ) v))) : IndV H.subtype Λ) = _
  rw [LinearEquiv.symm_apply_apply]
  exact LinearMap.congr_fun ((identityInclusion H Λ).isIntertwining' h) v

/-- On a subgroup where the quotient factor is trivial, the actual induced
restriction is exactly the faithful realization of the prescribed first factor. -/
theorem first_factor_action {J Q : Type*} [Group J] [Group Q]
    (i : J →* H) (q : J →* Q)
    (κ : Representation k J W) (σ : Representation k Q U)
    (hr : ∀ j, Λ (i j) = κ.tprod (σ.comp q) j)
    (j : J) (hj : q j = 1) :
    typeAction H Λ (i j) = TensorTypeOperators70.realize H Λ (κ j) := by
  change typeOperators H Λ (Λ (i j)) =
    typeOperators H Λ (TensorTypeOperators70.amplify (κ j))
  apply congrArg (typeOperators H Λ)
  rw [hr]
  ext w u
  simp [hj]

/-- Weighted finite packet projectors agree with averages of the actual
restricted inducing-type action, not merely with a relabeled operator. -/
theorem first_factor_average {J Q I : Type*} [Group J] [Group Q]
    (i : J →* H) (q : J →* Q)
    (κ : Representation k J W) (σ : Representation k Q U)
    (hr : ∀ j, Λ (i j) = κ.tprod (σ.comp q) j)
    (s : Finset I) (g : I → J) (c : I → k) (hg : ∀ a ∈ s, q (g a) = 1) :
    (∑ a ∈ s, c a • typeAction H Λ (i (g a))) =
      TensorTypeOperators70.realize H Λ (∑ a ∈ s, c a • κ (g a)) := by
  rw [TensorTypeOperators70.weighted_sum]
  apply Finset.sum_congr rfl
  intro a ha
  rw [first_factor_action H Λ i q κ σ hr (g a) (hg a ha)]

/-- The supplied first-factor uniformizer operator becomes the exact generator
operator on the type image after the tensor extension. -/
theorem generator_action (t : H) (A : Module.End k W)
    (hg : ∀ w u, Λ t (w ⊗ₜ[k] u) = A w ⊗ₜ[k] u) :
    typeAction H Λ t = TensorTypeOperators70.realize H Λ A := by
  change typeOperators H Λ (Λ t) =
    typeOperators H Λ (TensorTypeOperators70.amplify A)
  apply congrArg (typeOperators H Λ)
  ext w u
  exact hg w u

/-- Actual edgewise intertwining is neither lost nor spuriously created. -/
theorem edge_compatibility_iff [Nontrivial U] {X E : Type*}
    (s t : E → X) (F : X → Module.End k W) (A B : E → Module.End k W) :
    (∀ e, TensorTypeOperators70.realize H Λ (F (t e)) * TensorTypeOperators70.realize H Λ (A e) =
      TensorTypeOperators70.realize H Λ (B e) * TensorTypeOperators70.realize H Λ (F (s e))) ↔
    (∀ e, F (t e) * A e = B e * F (s e)) := by
  simp only [← map_mul, TensorTypeOperators70.realize_eq_iff]

/-- A literal graph edge defect has the same zero set after realization. -/
theorem edge_residual_iff [Nontrivial U] (Fₜ Fₛ A B : Module.End k W) :
    TensorTypeOperators70.realize H Λ Fₜ * TensorTypeOperators70.realize H Λ A -
      TensorTypeOperators70.realize H Λ B * TensorTypeOperators70.realize H Λ Fₛ = 0 ↔
      Fₜ * A - B * Fₛ = 0 := by
  rw [← map_mul, ← map_mul, TensorTypeOperators70.residual_zero_iff]

end PaperXI.PacketTypeAttachment70
