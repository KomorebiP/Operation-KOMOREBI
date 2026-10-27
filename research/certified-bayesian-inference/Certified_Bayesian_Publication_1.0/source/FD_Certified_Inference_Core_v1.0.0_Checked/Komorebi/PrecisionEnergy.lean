import Komorebi.PrecisionBudget

set_option autoImplicit false
namespace Komorebi.RoundedPosterior.Budget

/-- Coefficient of the linear-in-mesh inflation of an endpoint squared-energy bound. -/
def energyCoeff (q : Budget) : ℚ := 4*q.coeff*(q.mag+q.coeff)

theorem energyCoeff_nonneg (q : Budget) : 0 ≤ energyCoeff q := by
  have := q.mag_nonneg; have := q.coeff_nonneg
  unfold energyCoeff; positivity

theorem exact_energy_le {p : ℕ} {b : Ball} {x : ℚ} {q : Budget} (h : Bounds p b x q) :
    x^2 ≤ q.mag^2 := by
  have hh := mul_self_le_mul_self (abs_nonneg x) h.1
  simpa only [← pow_two, sq_abs] using hh

/-- The actual retained endpoint-energy expression approaches the exact squared value. -/
theorem energy_upper_le {p : ℕ} {b : Ball} {x : ℚ} {q : Budget} (h : Bounds p b x q) :
    energyUpper b ≤ x^2+energyCoeff q*mesh p := by
  have hc : |b.center| ≤ |x|+b.radius := by
    have hab : |b.center-x| ≤ b.radius := by
      rw [abs_sub_comm]
      exact h.2.1
    calc
      |b.center| = |x+(b.center-x)| := by congr 1; ring
      _ ≤ |x|+|b.center-x| := abs_add_le _ _
      _ ≤ |x|+b.radius := add_le_add le_rfl hab
  have hcr : |b.center|+b.radius ≤ |x|+2*(q.coeff*mesh p) := by
    linarith only [hc,h.2.2]
  have hp := mul_self_le_mul_self
    (add_nonneg (abs_nonneg b.center) (radius_nonneg h.2.1)) hcr
  have hr : q.coeff*mesh p ≤ q.coeff := by
    simpa using mul_le_mul_of_nonneg_left (mesh_le_one p) q.coeff_nonneg
  have hrr := mul_le_mul_of_nonneg_left hr (mul_nonneg q.coeff_nonneg (mesh_pos p).le)
  have hcross := mul_le_mul_of_nonneg_right h.1 (mul_nonneg q.coeff_nonneg (mesh_pos p).le)
  have hx := sq_abs x
  unfold energyUpper energyCoeff
  nlinarith only [hp,hrr,hcross,hx]

end Komorebi.RoundedPosterior.Budget
