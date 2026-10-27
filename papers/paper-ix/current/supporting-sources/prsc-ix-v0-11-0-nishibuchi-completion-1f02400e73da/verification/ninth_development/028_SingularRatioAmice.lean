module
public import SingularNormalizedSection
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.SingularRatioAmice
open PowerSeries WeightedAmice SingularNormalizedSection SectionLogBridge
variable (p : ℕ) [Fact p.Prime]

/-- Derivatives commute with the actual rational-to-p-adic coefficient map. -/
theorem derivative_map_rat (f : PowerSeries ℚ) :
    derivative ℚ_[p] (PowerSeries.map (Rat.castHom ℚ_[p]) f) =
      PowerSeries.map (Rat.castHom ℚ_[p]) (derivative ℚ f) := by
  ext n
  simp only [coeff_derivative, coeff_map, map_mul, map_natCast, map_add, map_one]

/-- The coupled differential relation for the actual logarithmic sections. -/
theorem section_theta (N : ℕ) (r : ZMod N) :
    derivative ℚ_[p] (sectionPadic p N r) * (1+X) = sectionPadic p N (r-1) := by
  have h := congrArg (PowerSeries.map (Rat.castHom ℚ_[p])) (pullback_equation N r)
  simpa only [map_mul, map_add, map_one, PowerSeries.map_X, ←derivative_map_rat,
    sectionPadic] using h

/-- Unnormalized ratio at address c+1, constructed from the original normalized kernels. -/
def ratioSeries (N : ℕ) (hN : N≠0) (c : ℕ) : PowerSeries ℚ :=
  C (c+1:ℚ) * expand N hN (Congruential.sectionKernel N c) *
    (expand N hN (Congruential.sectionKernel N (c+1)))⁻¹

/-- The ratio is identified without attempting to invert the forced zero of a section. -/
theorem ratio_cleared (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+1<N) :
    ratioSeries N hN c * ExponentialSection.originalSection N (c+1) =
      X * ExponentialSection.originalSection N c := by
  have hc' : c<N := by omega
  have hunit : constantCoeff (expand N hN (Congruential.sectionKernel N (c+1))) ≠ 0 := by
    rw [constantCoeff_expand, Congruential.kernel_constant_one]
    exact one_ne_zero
  have hi := PowerSeries.inv_mul_cancel (expand N hN (Congruential.sectionKernel N (c+1))) hunit
  rw [ExponentialSection.original_section_factorization N hN (c+1) hc,
    ExponentialSection.original_section_factorization N hN c hc']
  unfold ratioSeries ExponentialSection.expandedSource
  calc
    _ = (C (c+1:ℚ) * C (1/((c+1).factorial:ℚ))) * (X * X^c) *
        expand N hN (Congruential.sectionKernel N c) *
        ((expand N hN (Congruential.sectionKernel N (c+1)))⁻¹ *
          expand N hN (Congruential.sectionKernel N (c+1))) := by rw [pow_succ]; ring
    _ = _ := by
      rw [hi, mul_one, ←map_mul]
      have he : (c+1:ℚ) * (1/((c+1).factorial:ℚ)) = 1/(c.factorial:ℚ) := by
        rw [Nat.factorial_succ, Nat.cast_mul]
        push_cast
        field_simp
      rw [he]
      ring

/-- Actual formal logarithmic substitution of the original ratio. -/
def ratioPullback (N : ℕ) (hN : N≠0) (c : ℕ) : PowerSeries ℚ_[p] :=
  (PowerSeries.map (Rat.castHom ℚ_[p]) (ratioSeries N hN c)).subst (log ℚ_[p])

theorem sectionPadic_as_subst (N : ℕ) (r : ZMod N) :
    sectionPadic p N r = (PowerSeries.map (Rat.castHom ℚ_[p]) (sectionSeries N r)).subst
      (log ℚ_[p]) := by
  unfold sectionPadic sectionPullback
  change MvPowerSeries.map (Rat.castHom ℚ_[p]) ((sectionSeries N r).subst (log ℚ)) = _
  rw [PowerSeries.map_subst (HasSubst.log)]
  change (PowerSeries.map (Rat.castHom ℚ_[p]) (sectionSeries N r)).subst
    (PowerSeries.map (Rat.castHom ℚ_[p]) (log ℚ)) = _
  rw [PowerSeries.map_log]

/-- Cleared chain rule for the actual ratio and transformed section. -/
theorem ratio_pullback_cleared (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+1<N) :
    ratioPullback p N hN c * sectionPadic p N ((c+1:ℕ):ZMod N) =
      eulerLog p (sectionPadic p N ((c+1:ℕ):ZMod N)) := by
  have h := congrArg (fun f : PowerSeries ℚ =>
    (PowerSeries.map (Rat.castHom ℚ_[p]) f).subst (log ℚ_[p])) (ratio_cleared N hN c hc)
  simp only [map_mul, PowerSeries.map_X, subst_mul (HasSubst.log), subst_X (HasSubst.log)] at h
  rw [←sectionSeries_is_original N (c+1) hc, ←sectionSeries_is_original N c (by omega),
    ←sectionPadic_as_subst, ←sectionPadic_as_subst] at h
  change ratioPullback p N hN c * sectionPadic p N ((c+1:ℕ):ZMod N) = _ at h
  rw [h]
  unfold eulerLog
  have ht := section_theta p N ((c+1:ℕ):ZMod N)
  have hr : ((c+1:ℕ):ZMod N)-1=(c:ZMod N) := by push_cast; ring
  rw [hr] at ht
  rw [show log ℚ_[p] * (1+X) * derivative ℚ_[p] (sectionPadic p N ((c+1:ℕ):ZMod N)) =
    log ℚ_[p] * (derivative ℚ_[p] (sectionPadic p N ((c+1:ℕ):ZMod N))*(1+X)) by ring, ht]

/-- Euler differentiation of the actual power of X. -/
theorem X_derivative_power (c : ℕ) :
    X * derivative ℚ_[p] ((X : PowerSeries ℚ_[p])^c) = C (c:ℚ_[p])*X^c := by
  cases c with
  | zero => simp
  | succ c =>
    rw [derivative_pow, derivative_X, mul_one]
    simp only [Nat.add_sub_cancel, pow_succ]
    have hn : ((c+1:ℕ):PowerSeries ℚ_[p])=C ((c+1:ℕ):ℚ_[p]) := by simp
    rw [hn]
    ring

/-- Logarithmic differentiation after removing the forced X^c zero. -/
theorem normalized_log_derivative (c : ℕ) (b : ℚ_[p]) (U : PowerSeries ℚ_[p])
    (hU : constantCoeff U=1) :
    (C (c:ℚ_[p])*(1+X)*logUnit p + eulerLog p U * U⁻¹) * (C b*X^c*U) =
      eulerLog p (C b*X^c*U) := by
  have hi : U⁻¹*U=1 := PowerSeries.inv_mul_cancel U (by rw [hU]; exact one_ne_zero)
  have hd : derivative ℚ_[p] (C b*X^c*U) =
      C b*derivative ℚ_[p] (X^c)*U + C b*X^c*derivative ℚ_[p] U := by
    simp only [Derivation.leibniz, derivative_C, smul_eq_mul]
    ring
  simp only [eulerLog, hd, log_factorization]
  have hpw := X_derivative_power p c
  calc
    _ = C b*(1+X)*logUnit p * (C (c:ℚ_[p])*X^c*U) +
      C b*X^c*(X*logUnit p*(1+X)*derivative ℚ_[p] U)*(U⁻¹*U) := by ring
    _ = C b*(1+X)*logUnit p * (X*derivative ℚ_[p] (X^c)*U) +
      C b*X^c*(X*logUnit p*(1+X)*derivative ℚ_[p] U) := by rw [hi, mul_one, hpw]
    _ = _ := by ring

/-- The actual section is nonzero, even at a singular address. -/
theorem section_nonzero (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c<N) :
    sectionPadic p N (c:ZMod N) ≠ 0 := by
  rw [section_factorization p N hN c hc]
  apply mul_ne_zero
  · apply mul_ne_zero
    · intro h
      have hh := congrArg constantCoeff h
      have hz : (1/(c.factorial:ℚ_[p]))=0 := by simpa using hh
      exact (one_div_ne_zero (Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero c))) hz
    · exact pow_ne_zero _ X_ne_zero
  · intro h
    have hh := congrArg constantCoeff h
    rw [normalized_constant, map_zero] at hh
    exact one_ne_zero hh

/-- Exact decomposition of the genuine ratio pullback into weighted pieces. -/
theorem ratio_pullback_formula (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+1<N) :
    ratioPullback p N hN c = C ((c+1:ℕ):ℚ_[p])*(1+X)*logUnit p +
      eulerLog p (normalizedUnit p N hN (c+1)) * (normalizedUnit p N hN (c+1))⁻¹ := by
  apply mul_right_cancel₀ (section_nonzero p N hN (c+1) hc)
  rw [ratio_pullback_cleared p N hN c hc, section_factorization p N hN (c+1) hc]
  exact (normalized_log_derivative p (c+1) (1/((c+1).factorial:ℚ_[p]))
    (normalizedUnit p N hN (c+1)) (normalized_constant p N hN (c+1))).symm

/-- The weighted Amice estimate for the actual singular ratio R_(a*p). -/
theorem singular_ratio_weighted (N : ℕ) (hN : N≠0) (hdiv : N∣p*(p-1))
    (a c : ℕ) (hc : c+1=a*p) (ha : a*p<N) :
    Weighted p (ratioPullback p N hN c) := by
  rw [ratio_pullback_formula p N hN c (by omega)]
  have hU := weighted_normalized_singular p N hN hdiv a ha
  rw [←hc] at hU
  apply weighted_add p
  · convert weighted_singular_leading p a using 1
    congr 3
    exact_mod_cast hc
  · exact weighted_mul p (weighted_eulerLog p hU)
      (weighted_inverse p hU (normalized_constant p N hN (c+1)))

end KomorebiPaperIX.SingularRatioAmice
