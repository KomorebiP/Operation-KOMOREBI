module
public import H12CubicBranch
public import H12LineNorms
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.Positivity
@[expose] public section
namespace H12.PolarizedReality
open Complex

/-- A positive-real complex number is its own norm. -/
theorem norm_eq_real_part (z : ℂ) (hi : z.im=0) (hr : 0≤z.re) :
    ‖z‖=z.re := by
  have hz : z=(z.re : ℂ) := by apply Complex.ext <;> simp [hi]
  rw [hz, Complex.norm_real, Real.norm_of_nonneg hr]
  simp

theorem positive_real_equal_of_norm (x y : ℂ)
    (hx : x.im=0) (hy : y.im=0) (hxr : 0<x.re) (hyr : 0<y.re)
    (hn : ‖x‖=‖y‖) : x=y := by
  apply Complex.ext
  · rw [norm_eq_real_part x hx hxr.le, norm_eq_real_part y hy hyr.le] at hn
    exact hn
  · rw [hx,hy]

/-- The arithmetic phase theorem may be reduced to exact realness.
The modulus, sign and target realness are distinct explicit hypotheses. -/
theorem normalized_reality_implies_cube (z u c : ℂ) (hc : c≠0)
    (hm : ‖z‖=‖u‖) (hz : (c*z^3).im=0) (hu : (c*u^3).im=0)
    (hposz : 0<(c*z^3).re) (hposu : 0<(c*u^3).re) : z^3=u^3 := by
  have hn : ‖c*z^3‖=‖c*u^3‖ := by simp only [norm_mul,norm_pow,hm]
  have hh := positive_real_equal_of_norm (c*z^3) (c*u^3) hz hu hposz hposu hn
  exact mul_left_cancel₀ hc hh

/-- Exact reality is not proved by the numerical enclosure. Both appear here. -/
theorem normalized_reality_with_branch (z u c : ℂ) (hu0 : u≠0) (hc : c≠0)
    (hm : ‖z‖=‖u‖) (hz : (c*z^3).im=0) (hu : (c*u^3).im=0)
    (hposz : 0<(c*z^3).re) (hposu : 0<(c*u^3).re)
    (hnear : ‖z/u-1‖<1) : z=u := by
  exact H12.CubicBranch.cube_comparison_with_enclosure z u hu0
    (normalized_reality_implies_cube z u c hc hm hz hu hposz hposu) hnear

/-- Polarization turns the oriented algebraic factors into positive norms. -/
theorem conjugate_product_real (e a d : ℂ) :
    (e*(starRingEnd ℂ) e)^2*(a*(starRingEnd ℂ) a)^3*(d*(starRingEnd ℂ) d)^2 =
      ((‖e‖^4*‖a‖^6*‖d‖^4 : ℝ) : ℂ) := by
  rw [Complex.mul_conj',Complex.mul_conj',Complex.mul_conj']
  push_cast
  ring

theorem positive_polarized_product (e a d : ℂ)
    (he : e≠0) (ha : a≠0) (hd : d≠0) :
    0 < ‖e‖^4*‖a‖^6*‖d‖^4 := by
  exact mul_pos (mul_pos (pow_pos (norm_pos_iff.mpr he) 4)
    (pow_pos (norm_pos_iff.mpr ha) 6)) (pow_pos (norm_pos_iff.mpr hd) 4)

end H12.PolarizedReality
