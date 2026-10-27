import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff
import SpectralTraceConjugacy

namespace Komorebi.StrongArtin.SpectralDeterminantDifferential

open Polynomial
open Komorebi.StrongArtin.SpectralTraceConjugacy

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The projector trace functional is the exact first-order coefficient of the
spectral determinant coordinate `det(1 + T · P X)`. -/
theorem derivative_spectralDet_eq_traceProbe
    (P X : Matrix n n k) :
    (derivative <|
      Matrix.det
        (1 + (Polynomial.X : k[X]) • (P * X).map Polynomial.C)).eval 0 =
      traceProbe P X := by
  simpa [traceProbe] using Matrix.derivative_det_one_add_X_smul (P * X)

/-- Equivalent coefficient form: the linear coefficient of the spectral
determinant coordinate is the projector trace. -/
theorem coeff_one_spectralDet_eq_traceProbe
    (P X : Matrix n n k) :
    (Matrix.det
      (1 + (Polynomial.X : k[X]) • (P * X).map Polynomial.C)).coeff 1 =
      traceProbe P X := by
  simpa [traceProbe] using Matrix.coeff_det_one_add_X_smul_one (P * X)

end
end Komorebi.StrongArtin.SpectralDeterminantDifferential

#print axioms Komorebi.StrongArtin.SpectralDeterminantDifferential.derivative_spectralDet_eq_traceProbe
#print axioms Komorebi.StrongArtin.SpectralDeterminantDifferential.coeff_one_spectralDet_eq_traceProbe
