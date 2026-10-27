import SpectralTraceConjugacy
import Mathlib.Tactic

namespace Komorebi.StrongArtin.MatrixCocycleConjugacy

open Komorebi.StrongArtin.SpectralTraceConjugacy

noncomputable section

variable {k n G : Type*} [Field k] [Fintype n] [DecidableEq n] [Group G]

/-- A normalized matrix-valued one-cocycle for the conjugation action attached
to a residual matrix representation. -/
structure MatrixCocycleData (q : G →* (Matrix n n k)ˣ) where
  value : G → Matrix n n k
  map_one : value 1 = 0
  map_mul : ∀ g h : G,
    value (g * h) = value g +
      (q g : Matrix n n k) * value h * (↑(q g)⁻¹ : Matrix n n k)

namespace MatrixCocycleData

variable (q : G →* (Matrix n n k)ˣ)

@[simp]
theorem value_inv (f : MatrixCocycleData q) (g : G) :
    f.value g⁻¹ =
      -((↑(q g)⁻¹ : Matrix n n k) * f.value g * (q g : Matrix n n k)) := by
  have h := f.map_mul g g⁻¹
  rw [mul_inv_cancel, f.map_one] at h
  have h' :
      (q g : Matrix n n k) * f.value g⁻¹ * (↑(q g)⁻¹ : Matrix n n k) =
        -f.value g := by
    rw [eq_neg_iff_add_eq_zero]
    simpa [add_comm] using h.symm
  have := congrArg
    (fun X : Matrix n n k =>
      (↑(q g)⁻¹ : Matrix n n k) * X * (q g : Matrix n n k)) h'
  simpa [Matrix.mul_assoc] using this

/-- Exact affine conjugation formula for a matrix-valued cocycle. -/
theorem value_conj (f : MatrixCocycleData q) (h g : G) :
    f.value (h * g * h⁻¹) =
      (q h : Matrix n n k) * f.value g * (↑(q h)⁻¹ : Matrix n n k) +
      (f.value h -
        ((q h * q g * (q h)⁻¹ : (Matrix n n k)ˣ) : Matrix n n k) *
          f.value h *
          (↑(q h * q g * (q h)⁻¹)⁻¹ : Matrix n n k)) := by
  rw [f.map_mul, f.map_mul, value_inv q f]
  simp [Matrix.mul_assoc]
  abel

/-- Spectral-projector detection is a property of the finite conjugacy class:
a projector commuting with the residual element transports under conjugation,
and its nonzero cocycle evaluation is unchanged. -/
theorem traceProbe_value_conj
    (f : MatrixCocycleData q) (h g : G)
    (P : Matrix n n k)
    (hcomm : Commute P (q g : Matrix n n k)) :
    traceProbe
      ((q h : Matrix n n k) * P * (↑(q h)⁻¹ : Matrix n n k))
      (f.value (h * g * h⁻¹)) =
      traceProbe P (f.value g) := by
  rw [value_conj q f]
  simpa using traceProbe_affine_conjugacy
    (q h) (q g) P (f.value g) (f.value h) hcomm

/-- Nonvanishing of the transported projector detector survives conjugacy. -/
theorem traceProbe_value_conj_ne_zero
    (f : MatrixCocycleData q) (h g : G)
    (P : Matrix n n k)
    (hcomm : Commute P (q g : Matrix n n k))
    (hdet : traceProbe P (f.value g) ≠ 0) :
    traceProbe
      ((q h : Matrix n n k) * P * (↑(q h)⁻¹ : Matrix n n k))
      (f.value (h * g * h⁻¹)) ≠ 0 := by
  rw [traceProbe_value_conj q f h g P hcomm]
  exact hdet

end MatrixCocycleData

end
end Komorebi.StrongArtin.MatrixCocycleConjugacy

#print axioms Komorebi.StrongArtin.MatrixCocycleConjugacy.MatrixCocycleData.value_conj
#print axioms Komorebi.StrongArtin.MatrixCocycleConjugacy.MatrixCocycleData.traceProbe_value_conj_ne_zero
