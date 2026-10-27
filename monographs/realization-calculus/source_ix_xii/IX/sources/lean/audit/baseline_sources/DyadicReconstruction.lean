module

public import DyadicSeries
public import OddEulerReconstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicReconstruction

open PowerSeries EulerCoefficients KomorebiPaperIX.Dyadic KomorebiPaperIX.DyadicSeries

/-- The literal weighted summand; beta uses ordinary, not exponential, coefficients. -/
def summand (n m : ℕ) : ℚ :=
  beta m * 2^(2*m) * ((2*n).descFactorial (2*m) : ℚ) * sourceEven (n-m)

/-- The falling factorial is the factorial quotient in the manuscript. -/
theorem falling_factorial_fraction (n k : ℕ) (h : k ≤ n) :
    (n.descFactorial k : ℚ) = (n.factorial : ℚ) / (n-k).factorial := by
  apply (eq_div_iff (by positivity)).mpr
  rw [mul_comm]
  exact_mod_cast Nat.factorial_mul_descFactorial h

/-- Theorem 5.3, derived from the exact source and inverse series rather than supplied as a premise. -/
theorem dyadic_reconstruction (n : ℕ) :
    (eulerEven n : ℚ) = ∑ m ∈ Finset.range (n+1), summand n m := by
  have hs := congrArg (fun f => EGF.decode f (2*n)) dyadic_reconstruction_series
  have hp := EGF.egf_product (EGF.decode (rescale (2:ℚ) inverseSeries))
    (EGF.decode DyadicSeries.sourceSeries) (2*n)
  simp only [EGF.encode_decode] at hp
  have he : EGF.decode OddPower.sech (2*n) = (eulerEven n : ℚ) := by
    rw [← euler_egf, EGF.decode_encode, euler_even]
  rw [hp,he] at hs
  rw [OddEuler.sum_even_terms _ (fun m => by
    simp [EGF.decode, coeff_rescale, inverse_odd_coefficient])] at hs
  rw [← hs]
  apply Finset.sum_congr rfl
  intro m hm
  simp only [EGF.decode, coeff_rescale, inverse_even_coefficient,
    ← Nat.mul_sub_left_distrib, source_even_coefficient]
  unfold summand
  rw [Nat.descFactorial_eq_factorial_mul_choose]
  push_cast
  field_simp

/-- Ordinary row-degree form, with evenness explicit instead of relying on rounded division. -/
theorem dyadic_reconstruction_even_degree (n : ℕ) (hn : Even n) :
    (euler n : ℚ) = ∑ m ∈ Finset.range (n/2+1),
      beta m * 2^(2*m) * (n.descFactorial (2*m) : ℚ) * sourceEven (n/2-m) := by
  obtain ⟨r,hr⟩ := even_iff_two_dvd.mp hn
  subst n
  simpa only [euler_even, Nat.mul_div_cancel_left _ (by decide : 0 < 2), summand]
    using dyadic_reconstruction r

/-- The finite approximation includes precisely min(M,n)+1 terms. -/
def truncation (n M : ℕ) : ℚ := ∑ m ∈ Finset.range (min M n+1), summand n m

theorem full_depth_exact (n M : ℕ) (h : n ≤ M) : truncation n M = (eulerEven n : ℚ) := by
  rw [truncation, min_eq_right h, dyadic_reconstruction]

/-- Every term embeds into the actual completed integer ring. -/
def summandPadic (n m : ℕ) : ℤ_[2] :=
  betaPadic m * 2^(2*m) * ((2*n).descFactorial (2*m) : ℤ_[2]) * sourcePadic (n-m)

theorem summandPadic_coe (n m : ℕ) : (summandPadic n m : ℚ_[2]) = (summand n m : ℚ_[2]) := by
  simp only [summandPadic, summand, PadicInt.coe_mul, PadicInt.coe_pow,
    PadicInt.coe_natCast, betaPadic_coe, sourcePadic_coe,
    Rat.cast_mul, Rat.cast_pow, Rat.cast_ofNat, Rat.cast_natCast]
  rfl

def truncationPadic (n M : ℕ) : ℤ_[2] :=
  ∑ m ∈ Finset.range (min M n+1), summandPadic n m

theorem truncationPadic_coe (n M : ℕ) :
    (truncationPadic n M : ℚ_[2]) = (truncation n M : ℚ_[2]) := by
  simp [truncationPadic, truncation, summandPadic_coe]

/-- The exact rational identity is transported to Z_2 using the proved integrality witnesses. -/
theorem dyadic_reconstruction_padic (n : ℕ) :
    (eulerEven n : ℤ_[2]) = ∑ m ∈ Finset.range (n+1), summandPadic n m := by
  apply PadicInt.ext
  simp only [PadicInt.coe_intCast, PadicInt.coe_sum, summandPadic_coe]
  exact_mod_cast dyadic_reconstruction n

/-- Corollary 5.4: actual divisibility in Z_2, not vacuous divisibility in the field Q_2. -/
theorem dyadic_supercongruence (n M : ℕ) :
    (2:ℤ_[2])^(2*M+2) ∣ (eulerEven n : ℤ_[2]) - truncationPadic n M := by
  rw [dyadic_reconstruction_padic]
  have h := Filtered.even_weight_tail (2:ℤ_[2])
    (fun m => betaPadic m * ((2*n).descFactorial (2*m) : ℤ_[2]) * sourcePadic (n-m)) n M
  rw [OddEuler.filter_range_le] at h
  simpa only [truncationPadic, summandPadic, mul_assoc, mul_left_comm, mul_comm] using h

theorem full_depth_exact_padic (n M : ℕ) (h : n ≤ M) :
    truncationPadic n M = (eulerEven n : ℤ_[2]) := by
  rw [truncationPadic, min_eq_right h, dyadic_reconstruction_padic]

/-- Equivalent rational statement: the normalized error really is 2-adically integral. -/
theorem normalized_error_integral (n M : ℕ) :
    ((eulerEven n : ℚ) - truncation n M) / (2:ℚ)^(2*M+2) ∈ integralRationals := by
  rw [integral_iff_completed_norm]
  obtain ⟨z,hz⟩ := dyadic_supercongruence n M
  have hh := congrArg (fun x : ℤ_[2] => (x : ℚ_[2])) hz
  simp only [PadicInt.coe_sub, PadicInt.coe_intCast, truncationPadic_coe,
    PadicInt.coe_mul, PadicInt.coe_pow] at hh
  have hc : ((((eulerEven n : ℚ)-truncation n M)/(2:ℚ)^(2*M+2) : ℚ) : ℚ_[2]) = z := by
    push_cast
    rw [hh]
    have htwo : ((2:ℤ_[2]):ℚ_[2]) = (2:ℚ_[2]) := rfl
    rw [htwo]
    field_simp
  rw [hc]
  exact z.property

end KomorebiPaperIX.DyadicReconstruction
