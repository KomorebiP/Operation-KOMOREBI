import FormalPowerSeriesSystemHensel
import MvPolynomialExprDerivative
import Mathlib.RingTheory.MvPowerSeries.Trunc

/-!
# Linear coefficient matrix of a centered formal presentation

At the residual origin, the coordinate Jacobian of every total-degree
truncation containing the linear terms is exactly the matrix of linear
coefficients of the original untruncated formal power-series system.
-/

namespace Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.MvPolynomialExprCompiler
open Komorebi.StrongArtin.MvPolynomialExprDerivative
open Komorebi.StrongArtin.MvPowerSeriesArtinTruncation
open Komorebi.StrongArtin.FormalPowerSeriesSystemHensel
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel

noncomputable section

variable {R ι κ : Type*} [CommRing R]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]

/-- Matrix of the linear coefficients of a formal system at the chosen origin. -/
def linearCoefficientMatrix
    (system : FormalSystem ι κ R) : Matrix κ ι R :=
  fun j i => MvPowerSeries.coeff (Finsupp.single i 1) (system j)

omit [Fintype ι] [DecidableEq ι] in
/-- Evaluation at zero of one formal partial derivative is the corresponding
linear coefficient. -/
theorem eval_zero_pderiv_eq_linearCoefficient
    (p : MvPolynomial ι R) (i : ι) :
    MvPolynomial.eval (0 : ι → R) (MvPolynomial.pderiv i p) =
      p.coeff (Finsupp.single i 1) := by
  rw [MvPolynomial.eval_zero]
  rw [MvPolynomial.constantCoeff_eq]
  simp [MvPolynomial.coeff_pderiv]

omit [DecidableEq ι] in
/-- Every total-degree truncation of level at least two retains every linear
coefficient exactly. -/
theorem coeff_truncTotal_single_one
    (N : ℕ) (hN : 2 ≤ N) (f : MvPowerSeries ι R) (i : ι) :
    (f.truncTotal N).coeff (Finsupp.single i 1) =
      MvPowerSeries.coeff (Finsupp.single i 1) f := by
  apply MvPowerSeries.coeff_truncTotal
  simpa [Finsupp.degree_apply] using (lt_of_lt_of_le Nat.one_lt_two hN)

omit [DecidableEq κ] in
/-- The v0.20 coordinate Jacobian of the compiled truncation at the origin is
independent of the truncation level and equals the original formal linear
coefficient matrix. -/
theorem jacobianMatrix_compileSystemAt_zero
    (N : ℕ) (hN : 2 ≤ N) (system : FormalSystem ι κ R) :
    jacobianMatrix (compileSystemAt N system) (0 : ι → R) =
      linearCoefficientMatrix system := by
  ext j i
  rw [jacobianMatrix_apply]
  change Expr.deriv (compile (MvPowerSeries.truncTotal N (system j)))
      (0 : ι → R) (Pi.single i 1) = _
  rw [deriv_compile_single]
  rw [eval_zero_pderiv_eq_linearCoefficient]
  exact coeff_truncTotal_single_one N hN (system j) i

omit [DecidableEq κ] in
/-- Mapping the compiled residual Jacobian to any coefficient ring gives the
mapped matrix of the original formal linear coefficients. -/
theorem map_jacobianMatrix_compileSystemAt_zero
    {S : Type*} [CommRing S] (q : R →+* S)
    (N : ℕ) (hN : 2 ≤ N) (system : FormalSystem ι κ R) :
    (jacobianMatrix (compileSystemAt N system) (0 : ι → R)).map q =
      (linearCoefficientMatrix system).map q := by
  rw [jacobianMatrix_compileSystemAt_zero N hN system]

end

end Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin

#print axioms Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin.jacobianMatrix_compileSystemAt_zero
#print axioms Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin.map_jacobianMatrix_compileSystemAt_zero
