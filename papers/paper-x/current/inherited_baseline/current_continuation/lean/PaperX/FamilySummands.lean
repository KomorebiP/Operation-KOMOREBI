import PaperX.OrthogonalProjectors

/-! A complete orthogonal family gives the full equivariant decomposition into
its actual images. No bases or freeness of those images are assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.OrthogonalProjectors
namespace Family
open PaperX.RepresentationLimits PaperX.MatrixProjector
open PaperX.OrthogonalProjectors
open scoped BigOperators

variable {R Γ ι J : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι] [Fintype J]
  {ρ : MatrixRep R Γ ι} (E : Family ρ J)

theorem linear_total : ∑ j, (E.projector j).linear = LinearMap.id := by
  change ∑ j, Matrix.toLinAlgEquiv' (E.projector j).matrix = _
  rw [← map_sum, E.total, map_one]
  rfl

theorem linear_orthogonal (i j : J) (hij : i ≠ j) :
    (E.projector i).linear * (E.projector j).linear = 0 := by
  change Matrix.toLinAlgEquiv' (E.projector i).matrix *
    Matrix.toLinAlgEquiv' (E.projector j).matrix = 0
  rw [← map_mul, E.orthogonal i j hij, map_zero]

/-- Every component is the actual image of the corresponding projector. -/
abbrev Components := ∀ j, (E.projector j).image.toSubmodule

def assemble : E.Components →ₗ[R] (ι → R) where
  toFun v := ∑ j, ((v j : (E.projector j).image.toSubmodule) : ι → R)
  map_add' v w := by simp [Finset.sum_add_distrib]
  map_smul' a v := by simp [Finset.smul_sum]

def components : (ι → R) →ₗ[R] E.Components :=
  LinearMap.pi fun j => (E.projector j).retraction

theorem linear_image (j : J) (v : (E.projector j).image.toSubmodule) :
    (E.projector j).linear (v : ι → R) = v := by
  exact ((E.projector j).image_iff _).mp v.property

theorem linear_other_image (i j : J) (hij : i ≠ j)
    (v : (E.projector j).image.toSubmodule) :
    (E.projector i).linear (v : ι → R) = 0 := by
  rw [← E.linear_image j v]
  exact LinearMap.congr_fun (E.linear_orthogonal i j hij) (v : ι → R)

theorem assemble_components (v : ι → R) : E.assemble (E.components v) = v := by
  change (∑ j, (E.projector j).linear v) = v
  have h := LinearMap.congr_fun E.linear_total v
  simpa using h

theorem components_assemble (v : E.Components) : E.components (E.assemble v) = v := by
  classical
  funext i
  apply Subtype.ext
  change (E.projector i).linear (∑ j, (v j : ι → R)) = (v i : ι → R)
  rw [map_sum, Finset.sum_eq_single i]
  · exact E.linear_image i (v i)
  · intro j _ hji
    exact E.linear_other_image i j (Ne.symm hji) (v j)
  · simp

/-- The full decomposition, with summation as its forward map. -/
def decomposition : E.Components ≃ₗ[R] (ι → R) :=
  LinearEquiv.ofLinearMap E.assemble E.components
    (LinearMap.ext E.assemble_components) (LinearMap.ext E.components_assemble)

theorem decomposition_apply (v : E.Components) :
    E.decomposition v = ∑ j, (v j : ι → R) := rfl

theorem decomposition_symm_apply (v : ι → R) (j : J) :
    E.decomposition.symm v j = (E.projector j).retraction v := rfl

theorem decomposition_equivariant (g : Γ) (v : E.Components) :
    E.decomposition (fun j => (E.projector j).image.toRepresentation g (v j)) =
      carrier ρ g (E.decomposition v) := by
  change (∑ j, carrier ρ g (v j : ι → R)) = carrier ρ g (∑ j, (v j : ι → R))
  rw [map_sum]

theorem inverse_equivariant (g : Γ) (v : ι → R) (j : J) :
    E.decomposition.symm (carrier ρ g v) j =
      (E.projector j).image.toRepresentation g (E.decomposition.symm v j) :=
  (E.projector j).retraction_equivariant g v

end Family
end PaperX.OrthogonalProjectors
