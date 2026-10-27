module

public import OddPowerSeries
public import ExponentialSection

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.EulerCoefficients

open PowerSeries OddPower

def eulerEven (n : ℕ) : ℤ := (Congruential.coeff 2 0 n).num

def euler (n : ℕ) : ℤ := if Even n then eulerEven (n/2) else 0

theorem clearing_even_one (n : ℕ) : Congruential.clearing 2 0 n = 1 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Congruential.clearing, Congruential.row, ih]

theorem eulerEven_cast (n : ℕ) : (eulerEven n : ℚ) = Congruential.coeff 2 0 n := by
  have hi := Congruential.universal_denominator_clearing 2 0 n
  rw [clearing_even_one] at hi
  simp only [Int.cast_one, one_mul] at hi
  obtain ⟨z, hz⟩ := hi
  simp [eulerEven, hz]

@[simp] theorem euler_even (n : ℕ) : euler (2*n) = eulerEven n := by simp [euler]

@[simp] theorem euler_odd (n : ℕ) : euler (2*n+1) = 0 := by simp [euler]

@[simp] theorem euler_zero : euler 0 = 1 := by
  simp [euler, eulerEven]

/-- The cosine-hyperbolic series has literal even factorial coefficients. -/
theorem cosh_coeff (a : ℚ) (n : ℕ) :
    coeff n (coshAt a) = if Even n then a^n / n.factorial else 0 := by
  simp only [coshAt, coeff_C_mul, map_add, expAt_coeff]
  by_cases hn : Even n
  · rw [ite_eq_left hn, hn.neg_pow]; ring
  · rw [ite_eq_right hn, (Nat.not_even_iff_odd.mp hn).neg_pow]; ring

theorem original_even_section : ExponentialSection.originalSection 2 0 = coshAt 1 := by
  ext n
  rw [cosh_coeff]
  simp only [ExponentialSection.originalSection, coeff_mk, one_pow, Nat.even_iff]

theorem euler_series_expansion :
    EGF.encode (fun n => (euler n : ℚ)) =
      ExponentialSection.expandedPacket 2 (by decide) 0 := by
  ext n
  rw [EGF.encode_coeff]
  simp only [ExponentialSection.expandedPacket, coeff_expand, Congruential.packet_series_coeff]
  by_cases hn : Even n
  · have hd : 2 ∣ n := even_iff_two_dvd.mp hn
    rw [ite_eq_left hd, euler, ite_eq_left hn, eulerEven_cast, Nat.mul_div_cancel' hd]
  · rw [ite_eq_right (fun h => hn (even_iff_two_dvd.mpr h)), euler, ite_eq_right hn]
    simp

/-- Establishes that the integer sequence is the actual sech EGF, rather than naming it so. -/
theorem euler_egf : EGF.encode (fun n => (euler n : ℚ)) = sech := by
  rw [euler_series_expansion]
  apply (PowerSeries.eq_inv_iff_mul_eq_one (by simp)).mpr
  have h := ExponentialSection.original_section_inverse_identity 2 (by decide) 0 (by decide)
  rw [original_even_section] at h
  simpa using h

/-- Integer coefficients of sech squared, constructed by binomial convolution. -/
def inverseCoeff (n : ℕ) : ℤ :=
  ∑ r ∈ Finset.range (n+1), (n.choose r : ℤ) * euler r * euler (n-r)

def inverseEven (m : ℕ) : ℤ := inverseCoeff (2*m)

theorem inverse_coeff_cast (n : ℕ) :
    (inverseCoeff n : ℚ) = EGF.decode (sech^2) n := by
  rw [← euler_egf, pow_two, EGF.egf_product]
  simp [inverseCoeff]

@[simp] theorem inverse_zero : inverseCoeff 0 = 1 := by simp [inverseCoeff]

theorem inverse_odd_zero (n : ℕ) (hn : Odd n) : inverseCoeff n = 0 := by
  unfold inverseCoeff
  apply Finset.sum_eq_zero
  intro r hr
  by_cases he : Even r
  · have ho : ¬ Even (n-r) := by
      rw [Nat.even_iff] at he ⊢
      have hn1 := Nat.odd_iff.mp hn
      have hr1 := Finset.mem_range_succ_iff.mp hr
      omega
    simp [euler, ho]
  · simp [euler, he]

theorem inverse_even_egf :
    EGF.encode (fun n => (inverseCoeff n : ℚ)) = sech^2 := by
  rw [show (fun n => (inverseCoeff n : ℚ)) = EGF.decode (sech^2) by funext n; exact inverse_coeff_cast n]
  exact EGF.encode_decode _

/-- Actual coefficient relation to the formal hyperbolic secant squared. -/
theorem sech_square_coeff (m : ℕ) :
    coeff (2*m) (sech^2) = (inverseEven m : ℚ) / (2*m).factorial := by
  rw [← inverse_even_egf, EGF.encode_coeff]
  rfl

end KomorebiPaperIX.EulerCoefficients
