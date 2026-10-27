module
public import CyclicAmiceCoefficients
public import BinomialLogSeries
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.SectionLogBridge
open PowerSeries PrimeBlockPolynomial CyclicAmiceCoefficients

/-- Literal exponential residue section, indexed by the actual cyclic residue. -/
def sectionSeries (N : ℕ) (r : ZMod N) : PowerSeries ℚ :=
  PowerSeries.mk (fun d => if (d : ZMod N) = r then 1 / (d.factorial : ℚ) else 0)

/-- The actual formal substitution t = log(1+T). -/
def sectionPullback (N : ℕ) (r : ZMod N) : PowerSeries ℚ :=
  (sectionSeries N r).subst (log ℚ)

theorem section_derivative (N : ℕ) (r : ZMod N) :
    derivative ℚ (sectionSeries N r) = sectionSeries N (r-1) := by
  ext n
  have he : ((n+1 : ℕ) : ZMod N) = r ↔ (n : ZMod N) = r-1 := by
    push_cast
    exact eq_sub_iff_add_eq.symm
  simp only [coeff_derivative, sectionSeries, coeff_mk, he]
  by_cases hn : (n : ZMod N) = r-1
  · simp only [ite_eq_left hn]
    rw [Nat.factorial_succ, Nat.cast_mul]
    have h0 : (n.factorial : ℚ) ≠ 0 := by positivity
    have h1 : ((n+1 : ℕ) : ℚ) ≠ 0 := by positivity
    field_simp
    push_cast
  · simp [hn]

theorem pullback_zero (N : ℕ) (r : ZMod N) :
    coeff 0 (sectionPullback N r) = if r = 0 then 1 else 0 := by
  rw [sectionPullback, coeff_zero_eq_constantCoeff, constantCoeff_eq,
    constantCoeff_subst_of_constantCoeff_zero constantCoeff_log]
  simp [sectionSeries, constantCoeff_mk, eq_comm]

theorem pullback_equation (N : ℕ) (r : ZMod N) :
    derivative ℚ (sectionPullback N r) * (1+X) = sectionPullback N (r-1) := by
  rw [sectionPullback, derivative_subst (HasSubst.log), section_derivative]
  rw [mul_assoc, derivative_log_mul_one_add_X, mul_one]
  rfl

theorem pullback_recurrence (N n : ℕ) (r : ZMod N) :
    (n+1 : ℚ) * coeff (n+1) (sectionPullback N r) =
      coeff n (sectionPullback N (r-1)) - (n:ℚ)*coeff n (sectionPullback N r) := by
  have h := congrArg (coeff n) (pullback_equation N r)
  cases n with
  | zero =>
    simpa using h
  | succ n =>
    have hx : coeff (n+1) (derivative ℚ (sectionPullback N r)*X) =
        coeff n (derivative ℚ (sectionPullback N r)) := by simp
    simp only [mul_add, mul_one, map_add, hx, coeff_derivative] at h
    push_cast at h ⊢
    linear_combination h

theorem numerator_zero (N : ℕ) (r : ZMod N) :
    numerator N 0 r = if r = 0 then 1 else 0 := by
  change (Finsupp.single 0 (1:ℤ)) r = if r = 0 then 1 else 0
  simp [eq_comm]

theorem numerator_succ (N n : ℕ) (r : ZMod N) :
    numerator N (n+1) r = numerator N n (r-1) - (n:ℤ)*numerator N n r := by
  unfold numerator
  rw [BinomialLogSeries.fallingAt_succ, mul_sub]
  simp only [AddMonoidAlgebra.coeff_sub, Finsupp.sub_apply]
  rw [mul_comm _ (n : CyclicRing N), coeff_nat_mul]
  simp [generator, AddMonoidAlgebra.coeff_mul_single_apply, sub_eq_add_neg]

/-- The cyclic-ring numerator really is the factorial-scaled logarithmic section coefficient. -/
theorem factorial_coeff_section (N d : ℕ) (r : ZMod N) :
    (d.factorial : ℚ) * coeff d (sectionPullback N r) = (numerator N d r : ℚ) := by
  induction d generalizing r with
  | zero => simp [pullback_zero, numerator_zero]
  | succ d ih =>
    rw [Nat.factorial_succ, Nat.cast_mul, numerator_succ]
    push_cast
    calc
      _ = (d.factorial : ℚ) * ((d+1 : ℚ)*coeff (d+1) (sectionPullback N r)) := by ring
      _ = (d.factorial : ℚ) * (coeff d (sectionPullback N (r-1)) -
          (d:ℚ)*coeff d (sectionPullback N r)) := by rw [pullback_recurrence]
      _ = (d.factorial : ℚ)*coeff d (sectionPullback N (r-1)) -
          (d:ℚ)*((d.factorial : ℚ)*coeff d (sectionPullback N r)) := by ring
      _ = _ := by rw [ih, ih]

/-- No root-of-unity trace or binomial-series identity is left as an assumption. -/
theorem coefficient_section (N d : ℕ) (r : ZMod N) :
    coeff d (sectionPullback N r) = coefficient N d r := by
  unfold coefficient
  apply (eq_div_iff (by positivity : (d.factorial : ℚ) ≠ 0)).mpr
  simpa [mul_comm] using factorial_coeff_section N d r

/-- Weighted Amice estimate for every residue section, including singular addresses. -/
theorem section_weighted_integral (p N d : ℕ) [hp : Fact p.Prime]
    (hN : N ∣ p*(p-1)) (r : ZMod N) :
    (p:ℚ_[p])^(d/p) * ((coeff d (sectionPullback N r) : ℚ) : ℚ_[p]) ∈ PadicInt.subring p := by
  rw [coefficient_section]
  exact coefficient_weighted_integral p N d hN r

end KomorebiPaperIX.SectionLogBridge
