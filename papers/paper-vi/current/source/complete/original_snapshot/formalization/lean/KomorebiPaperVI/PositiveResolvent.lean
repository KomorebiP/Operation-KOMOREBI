import KomorebiPaperVI.FractionalSemigroup
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Order

/-! Author: Komorebi P. Literal positive resolvents and their operator norm bounds. -/
namespace KomorebiPaperVI.PositiveResolvent
open Set
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
set_option backward.isDefEq.respectTransparency false
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

noncomputable def resolvent (A : R) (t : ℝ) : R := cfc (fun x : ℝ => (t+x)⁻¹) A

theorem spectral_positive (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t)
    (x : ℝ) (hx : x∈spectrum ℝ A) : 0 < t+x := by
  have hx0 : 0 ≤ x := spectrum_nonneg_of_nonneg hA hx
  linarith

theorem resolvent_inverse (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    resolvent A t=Ring.inverse (algebraMap ℝ R t+A) := by
  unfold resolvent
  rw [cfc_inv (fun x : ℝ => t+x) A (fun x hx => (spectral_positive A hA t ht x hx).ne')]
  rw [cfc_add A (fun _ : ℝ => t) (fun x : ℝ => x),cfc_const t A,cfc_id' (R := ℝ) (a := A) hA.isSelfAdjoint]

theorem resolvent_left_inverse (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    (algebraMap ℝ R t+A)*resolvent A t=1 := by
  have hc : ContinuousOn (fun x : ℝ => (t+x)⁻¹) (spectrum ℝ A) := by
    apply ContinuousOn.inv₀ (by fun_prop)
    exact fun x hx => (spectral_positive A hA t ht x hx).ne'
  have he : algebraMap ℝ R t+A=cfc (fun x : ℝ => t+x) A := by
    rw [cfc_add A (fun _ : ℝ => t) (fun x : ℝ => x),cfc_const t A,cfc_id' (R := ℝ) (a := A) hA.isSelfAdjoint]
  rw [he,resolvent,← cfc_mul (fun x : ℝ => t+x) (fun x : ℝ => (t+x)⁻¹) A (by fun_prop) hc]
  rw [← cfc_const_one ℝ A]
  apply cfc_congr
  intro x hx
  exact mul_inv_cancel₀ (spectral_positive A hA t ht x hx).ne'

theorem resolvent_right_inverse (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    resolvent A t*(algebraMap ℝ R t+A)=1 := by
  have he : algebraMap ℝ R t+A=cfc (fun x : ℝ => t+x) A := by
    rw [cfc_add A (fun _ : ℝ => t) (fun x : ℝ => x),cfc_const t A,cfc_id' (R := ℝ) (a := A) hA.isSelfAdjoint]
  have h := resolvent_left_inverse A hA t ht
  rw [he] at h ⊢
  exact (cfc_commute_cfc (fun x : ℝ => (t+x)⁻¹) (fun x : ℝ => t+x) A).eq.trans h

theorem resolvent_gap_norm (A : R) (hA : 0 ≤ A) (t m : ℝ) (ht : 0 < t) (hm : 0 ≤ m)
    (hg : algebraMap ℝ R m ≤ A) : ‖resolvent A t‖ ≤ (t+m)⁻¹ := by
  apply norm_cfc_le (by positivity)
  intro x hx
  have hmx : m ≤ x := (algebraMap_le_iff_le_spectrum hA.isSelfAdjoint).mp hg x hx
  rw [Real.norm_of_nonneg (inv_nonneg.mpr (spectral_positive A hA t ht x hx).le)]
  exact inv_anti₀ (by positivity) (by linarith)

theorem resolvent_norm (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    ‖resolvent A t‖ ≤ t⁻¹ := by
  simpa using resolvent_gap_norm A hA t 0 ht le_rfl (by simpa using hA)

theorem resolvent_defect (A B C : R) (hA : 0 ≤ A) (hB : 0 ≤ B) (t : ℝ) (ht : 0 < t) :
    resolvent B t*C-C*resolvent A t=resolvent B t*(C*A-B*C)*resolvent A t := by
  have hAinv := resolvent_left_inverse A hA t ht
  have hBinv := resolvent_right_inverse B hB t ht
  have hc := Algebra.commutes (R := ℝ) (A := R) t C
  have hm : C*A-B*C=C*(algebraMap ℝ R t+A)-(algebraMap ℝ R t+B)*C := by
    simp only [mul_add,add_mul,hc]
    abel
  rw [hm]
  calc
    _ = resolvent B t*C*((algebraMap ℝ R t+A)*resolvent A t)-
          (resolvent B t*(algebraMap ℝ R t+B))*C*resolvent A t := by rw [hAinv,hBinv]; simp
    _ = _ := by noncomm_ring

theorem saturation_cfc (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    A*resolvent A t=cfc (fun x : ℝ => x*(t+x)⁻¹) A := by
  have hc : ContinuousOn (fun x : ℝ => (t+x)⁻¹) (spectrum ℝ A) := by
    apply ContinuousOn.inv₀ (by fun_prop)
    exact fun x hx => (spectral_positive A hA t ht x hx).ne'
  rw [cfc_mul (fun x : ℝ => x) (fun x : ℝ => (t+x)⁻¹) A (by fun_prop) hc,cfc_id' ℝ A hA.isSelfAdjoint]
  rfl

theorem saturation_norm (A : R) (hA : 0 ≤ A) (t : ℝ) (ht : 0 < t) :
    ‖A*resolvent A t‖ ≤ 1 := by
  rw [saturation_cfc A hA t ht]
  apply norm_cfc_le zero_le_one
  intro x hx
  have hx0 : 0 ≤ x := spectrum_nonneg_of_nonneg hA hx
  rw [Real.norm_of_nonneg (mul_nonneg hx0 (inv_nonneg.mpr (spectral_positive A hA t ht x hx).le)),← div_eq_mul_inv]
  exact (div_le_one (spectral_positive A hA t ht x hx)).mpr (by linarith)

end KomorebiPaperVI.PositiveResolvent
