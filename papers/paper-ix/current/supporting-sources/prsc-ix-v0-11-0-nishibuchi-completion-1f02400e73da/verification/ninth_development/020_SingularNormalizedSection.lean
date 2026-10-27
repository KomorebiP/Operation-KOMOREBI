module
public import WeightedAmiceDifferential
public import ExponentialSection
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.SingularNormalizedSection
open PowerSeries WeightedAmice SectionLogBridge
variable (p : ℕ) [hp : Fact p.Prime]

/-- Removing the forced zero of the logarithm without attempting to invert X. -/
def logUnit : PowerSeries ℚ_[p] := PowerSeries.mk (fun n => coeff (n+1) (log ℚ_[p]))

theorem log_factorization : log ℚ_[p] = X * logUnit p := by
  simpa only [constantCoeff_log, map_zero, add_zero] using eq_X_mul_shift_add_const (log ℚ_[p])

theorem logUnit_constant : constantCoeff (logUnit p)=1 := by
  simp [logUnit, coeff_one_log]

theorem weighted_prime_logUnit : Weighted p (C (p:ℚ_[p]) * logUnit p) := by
  intro n
  simp only [coeff_C_mul, logUnit, coeff_mk]
  have hh := weighted_log p (n+1)
  have he : (n+1)/p ≤ n/p+1 := by rw [Nat.succ_div]; split_ifs <;> omega
  have hb := scaled_mono p he hh
  convert hb using 1
  rw [pow_succ]
  ring

/-- The singular leading term c(1+T)log(1+T)/T is weighted when p divides c. -/
theorem weighted_singular_leading (a : ℕ) :
    Weighted p (C ((a*p:ℕ):ℚ_[p]) * (1+X) * logUnit p) := by
  have h := weighted_mul p (weighted_mul p (weighted_constant p (integral_nat p a))
    (weighted_prime_logUnit p)) (weighted_add p (weighted_one p) (weighted_X p))
  convert h using 1
  simp only [Nat.cast_mul, map_mul]
  ring

/-- Exact bridge to the source section already used in the checked Euler recurrence project. -/
theorem sectionSeries_is_original (N c : ℕ) (hc : c<N) :
    sectionSeries N (c:ZMod N) = ExponentialSection.originalSection N c := by
  ext d
  have he : ((d:ZMod N)=(c:ZMod N)) ↔ d%N=c := by
    rw [ZMod.natCast_eq_natCast_iff]
    change d%N=c%N ↔ d%N=c
    rw [Nat.mod_eq_of_lt hc]
  simp only [sectionSeries, ExponentialSection.originalSection, coeff_mk, he]

/-- The normalized original source, with constant coefficient one. -/
def kernelPadic (N : ℕ) (hN : N≠0) (c : ℕ) : PowerSeries ℚ_[p] :=
  PowerSeries.map (Rat.castHom ℚ_[p]) (expand N hN (Congruential.sectionKernel N c))

/-- The actual normalized logarithmic section c! T^(-c) H(log(1+T)). -/
def normalizedUnit (N : ℕ) (hN : N≠0) (c : ℕ) : PowerSeries ℚ_[p] :=
  (logUnit p)^c * (kernelPadic p N hN c).subst (log ℚ_[p])

theorem kernel_constant (N : ℕ) (hN : N≠0) (c : ℕ) :
    constantCoeff (kernelPadic p N hN c)=1 := by
  simp [kernelPadic]

theorem normalized_constant (N : ℕ) (hN : N≠0) (c : ℕ) :
    constantCoeff (normalizedUnit p N hN c)=1 := by
  rw [normalizedUnit, map_mul, map_pow, logUnit_constant, one_pow, one_mul,
    constantCoeff_eq, constantCoeff_subst_of_constantCoeff_zero constantCoeff_log]
  simp only [Algebra.algebraMap_self, RingHom.id_apply, kernel_constant]

theorem mapped_original_factorization (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c<N) :
    PowerSeries.map (Rat.castHom ℚ_[p]) (sectionSeries N (c:ZMod N)) =
      C (1/(c.factorial:ℚ_[p])) * X^c * kernelPadic p N hN c := by
  rw [sectionSeries_is_original N c hc,
    ExponentialSection.original_section_factorization N hN c hc]
  simp only [ExponentialSection.expandedSource, kernelPadic, map_mul, map_pow,
    PowerSeries.map_C, PowerSeries.map_X, Rat.coe_castHom, Rat.cast_div,
    Rat.cast_one, Rat.cast_natCast]
  ring

/-- The forced T^c zero and normalization are established for the actual substituted section. -/
theorem section_factorization (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c<N) :
    sectionPadic p N (c:ZMod N) =
      C (1/(c.factorial:ℚ_[p])) * X^c * normalizedUnit p N hN c := by
  unfold sectionPadic sectionPullback
  rw [PowerSeries.map_subst (HasSubst.log), PowerSeries.map_log,
    mapped_original_factorization p N hN c hc]
  rw [subst_mul (HasSubst.log), subst_mul (HasSubst.log), subst_C,
    subst_pow (HasSubst.log), subst_X (HasSubst.log), log_factorization]
  simp only [normalizedUnit, mul_pow]
  ring

theorem normalized_coefficient (N : ℕ) (hN : N≠0) (c d : ℕ) (hc : c<N) :
    coeff d (normalizedUnit p N hN c) =
      (c.factorial:ℚ_[p])*coeff (d+c) (sectionPadic p N (c:ZMod N)) := by
  rw [section_factorization p N hN c hc, mul_assoc, coeff_C_mul, coeff_X_pow_mul]
  have hc0 : (c.factorial:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero c)
  field_simp

/-- No assumption on a factorial valuation: the needed divisibility follows from Legendre. -/
theorem prime_power_dvd_singular_factorial (a : ℕ) : p^a ∣ (a*p).factorial := by
  apply (padicValNat_dvd_iff_le (Nat.factorial_ne_zero _)).mpr
  rw [Nat.mul_comm a p, padicValNat_factorial_mul]
  omega

/-- The singular normalized denominator is a weighted unit, for every positive allowed address. -/
theorem weighted_normalized_singular (N : ℕ) (hN : N≠0)
    (hdiv : N∣p*(p-1)) (a : ℕ) (ha : a*p<N) :
    Weighted p (normalizedUnit p N hN (a*p)) := by
  intro d
  rw [normalized_coefficient p N hN (a*p) d ha]
  have hh := weighted_section p N hdiv (a*p:ZMod N) (d+a*p)
  have he : (d+a*p)/p=d/p+a := by
    rw [Nat.mul_comm a p, Nat.add_mul_div_left d a hp.out.pos]
  rw [he] at hh
  obtain ⟨z,hz⟩ := prime_power_dvd_singular_factorial p a
  have hz' : ((a*p).factorial:ℚ_[p]) = (p:ℚ_[p])^a*(z:ℚ_[p]) := by exact_mod_cast hz
  rw [hz']
  convert integral_mul p (integral_nat p z) hh using 1
  rw [pow_add]
  ring

end KomorebiPaperIX.SingularNormalizedSection
