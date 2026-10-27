import FrobeniusCocycleQuotient
import SpectralDeterminantDifferential

namespace Komorebi.StrongArtin.LocalTaylorWilesLinearInterface

open Polynomial
open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.SpectralDeterminantDifferential

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The exact linear-algebraic local datum used by a Frobenius-block
Taylor--Wiles condition. The arithmetic theorem identifying this quotient with
the relevant local Tate-dual tangent quotient remains external. -/
structure LocalSpectralLinearDatum where
  frobenius : (Matrix n n k)ˣ
  projector : Matrix n n k
  commutes : Commute projector (frobenius : Matrix n n k)

namespace LocalSpectralLinearDatum

/-- The canonical scalar functional on the local Frobenius-cocycle quotient. -/
def localFunctional (D : LocalSpectralLinearDatum (k := k) (n := n)) :
    (Matrix n n k ⧸ frobeniusCoboundaries D.frobenius) →ₗ[k] k :=
  frobeniusQuotientProbe D.frobenius D.projector D.commutes

@[simp]
theorem localFunctional_mkQ
    (D : LocalSpectralLinearDatum (k := k) (n := n))
    (X : Matrix n n k) :
    D.localFunctional ((frobeniusCoboundaries D.frobenius).mkQ X) =
      traceProbe D.projector X := rfl

/-- The local quotient functional is exactly the first derivative of the
selected block-determinant coordinate. -/
theorem localFunctional_eq_spectralDet_derivative
    (D : LocalSpectralLinearDatum (k := k) (n := n))
    (X : Matrix n n k) :
    D.localFunctional ((frobeniusCoboundaries D.frobenius).mkQ X) =
      (derivative <|
        Matrix.det
          (1 + (Polynomial.X : k[X]) •
            (D.projector * X).map Polynomial.C)).eval 0 := by
  rw [D.localFunctional_mkQ]
  symm
  exact derivative_spectralDet_eq_traceProbe D.projector X

/-- A nonzero spectral derivative is a nonzero class detector on the local
Frobenius-cocycle quotient. -/
theorem localFunctional_ne_zero_of_spectralDerivative
    (D : LocalSpectralLinearDatum (k := k) (n := n))
    (X : Matrix n n k)
    (h : (derivative <|
      Matrix.det
        (1 + (Polynomial.X : k[X]) •
          (D.projector * X).map Polynomial.C)).eval 0 ≠ 0) :
    D.localFunctional ((frobeniusCoboundaries D.frobenius).mkQ X) ≠ 0 := by
  rw [D.localFunctional_eq_spectralDet_derivative]
  exact h

end LocalSpectralLinearDatum

end
end Komorebi.StrongArtin.LocalTaylorWilesLinearInterface

#print axioms Komorebi.StrongArtin.LocalTaylorWilesLinearInterface.LocalSpectralLinearDatum.localFunctional_eq_spectralDet_derivative
#print axioms Komorebi.StrongArtin.LocalTaylorWilesLinearInterface.LocalSpectralLinearDatum.localFunctional_ne_zero_of_spectralDerivative
