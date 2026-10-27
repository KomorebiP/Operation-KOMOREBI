/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FiniteAnalytic
import Mathlib.Analysis.SpecialFunctions.ExpDeriv

/-!
# Pointwise entire realization

Finite exponential sums are entire. Their absolutely convergent Taylor series
are identified with the existing formal transfer and signed sections below.
The definitions do not assume any convergence or differential equation.
-/

namespace Komorebi.PaperIV
open scoped PowerSeries
noncomputable section

/-- The kth derivative expression of a finite exponential sum. -/
def exponentialSumJet (N : ℕ) (w a : ℕ → ℂ) (k : ℕ) (z : ℂ) : ℂ :=
  ∑ l ∈ Finset.range N, w l * a l ^ k * Complex.exp (a l * z)

theorem analyticAt_exponentialSumJet (N : ℕ) (w a : ℕ → ℂ) (k : ℕ) (z : ℂ) :
    AnalyticAt ℂ (exponentialSumJet N w a k) z := by
  unfold exponentialSumJet
  fun_prop

theorem hasDerivAt_exponentialSumJet (N : ℕ) (w a : ℕ → ℂ) (k : ℕ) (z : ℂ) :
    HasDerivAt (exponentialSumJet N w a k) (exponentialSumJet N w a (k + 1) z) z := by
  have h := HasDerivAt.fun_sum (u := Finset.range N) (fun l _ =>
    (((hasDerivAt_id z).const_mul (a l)).cexp).const_mul (w l * a l ^ k))
  have hd : (∑ l ∈ Finset.range N,
      w l * a l ^ k * (Complex.exp (a l * id z) * (a l * 1))) =
      exponentialSumJet N w a (k + 1) z := by
    apply Finset.sum_congr rfl
    intro l _
    simp only [pow_succ, id_eq]
    ring
  rw [hd] at h
  convert h using 1 <;> rfl

theorem iteratedDeriv_exponentialSum (N : ℕ) (w a : ℕ → ℂ) (k : ℕ) :
    deriv^[k] (exponentialSumJet N w a 0) = exponentialSumJet N w a k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    rw [Function.iterate_succ_apply', ih]
    exact funext (fun z => (hasDerivAt_exponentialSumJet N w a k z).deriv)

/-- A finite exponential sum whose exponents satisfy `a^N = c` solves the
corresponding scalar constant-coefficient ODE everywhere. -/
theorem exponentialSum_ode (N : ℕ) (w a : ℕ → ℂ) (c : ℂ)
    (ha : ∀ l ∈ Finset.range N, a l ^ N = c) (z : ℂ) :
    deriv^[N] (exponentialSumJet N w a 0) z =
      c * exponentialSumJet N w a 0 z := by
  rw [iteratedDeriv_exponentialSum, exponentialSumJet, exponentialSumJet,
    Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro l hl
  rw [ha l hl]
  simp only [pow_zero]
  ring

/-- The pointwise Fourier average for the transfer section. -/
def entireTransfer (N j : ℕ) (omega lambda : ℂ) (z : ℂ) : ℂ :=
  (N : ℂ)⁻¹ *
    ∑ l ∈ Finset.range N,
      ((omega ^ j)⁻¹) ^ l * Complex.exp ((lambda * omega ^ l) * z)

theorem analyticAt_entireTransfer (N j : ℕ) (omega lambda z : ℂ) :
    AnalyticAt ℂ (entireTransfer N j omega lambda) z := by
  unfold entireTransfer
  fun_prop

theorem entireTransfer_eq_exponentialSum (N j : ℕ) (omega lambda : ℂ) :
    entireTransfer N j omega lambda =
      exponentialSumJet N (fun l => (N : ℂ)⁻¹ * ((omega ^ j)⁻¹) ^ l)
        (fun l => lambda * omega ^ l) 0 := by
  funext z
  simp [entireTransfer, exponentialSumJet, Finset.mul_sum, mul_assoc]

/-- Convergence to the pointwise function of exactly the formal coefficients
already used in the root-filter formalization. -/
theorem hasSum_finiteRootAverage (N j : ℕ) (omega lambda z : ℂ) :
    HasSum (fun n =>
      PowerSeries.coeff n (finiteRootAverage N j omega
        (PowerSeries.rescale lambda (PowerSeries.exp ℂ))) * z ^ n)
      (entireTransfer N j omega lambda z) := by
  have h := (hasSum_sum (s := Finset.range N) (fun l _ =>
    (NormedSpace.expSeries_div_hasSum_exp ((lambda * omega ^ l) * z)).mul_left
      (((omega ^ j)⁻¹) ^ l))).mul_left ((N : ℂ)⁻¹)
  rw [← Complex.exp_eq_exp_ℂ] at h
  apply h.congr_fun
  intro n
  simp only [finiteRootAverage, PowerSeries.coeff_C_mul, map_sum,
    PowerSeries.coeff_rescale, PowerSeries.coeff_exp]
  rw [mul_assoc, Finset.sum_mul]
  congr 1
  apply Finset.sum_congr rfl
  intro l _
  simp [mul_pow]
  ring

/-- The analytic transfer function is the sum of its formal transfer series. -/
theorem hasSum_entireTransfer {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    HasSum (fun n => PowerSeries.coeff n (transferSection N j lambda) * z ^ n)
      (entireTransfer N j omega lambda z) := by
  simpa only [finiteRootAverage_rescale_exp_eq_transferSection hN hj homega]
    using hasSum_finiteRootAverage N j omega lambda z

theorem entireTransfer_eq_tsum {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    entireTransfer N j omega lambda z =
      ∑' n, PowerSeries.coeff n (transferSection N j lambda) * z ^ n :=
  (hasSum_entireTransfer hN hj homega lambda z).tsum_eq.symm

/-- Independence of the chosen primitive root follows from the actual series. -/
theorem entireTransfer_independent_root {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega eta : ℂ} (homega : IsPrimitiveRoot omega N)
    (heta : IsPrimitiveRoot eta N) (lambda z : ℂ) :
    entireTransfer N j omega lambda z = entireTransfer N j eta lambda z := by
  exact (hasSum_entireTransfer hN hj homega lambda z).unique
    (hasSum_entireTransfer hN hj heta lambda z)

theorem entireTransfer_ode {N : ℕ} {omega : ℂ}
    (homega : IsPrimitiveRoot omega N) (j : ℕ) (lambda z : ℂ) :
    deriv^[N] (entireTransfer N j omega lambda) z =
      lambda ^ N * entireTransfer N j omega lambda z := by
  rw [entireTransfer_eq_exponentialSum]
  apply exponentialSum_ode
  intro l _
  rw [mul_pow, ← pow_mul, Nat.mul_comm l N, pow_mul, homega.pow_eq_one]
  simp

/-- Pointwise signed section using any chosen Nth root of minus one. -/
def entireSigned (N j : ℕ) (omega rho : ℂ) (z : ℂ) : ℂ :=
  (rho ^ j)⁻¹ * entireTransfer N j omega rho z

theorem analyticAt_entireSigned (N j : ℕ) (omega rho z : ℂ) :
    AnalyticAt ℂ (entireSigned N j omega rho) z := by
  exact analyticAt_const.mul (analyticAt_entireTransfer N j omega rho z)

/-- Exact entire realization of the signed formal series. -/
theorem hasSum_entireSigned {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) :
    HasSum (fun n => PowerSeries.coeff n (signedSection (R := ℂ) N j) * z ^ n)
      (entireSigned N j omega rho z) := by
  have h := (hasSum_entireTransfer hN hj homega rho z).mul_left ((rho ^ j)⁻¹)
  rw [signedSection_eq_inv_pow_mul_transferSection hN hj hrho]
  simpa only [entireSigned, PowerSeries.coeff_C_mul, mul_assoc] using h

theorem entireSigned_eq_tsum {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    (z : ℂ) :
    entireSigned N j omega rho z =
      ∑' n, PowerSeries.coeff n (signedSection (R := ℂ) N j) * z ^ n :=
  (hasSum_entireSigned hN hj homega hrho z).tsum_eq.symm

theorem entireSigned_independent_roots {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega eta rho sigma : ℂ} (homega : IsPrimitiveRoot omega N)
    (heta : IsPrimitiveRoot eta N) (hrho : rho ^ N = -1) (hsigma : sigma ^ N = -1)
    (z : ℂ) :
    entireSigned N j omega rho z = entireSigned N j eta sigma z :=
  (hasSum_entireSigned hN hj homega hrho z).unique
    (hasSum_entireSigned hN hj heta hsigma z)

/-- The denominator's pointwise finite exponential representation. -/
theorem entireSigned_zero_eq_average (N : ℕ) (omega rho z : ℂ) :
    entireSigned N 0 omega rho z =
      (N : ℂ)⁻¹ * ∑ l ∈ Finset.range N, Complex.exp ((rho * omega ^ l) * z) := by
  simp [entireSigned, entireTransfer]

/-- Exact derivative/Taylor-coefficient correspondence at the origin. -/
theorem entireTransfer_derivative_at_zero {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (lambda : ℂ) (k : ℕ) :
    deriv^[k] (entireTransfer N j omega lambda) 0 =
      (k.factorial : ℂ) * PowerSeries.coeff k (transferSection N j lambda) := by
  rw [entireTransfer_eq_exponentialSum, iteratedDeriv_exponentialSum]
  rw [← finiteRootAverage_rescale_exp_eq_transferSection hN hj homega lambda]
  simp only [exponentialSumJet, mul_zero, Complex.exp_zero, mul_one,
    finiteRootAverage, PowerSeries.coeff_C_mul, map_sum, PowerSeries.coeff_rescale,
    PowerSeries.coeff_exp]
  rw [Finset.mul_sum, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro l _
  simp only [mul_pow, map_inv₀, map_natCast, one_div]
  have hk : (k.factorial : ℂ) ≠ 0 := by exact_mod_cast k.factorial_ne_zero
  field_simp

/-- The initial derivative matrix is genuinely diagonal for the entire functions. -/
theorem entireTransfer_initial_data {N j k : ℕ} (hN : 0 < N)
    (hj : j < N) (hk : k < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N)
    (lambda : ℂ) :
    deriv^[k] (entireTransfer N j omega lambda) 0 =
      if k = j then lambda ^ j else 0 := by
  rw [entireTransfer_derivative_at_zero hN hj homega, coeff_transferSection]
  have hfac : (k.factorial : ℂ) ≠ 0 := by exact_mod_cast k.factorial_ne_zero
  by_cases h : k = j
  · subst k
    simp [transferSectionCoeff, Nat.mod_eq_of_lt hk]
    field_simp
  · simp [transferSectionCoeff, Nat.mod_eq_of_lt hk, h]

theorem entireSigned_eq_exponentialSum (N j : ℕ) (omega rho : ℂ) :
    entireSigned N j omega rho =
      exponentialSumJet N
        (fun l => (rho ^ j)⁻¹ * (N : ℂ)⁻¹ * ((omega ^ j)⁻¹) ^ l)
        (fun l => rho * omega ^ l) 0 := by
  funext z
  simp [entireSigned, entireTransfer, exponentialSumJet, Finset.mul_sum, mul_assoc]

theorem entireSigned_ode {N : ℕ} {omega rho : ℂ}
    (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) (j : ℕ) (z : ℂ) :
    deriv^[N] (entireSigned N j omega rho) z = -entireSigned N j omega rho z := by
  rw [entireSigned_eq_exponentialSum]
  have h := exponentialSum_ode N
    (fun l => (rho ^ j)⁻¹ * (N : ℂ)⁻¹ * ((omega ^ j)⁻¹) ^ l)
    (fun l => rho * omega ^ l) (-1) (by
      intro l _
      rw [mul_pow, ← pow_mul, Nat.mul_comm l N, pow_mul, homega.pow_eq_one, hrho]
      simp) z
  simpa using h

theorem entireSigned_derivative_eq_scaled_transfer (N j k : ℕ) (omega rho z : ℂ) :
    deriv^[k] (entireSigned N j omega rho) z =
      (rho ^ j)⁻¹ * deriv^[k] (entireTransfer N j omega rho) z := by
  rw [entireSigned_eq_exponentialSum, entireTransfer_eq_exponentialSum,
    iteratedDeriv_exponentialSum, iteratedDeriv_exponentialSum]
  simp [exponentialSumJet, Finset.mul_sum, mul_assoc]

theorem entireSigned_initial_data {N j k : ℕ} (hN : 0 < N)
    (hj : j < N) (hk : k < N) {omega rho : ℂ} (homega : IsPrimitiveRoot omega N)
    (hrho : rho ^ N = -1) :
    deriv^[k] (entireSigned N j omega rho) 0 = if k = j then 1 else 0 := by
  have hr : rho ≠ 0 := by
    intro h
    simp [h, hN.ne'] at hrho
  rw [entireSigned_derivative_eq_scaled_transfer,
    entireTransfer_initial_data hN hj hk homega]
  split_ifs <;> simp [pow_ne_zero j hr]

end
end Komorebi.PaperIV
