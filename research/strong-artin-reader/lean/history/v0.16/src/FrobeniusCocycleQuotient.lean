import Mathlib.LinearAlgebra.Quotient.Basic
import SpectralTraceConjugacy

namespace Komorebi.StrongArtin.FrobeniusCocycleQuotient

open Komorebi.StrongArtin.SpectralTraceConjugacy

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- Conjugation by an invertible residual Frobenius matrix, as a linear map. -/
def conjugationLinear (A : (Matrix n n k)ˣ) :
    Matrix n n k →ₗ[k] Matrix n n k where
  toFun X := (A : Matrix n n k) * X * (↑A⁻¹ : Matrix n n k)
  map_add' X Y := by simp [Matrix.mul_add, Matrix.add_mul]
  map_smul' a X := by simp

@[simp]
theorem conjugationLinear_apply (A : (Matrix n n k)ˣ) (X : Matrix n n k) :
    conjugationLinear A X =
      (A : Matrix n n k) * X * (↑A⁻¹ : Matrix n n k) := rfl

/-- The local unramified coboundary operator `1 - Ad(A)`. -/
def frobeniusCoboundaryMap (A : (Matrix n n k)ˣ) :
    Matrix n n k →ₗ[k] Matrix n n k :=
  LinearMap.id - conjugationLinear A

@[simp]
theorem frobeniusCoboundaryMap_apply
    (A : (Matrix n n k)ˣ) (Y : Matrix n n k) :
    frobeniusCoboundaryMap A Y =
      Y - (A : Matrix n n k) * Y * (↑A⁻¹ : Matrix n n k) := rfl

/-- The subspace of tangent representatives differing by a local Frobenius coboundary. -/
def frobeniusCoboundaries (A : (Matrix n n k)ˣ) :
    Submodule k (Matrix n n k) :=
  LinearMap.range (frobeniusCoboundaryMap A)

/-- Left multiplication by a projector, as a linear map. -/
def leftMulLinear (P : Matrix n n k) :
    Matrix n n k →ₗ[k] Matrix n n k where
  toFun X := P * X
  map_add' X Y := by simp [Matrix.mul_add]
  map_smul' a X := by simp

/-- The trace functional associated with a spectral projector. -/
def traceProbeLinear (P : Matrix n n k) :
    Matrix n n k →ₗ[k] k :=
  (Matrix.traceLinearMap n k k).comp (leftMulLinear P)

@[simp]
theorem traceProbeLinear_apply (P X : Matrix n n k) :
    traceProbeLinear P X = traceProbe P X := rfl

/-- A projector commuting with Frobenius kills every local Frobenius coboundary. -/
theorem frobeniusCoboundaries_le_ker_traceProbe
    (A : (Matrix n n k)ˣ) (P : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    frobeniusCoboundaries A ≤ LinearMap.ker (traceProbeLinear P) := by
  rintro Z ⟨Y, rfl⟩
  rw [LinearMap.mem_ker]
  exact traceProbe_coboundary_eq_zero A P Y hcomm

/-- The projector trace descends to the quotient of unramified tangent
representatives by local Frobenius coboundaries. This is the linear-algebraic
core of the local Taylor--Wiles functional; no local Tate-duality normalization
is asserted here. -/
def frobeniusQuotientProbe
    (A : (Matrix n n k)ˣ) (P : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    (Matrix n n k ⧸ frobeniusCoboundaries A) →ₗ[k] k :=
  (frobeniusCoboundaries A).liftQ (traceProbeLinear P)
    (frobeniusCoboundaries_le_ker_traceProbe A P hcomm)

@[simp]
theorem frobeniusQuotientProbe_mkQ
    (A : (Matrix n n k)ˣ) (P X : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    frobeniusQuotientProbe A P hcomm
        ((frobeniusCoboundaries A).mkQ X) = traceProbe P X := rfl

/-- A nonzero projector trace gives a genuinely nonzero functional value on
the local Frobenius-cocycle quotient. -/
theorem frobeniusQuotientProbe_ne_zero_on_mkQ
    (A : (Matrix n n k)ˣ) (P X : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k))
    (hPX : traceProbe P X ≠ 0) :
    frobeniusQuotientProbe A P hcomm
        ((frobeniusCoboundaries A).mkQ X) ≠ 0 := by
  intro hzero
  apply hPX
  rw [← frobeniusQuotientProbe_mkQ A P X hcomm]
  exact hzero

end
end Komorebi.StrongArtin.FrobeniusCocycleQuotient

#print axioms Komorebi.StrongArtin.FrobeniusCocycleQuotient.frobeniusCoboundaries_le_ker_traceProbe
#print axioms Komorebi.StrongArtin.FrobeniusCocycleQuotient.frobeniusQuotientProbe_ne_zero_on_mkQ
