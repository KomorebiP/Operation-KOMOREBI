/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ParameterThetaCompletion

namespace Komorebi.PaperIV
open scoped PowerSeries
noncomputable section
variable {R : Type*} [CommRing R]

theorem truncatedDifferentialOperator_apply (d : ℕ) (A : R⟦X⟧) (p : Polynomial R) :
    truncatedDifferentialOperator d A p =
      ∑ q ∈ Finset.range (d + 1), Polynomial.C (PowerSeries.coeff q A) *
        Polynomial.derivative^[q] p := by
  change (Polynomial.eval₂ (algebraMap R (Module.End R (Polynomial R)))
    Polynomial.derivative (PowerSeries.trunc (d + 1) A)) p = _
  rw [PowerSeries.eval₂_trunc_eq_sum_range]
  simp only [LinearMap.sum_apply, Module.End.mul_apply, Module.End.pow_apply,
    Algebra.algebraMap_eq_smul_one, LinearMap.smul_apply, Module.End.one_apply,
    Polynomial.smul_eq_C_mul]

theorem truncatedDifferentialOperator_egfAction (A : R⟦X⟧) (p : Polynomial R) :
    truncatedDifferentialOperator p.natDegree A p =
      egfConstantCoeffAction (fun q => (q.factorial : R) * PowerSeries.coeff q A) p := by
  rw [truncatedDifferentialOperator_apply, egfConstantCoeffAction]
  apply Finset.sum_congr rfl
  intro q _
  have h := congrFun (Polynomial.factorial_smul_hasseDeriv (R := R) q) p
  change q.factorial • (Polynomial.hasseDeriv q p) = Polynomial.derivative^[q] p at h
  rw [← h]
  simp only [nsmul_eq_mul, map_mul, map_natCast]
  ring

variable [Algebra ℚ R] [Nontrivial R]

theorem residueAppell_operator_forward (N j : ℕ) (hN : 0 < N) (r : R) (m : ℕ) :
    truncatedDifferentialOperator m
        (PowerSeries.expand N hN.ne' (residuePowerSeries N j r)) (Polynomial.X ^ m) =
      residueAppellPolynomialParam N j hN r m := by
  have h := truncatedDifferentialOperator_egfAction
    (PowerSeries.expand N hN.ne' (residuePowerSeries N j r)) (Polynomial.X ^ m)
  rw [Polynomial.natDegree_X_pow] at h
  exact h.trans (egfConstantCoeffAction_residuePowerSeries_X_pow N j hN r m)

/-- The actual inverse relation on the named arbitrary-order Appell polynomial.
The expanded opposite-order symbol is Phi_(N,j)(X^N)^r. -/
theorem residueAppell_operator_inverse (N j : ℕ) (hN : 0 < N) (r : R) (m : ℕ) :
    truncatedDifferentialOperator m
        (PowerSeries.expand N hN.ne' (residuePowerSeries N j (-r)))
        (residueAppellPolynomialParam N j hN r m) = Polynomial.X ^ m := by
  rw [← residueAppell_operator_forward N j hN r m]
  exact truncatedDifferentialOperator_residuePowerSeries_inverse N j hN r m
    (by simp)

end
end Komorebi.PaperIV
