module
public import Euler.EulerKernel
public import Mathlib.RingTheory.PowerSeries.Exp
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- The rational exponential series with its argument scaled by a. -/
def formalExp (a : ℚ) : PowerSeries ℚ := rescale a (exp ℚ)

lemma formalExp_coeff (a : ℚ) (n : ℕ) : coeff n (formalExp a) = a^n / n.factorial := by
  simp [formalExp, coeff_rescale, div_eq_mul_inv]

@[simp] lemma formalExp_zero : formalExp 0 = 1 := by
  simp [formalExp]

lemma formalExp_mul (a b : ℚ) : formalExp a * formalExp b = formalExp (a+b) :=
  exp_mul_exp_eq_exp_add a b

lemma formalExp_neg_mul (a : ℚ) : formalExp (-a)*formalExp a=1 := by
  rw [formalExp_mul]
  simp

lemma formalExp_derivative (a : ℚ) : d⁄dX ℚ (formalExp a) = C a * formalExp a := by
  ext n
  rw [coeff_derivative, formalExp_coeff, coeff_C_mul, formalExp_coeff]
  simp only [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, pow_succ]
  have h : (n:ℚ)+1≠0 := by positivity
  field_simp

/-- The scaled Bernoulli EGF, before taking its Euler differential operator. -/
def scaledBernoulli : PowerSeries ℚ := rescale 4 (bernoulliPowerSeries ℚ)

lemma scaledBernoulli_coeff (n : ℕ) :
    coeff n scaledBernoulli = (4:ℚ)^n * bernoulli n / n.factorial := by
  simp [scaledBernoulli, bernoulliPowerSeries, coeff_rescale, div_eq_mul_inv, mul_assoc]

lemma scaledBernoulli_identity :
    scaledBernoulli * (formalExp 4 - 1) = 4 * X := by
  have h := congrArg (rescale (4:ℚ)) (bernoulliPowerSeries_mul_exp_sub_one ℚ)
  have hc : (C (4:ℚ):PowerSeries ℚ) = 4 := by norm_cast
  simpa [scaledBernoulli, formalExp, rescale_X, hc] using h

lemma scaledBernoulli_differential_identity :
    (d⁄dX ℚ scaledBernoulli)*(formalExp 4-1) +
      4*scaledBernoulli*formalExp 4 = 4 := by
  have h := congrArg (d⁄dX ℚ) scaledBernoulli_identity
  simp only [Derivation.leibniz, map_sub, derivative_one, sub_zero, formalExp_derivative,
    derivative_X] at h
  have hc : (C (4:ℚ):PowerSeries ℚ) = 4 := by norm_cast
  have hd4 : d⁄dX ℚ (4:PowerSeries ℚ) = 0 := by rw [← hc, derivative_C]
  simp only [hc, hd4, mul_one, smul_eq_mul] at h
  convert h using 1 <;> ring

/-- Rational EGF for the kappa coefficients, defined from the Bernoulli EGF. -/
def formalKernel : PowerSeries ℚ := scaledBernoulli - X*(d⁄dX ℚ scaledBernoulli)

lemma formalKernel_cleared_identity :
    formalKernel*(formalExp 4-1)^2 = 16*X^2*formalExp 4 := by
  have h := scaledBernoulli_identity
  have hd := scaledBernoulli_differential_identity
  have hd' : (d⁄dX ℚ scaledBernoulli)*(formalExp 4-1) =
      4-4*scaledBernoulli*formalExp 4 := eq_sub_of_add_eq hd
  calc
    _ = (scaledBernoulli*(formalExp 4-1))*(formalExp 4-1) -
      X*((d⁄dX ℚ scaledBernoulli)*(formalExp 4-1))*(formalExp 4-1) := by
        unfold formalKernel; ring
    _ = (4*X)*(formalExp 4-1)-X*(4-4*scaledBernoulli*formalExp 4)*(formalExp 4-1) := by
        rw [h,hd']
    _ = 4*X*(scaledBernoulli*(formalExp 4-1))*formalExp 4 := by ring
    _ = _ := by rw [h]; ring

end Komorebi.Euler
