import Komorebi.DyadicBall
import Mathlib.Data.Nat.Log

set_option autoImplicit false
namespace Komorebi.RoundedPosterior

/-- One unit in the last fractional place of the retained dyadic evaluator. -/
def mesh (p : ℕ) : ℚ := 1 / scale p

theorem mesh_pos (p : ℕ) : 0 < mesh p := div_pos (by norm_num) (scale_pos p)

theorem mesh_le_one (p : ℕ) : mesh p ≤ 1 := by
  apply (div_le_one (scale_pos p)).mpr
  exact one_le_pow₀ (by norm_num : (1 : ℚ) ≤ 2)

/-- Downward center rounding loses at most one mesh unit for either input sign. -/
theorem down_error_le_mesh (p : ℕ) (x : ℚ) : |x-down p x| ≤ mesh p := by
  rw [abs_of_nonneg (sub_nonneg.mpr (down_le p x))]
  have h : x ≤ down p x + mesh p := by
    change x ≤ (⌊x*scale p⌋ : ℚ)/scale p + 1/scale p
    rw [← add_div, le_div_iff₀ (scale_pos p)]
    exact (Int.lt_floor_add_one _).le
  linarith

/-- Upward endpoint rounding adds at most one mesh unit. -/
theorem up_le_add_mesh (p : ℕ) (x : ℚ) : up p x ≤ x + mesh p := by
  unfold up mesh
  apply (div_le_iff₀ (scale_pos p)).mpr
  rw [add_mul, div_mul_cancel₀ _ (ne_of_gt (scale_pos p))]
  exact (Int.ceil_lt_add_one (x*scale p)).le

/-- One recentering and outward-radius operation adds at most two mesh units. -/
theorem round_radius_le (p : ℕ) (b : Ball) :
    (round p b).radius ≤ b.radius + 2*mesh p := by
  change up p (b.radius+|b.center-down p b.center|) ≤ _
  have h := up_le_add_mesh p (b.radius+|b.center-down p b.center|)
  have hc := down_error_le_mesh p b.center
  linarith

end Komorebi.RoundedPosterior
