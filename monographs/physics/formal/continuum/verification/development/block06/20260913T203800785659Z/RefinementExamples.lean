module

public import KomorebiPhysics.RefinementAsymptotics
public import KomorebiPhysics.RefinementBounds

/-!
Literal dyadic formulas (4.63)--(4.67), exact polynomial witnesses and
hypothesis-sensitive tests. There are no floating-point computations here.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation
open KomorebiPhysics.RefinementAsymptotics
open KomorebiPhysics.RefinementBounds
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- Equations (4.63), (4.65), for vector-space-valued samples. -/
theorem dyadic_first (f : ℝ → E) (h : ℝ) :
    tower 2 f 1 h = 2 • f (h/2) - f h := by
  norm_num [tower]

/-- Equation (4.66). -/
theorem dyadic_second (f : ℝ → E) (h : ℝ) :
    tower 2 f 2 h = (1/3 : ℝ) • (8 • f (h/4) - 6 • f (h/2) + f h) := by
  norm_num [tower, div_div]
  module

/-- Equation (4.67). -/
theorem dyadic_third (f : ℝ → E) (h : ℝ) :
    tower 2 f 3 h = (1/21 : ℝ) •
      (64 • f (h/8) - 56 • f (h/4) + 14 • f (h/2) - f h) := by
  norm_num [tower, div_div]
  module

/-- One additional level, obtained from the same checked recursion. -/
theorem dyadic_fourth (f : ℝ → E) (h : ℝ) :
    tower 2 f 4 h = (1/315 : ℝ) •
      (1024 • f (h/16) - 960 • f (h/8) + 280 • f (h/4) - 30 • f (h/2) + f h) := by
  norm_num [tower, div_div]
  module

/-- The surviving quadratic coefficient has the source's negative half sign. -/
theorem quadratic_response (F a c h : ℝ) :
    tower 2 (fun x : ℝ => F+a*x+c*x^2) 1 h = F-c*h^2/2 := by
  norm_num [tower]
  ring

theorem cubic_response (F a b c h : ℝ) :
    tower 2 (fun x : ℝ => F+a*x+b*x^2+c*x^3) 2 h = F+c*h^3/8 := by
  norm_num [tower, div_div]
  ring

theorem quartic_response (F a b c d h : ℝ) :
    tower 2 (fun x : ℝ => F+a*x+b*x^2+c*x^3+d*x^4) 3 h = F-d*h^4/64 := by
  norm_num [tower, div_div]
  ring

/-- Literal analytic (4.64), from a cubic-order remainder of the original f. -/
theorem first_level_second_order (f : ℝ → ℝ) (F a c : ℝ)
    (hr : (fun h => f h-(F+a*h+c*h^2)) =O[𝓝[≠] 0] (fun h : ℝ => h^3)) :
    (fun h => tower 2 f 1 h-(F-c*h^2/2)) =O[𝓝[≠] 0] (fun h : ℝ => h^3) := by
  have ht := tower_isBigO (by norm_num : (2 : ℝ) ≠ 0) 1 3 hr
  exact ht.congr_left (fun h => by rw [tower_sub, quadratic_response])

/-- Non-dyadic example of the general refinement-ratio theorem. -/
theorem ternary_quadratic (h : ℝ) :
    tower 3 (fun x : ℝ => 5+2*x+3*x^2) 1 h = 5-h^2 := by
  norm_num [tower]
  ring

/-- Simultaneous observables use the same actual vector-valued tower. -/
theorem paired_observables (h : ℝ) :
    tower 2 (fun x : ℝ => (1+x+2*x^2, 3-2*x+x^3)) 2 h =
      (1, 3+h^3/8) := by
  ext <;> norm_num [tower, div_div] <;> ring

/-- The first surviving term is genuinely nonzero, not a sampled numerical fit. -/
theorem surviving_quadratic : tower 2 (fun h : ℝ => h^2) 1 1 = -1/2 := by
  norm_num [tower]

theorem surviving_cubic : tower 2 (fun h : ℝ => h^3) 2 1 = 1/8 := by
  norm_num [tower]

theorem surviving_quartic : tower 2 (fun h : ℝ => h^4) 3 1 = -1/64 := by
  norm_num [tower]

/-- Genuine asymptotic rejection, not just a finite-point mismatch. -/
theorem quadratic_not_third_order :
    ¬ (tower 2 (fun h : ℝ => h^2) 1 =O[𝓝[≠] 0] (fun h : ℝ => h^3)) := by
  exact tower_not_extra_order (by norm_num : (1 : ℝ) < 2) 1

/-- Lean's total division at the forbidden ratio does not preserve constants. -/
theorem unit_ratio_degenerate : tower 1 (fun _ : ℝ => (1 : ℝ)) 1 1 = 0 := by
  norm_num [tower]

theorem unit_ratio_denominator : (1 : ℝ)^(1 : ℕ)-1 = 0 := by norm_num

/-- Using weight 4 instead of 2 at level 1 fails to remove a linear error. -/
theorem wrong_first_weight : (4*(1/2 : ℝ)-1)/(4-1) = 1/3 := by norm_num

/-- Deliberately irregular bounded sample error. No smoothness is required by
our perturbation estimate, and this witness is not a physical time evolution. -/
def sampleNoise (h : ℝ) : ℝ := if h = 1/2 then 1 else -1

theorem sampleNoise_norm (h : ℝ) : ‖sampleNoise h‖ = 1 := by
  unfold sampleNoise
  split_ifs <;> norm_num

theorem sampleNoise_amplified : tower 2 sampleNoise 1 1 = 3 := by
  norm_num [tower, sampleNoise]

theorem sampleNoise_not_contractive : ‖tower 2 sampleNoise 1 1‖ > 1 := by
  rw [sampleNoise_amplified]
  norm_num

theorem noise_bound_first : amplification 2 0 1 = 3 := by norm_num [amplification]

theorem noise_bound_second : amplification 2 0 2 = 5 := by norm_num [amplification]

theorem noise_bound_third : amplification 2 0 3 = 45/7 := by norm_num [amplification]

theorem quadratic_remainder_bound : amplification 2 2 1 = 3/2 := by norm_num [amplification]

theorem cubic_remainder_bound : amplification 2 3 2 = 5/8 := by norm_num [amplification]

end KomorebiPhysics.RefinementExamples
