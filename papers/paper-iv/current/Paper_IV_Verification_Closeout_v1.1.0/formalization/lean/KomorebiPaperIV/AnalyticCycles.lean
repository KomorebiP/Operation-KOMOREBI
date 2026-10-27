/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ODESolutions
import KomorebiPaperIV.CompanionCompletion

/-! # Exact pointwise derivative cycles from formal Taylor coefficients -/

namespace Komorebi.PaperIV
noncomputable section
open scoped PowerSeries

/-- Entire functions are determined by all their derivatives at the origin. -/
theorem entire_eq_of_all_derivatives {f g : ℂ → ℂ}
    (hf : ∀ z, AnalyticAt ℂ f z) (hg : ∀ z, AnalyticAt ℂ g z)
    (hjets : ∀ k, deriv^[k] f 0 = deriv^[k] g 0) : f = g := by
  have hd : ∀ z, AnalyticAt ℂ (f - g) z := fun z => (hf z).sub (hg z)
  have hzero : f - g = 0 := by
    apply (AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero 0 hd).mp
    rw [ENat.eq_top_iff_forall_ge]
    intro n
    apply (natCast_le_analyticOrderAt_iff_iteratedDeriv_eq_zero (hd 0)).mpr
    intro k _
    rw [iteratedDeriv_sub (hf 0).contDiffAt (hg 0).contDiffAt,
      iteratedDeriv_eq_iterate, iteratedDeriv_eq_iterate, hjets k, sub_self]
  exact sub_eq_zero.mp hzero

/-- A formal differential identity transfers to entire analytic realizations
with the corresponding Taylor coefficients. -/
theorem entire_derivative_of_formal {f g : ℂ → ℂ} {F G : ℂ⟦X⟧} (c : ℂ)
    (hf : ∀ z, AnalyticAt ℂ f z) (hg : ∀ z, AnalyticAt ℂ g z)
    (hfjets : ∀ k, deriv^[k] f 0 = (k.factorial : ℂ) * PowerSeries.coeff k F)
    (hgjets : ∀ k, deriv^[k] g 0 = (k.factorial : ℂ) * PowerSeries.coeff k G)
    (hformal : PowerSeries.derivative ℂ F = PowerSeries.C c * G) :
    deriv f = fun z => c * g z := by
  apply entire_eq_of_all_derivatives (fun z => (hf z).deriv)
    (fun z => analyticAt_const.mul (hg z))
  intro k
  change deriv^[k] (deriv f) 0 = deriv^[k] (fun z => c * g z) 0
  rw [← Function.iterate_succ_apply, hfjets,
    ← iteratedDeriv_eq_iterate, iteratedDeriv_const_mul_field, iteratedDeriv_eq_iterate,
    hgjets]
  have hc := congrArg (PowerSeries.coeff k) hformal
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_C_mul] at hc
  rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  linear_combination (k.factorial : ℂ) * hc

theorem entireTransfer_derivative_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N)
    (lambda : ℂ) :
    deriv (entireTransfer N j omega lambda) =
      fun z => lambda * entireTransfer N (j - 1) omega lambda z := by
  apply entire_derivative_of_formal lambda
    (analyticAt_entireTransfer N j omega lambda)
    (analyticAt_entireTransfer N (j - 1) omega lambda)
    (entireTransfer_derivative_at_zero hN hjN homega lambda)
    (entireTransfer_derivative_at_zero hN (by omega) homega lambda)
  exact derivative_transferSection_of_pos hN hj hjN lambda

theorem entireTransfer_derivative_zero {N : ℕ} (hN : 0 < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (lambda : ℂ) :
    deriv (entireTransfer N 0 omega lambda) =
      fun z => lambda * entireTransfer N (N - 1) omega lambda z := by
  apply entire_derivative_of_formal lambda
    (analyticAt_entireTransfer N 0 omega lambda)
    (analyticAt_entireTransfer N (N - 1) omega lambda)
    (entireTransfer_derivative_at_zero hN hN homega lambda)
    (entireTransfer_derivative_at_zero hN (by omega) homega lambda)
  exact derivative_transferSection_zero hN lambda

theorem entireSigned_derivative_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) {omega rho : ℂ}
    (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) :
    deriv (entireSigned N j omega rho) = entireSigned N (j - 1) omega rho := by
  have h := entire_derivative_of_formal 1
    (analyticAt_entireSigned N j omega rho)
    (analyticAt_entireSigned N (j - 1) omega rho)
    (entireSigned_derivative_at_zero hN hjN homega hrho)
    (entireSigned_derivative_at_zero hN (by omega) homega hrho)
    (by simpa using derivative_signedSection_of_pos (R := ℂ) hN hj hjN)
  simpa using h

theorem entireSigned_derivative_zero {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) :
    deriv (entireSigned N 0 omega rho) = fun z => -entireSigned N (N - 1) omega rho z := by
  have h := entire_derivative_of_formal (-1)
    (analyticAt_entireSigned N 0 omega rho)
    (analyticAt_entireSigned N (N - 1) omega rho)
    (entireSigned_derivative_at_zero hN hN homega hrho)
    (entireSigned_derivative_at_zero hN (by omega) homega hrho)
    (by simpa using derivative_signedSection_zero (R := ℂ) hN)
  simpa using h

end
end Komorebi.PaperIV
