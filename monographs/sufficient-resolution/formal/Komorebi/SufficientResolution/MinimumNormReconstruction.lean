import Komorebi.SufficientResolution.OrthogonalResolution
import Mathlib.Analysis.Normed.Operator.Banach

/-!
# Canonical bounded reconstruction from a closed range

The inverse is constructed on the actual range of A, not its closure. The
CompleteSpace A.range hypothesis is supplied by closedness in a Hilbert space.
No injectivity, finite dimension, or supplied pseudoinverse is assumed.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MinimumNormReconstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable (A : G →L[ℝ] V)

/-- The generator restricted to the distinguishable source directions. -/
def restricted : A.kerᗮ →L[ℝ] A.range :=
  A.rangeRestrict.comp A.kerᗮ.subtypeL

omit [CompleteSpace G] in
 theorem restricted_apply (x : A.kerᗮ) : (restricted A x : V) = A (x : G) := rfl

 theorem source_projection_image (g : G) :
    A (A.kerᗮ.starProjection g) = A g := by
  rw [Submodule.starProjection_orthogonal_val, map_sub,
    show A (A.ker.starProjection g) = 0 from A.ker.starProjection_apply_mem g,
    sub_zero]

omit [CompleteSpace G] in
 theorem injective_on_kernel_orthogonal {x y : G}
    (hx : x ∈ A.kerᗮ) (hy : y ∈ A.kerᗮ) (he : A x = A y) : x = y := by
  have hz : x-y ∈ A.ker := by change A (x-y) = 0; rw [map_sub, he, sub_self]
  have ho := A.kerᗮ.sub_mem hx hy
  exact sub_eq_zero.mp (inner_self_eq_zero.mp (ho _ hz))

omit [CompleteSpace G] in
 theorem restricted_injective : Function.Injective (restricted A) := by
  intro x y he
  apply Subtype.ext
  apply injective_on_kernel_orthogonal A x.2 y.2
  exact congrArg (fun z : A.range => (z : V)) he

 theorem restricted_surjective : Function.Surjective (restricted A) := by
  intro v
  obtain ⟨g, hg⟩ := v.2
  refine ⟨A.kerᗮ.orthogonalProjectionOnto g, ?_⟩
  apply Subtype.ext
  exact (source_projection_image A g).trans hg

variable [CompleteSpace A.range]

/-- The open mapping theorem supplies a continuous inverse on the actual range. -/
def restrictionEquiv : A.kerᗮ ≃L[ℝ] A.range :=
  ContinuousLinearEquiv.ofBijective (restricted A)
    (LinearMap.ker_eq_bot.mpr (restricted_injective A))
    (LinearMap.range_eq_top.mpr (restricted_surjective A))

 theorem restrictionEquiv_apply (x : A.kerᗮ) :
    (restrictionEquiv A x : V) = A (x : G) := rfl

/-- Canonical bounded minimum-norm reconstruction, defined for all local data. -/
def recover : V →L[ℝ] G :=
  A.kerᗮ.subtypeL.comp ((restrictionEquiv A).symm.toContinuousLinearMap.comp
    A.range.orthogonalProjectionOnto)

 theorem recover_mem (v : V) : recover A v ∈ A.kerᗮ :=
  ((restrictionEquiv A).symm (A.range.orthogonalProjectionOnto v)).2

 theorem image_recover (v : V) : A (recover A v) = A.range.starProjection v := by
  exact congrArg (fun z : A.range => (z : V))
    ((restrictionEquiv A).apply_symm_apply (A.range.orthogonalProjectionOnto v))

 theorem recover_image (g : G) : recover A (A g) = A.kerᗮ.starProjection g := by
  apply injective_on_kernel_orthogonal A (recover_mem A _) (A.kerᗮ.starProjection_apply_mem g)
  rw [image_recover, source_projection_image]
  exact Submodule.starProjection_eq_self_iff.mpr (A.mem_range_self g)

 theorem image_comp_recover : A.comp (recover A) = A.range.starProjection := by
  ext v
  exact image_recover A v

 theorem recover_comp_image : (recover A).comp A = A.kerᗮ.starProjection := by
  ext g
  exact recover_image A g

 theorem penrose_image (g : G) : A (recover A (A g)) = A g := by
  rw [recover_image, source_projection_image]

 theorem penrose_recover (v : V) : recover A (A (recover A v)) = recover A v := by
  rw [recover_image, Submodule.starProjection_eq_self_iff.mpr (recover_mem A v)]

 theorem recover_projected_data (v : V) :
    recover A (A.range.starProjection v) = recover A v := by
  rw [← image_recover A v]
  exact penrose_recover A v

 theorem recover_eq_zero_iff (v : V) : recover A v = 0 ↔ v ∈ A.rangeᗮ := by
  constructor
  · intro hz
    have hp : A.range.starProjection v = 0 := by rw [← image_recover A v, hz, map_zero]
    change v ∈ A.range.starProjection.ker at hp
    rwa [Submodule.ker_starProjection] at hp
  · intro hv
    have hp : A.range.starProjection v = 0 := by
      change v ∈ A.range.starProjection.ker
      rw [Submodule.ker_starProjection]
      exact hv
    rw [← recover_projected_data A v, hp, map_zero]

 theorem recover_kernel : (recover A).ker = A.rangeᗮ := by
  ext v
  exact recover_eq_zero_iff A v

 theorem recover_range : (recover A).range = A.kerᗮ := by
  apply le_antisymm
  · rintro g ⟨v, rfl⟩
    exact recover_mem A v
  · intro g hg
    exact ⟨A g, (recover_image A g).trans (Submodule.starProjection_eq_self_iff.mpr hg)⟩

 theorem discarded_data_ignored (v : V) {e : V} (he : e ∈ A.rangeᗮ) :
    recover A (v+e) = recover A v := by
  rw [map_add, (recover_eq_zero_iff A e).mpr he, add_zero]

/-- Orthogonal selection, together with the best-image identity, determines the map. -/
 theorem recover_unique (B : V →L[ℝ] G)
    (himage : ∀ v, A (B v) = A.range.starProjection v)
    (horth : ∀ v, B v ∈ A.kerᗮ) : B = recover A := by
  ext v
  exact injective_on_kernel_orthogonal A (horth v) (recover_mem A v)
    ((himage v).trans (image_recover A v).symm)

 theorem image_projection_symmetric (v w : V) :
    inner ℝ (A (recover A v)) w = inner ℝ v (A (recover A w)) := by
  rw [image_recover, image_recover]
  exact Submodule.inner_starProjection_left_eq_right _ _ _

 theorem source_projection_symmetric (g h : G) :
    inner ℝ (recover A (A g)) h = inner ℝ g (recover A (A h)) := by
  rw [recover_image, recover_image]
  exact Submodule.inner_starProjection_left_eq_right _ _ _

end Komorebi.SufficientResolution.MinimumNormReconstruction
