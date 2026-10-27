module
public import ThetaWeighted
public import HurwitzDworkClosure
public import SingularRatioAmice
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.WeightedDworkTransfer
open PowerSeries DworkAlgebra DworkClosure ThetaWeighted HurwitzDworkClosure
variable (p : ℕ) [Fact p.Prime]

/-- The actual substitution T = exp(t)-1. -/
def expPull (f : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  f.subst (exp ℚ_[p]-1)

/-- Chain rule, not an assumed intertwining certificate. -/
theorem derivative_expPull (f : PowerSeries ℚ_[p]) :
    derivative ℚ_[p] (expPull p f) = expPull p (theta p f) := by
  rw [expPull, derivative_subst (HasSubst.exp_sub_one)]
  simp only [Derivation.map_sub, derivative_exp, derivative_one, sub_zero]
  have h1 : (1 : PowerSeries ℚ_[p]).subst (exp ℚ_[p]-1) = 1 := by
    rw [← coe_substAlgHom (HasSubst.exp_sub_one), map_one]
  rw [expPull, theta_apply, subst_mul (HasSubst.exp_sub_one),
    subst_add (HasSubst.exp_sub_one), h1, subst_X (HasSubst.exp_sub_one)]
  ring

/-- Every derivative is transported through the actual substitution. -/
theorem deriv_expPull (s : ℕ) (f : PowerSeries ℚ_[p]) :
    deriv (derivative ℚ_[p]) s (expPull p f) = expPull p (deriv (theta p) s f) := by
  induction s with
  | zero => rfl
  | succ s ih => rw [deriv_succ, ih, derivative_expPull, deriv_succ]

theorem constant_expPull (f : PowerSeries ℚ_[p]) :
    constantCoeff (expPull p f) = constantCoeff f := by
  rw [expPull, constantCoeff_eq, constantCoeff_subst_of_constantCoeff_zero (by rw [←constantCoeff_eq]; simp)]
  rfl

/-- Factorial-scaled coefficients come from constant terms of the genuine Theta iterates. -/
theorem decode_expPull (f : PowerSeries ℚ_[p]) (n : ℕ) :
    EGF.decode (expPull p f) n = constantCoeff (deriv (theta p) n f) := by
  have h := decode_deriv p (expPull p f) n 0
  rw [zero_add, deriv_expPull] at h
  rw [← h]
  simpa [EGF.decode, coeff_zero_eq_constantCoeff] using constant_expPull p (deriv (theta p) n f)

/-- Weighted ordinary coefficients become integral Hurwitz coefficients under exp(t)-1. -/
theorem expPull_integral {f : PowerSeries ℚ_[p]} (hf : f∈WeightedAmice.ring p) :
    expPull p f∈integralSeries p := by
  intro n
  rw [decode_expPull]
  have h := ThetaWeighted.deriv_mem p n f hf 0
  simpa [coeff_zero_eq_constantCoeff] using h

/-- The normalized defects commute with the actual change of variables. -/
theorem B_expPull (f : PowerSeries ℚ_[p]) :
    B (derivative ℚ_[p]) p (expPull p f) = expPull p (B (theta p) p f) := by
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, deriv_expPull]
  simp only [expPull, subst_smul (HasSubst.exp_sub_one), subst_sub (HasSubst.exp_sub_one)]

theorem iterate_B_expPull (s : ℕ) (f : PowerSeries ℚ_[p]) :
    (B (derivative ℚ_[p]) p ^ s) (expPull p f) = expPull p ((B (theta p) p ^ s) f) := by
  induction s with
  | zero => rfl
  | succ s ih => rw [pow_succ', Module.End.mul_apply, ih, B_expPull, pow_succ', Module.End.mul_apply]

/-- Universal weighted-to-Dwork transfer; no flatness premise is assumed. -/
theorem expPull_flat {f : PowerSeries ℚ_[p]} (hf : f∈WeightedAmice.ring p) :
    DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p) (expPull p f) := by
  intro s
  rw [iterate_B_expPull]
  exact expPull_integral p (B_iter_mem p s f hf)

/-- The logarithmic and exponential substitutions cancel as formal series. -/
theorem expPull_log (f : PowerSeries ℚ_[p]) :
    expPull p (f.subst (log ℚ_[p])) = f := by
  rw [expPull, subst_comp_subst_apply (HasSubst.log) (HasSubst.exp_sub_one),
    subst_log_exp_sub_one, X_subst]

/-- Weightedness of the actual logarithmic transform suffices for original-series flatness. -/
theorem flat_of_log_weighted {f : PowerSeries ℚ_[p]}
    (hf : WeightedAmice.Weighted p (f.subst (log ℚ_[p]))) :
    DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p) f := by
  have h := expPull_flat p (show f.subst (log ℚ_[p])∈WeightedAmice.ring p from hf)
  rwa [expPull_log] at h

/-- Singular higher-defect estimate for the original ratio, not merely its transformed coefficients. -/
theorem singular_ratio_flat (m a : ℕ) (hm : m∣p-1) (ha : 0<a) (ham : a<m) :
    DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p)
      (PowerSeries.map (Rat.castHom ℚ_[p])
        (SingularRatioAmice.ratioSeries (m*p)
          (Nat.mul_ne_zero (by omega) (Fact.out : p.Prime).ne_zero) (a*p-1))) := by
  exact flat_of_log_weighted p (SingularRatioAmice.paper_singular_amice_estimate p m a hm ha ham)

end KomorebiPaperIX.WeightedDworkTransfer
