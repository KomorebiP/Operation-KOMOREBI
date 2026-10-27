module
public import SeriesDifferenceBridge
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.RatioSeriesSupport
open PowerSeries SingularRatioAmice

/-- The reciprocal of the expanded source is the expansion of the proved packet inverse. -/
theorem expanded_inverse (N : ℕ) (hN : N≠0) (c : ℕ) :
    (expand N hN (Congruential.sectionKernel N c))⁻¹ =
      expand N hN (Congruential.packetSeries N c) := by
  symm
  apply (PowerSeries.eq_inv_iff_mul_eq_one (by
    rw [constantCoeff_expand, Congruential.kernel_constant_one]; exact one_ne_zero)).mpr
  rw [←map_mul, Congruential.packet_times_kernel, map_one]

/-- The actual ratio is an expansion in the packet variable, so its sparse support is derived. -/
theorem ratio_expansion (N : ℕ) (hN : N≠0) (c : ℕ) :
    ratioSeries N hN c = expand N hN
      (C (c+1:ℚ) * Congruential.sectionKernel N c * Congruential.packetSeries N (c+1)) := by
  rw [ratioSeries, expanded_inverse, map_mul, map_mul, expand_C]

/-- Coefficients outside the original packet support vanish. -/
theorem ratio_support (N : ℕ) (hN : N≠0) (c d : ℕ) (hd : ¬N∣d) :
    coeff d (ratioSeries N hN c)=0 := by
  rw [ratio_expansion]
  exact coeff_expand_of_not_dvd N hN _ hd

/-- The genuine rational Hurwitz coefficient sequence of R_(c+1). -/
def ratioCoefficient (N : ℕ) (hN : N≠0) (c n : ℕ) : ℚ :=
  EGF.decode (ratioSeries N hN c) (N*n)

@[simp] theorem ratioCoefficient_zero (N : ℕ) (hN : N≠0) (c : ℕ) :
    ratioCoefficient N hN c 0 = (c+1:ℚ) := by
  simp [ratioCoefficient, EGF.decode, coeff_zero_eq_constantCoeff, ratio_constant]

variable (p : ℕ) [Fact p.Prime]

/-- The full saturated higher-difference bound for every actual singular ratio. -/
theorem singular_ratio_precision (m a : ℕ) (hm : m∣p-1) (ha : 0<a) (ham : a<m)
    (u k n : ℕ) :
    GlobalEulerBoundary.precision p ((min k (m*n):ℕ):ℤ)
      (Mahler.difference (u*((p-1)/m)) k
        (ratioCoefficient (m*p) (Nat.mul_ne_zero (by omega) (Fact.out : p.Prime).ne_zero)
          (a*p-1)) n) := by
  apply SeriesDifferenceBridge.packet_precision p m hm (by omega)
  · exact WeightedDworkTransfer.singular_ratio_flat p m a hm ha ham
  · intro d hd
    exact ratio_support (m*p) _ (a*p-1) d hd

/-- Singularity does not destroy integrality of the unnormalized ratio coefficients. -/
theorem singular_ratio_integral (m a : ℕ) (hm : m∣p-1) (ha : 0<a) (ham : a<m) (n : ℕ) :
    (ratioCoefficient (m*p) (Nat.mul_ne_zero (by omega) (Fact.out : p.Prime).ne_zero)
        (a*p-1) n : ℚ_[p]) ∈ PadicInt.subring p := by
  have h := WeightedDworkTransfer.singular_ratio_flat p m a hm ha ham 0
  have hn := h (m*p*n)
  change EGF.decode (SeriesDifferenceBridge.rationalMap p _) (m*p*n) ∈ _ at hn
  rw [SeriesDifferenceBridge.decode_rationalMap] at hn
  exact hn

end KomorebiPaperIX.RatioSeriesSupport
