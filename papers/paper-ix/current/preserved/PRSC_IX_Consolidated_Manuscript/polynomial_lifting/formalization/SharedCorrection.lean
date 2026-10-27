module
public import Mathlib.LinearAlgebra.Isomorphisms
public import Mathlib.Tactic.Abel

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.SharedCorrection

variable {R U V W : Type*} [CommRing R]
variable [AddCommGroup U] [Module R U]
variable [AddCommGroup V] [Module R V]
variable [AddCommGroup W] [Module R W]

/-- Corrections invisible to either local map generate the common kernel. -/
def commonKernel (J : U →ₗ[R] V) (K : U →ₗ[R] W) : Submodule R U :=
  LinearMap.ker J ⊔ LinearMap.ker K

/-- The common quotient retains exactly the information shared by the two maps. -/
abbrev Common (J : U →ₗ[R] V) (K : U →ₗ[R] W) := U ⧸ commonKernel J K

/-- Equality in the common quotient is precisely simultaneous realizability
of the left image of one correction and the right image of the other. -/
theorem quotient_mk_eq_iff_common (J : U →ₗ[R] V) (K : U →ₗ[R] W) (u v : U) :
    (Submodule.Quotient.mk u : Common J K) = Submodule.Quotient.mk v ↔
      ∃ w : U, J w = J u ∧ K w = K v := by
  rw [Submodule.Quotient.eq]
  change u - v ∈ LinearMap.ker J ⊔ LinearMap.ker K ↔ _
  constructor
  · intro h
    obtain ⟨s, hs, t, ht, hst⟩ := Submodule.mem_sup.mp h
    have hs0 : J s = 0 := hs
    have ht0 : K t = 0 := ht
    refine ⟨u - s, ?_, ?_⟩
    · rw [map_sub, hs0, sub_zero]
    · have hw : u - s = v + t := by
        calc
          u - s = (u - v) + v - s := by abel
          _ = (s + t) + v - s := by rw [hst]
          _ = v + t := by abel
      rw [hw, map_add, ht0, add_zero]
  · rintro ⟨w, hwJ, hwK⟩
    apply Submodule.mem_sup.mpr
    refine ⟨u - w, ?_, w - v, ?_, ?_⟩
    · change J (u - w) = 0
      rw [map_sub, hwJ, sub_self]
    · change K (w - v) = 0
      rw [map_sub, hwK, sub_self]
    · abel

/-- Linear label for an attainable left packet. -/
def labelJ (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    LinearMap.range J →ₗ[R] Common J K :=
  ((LinearMap.ker J).liftQ (commonKernel J K).mkQ (by
    rw [Submodule.ker_mkQ]
    exact le_sup_left)).comp J.quotKerEquivRange.symm.toLinearMap

/-- Linear label for an attainable right packet. -/
def labelK (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    LinearMap.range K →ₗ[R] Common J K :=
  ((LinearMap.ker K).liftQ (commonKernel J K).mkQ (by
    rw [Submodule.ker_mkQ]
    exact le_sup_right)).comp K.quotKerEquivRange.symm.toLinearMap

@[simp]
theorem labelJ_image (J : U →ₗ[R] V) (K : U →ₗ[R] W) (u : U) :
    labelJ J K (J.rangeRestrict u) = (commonKernel J K).mkQ u := by
  have h : J.quotKerEquivRange.symm (J.rangeRestrict u) = (LinearMap.ker J).mkQ u :=
    J.quotKerEquivRange_symm_apply_image u _
  simp only [labelJ, LinearMap.comp_apply, LinearEquiv.coe_toLinearMap]
  rw [h]
  rfl

@[simp]
theorem labelK_image (J : U →ₗ[R] V) (K : U →ₗ[R] W) (u : U) :
    labelK J K (K.rangeRestrict u) = (commonKernel J K).mkQ u := by
  have h : K.quotKerEquivRange.symm (K.rangeRestrict u) = (LinearMap.ker K).mkQ u :=
    K.quotKerEquivRange_symm_apply_image u _
  simp only [labelK, LinearMap.comp_apply, LinearEquiv.coe_toLinearMap]
  rw [h]
  rfl

/-- The left label covers the common quotient, without assuming J is onto V. -/
theorem labelJ_surjective (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    Function.Surjective (labelJ J K) := by
  intro c
  obtain ⟨u, rfl⟩ := (commonKernel J K).mkQ_surjective c
  exact ⟨J.rangeRestrict u, labelJ_image J K u⟩

/-- The right label also covers the common quotient. -/
theorem labelK_surjective (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    Function.Surjective (labelK J K) := by
  intro c
  obtain ⟨u, rfl⟩ := (commonKernel J K).mkQ_surjective c
  exact ⟨K.rangeRestrict u, labelK_image J K u⟩

/-- A finite left target suffices for a finite common quotient, even if U is infinite. -/
theorem common_finite_of_left (J : U →ₗ[R] V) (K : U →ₗ[R] W) [Finite V] :
    Finite (Common J K) :=
  Finite.of_surjective (labelJ J K) (labelJ_surjective J K)

/-- A finite right target likewise suffices. -/
theorem common_finite_of_right (J : U →ₗ[R] V) (K : U →ₗ[R] W) [Finite W] :
    Finite (Common J K) :=
  Finite.of_surjective (labelK J K) (labelK_surjective J K)

/-- Individually attainable packets have equal labels exactly when a single
correction realizes both. -/
theorem labels_eq_iff_common (J : U →ₗ[R] V) (K : U →ₗ[R] W)
    (a : LinearMap.range J) (b : LinearMap.range K) :
    labelJ J K a = labelK J K b ↔
      ∃ u : U, J.rangeRestrict u = a ∧ K.rangeRestrict u = b := by
  obtain ⟨u, hu⟩ := a.property
  obtain ⟨v, hv⟩ := b.property
  have ha : J.rangeRestrict u = a := Subtype.ext hu
  have hb : K.rangeRestrict v = b := Subtype.ext hv
  rw [← ha, ← hb, labelJ_image, labelK_image]
  change (Submodule.Quotient.mk u : Common J K) = Submodule.Quotient.mk v ↔ _
  rw [quotient_mk_eq_iff_common]
  constructor
  · rintro ⟨w, hwJ, hwK⟩
    exact ⟨w, Subtype.ext hwJ, Subtype.ext hwK⟩
  · rintro ⟨w, hwJ, hwK⟩
    exact ⟨w, congrArg Subtype.val hwJ, congrArg Subtype.val hwK⟩

/-- The map sending one correction to its two local images. -/
def joint (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    U →ₗ[R] LinearMap.range J × LinearMap.range K :=
  J.rangeRestrict.prod K.rangeRestrict

/-- The genuine fiber-product submodule over the common quotient. -/
def fiber (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    Submodule R (LinearMap.range J × LinearMap.range K) :=
  LinearMap.ker ((labelJ J K).comp (LinearMap.fst R (LinearMap.range J) (LinearMap.range K)) -
    (labelK J K).comp (LinearMap.snd R (LinearMap.range J) (LinearMap.range K)))

@[simp]
theorem mem_fiber (J : U →ₗ[R] V) (K : U →ₗ[R] W)
    (z : LinearMap.range J × LinearMap.range K) :
    z ∈ fiber J K ↔ labelJ J K z.1 = labelK J K z.2 := by
  change labelJ J K z.1 - labelK J K z.2 = 0 ↔ _
  exact sub_eq_zero

/-- The joint image is exactly the fiber product, not merely contained in it. -/
theorem joint_range_eq_fiber (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    LinearMap.range (joint J K) = fiber J K := by
  ext z
  rw [mem_fiber, labels_eq_iff_common]
  constructor
  · rintro ⟨u, hu⟩
    exact ⟨u, congrArg Prod.fst hu, congrArg Prod.snd hu⟩
  · rintro ⟨u, huJ, huK⟩
    exact ⟨u, Prod.ext huJ huK⟩

/-- Explicit linear equivalence between the joint image and fiber-product submodule. -/
def jointImageEquivFiber (J : U →ₗ[R] V) (K : U →ₗ[R] W) :
    LinearMap.range (joint J K) ≃ₗ[R] fiber J K :=
  LinearEquiv.ofEq _ _ (joint_range_eq_fiber J K)

variable {T : Type*} [AddCommGroup T] [Module R T]

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

#print axioms commonKernel
#print axioms Common
#print axioms quotient_mk_eq_iff_common
#print axioms labelJ
#print axioms labelK
#print axioms labelJ_image
#print axioms labelK_image
#print axioms labelJ_surjective
#print axioms labelK_surjective
#print axioms common_finite_of_left
#print axioms common_finite_of_right
#print axioms labels_eq_iff_common
#print axioms joint
#print axioms fiber
#print axioms mem_fiber
#print axioms joint_range_eq_fiber
#print axioms jointImageEquivFiber
#print axioms common_universal
#print axioms common_paired_universal

end Komorebi.SharedCorrection
