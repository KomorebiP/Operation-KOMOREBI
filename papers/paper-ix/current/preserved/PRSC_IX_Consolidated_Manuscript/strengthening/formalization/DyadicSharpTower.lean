module

public import DyadicReconstruction
public import Mathlib.NumberTheory.Bernoulli
public import Mathlib.RingTheory.PowerSeries.Derivative

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicSharpTower

open PowerSeries OddPower KomorebiPaperIX.Dyadic KomorebiPaperIX.DyadicSeries

def cothNormalized : PowerSeries ℚ := rescale 2 (bernoulliPowerSeries ℚ) + X

theorem expAt_derivative (a : ℚ) : derivative ℚ (expAt a) = C a * expAt a := by
  ext n
  rw [coeff_derivative, expAt_coeff, coeff_C_mul, expAt_coeff]
  rw [Nat.factorial_succ, pow_succ]
  push_cast
  field_simp

theorem sinh_derivative : derivative ℚ (sinhAt 1) = coshAt 1 := by
  simp only [sinhAt, coshAt, Derivation.leibniz, map_sub, derivative_C,
    smul_eq_mul, mul_zero, add_zero, expAt_derivative, map_one, map_neg]
  ring

theorem cosh_derivative : derivative ℚ (coshAt 1) = sinhAt 1 := by
  simp only [sinhAt, coshAt, Derivation.leibniz, map_add, derivative_C,
    smul_eq_mul, mul_zero, add_zero, expAt_derivative, map_one, map_neg]
  ring

theorem hyperbolic_identity : coshAt 1 ^ 2 - sinhAt 1 ^ 2 = 1 := by
  have hp : expAt 1 * expAt (-1) = 1 := by rw [expAt_mul]; norm_num
  have hc : C (1/2:ℚ) * C (1/2) * 4 = (1:PowerSeries ℚ) := by
    have h := congrArg (C (R:=ℚ)) (show (1/2:ℚ)*(1/2)*4=1 by norm_num)
    simpa only [map_mul, map_ofNat, map_one] using h
  unfold coshAt sinhAt
  calc
    _ = (C (1/2) * C (1/2) * 4) * (expAt 1 * expAt (-1)) := by ring
    _ = 1 := by rw [hp, hc, mul_one]

theorem coth_times_sinh : cothNormalized * sinhAt 1 = X * coshAt 1 := by
  have hb := congrArg (rescale (2:ℚ)) (bernoulliPowerSeries_mul_exp_sub_one ℚ)
  simp only [map_mul, map_sub, map_one, rescale_X] at hb
  change rescale 2 (bernoulliPowerSeries ℚ) * (expAt 2 - 1) = C 2 * X at hb
  have hp : expAt 2 * expAt (-1) = expAt 1 := by rw [expAt_mul]; norm_num
  have hh := congrArg (fun f : PowerSeries ℚ => f * expAt (-1)) hb
  unfold cothNormalized sinhAt coshAt
  simp only [mul_sub, sub_mul, mul_one, mul_assoc, hp] at hh
  calc
    _ = C (1/2) * (rescale 2 (bernoulliPowerSeries ℚ) * expAt 1 -
      rescale 2 (bernoulliPowerSeries ℚ) * expAt (-1)) +
      X * C (1/2) * (expAt 1 - expAt (-1)) := by ring
    _ = _ := by rw [hh]; norm_num only [map_ofNat]; ring

theorem inverse_eq_coth_derivative :
    inverseSeries = cothNormalized - X * derivative ℚ cothNormalized := by
  have hd := congrArg (derivative ℚ) coth_times_sinh
  simp only [Derivation.leibniz, sinh_derivative, cosh_derivative, derivative_X,
    smul_eq_mul, mul_one] at hd
  have hprod : (cothNormalized - X * derivative ℚ cothNormalized) * sinhAt 1 ^ 2 = X^2 := by
    linear_combination (sinhAt 1 + X * coshAt 1) * coth_times_sinh -
      X * sinhAt 1 * hd + X^2 * hyperbolic_identity
  have hnonzero : sinhAt 1 ^ 2 ≠ 0 := by
    intro h
    have hh := beta_original_generating_function
    rw [h, mul_zero] at hh
    exact (pow_ne_zero 2 PowerSeries.X_ne_zero) hh.symm
  exact mul_right_cancel₀ hnonzero (beta_original_generating_function.trans hprod.symm)

theorem beta_bernoulli (m : ℕ) (hm : 0 < m) :
    beta m = -(2^(2*m) * (2*(m:ℚ)-1) * bernoulli (2*m)) / (2*m).factorial := by
  have h := congrArg (coeff (2*m)) inverse_eq_coth_derivative
  rw [inverse_even_coefficient, map_sub] at h
  have hcoef : coeff (2*m) cothNormalized = 2^(2*m) * bernoulli (2*m) / (2*m).factorial := by
    simp [cothNormalized, coeff_rescale, bernoulliPowerSeries,
      coeff_X, show 2*m ≠ 1 by omega, mul_div_assoc]
  have hderiv : coeff (2*m) (X * derivative ℚ cothNormalized) =
      (2*m:ℚ) * coeff (2*m) cothNormalized := by
    obtain ⟨k,hk⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : 2*m ≠ 0)
    have hkq : (2*m:ℚ) = k+1 := by exact_mod_cast hk
    rw [hk, coeff_succ_X_mul, coeff_derivative, hkq]
    ring
  rw [hderiv, hcoef] at h
  rw [h]
  ring

def kappa (m : ℕ) : ℚ := beta m * 2^(2*m) * (2*m).factorial

theorem kappa_bernoulli (m : ℕ) (hm : 0 < m) :
    kappa m = -(2^(4*m) * (2*(m:ℚ)-1) * bernoulli (2*m)) := by
  rw [kappa, beta_bernoulli m hm]
  have hfac : ((2*m).factorial:ℚ) ≠ 0 := by positivity
  rw [show 4*m=2*m+2*m by omega, pow_add]
  field_simp

theorem odd_factor_valuation (m : ℕ) (hm : 0 < m) :
    padicValRat 2 (2*(m:ℚ)-1) = 0 := by
  have he : (2*(m:ℚ)-1) = ((2*m-1:ℕ):ℚ) := by
    rw [Nat.cast_sub (by omega)]; push_cast; rfl
  rw [he, padicValRat.of_nat, padicValNat.eq_zero_of_not_dvd (by omega)]
  rfl

theorem bernoulli_dyadic_valuation (m : ℕ) (hm : 0 < m) :
    padicValRat 2 (bernoulli (2*m)) = -1 :=
  Bernoulli.padicValRat_bernoulli hm (by norm_num)

theorem bernoulli_even_nonzero (m : ℕ) (hm : 0 < m) : bernoulli (2*m) ≠ 0 := by
  intro h
  have hv := bernoulli_dyadic_valuation m hm
  rw [h] at hv
  norm_num at hv

/-- Exact valuation of the genuine weighted inverse coefficient, for every positive depth. -/
theorem kappa_valuation (m : ℕ) (hm : 0 < m) :
    padicValRat 2 (kappa m) = 4*(m:ℤ)-1 := by
  have ho : 2*(m:ℚ)-1 ≠ 0 := by
    have hmq : (1:ℚ) ≤ m := by exact_mod_cast hm
    linarith
  have ht : padicValRat 2 (2:ℚ) = 1 := padicValRat.self (by decide : 1 < 2)
  rw [kappa_bernoulli m hm, padicValRat.neg,
    padicValRat.mul (mul_ne_zero (by positivity) ho) (bernoulli_even_nonzero m hm),
    padicValRat.mul (by positivity) ho, odd_factor_valuation m hm,
    bernoulli_dyadic_valuation m hm, padicValRat.pow, ht]
  push_cast
  ring

theorem kappa_nonzero (m : ℕ) (hm : 0 < m) : kappa m ≠ 0 := by
  intro h
  have hv := kappa_valuation m hm
  rw [h] at hv
  norm_num at hv
  omega

def kappaPadic (m : ℕ) : ℤ_[2] := betaPadic m * 2^(2*m) * (2*m).factorial

theorem kappaPadic_coe (m : ℕ) : (kappaPadic m : ℚ_[2]) = (kappa m : ℚ_[2]) := by
  simp only [kappaPadic, kappa, PadicInt.coe_mul, PadicInt.coe_pow, PadicInt.coe_natCast,
    betaPadic_coe, Rat.cast_mul, Rat.cast_pow, Rat.cast_ofNat, Rat.cast_natCast]
  rfl

theorem kappaPadic_norm (m : ℕ) (hm : 0 < m) :
    ‖kappaPadic m‖ = (2:ℝ)^(-(4*(m:ℤ)-1)) := by
  rw [PadicInt.norm_def, kappaPadic_coe, Padic.eq_padicNorm,
    padicNorm.eq_zpow_of_nonzero (kappa_nonzero m hm), kappa_valuation m hm]
  push_cast
  rfl

theorem kappaPadic_divisible (m : ℕ) (hm : 0 < m) :
    (2:ℤ_[2])^(4*m-1) ∣ kappaPadic m := by
  rw [← Ideal.mem_span_singleton]
  apply (PadicInt.norm_le_pow_iff_mem_span_pow (p:=2) (kappaPadic m) (4*m-1)).mp
  rw [kappaPadic_norm m hm]
  have hc : ((4*m-1:ℕ):ℤ) = 4*(m:ℤ)-1 := by
    rw [Nat.cast_sub (by omega)]; push_cast; rfl
  rw [hc]
  norm_num

open KomorebiPaperIX.DyadicReconstruction

theorem summand_kappa (n m : ℕ) :
    summand n m = kappa m * ((2*n).choose (2*m):ℚ) * sourceEven (n-m) := by
  rw [summand, Nat.descFactorial_eq_factorial_mul_choose, kappa]
  push_cast
  ring

theorem summandPadic_kappa (n m : ℕ) :
    summandPadic n m = kappaPadic m * ((2*n).choose (2*m):ℤ_[2]) * sourcePadic (n-m) := by
  rw [summandPadic, Nat.descFactorial_eq_factorial_mul_choose, kappaPadic]
  push_cast
  ring

/-- The exact dyadic coefficient valuation yields four powers of two per omitted level. -/
theorem dyadic_supercongruence_sharp (n M : ℕ) :
    (2:ℤ_[2])^(4*M+3) ∣ (EulerCoefficients.eulerEven n:ℤ_[2]) - truncationPadic n M := by
  rw [dyadic_reconstruction_padic, truncationPadic, ← OddEuler.filter_range_le]
  classical
  rw [← Finset.sum_filter_add_sum_filter_not (Finset.range (n+1)) (fun m => m ≤ M)
    (summandPadic n), add_sub_cancel_left]
  apply Finset.dvd_sum
  intro m hm
  obtain ⟨_, hm⟩ := Finset.mem_filter.mp hm
  have hpos : 0 < m := by omega
  have hpow : (2:ℤ_[2])^(4*M+3) ∣ (2:ℤ_[2])^(4*m-1) := pow_dvd_pow 2 (by omega)
  rw [summandPadic_kappa]
  exact dvd_mul_of_dvd_left (dvd_mul_of_dvd_left
    (hpow.trans (kappaPadic_divisible m hpos)) _) _

/-- The first omitted row has just one nonzero omitted term. -/
theorem first_omitted_error (M : ℕ) :
    (EulerCoefficients.eulerEven (M+1):ℚ) - truncation (M+1) M = kappa (M+1) := by
  rw [truncation, min_eq_left (by omega), dyadic_reconstruction, Finset.sum_range_succ,
    add_sub_cancel_left, summand_kappa, Nat.choose_self, Nat.sub_self]
  norm_num [sourceEven]

/-- Hence the exponent 4M+3 cannot be increased uniformly in the Euler row. -/
theorem first_omitted_error_valuation (M : ℕ) :
    padicValRat 2 ((EulerCoefficients.eulerEven (M+1):ℚ) - truncation (M+1) M) =
      4*(M:ℤ)+3 := by
  rw [first_omitted_error, kappa_valuation (M+1) (by omega)]
  push_cast
  ring

/-- Exact row-dependent precision of each nonzero positive-depth term. -/
theorem summand_valuation (n m : ℕ) (hm : 0 < m) (hmn : m ≤ n) :
    padicValRat 2 (summand n m) =
      4*(m:ℤ)-1 + (padicValNat 2 ((2*n).choose (2*m)):ℤ) := by
  have hc : (((2*n).choose (2*m)):ℚ) ≠ 0 := by
    exact_mod_cast Nat.ne_of_gt (Nat.choose_pos (by omega : 2*m ≤ 2*n))
  rw [summand_kappa,
    padicValRat.mul (mul_ne_zero (kappa_nonzero m hm) hc) (source_nonzero (n-m)),
    padicValRat.mul (kappa_nonzero m hm) hc,
    kappa_valuation m hm, source_valuation, padicValRat.of_nat, add_zero]

/-- The binomial factor contributes additional row-specific powers of two. -/
theorem summandPadic_divisible (n m : ℕ) (hm : 0 < m) :
    (2:ℤ_[2])^(4*m-1 + padicValNat 2 ((2*n).choose (2*m))) ∣ summandPadic n m := by
  have hc : (2:ℤ_[2])^(padicValNat 2 ((2*n).choose (2*m))) ∣
      (((2*n).choose (2*m)):ℤ_[2]) := by
    have hnat : 2^(padicValNat 2 ((2*n).choose (2*m))) ∣ (2*n).choose (2*m) :=
      (padicValNat_dvd_iff _ _).mpr (Or.inr le_rfl)
    obtain ⟨z,hz⟩ := hnat
    refine ⟨(z:ℤ_[2]), ?_⟩
    exact_mod_cast hz
  rw [summandPadic_kappa, pow_add]
  exact dvd_mul_of_dvd_left (mul_dvd_mul (kappaPadic_divisible m hm) hc) _

/-- Any lower bound on the explicit omitted row weights is a valid tail precision. -/
theorem dyadic_supercongruence_row_weight (n M L : ℕ)
    (hL : ∀ m, M < m → m ≤ n → L ≤ 4*m-1 + padicValNat 2 ((2*n).choose (2*m))) :
    (2:ℤ_[2])^L ∣ (EulerCoefficients.eulerEven n:ℤ_[2]) - truncationPadic n M := by
  rw [dyadic_reconstruction_padic, truncationPadic, ← OddEuler.filter_range_le]
  classical
  rw [← Finset.sum_filter_add_sum_filter_not (Finset.range (n+1)) (fun m => m ≤ M)
    (summandPadic n), add_sub_cancel_left]
  apply Finset.dvd_sum
  intro m hm
  obtain ⟨hn,hm⟩ := Finset.mem_filter.mp hm
  have hmn : m ≤ n := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hn
  have hmm : M < m := by omega
  exact (pow_dvd_pow (2:ℤ_[2]) (hL m hmm hmn)).trans
    (summandPadic_divisible n m (by omega))

end KomorebiPaperIX.DyadicSharpTower
