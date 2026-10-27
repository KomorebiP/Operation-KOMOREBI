module
public import SharedCorrection

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.SharedCorrection

variable {R U V W T : Type*} [CommRing R]
variable [AddCommGroup U] [Module R U]
variable [AddCommGroup V] [Module R V]
variable [AddCommGroup W] [Module R W]
variable [AddCommGroup T] [Module R T]

/-- Every linear observation insensitive to either local kernel factors
uniquely through the common quotient. -/
theorem common_universal (J : U →ₗ[R] V) (K : U →ₗ[R] W) (F : U →ₗ[R] T)
    (hJ : LinearMap.ker J ≤ LinearMap.ker F)
    (hK : LinearMap.ker K ≤ LinearMap.ker F) :
    ∃! q : Common J K →ₗ[R] T, q.comp (commonKernel J K).mkQ = F := by
  have hF : commonKernel J K ≤ LinearMap.ker F := sup_le hJ hK
  refine ⟨(commonKernel J K).liftQ F hF, Submodule.liftQ_mkQ _ _ _, ?_⟩
  intro q hq
  apply LinearMap.ext
  intro c
  obtain ⟨u, rfl⟩ := (commonKernel J K).mkQ_surjective c
  change q ((commonKernel J K).mkQ u) = F u
  exact LinearMap.congr_fun hq u

/-- A pair of linear observations on attainable local packets that agree
on every common correction factor uniquely through the common quotient.
This is the pushout universal property for the two range restrictions. -/
theorem common_paired_universal (J : U →ₗ[R] V) (K : U →ₗ[R] W)
    (h : LinearMap.range J →ₗ[R] T) (k : LinearMap.range K →ₗ[R] T)
    (agree : h.comp J.rangeRestrict = k.comp K.rangeRestrict) :
    ∃! q : Common J K →ₗ[R] T,
      q.comp (labelJ J K) = h ∧ q.comp (labelK J K) = k := by
  let F := h.comp J.rangeRestrict
  have hJ : LinearMap.ker J ≤ LinearMap.ker F := by
    intro u hu
    change h (J.rangeRestrict u) = 0
    have hJu : J.rangeRestrict u = 0 := Subtype.ext hu
    rw [hJu, map_zero]
  have hK : LinearMap.ker K ≤ LinearMap.ker F := by
    intro u hu
    change (h.comp J.rangeRestrict) u = 0
    rw [agree]
    change k (K.rangeRestrict u) = 0
    have hKu : K.rangeRestrict u = 0 := Subtype.ext hu
    rw [hKu, map_zero]
  obtain ⟨q, hq, _⟩ := common_universal J K F hJ hK
  have hqJ : q.comp (labelJ J K) = h := by
    ext a
    obtain ⟨u, hu⟩ := a.property
    have ha : J.rangeRestrict u = a := Subtype.ext hu
    rw [← ha]
    change q (labelJ J K (J.rangeRestrict u)) = h (J.rangeRestrict u)
    rw [labelJ_image]
    exact LinearMap.congr_fun hq u
  have hqK : q.comp (labelK J K) = k := by
    ext b
    obtain ⟨u, hu⟩ := b.property
    have hb : K.rangeRestrict u = b := Subtype.ext hu
    rw [← hb]
    change q (labelK J K (K.rangeRestrict u)) = k (K.rangeRestrict u)
    rw [labelK_image]
    have hqu := LinearMap.congr_fun hq u
    change q ((commonKernel J K).mkQ u) = (h.comp J.rangeRestrict) u at hqu
    rw [agree] at hqu
    exact hqu
  refine ⟨q, ⟨hqJ, hqK⟩, ?_⟩
  intro q' hq'
  apply LinearMap.ext
  intro c
  obtain ⟨a, rfl⟩ := labelJ_surjective J K c
  exact (LinearMap.congr_fun hq'.1 a).trans (LinearMap.congr_fun hqJ a).symm

#print axioms common_universal
#print axioms common_paired_universal

end Komorebi.SharedCorrection
