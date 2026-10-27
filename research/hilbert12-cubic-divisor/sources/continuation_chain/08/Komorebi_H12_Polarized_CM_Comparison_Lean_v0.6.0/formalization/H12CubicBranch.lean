module
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FieldSimp
@[expose] public section
namespace H12.CubicBranch

theorem cube_root_norm_one (z : ℂ) (hz : z^3=1) : ‖z‖=1 := by
  apply (pow_eq_one_iff_of_nonneg (norm_nonneg z) (by decide : (3:ℕ)≠0)).mp
  simpa only [norm_pow, norm_one] using congrArg norm hz

theorem nontrivial_cube_root_distance (z : ℂ) (hz : z^3=1) (hne : z≠1) :
    ‖z-1‖^2=3 := by
  have hpoly : z^2+z+1=0 := by
    have hprod : (z-1)*(z^2+z+1)=0 := by calc
      (z-1)*(z^2+z+1)=z^3-1 := by ring
      _=0 := by rw [hz]; ring
    exact (mul_eq_zero.mp hprod).resolve_left (sub_ne_zero.mpr hne)
  have hsq : (z-1)^2=(-3:ℂ)*z := by
    calc
      (z-1)^2=(z^2+z+1)-3*z := by ring
      _=(-3:ℂ)*z := by rw [hpoly]; ring
  have hn := congrArg norm hsq
  rw [norm_pow, norm_mul, cube_root_norm_one z hz] at hn
  norm_num at hn
  exact hn

/-- The interval certificate supplies the distance inequality; the arithmetic
power equality remains an explicit hypothesis. -/
theorem cube_root_near_one (z : ℂ) (hz : z^3=1) (hnear : ‖z-1‖<1) : z=1 := by
  by_contra hne
  have hs := nontrivial_cube_root_distance z hz hne
  have hn := norm_nonneg (z-1)
  nlinarith

theorem cube_comparison_with_enclosure (u v : ℂ) (hv : v≠0)
    (hc : u^3=v^3) (hb : ‖u/v-1‖<1) : u=v := by
  have hz : (u/v)^3=1 := by rw [div_pow,hc]; exact div_self (pow_ne_zero 3 hv)
  have he := cube_root_near_one (u/v) hz hb
  exact (div_eq_one_iff_eq hv).mp he

end H12.CubicBranch
