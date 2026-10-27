import Mathlib.LinearAlgebra.Matrix.Trace

namespace Komorebi.StrongArtin.SpectralTraceConjugacy

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The trace functional attached to a spectral projector. -/
def traceProbe (P X : Matrix n n k) : k :=
  Matrix.trace (P * X)

/-- Simultaneous conjugation of a projector and tangent vector preserves the
trace-probe value. -/
theorem traceProbe_conj
    (H : (Matrix n n k)ˣ) (P X : Matrix n n k) :
    traceProbe
        ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
        ((H : Matrix n n k) * X * (↑H⁻¹ : Matrix n n k)) =
      traceProbe P X := by
  change
    Matrix.trace
      (((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k)) *
        ((H : Matrix n n k) * X * (↑H⁻¹ : Matrix n n k))) =
      Matrix.trace (P * X)
  have hmat :
      ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k)) *
          ((H : Matrix n n k) * X * (↑H⁻¹ : Matrix n n k)) =
        (H : Matrix n n k) * (P * X) * (↑H⁻¹ : Matrix n n k) := by
    simp [Matrix.mul_assoc]
  rw [hmat]
  exact Matrix.trace_units_conj H (P * X)

/-- A projector commuting with the residual Frobenius matrix annihilates the
local coboundary direction `Y - A Y A⁻¹`. -/
theorem traceProbe_coboundary_eq_zero
    (A : (Matrix n n k)ˣ) (P Y : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    traceProbe P
        (Y - (A : Matrix n n k) * Y * (↑A⁻¹ : Matrix n n k)) = 0 := by
  have hmat :
      P * ((A : Matrix n n k) * Y * (↑A⁻¹ : Matrix n n k)) =
        (A : Matrix n n k) * (P * Y) * (↑A⁻¹ : Matrix n n k) := by
    calc
      P * ((A : Matrix n n k) * Y * (↑A⁻¹ : Matrix n n k)) =
          (P * (A : Matrix n n k)) * Y * (↑A⁻¹ : Matrix n n k) := by
            simp [Matrix.mul_assoc]
      _ = ((A : Matrix n n k) * P) * Y * (↑A⁻¹ : Matrix n n k) := by
            rw [hcomm.eq]
      _ = (A : Matrix n n k) * (P * Y) * (↑A⁻¹ : Matrix n n k) := by
            simp [Matrix.mul_assoc]
  simp [traceProbe, Matrix.mul_sub, hmat, Matrix.trace_units_conj]

/-- Commutation with Frobenius is preserved by simultaneous conjugation. -/
theorem commute_conj
    (H A : (Matrix n n k)ˣ) (P : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    Commute
      ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
      ((H * A * H⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) := by
  change
    ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k)) *
        ((H * A * H⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) =
      ((H * A * H⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) *
        ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
  simpa [Matrix.mul_assoc] using congrArg
    (fun Z : Matrix n n k =>
      (H : Matrix n n k) * Z * (↑H⁻¹ : Matrix n n k)) hcomm.eq

/-- Full conjugacy-class invariance for the affine cocycle coordinate: after
transporting the spectral projector, the conjugated tangent value plus any
local coboundary has exactly the original detector value. -/
theorem traceProbe_affine_conjugacy
    (H A : (Matrix n n k)ˣ) (P X Y : Matrix n n k)
    (hcomm : Commute P (A : Matrix n n k)) :
    traceProbe
      ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
      (((H : Matrix n n k) * X * (↑H⁻¹ : Matrix n n k)) +
        (Y -
          ((H * A * H⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) * Y *
            (↑(H * A * H⁻¹)⁻¹ : Matrix n n k))) =
      traceProbe P X := by
  rw [traceProbe]
  rw [Matrix.mul_add, Matrix.trace_add]
  have hfirst := traceProbe_conj H P X
  have hsecond := traceProbe_coboundary_eq_zero
    (H * A * H⁻¹) ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k)) Y
    (commute_conj H A P hcomm)
  change
    traceProbe
        ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
        ((H : Matrix n n k) * X * (↑H⁻¹ : Matrix n n k)) +
      traceProbe
        ((H : Matrix n n k) * P * (↑H⁻¹ : Matrix n n k))
        (Y -
          ((H * A * H⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) * Y *
            (↑(H * A * H⁻¹)⁻¹ : Matrix n n k)) =
      traceProbe P X
  rw [hfirst, hsecond, add_zero]

end
end Komorebi.StrongArtin.SpectralTraceConjugacy

#print axioms Komorebi.StrongArtin.SpectralTraceConjugacy.traceProbe_conj
#print axioms Komorebi.StrongArtin.SpectralTraceConjugacy.traceProbe_coboundary_eq_zero
#print axioms Komorebi.StrongArtin.SpectralTraceConjugacy.traceProbe_affine_conjugacy
