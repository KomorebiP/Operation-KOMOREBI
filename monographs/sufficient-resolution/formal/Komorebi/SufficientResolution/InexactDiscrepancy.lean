import Komorebi.SufficientResolution.InexactResidual
import Komorebi.SufficientResolution.DiscrepancyRule

/-!
# Robust discrepancy certificates with exact comparison sources

An inexact source is close to an actual accepted exact source. The comparison is
proved from the normal residual and the measured discrepancy with explicit margins.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.InexactDiscrepancy

open TikhonovConstruction TikhonovBounds DiscrepancyResidual DiscrepancyRule
open InexactResidual

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- A source within a specified tolerance of an actual accepted discrepancy source. -/
def NearAccepted (v : V) (eta tau kappa : ℝ) (x : G) : Prop :=
  ∃ y : G, Accepted A v eta tau y ∧ ‖x-y‖ ≤ kappa

 theorem exact_is_near (v : V) (eta tau : ℝ) (x : G)
    (hx : Accepted A v eta tau x) : NearAccepted A v eta tau 0 x :=
  ⟨x, hx, by simp⟩

 theorem near_tolerance_nonneg (v : V) (eta tau kappa : ℝ) (x : G)
    (hx : NearAccepted A v eta tau kappa x) : 0 ≤ kappa := by
  obtain ⟨y, _, h⟩ := hx
  exact (norm_nonneg (x-y)).trans h

 theorem near_weaken (v : V) (eta tau kappa kappa' : ℝ) (x : G)
    (hx : NearAccepted A v eta tau kappa x) (h : kappa ≤ kappa') :
    NearAccepted A v eta tau kappa' x := by
  obtain ⟨y, hy, hd⟩ := hx
  exact ⟨y, hy, hd.trans h⟩

 theorem near_zero_iff (v : V) (eta tau : ℝ) (x : G) :
    NearAccepted A v eta tau 0 x ↔ Accepted A v eta tau x := by
  constructor
  · rintro ⟨y, hy, h⟩
    have he : x = y := sub_eq_zero.mp (norm_eq_zero.mp (le_antisymm h (norm_nonneg _)))
    simpa only [he] using hy
  · exact exact_is_near A v eta tau x

 theorem near_norm (v : V) (eta tau kappa : ℝ) (x g : G)
    (hnoise : ‖A g-v‖ ≤ eta) (hx : NearAccepted A v eta tau kappa x) :
    ‖x‖ ≤ ‖A.kerᗮ.starProjection g‖ + kappa := by
  obtain ⟨y, hy, hd⟩ := hx
  calc
    ‖x‖ ≤ ‖x-y‖ + ‖y‖ := norm_le_norm_sub_add _ _
    _ ≤ kappa + ‖A.kerᗮ.starProjection g‖ :=
      add_le_add hd (accepted_norm A v eta tau y g hnoise hy)
    _ = _ := add_comm _ _

 theorem near_true_residual (v : V) (eta tau kappa : ℝ) (x g : G)
    (hnoise : ‖A g-v‖ ≤ eta) (hx : NearAccepted A v eta tau kappa x) :
    ‖A x-A g‖ ≤ (tau+1)*eta + ‖A‖*kappa := by
  obtain ⟨y, hy, hd⟩ := hx
  have hb : ‖A x-A y‖ ≤ ‖A‖*kappa := by
    rw [← map_sub]
    exact (A.le_opNorm (x-y)).trans (mul_le_mul_of_nonneg_left hd (norm_nonneg _))
  calc
    _ ≤ ‖A x-A y‖+‖A y-A g‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ ‖A‖*kappa+(tau+1)*eta :=
      add_le_add hb (accepted_true_residual A v eta tau y g hnoise hy)
    _ = _ := add_comm _ _

 theorem near_kernel_leakage (v : V) (eta tau kappa : ℝ) (x : G)
    (hx : NearAccepted A v eta tau kappa x) :
    ‖A.ker.starProjection x‖ ≤ kappa := by
  obtain ⟨y, hy, hd⟩ := hx
  have hz : A.ker.starProjection y = 0 :=
    (Submodule.starProjection_apply_eq_zero_iff A.ker).mpr (accepted_identifiable A v eta tau y hy)
  calc
    _ = ‖A.ker.starProjection (x-y)‖ := by rw [map_sub, hz, sub_zero]
    _ ≤ ‖x-y‖ := A.ker.norm_starProjection_apply_le _
    _ ≤ kappa := hd

 theorem near_source_rate (v w : V) (eta tau kappa rate : ℝ) (x : G)
    (hrate : 0 ≤ rate) (hnoise : ‖A (A.adjoint w)-v‖ ≤ eta)
    (hx : NearAccepted A v eta tau kappa x)
    (hbudget : 2*‖w‖*(tau+1)*eta ≤ rate^2) :
    ‖x-A.adjoint w‖ ≤ kappa+rate := by
  obtain ⟨y, hy, hd⟩ := hx
  have hb : ‖y-A.adjoint w‖ ≤ rate :=
    (sq_le_sq₀ (norm_nonneg _) hrate).mp
      ((accepted_source_rate A v w eta tau y hnoise hy).trans hbudget)
  exact (norm_sub_le_norm_sub_add_norm_sub x y (A.adjoint w)).trans (add_le_add hd hb)

 theorem normal_band_certificate (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (eta tau kappa xi : ℝ)
    (hs : ‖normalResidual A lam v x‖ ≤ lam*kappa)
    (hi : ‖normalResidual A lam v x‖ ≤ 2*Real.sqrt lam*xi)
    (hlo : eta+xi ≤ ‖A x-v‖) (hhi : ‖A x-v‖ ≤ tau*eta-xi) :
    NearAccepted A v eta tau kappa x := by
  obtain ⟨lo, up⟩ := measured_band_transfer A lam hl v x eta tau ‖A x-v‖ 0 xi
    (by simp) hi (by linarith) (by linarith)
  exact ⟨regularized A lam hl v, Or.inr ⟨lam, hl, rfl, lo, up⟩,
    certified_correction A lam hl v x kappa hs⟩

 theorem measured_certificate (lam : ℝ) (hl : 0 < lam) (v : V) (x : G)
    (eta tau kappa measured omega xi : ℝ)
    (hs : ‖normalResidual A lam v x‖ ≤ lam*kappa)
    (hi : ‖normalResidual A lam v x‖ ≤ 2*Real.sqrt lam*xi)
    (hmeas : |measured-‖A x-v‖| ≤ omega)
    (hlo : eta+omega+xi ≤ measured) (hhi : measured ≤ tau*eta-omega-xi) :
    NearAccepted A v eta tau kappa x := by
  obtain ⟨lo, up⟩ := measured_band_transfer A lam hl v x eta tau measured omega xi hmeas hi hlo hhi
  exact ⟨regularized A lam hl v, Or.inr ⟨lam, hl, rfl, lo, up⟩,
    certified_correction A lam hl v x kappa hs⟩

 theorem small_data_certificate (v : V) (x : G) (eta tau kappa : ℝ)
    (hv : ‖v‖ ≤ tau*eta) (hx : ‖x‖ ≤ kappa) :
    NearAccepted A v eta tau kappa x := by
  exact ⟨0, Or.inl ⟨hv, rfl⟩, by simpa only [sub_zero] using hx⟩

 theorem measured_small_data_certificate (v : V) (x : G)
    (eta tau kappa measured omega : ℝ)
    (hm : |measured-‖v‖| ≤ omega) (hhi : measured+omega ≤ tau*eta)
    (hx : ‖x‖ ≤ kappa) : NearAccepted A v eta tau kappa x := by
  apply small_data_certificate A v x eta tau kappa _ hx
  obtain ⟨h1, _⟩ := abs_le.mp hm
  linarith

 theorem perturbation_of_near (v : V) (eta tau kappa h : ℝ) (x x' : G)
    (hx : NearAccepted A v eta tau kappa x) (hp : ‖x'-x‖ ≤ h) :
    NearAccepted A v eta tau (kappa+h) x' := by
  obtain ⟨y, hy, hd⟩ := hx
  refine ⟨y, hy, ?_⟩
  calc
    _ ≤ ‖x'-x‖+‖x-y‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ h+kappa := add_le_add hp hd
    _ = _ := add_comm _ _

end Komorebi.SufficientResolution.InexactDiscrepancy
