module
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
public import Mathlib.Analysis.SpecialFunctions.Complex.LogDeriv
public import Mathlib.Analysis.Complex.RealDeriv
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FieldSimp
@[expose] public section
open MeasureTheory intervalIntegral
namespace H12.PhaseRegulator

/-- Integration of a linear weight times a genuine second derivative.
The derivative hypotheses are analytic, not field identities. -/
theorem integral_linear_second
    (f f1 f2 : ℝ → ℂ) (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x) (hc : Continuous f2)
    (a b c : ℝ) :
    (∫ x in a..b, ((x-c : ℝ) : ℂ) * f2 x) =
      ((b-c : ℝ) : ℂ) * f1 b - f b -
      (((a-c : ℝ) : ℂ) * f1 a - f a) := by
  apply intervalIntegral.integral_eq_sub_of_hasDerivAt
  · intro x _
    have hd := ((((hasDerivAt_id x).ofReal_comp).sub_const (c : ℂ)).mul (hf1 x)).sub (hf x)
    convert hd using 1
    · ext y
      simp
    · simp
  · exact ((Complex.continuous_ofReal.comp (continuous_id.sub continuous_const)).mul hc).intervalIntegrable a b

/-- The two-segment conductor-three Green functional. -/
noncomputable def regulator3 (g : ℝ → ℂ) : ℂ :=
  -2 * (∫ x in (0:ℝ)..(1/3:ℝ), (x : ℂ) * g x) +
    (∫ x in (1/3:ℝ)..(1:ℝ), ((x-1 : ℝ) : ℂ) * g x)

theorem regulator3_endpoint
    (f f1 f2 : ℝ → ℂ) (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x) (hc : Continuous f2) :
    regulator3 f2 = 3*f (1/3) - 2*f 0 - f 1 := by
  have h0 := integral_linear_second f f1 f2 hf hf1 hc 0 (1/3) 0
  have h1 := integral_linear_second f f1 f2 hf hf1 hc (1/3) 1 1
  simp only [sub_zero] at h0
  unfold regulator3
  rw [h0,h1]
  push_cast
  ring


/-- Exponentiating removes all choices of logarithm at the endpoints. -/
theorem regulator3_exponential_endpoints
    (f f1 f2 : ℝ → ℂ) (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x) (hc : Continuous f2) :
    Complex.exp (regulator3 f2) * (Complex.exp (f 0))^2 * Complex.exp (f 1) =
      (Complex.exp (f (1/3)))^3 := by
  rw [regulator3_endpoint f f1 f2 hf hf1 hc]
  rw [← Complex.exp_nat_mul (f 0) 2, ← Complex.exp_add, ← Complex.exp_add,
    ← Complex.exp_nat_mul (f (1/3)) 3]
  congr 1
  push_cast
  ring

/-- Periodic exponentials require no assumption that the logarithm is periodic. -/
theorem regulator3_periodic_cube
    (f f1 f2 : ℝ → ℂ) (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x) (hc : Continuous f2)
    (hp : Complex.exp (f 1) = Complex.exp (f 0)) :
    Complex.exp (regulator3 f2) * (Complex.exp (f 0))^3 =
      (Complex.exp (f (1/3)))^3 := by
  have hh := regulator3_exponential_endpoints f f1 f2 hf hf1 hc
  rw [hp] at hh
  simpa only [pow_succ, mul_assoc] using hh

/-- An actual periodic logarithm fixes the remaining winding. -/
theorem regulator3_zero_winding
    (f f1 f2 : ℝ → ℂ) (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x) (hc : Continuous f2)
    (hp : f 1 = f 0) :
    regulator3 f2 = 3 * (f (1/3) - f 0) := by
  rw [regulator3_endpoint f f1 f2 hf hf1 hc, hp]
  ring

/-- Genuine analytic comparison: both second derivatives and endpoint
normalizations are explicit data, not a presumed gamma identity. -/
theorem same_second_derivative_same_normalized_cube
    (f f1 g g1 q : ℝ → ℂ)
    (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (q x) x)
    (hg : ∀ x, HasDerivAt g (g1 x) x)
    (hg1 : ∀ x, HasDerivAt g1 (q x) x)
    (hc : Continuous q)
    (hpf : Complex.exp (f 1) = Complex.exp (f 0))
    (hpg : Complex.exp (g 1) = Complex.exp (g 0))
    (h0 : Complex.exp (f 0) = Complex.exp (g 0)) :
    (Complex.exp (f (1/3)))^3 = (Complex.exp (g (1/3)))^3 := by
  rw [← regulator3_periodic_cube f f1 q hf hf1 hc hpf,
      ← regulator3_periodic_cube g g1 q hg hg1 hc hpg, h0]

/-- Only equality of the two Green integrals is needed, not equality
of the functions being integrated. -/
theorem same_regulator_same_normalized_cube
    (f f1 f2 g g1 g2 : ℝ → ℂ)
    (hf : ∀ x, HasDerivAt f (f1 x) x)
    (hf1 : ∀ x, HasDerivAt f1 (f2 x) x)
    (hg : ∀ x, HasDerivAt g (g1 x) x)
    (hg1 : ∀ x, HasDerivAt g1 (g2 x) x)
    (hcf : Continuous f2) (hcg : Continuous g2)
    (hpf : Complex.exp (f 1) = Complex.exp (f 0))
    (hpg : Complex.exp (g 1) = Complex.exp (g 0))
    (h0 : Complex.exp (f 0) = Complex.exp (g 0))
    (hr : Complex.exp (regulator3 f2) = Complex.exp (regulator3 g2)) :
    (Complex.exp (f (1/3)))^3 = (Complex.exp (g (1/3)))^3 := by
  rw [← regulator3_periodic_cube f f1 f2 hf hf1 hcf hpf,
      ← regulator3_periodic_cube g g1 g2 hg hg1 hcg hpg, hr, h0]

end H12.PhaseRegulator

