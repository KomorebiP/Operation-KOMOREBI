import PaperX.ProjectorSummands
import PaperX.RepresentationLimits

/-! Commuting matrix projectors as actual split subrepresentations, and the
precise image of their reduction through a surjective coefficient map. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.MatrixProjector
open PaperX.RepresentationLimits

variable {R Γ ι : Type*} [CommRing R] [Group Γ] [Fintype ι] [DecidableEq ι]

def carrier (ρ : MatrixRep R Γ ι) : Representation R Γ (ι → R) :=
  Matrix.toLinAlgEquiv'.toAlgHom.toMonoidHom.comp ρ

/-- Both equations are obligations on the actual integral matrix. -/
structure Projector (ρ : MatrixRep R Γ ι) where
  matrix : Matrix ι ι R
  idempotent : matrix * matrix = matrix
  commutes : ∀ g, ρ g * matrix = matrix * ρ g

namespace Projector
variable {ρ : MatrixRep R Γ ι} (P : Projector ρ)

def linear : Module.End R (ι → R) := Matrix.toLinAlgEquiv' P.matrix

theorem linear_idempotent : IsIdempotentElem P.linear := by
  change Matrix.toLinAlgEquiv' P.matrix * Matrix.toLinAlgEquiv' P.matrix = _
  rw [← map_mul, P.idempotent]
  rfl

theorem linear_commutes (g : Γ) : carrier ρ g * P.linear = P.linear * carrier ρ g := by
  change Matrix.toLinAlgEquiv' (ρ g) * Matrix.toLinAlgEquiv' P.matrix =
    Matrix.toLinAlgEquiv' P.matrix * Matrix.toLinAlgEquiv' (ρ g)
  rw [← map_mul, ← map_mul, P.commutes]

def image : Subrepresentation (carrier ρ) :=
  ProjectorSummands.image (carrier ρ) P.linear P.linear_commutes

def kernel : Subrepresentation (carrier ρ) :=
  ProjectorSummands.kernel (carrier ρ) P.linear P.linear_commutes

def inclusion : P.image.toSubmodule →ₗ[R] (ι → R) :=
  ProjectorSummands.inclusion (carrier ρ) P.linear P.linear_commutes

def retraction : (ι → R) →ₗ[R] P.image.toSubmodule :=
  ProjectorSummands.retraction (carrier ρ) P.linear P.linear_commutes

theorem split_law : P.retraction.comp P.inclusion = LinearMap.id :=
  ProjectorSummands.split_law _ _ P.linear_idempotent P.linear_commutes

theorem inclusion_retraction : P.inclusion.comp P.retraction = P.linear := rfl

theorem inclusion_equivariant (g : Γ) (v : P.image.toSubmodule) :
    P.inclusion (P.image.toRepresentation g v) = carrier ρ g (P.inclusion v) := rfl

theorem retraction_equivariant (g : Γ) (v : ι → R) :
    P.retraction (carrier ρ g v) = P.image.toRepresentation g (P.retraction v) :=
  ProjectorSummands.retraction_equivariant _ _ P.linear_commutes g v

theorem image_iff (v : ι → R) :
    v ∈ P.image.toSubmodule ↔ P.matrix.mulVec v = v :=
  ProjectorSummands.image_iff _ _ P.linear_idempotent P.linear_commutes v

theorem range_inclusion : LinearMap.range P.inclusion = LinearMap.range P.linear :=
  ProjectorSummands.range_inclusion _ _ P.linear_commutes

def decomposition : (P.image.toSubmodule × P.kernel.toSubmodule) ≃ₗ[R] (ι → R) :=
  ProjectorSummands.decomposition _ _ P.linear_idempotent P.linear_commutes

theorem decomposition_equivariant (g : Γ)
    (v : P.image.toSubmodule × P.kernel.toSubmodule) :
    P.decomposition (P.image.toRepresentation g v.1, P.kernel.toRepresentation g v.2) =
      carrier ρ g (P.decomposition v) :=
  ProjectorSummands.decomposition_equivariant _ _ P.linear_idempotent P.linear_commutes g v

variable {S : Type*} [CommRing S]

def changeCoefficients (f : R →+* S) : Projector (RepresentationLimits.changeCoefficients f ρ) where
  matrix := P.matrix.map f
  idempotent := by rw [← Matrix.map_mul, P.idempotent]
  commutes g := by
    change (ρ g).map f * P.matrix.map f = P.matrix.map f * (ρ g).map f
    rw [← Matrix.map_mul, ← Matrix.map_mul, P.commutes]

theorem projection_reduces (f : R →+* S) (v : ι → R) :
    f ∘ P.matrix.mulVec v = (P.changeCoefficients f).matrix.mulVec (f ∘ v) := by
  funext i
  exact f.map_mulVec _ _ i

/-- The reduction of the actual image equals the image of the reduced projector.
This proves surjectivity onto that image, not only containment. -/
theorem image_reduction_iff (f : R →+* S) (hf : Function.Surjective f) (w : ι → S) :
    (∃ v : P.image.toSubmodule, f ∘ (v : ι → R) = w) ↔
      w ∈ (P.changeCoefficients f).image.toSubmodule := by
  constructor
  · rintro ⟨v, rfl⟩
    rw [(P.changeCoefficients f).image_iff]
    rw [← P.projection_reduces, (P.image_iff _).mp v.property]
  · intro hw
    choose v hv using fun i => hf (w i)
    have hvec : f ∘ v = w := funext hv
    refine ⟨⟨P.matrix.mulVec v, ?_⟩, ?_⟩
    · exact ⟨v, rfl⟩
    · rw [P.projection_reduces, hvec, ((P.changeCoefficients f).image_iff _).mp hw]

/-- The complementary kernel also has exactly the expected reduced image. -/
theorem kernel_reduction_iff (f : R →+* S) (hf : Function.Surjective f) (w : ι → S) :
    (∃ v : P.kernel.toSubmodule, f ∘ (v : ι → R) = w) ↔
      w ∈ (P.changeCoefficients f).kernel.toSubmodule := by
  constructor
  · rintro ⟨v, rfl⟩
    change (P.changeCoefficients f).matrix.mulVec (f ∘ (v : ι → R)) = 0
    rw [← P.projection_reduces]
    have hv : P.matrix.mulVec (v : ι → R) = 0 := v.property
    rw [hv]
    ext i
    exact map_zero f
  · intro hw
    choose v hv using fun i => hf (w i)
    have hvec : f ∘ v = w := funext hv
    refine ⟨⟨v - P.linear v, ?_⟩, ?_⟩
    · change P.linear (v - P.linear v) = 0
      rw [map_sub]
      have h : P.linear (P.linear v) = P.linear v :=
        LinearMap.congr_fun P.linear_idempotent v
      rw [h, sub_self]
    · have hm : f ∘ P.matrix.mulVec v = 0 := by
        rw [P.projection_reduces, hvec]
        exact hw
      ext i
      have hm' := congrFun hm i
      change f (v i - P.matrix.mulVec v i) = w i
      rw [map_sub, show f (P.matrix.mulVec v i) = 0 from hm', sub_zero, hv]

end Projector
end PaperX.MatrixProjector
