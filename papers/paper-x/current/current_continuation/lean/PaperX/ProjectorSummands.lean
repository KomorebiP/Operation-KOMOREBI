import Mathlib.RepresentationTheory.Subrepresentation
import Mathlib.LinearAlgebra.Projection

/-! Actual equivariant image and complementary kernel of a commuting projector.
The carrier is arbitrary; no decomposition or basis for its summands is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ProjectorSummands

variable {R G V : Type*} [CommRing R] [Monoid G]
  [AddCommGroup V] [Module R V]

variable (ρ : Representation R G V) (E : Module.End R V)
  (hE : IsIdempotentElem E) (hcomm : ∀ g, ρ g * E = E * ρ g)

/-- The summand is the actual image, with its inherited carrier action. -/
def image : Subrepresentation ρ where
  toSubmodule := LinearMap.range E
  apply_mem_toSubmodule g := by
    rintro v ⟨x, rfl⟩
    exact ⟨ρ g x, (LinearMap.congr_fun (hcomm g) x).symm⟩

/-- The complementary subrepresentation is the actual kernel. -/
def kernel : Subrepresentation ρ where
  toSubmodule := LinearMap.ker E
  apply_mem_toSubmodule g := by
    intro v hv
    change E (ρ g v) = 0
    have H : ρ g (E v) = E (ρ g v) := LinearMap.congr_fun (hcomm g) v
    rw [← H]
    change E v = 0 at hv
    rw [hv, map_zero]

def inclusion : (image ρ E hcomm).toSubmodule →ₗ[R] V :=
  (LinearMap.range E).subtype

def retraction : V →ₗ[R] (image ρ E hcomm).toSubmodule := E.rangeRestrict

include hE in
theorem image_iff (v : V) :
    v ∈ (image ρ E hcomm).toSubmodule ↔ E v = v := (LinearMap.IsIdempotentElem.mem_range_iff hE)

include hE in
theorem retraction_inclusion (v : (image ρ E hcomm).toSubmodule) :
    retraction ρ E hcomm (inclusion ρ E hcomm v) = v := by
  apply Subtype.ext
  exact (LinearMap.IsIdempotentElem.mem_range_iff hE).mp v.property

include hE in
theorem split_law :
    (retraction ρ E hcomm).comp (inclusion ρ E hcomm) = LinearMap.id := by
  ext v : 1
  exact retraction_inclusion ρ E hE hcomm v

theorem inclusion_retraction :
    (inclusion ρ E hcomm).comp (retraction ρ E hcomm) = E := rfl

theorem inclusion_injective : Function.Injective (inclusion ρ E hcomm) :=
  Subtype.val_injective

include hE in
theorem retraction_surjective : Function.Surjective (retraction ρ E hcomm) :=
  Function.LeftInverse.surjective (retraction_inclusion ρ E hE hcomm)

theorem range_inclusion :
    LinearMap.range (inclusion ρ E hcomm) = LinearMap.range E :=
  Submodule.range_subtype _

theorem inclusion_equivariant (g : G) (v : (image ρ E hcomm).toSubmodule) :
    inclusion ρ E hcomm ((image ρ E hcomm).toRepresentation g v) =
      ρ g (inclusion ρ E hcomm v) := rfl

theorem retraction_equivariant (g : G) (v : V) :
    retraction ρ E hcomm (ρ g v) =
      (image ρ E hcomm).toRepresentation g (retraction ρ E hcomm v) := by
  apply Subtype.ext
  exact (LinearMap.congr_fun (hcomm g) v).symm

include hE in
theorem image_kernel_complementary :
    IsCompl (image ρ E hcomm).toSubmodule (kernel ρ E hcomm).toSubmodule :=
  LinearMap.IsIdempotentElem.isCompl hE

/-- Addition gives an actual decomposition of the original carrier. -/
def decomposition :
    ((image ρ E hcomm).toSubmodule × (kernel ρ E hcomm).toSubmodule) ≃ₗ[R] V :=
  Submodule.prodEquivOfIsCompl _ _ (image_kernel_complementary ρ E hE hcomm)

theorem decomposition_apply
    (v : (image ρ E hcomm).toSubmodule × (kernel ρ E hcomm).toSubmodule) :
    decomposition ρ E hE hcomm v = (v.1 : V) + (v.2 : V) := rfl

theorem decomposition_equivariant (g : G)
    (v : (image ρ E hcomm).toSubmodule × (kernel ρ E hcomm).toSubmodule) :
    decomposition ρ E hE hcomm
      ((image ρ E hcomm).toRepresentation g v.1,
       (kernel ρ E hcomm).toRepresentation g v.2) =
      ρ g (decomposition ρ E hE hcomm v) := by
  change ρ g (v.1 : V) + ρ g (v.2 : V) = ρ g ((v.1 : V) + (v.2 : V))
  exact (map_add (ρ g) _ _).symm

theorem decomposition_inverse_first (v : V) :
    ((decomposition ρ E hE hcomm).symm v).1 = retraction ρ E hcomm v := by
  apply Subtype.ext
  have hv := (decomposition ρ E hE hcomm).apply_symm_apply v
  have hv' := congrArg E hv
  rw [decomposition_apply, map_add] at hv'
  rw [(LinearMap.IsIdempotentElem.mem_range_iff hE).mp (((decomposition ρ E hE hcomm).symm v).1.property),
    show E (((decomposition ρ E hE hcomm).symm v).2 : V) = 0 from
      ((decomposition ρ E hE hcomm).symm v).2.property, add_zero] at hv'
  exact hv'

include hE in
theorem unique_image_kernel_decomposition (v : V) :
    ∃! w : (image ρ E hcomm).toSubmodule × (kernel ρ E hcomm).toSubmodule,
      (w.1 : V) + (w.2 : V) = v :=
  (decomposition ρ E hE hcomm).toEquiv.bijective.existsUnique v

end PaperX.ProjectorSummands
