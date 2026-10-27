import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.Tactic

/-! Algebraic data-span identification. The analytic Moore-Penrose adapter is separate. -/
set_option autoImplicit false
namespace Komorebi.LSM.Identification
variable {K X Y Z : Type*} [Field K]
variable [AddCommGroup X] [Module K X] [AddCommGroup Y] [Module K Y]
variable [AddCommGroup Z] [Module K Z]

noncomputable def onRange (A : X →ₗ[K] Y) (B : X →ₗ[K] Z)
    (h : LinearMap.ker A ≤ LinearMap.ker B) : LinearMap.range A →ₗ[K] Z :=
  ((LinearMap.ker A).liftQ B h).comp A.quotKerEquivRange.symm.toLinearMap

@[simp] theorem onRange_apply (A : X →ₗ[K] Y) (B : X →ₗ[K] Z)
    (h : LinearMap.ker A ≤ LinearMap.ker B) (x : X) :
    onRange A B h (A.rangeRestrict x) = B x := by
  change (LinearMap.ker A).liftQ B h (A.quotKerEquivRange.symm ⟨A x, _⟩) = B x
  rw [LinearMap.quotKerEquivRange_symm_apply_image]
  rfl

theorem fit_iff_kernel (A : X →ₗ[K] Y) (B : X →ₗ[K] Z) :
    (∃ F : Y →ₗ[K] Z, F.comp A = B) ↔ LinearMap.ker A ≤ LinearMap.ker B := by
  constructor
  · rintro ⟨F, rfl⟩ x hx
    change F (A x) = 0
    rw [LinearMap.mem_ker.mp hx, map_zero]
  · intro h
    obtain ⟨F,hF⟩ := (onRange A B h).exists_extend
    refine ⟨F, ?_⟩
    apply LinearMap.ext
    intro x
    have hx := congrArg (fun G : LinearMap.range A →ₗ[K] Z => G (A.rangeRestrict x)) hF
    simpa using hx

theorem fits_agree_on_range (A : X →ₗ[K] Y) (B : X →ₗ[K] Z)
    (F G : Y →ₗ[K] Z) (hF : F.comp A = B) (hG : G.comp A = B)
    (y : Y) (hy : y ∈ LinearMap.range A) : F y = G y := by
  obtain ⟨x,rfl⟩ := hy
  exact (congrArg (fun H : X →ₗ[K] Z => H x) hF).trans
    (congrArg (fun H : X →ₗ[K] Z => H x) hG).symm

theorem fitted_range (A : X →ₗ[K] Y) (B : X →ₗ[K] Y)
    (F : Y →ₗ[K] Y) (hF : F.comp A = B) :
    (∀ y ∈ LinearMap.range A, F y ∈ LinearMap.range A) ↔
      LinearMap.range B ≤ LinearMap.range A := by
  constructor
  · intro h y hy
    obtain ⟨x,rfl⟩ := hy
    rw [← hF]
    exact h (A x) ⟨x,rfl⟩
  · intro h y hy
    obtain ⟨x,rfl⟩ := hy
    apply h
    exact ⟨x, congrArg (fun H : X →ₗ[K] Y => H x) hF |>.symm⟩

theorem generalized_inverse_fit (A : X →ₗ[K] Y) (B : X →ₗ[K] Z)
    (J : Y →ₗ[K] X) (h : LinearMap.ker A ≤ LinearMap.ker B)
    (hJ : A.comp (J.comp A) = A) : (B.comp J).comp A = B := by
  apply LinearMap.ext
  intro x
  have hx : x - J (A x) ∈ LinearMap.ker A := by
    change A (x - J (A x)) = 0
    rw [map_sub]
    exact sub_eq_zero.mpr (congrArg (fun F : X →ₗ[K] Y => F x) hJ).symm
  have hb := LinearMap.mem_ker.mp (h hx)
  rw [map_sub] at hb
  exact (sub_eq_zero.mp hb).symm

theorem unseen_direction_not_identified (W : Submodule K Y) (y : Y) (hy : y ∉ W)
    (F : Y →ₗ[K] Y) : ∃ G : Y →ₗ[K] Y,
      (∀ w ∈ W, F w = G w) ∧ F y ≠ G y := by
  have yn : y ≠ 0 := fun hz => hy (hz ▸ W.zero_mem)
  obtain ⟨G,hG,hGy⟩ := (F.comp W.subtype).exists_extend_of_notMem hy (F y + y)
  refine ⟨G, ?_, ?_⟩
  · intro w hw
    exact (congrArg (fun H : W →ₗ[K] Y => H ⟨w,hw⟩) hG).symm
  · rw [hGy]
    exact fun he => yn (add_left_cancel (show F y + y = F y + 0 by simpa using he.symm))

end Komorebi.LSM.Identification
