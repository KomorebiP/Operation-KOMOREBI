import Komorebi.SufficientResolution.InexactDiscrepancy

/-!
# Strong consistency of imperfect discrepancy reconstructions

A fixed bounded real Hilbert operator, a valid noise allowance tending to zero,
and a source-correction budget tending to zero suffice. No separate asymptotic
parameter/noise schedule or closed-range assumption is imposed.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.InexactConsistency

open TikhonovConstruction DiscrepancyRule InexactResidual InexactDiscrepancy
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem near_consistent {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted A (v i) (eta i) tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  choose y hy hd using hx
  have hc : Tendsto (fun i => x i-y i) f (𝓝 0) := squeeze_zero_norm hd hkappa
  have he := accepted_consistent A f eta v y g tau hnoise hy heta
  simpa only [sub_add_cancel, zero_add] using hc.add he

 theorem near_error_norm_limit {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted A (v i) (eta i) tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => ‖x i-g‖) f (𝓝 ‖A.ker.starProjection g‖) := by
  have h := ((near_consistent A f eta kappa v x g tau hnoise hx heta hkappa).sub
    (tendsto_const_nhds (x := g))).norm
  have he : A.kerᗮ.starProjection g-g = -(A.ker.starProjection g) := by
    rw [Submodule.starProjection_orthogonal_val]; abel
  simpa only [he, norm_neg] using h

 theorem near_kernel_tendsto_zero {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (tau : ℝ)
    (hx : ∀ i, NearAccepted A (v i) (eta i) tau (kappa i) (x i))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => A.ker.starProjection (x i)) f (𝓝 0) := by
  exact squeeze_zero_norm
    (fun i => near_kernel_leakage A (v i) (eta i) tau (kappa i) (x i) (hx i)) hkappa

 theorem measured_consistent {ι : Type*} (f : Filter ι)
    (lam eta kappa measured omega xi : ι → ℝ) (hl : ∀ i, 0 < lam i)
    (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hs : ∀ i, ‖normalResidual A (lam i) (v i) (x i)‖ ≤ lam i*kappa i)
    (hi : ∀ i, ‖normalResidual A (lam i) (v i) (x i)‖ ≤ 2*Real.sqrt (lam i)*xi i)
    (hm : ∀ i, |measured i-‖A (x i)-v i‖| ≤ omega i)
    (hlo : ∀ i, eta i+omega i+xi i ≤ measured i)
    (hhi : ∀ i, measured i ≤ tau*eta i-omega i-xi i)
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  apply near_consistent A f eta kappa v x g tau hnoise _ heta hkappa
  intro i
  exact measured_certificate A (lam i) (hl i) (v i) (x i) (eta i) tau (kappa i)
    (measured i) (omega i) (xi i) (hs i) (hi i) (hm i) (hlo i) (hhi i)

 theorem scaled_normal_consistent {ι : Type*} (f : Filter ι)
    (lam eta measured omega : ι → ℝ) (hl : ∀ i, 0 < lam i)
    (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hm : ∀ i, |measured i-‖A (x i)-v i‖| ≤ omega i)
    (hlo : ∀ i, eta i+omega i+
      ‖normalResidual A (lam i) (v i) (x i)‖/(2*Real.sqrt (lam i)) ≤ measured i)
    (hhi : ∀ i, measured i ≤ tau*eta i-omega i-
      ‖normalResidual A (lam i) (v i) (x i)‖/(2*Real.sqrt (lam i)))
    (heta : Tendsto eta f (𝓝 0))
    (hscaled : Tendsto (fun i => ‖normalResidual A (lam i) (v i) (x i)‖/lam i)
      f (𝓝 0)) : Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  apply measured_consistent A f lam eta
    (fun i => ‖normalResidual A (lam i) (v i) (x i)‖/lam i) measured omega
    (fun i => ‖normalResidual A (lam i) (v i) (x i)‖/(2*Real.sqrt (lam i)))
    hl v x g tau hnoise _ _ hm hlo hhi heta hscaled
  · intro i
    have he := div_mul_cancel₀ ‖normalResidual A (lam i) (v i) (x i)‖ (hl i).ne'
    nlinarith
  · intro i
    have hp : (2*Real.sqrt (lam i)) ≠ 0 := ne_of_gt (mul_pos (by norm_num) (Real.sqrt_pos.mpr (hl i)))
    have he := div_mul_cancel₀ ‖normalResidual A (lam i) (v i) (x i)‖ hp
    nlinarith

 theorem noise_scaled_solver_consistent {ι : Type*} (f : Filter ι)
    (lam eta measured omega xi : ι → ℝ) (hl : ∀ i, 0 < lam i)
    (v : ι → V) (x : ι → G) (g : G) (tau c : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hs : ∀ i, ‖normalResidual A (lam i) (v i) (x i)‖ ≤ lam i*(c*eta i))
    (hi : ∀ i, ‖normalResidual A (lam i) (v i) (x i)‖ ≤ 2*Real.sqrt (lam i)*xi i)
    (hm : ∀ i, |measured i-‖A (x i)-v i‖| ≤ omega i)
    (hlo : ∀ i, eta i+omega i+xi i ≤ measured i)
    (hhi : ∀ i, measured i ≤ tau*eta i-omega i-xi i)
    (heta : Tendsto eta f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  exact measured_consistent A f lam eta (fun i => c*eta i) measured omega xi hl
    v x g tau hnoise hs hi hm hlo hhi heta
    (by simpa only [mul_zero] using (tendsto_const_nhds (x := c)).mul heta)

 theorem small_data_inexact_consistent {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hv : ∀ i, ‖v i‖ ≤ tau*eta i) (hx : ∀ i, ‖x i‖ ≤ kappa i)
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  exact near_consistent A f eta kappa v x g tau hnoise
    (fun i => small_data_certificate A (v i) (x i) (eta i) tau (kappa i) (hv i) (hx i))
    heta hkappa

end Komorebi.SufficientResolution.InexactConsistency
