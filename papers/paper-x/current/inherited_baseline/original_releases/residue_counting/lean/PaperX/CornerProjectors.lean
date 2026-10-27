import PaperX.AdicIdempotent
import PaperX.MatrixProjector

/-! Polynomial correction inside a supplied equivariant corner, and detection
of a zero idempotent in an adically separated matrix algebra. -/
set_option autoImplicit false
namespace PaperX.CornerProjectors
open PaperX.RepresentationLimits PaperX.MatrixProjector PaperX.AdicIdempotent

variable {R Γ ι : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι]

/-- Correct an approximate idempotent while retaining both support equations
in an exact equivariant corner. -/
theorem exists_in_corner (I : Ideal R) [IsAdicComplete I R]
    (k : ℕ) (hk : 0 < k) (ρ : MatrixRep R Γ ι)
    (C : Projector ρ) (A : Matrix ι ι R)
    (hcomm : ∀ g, ρ g * A = A * ρ g)
    (hid : (A.map (Ideal.Quotient.mk (I^k)))^2 =
      A.map (Ideal.Quotient.mk (I^k)))
    (hleft : C.matrix.map (Ideal.Quotient.mk (I^k)) *
        A.map (Ideal.Quotient.mk (I^k)) = A.map (Ideal.Quotient.mk (I^k)))
    (hright : A.map (Ideal.Quotient.mk (I^k)) *
        C.matrix.map (Ideal.Quotient.mk (I^k)) = A.map (Ideal.Quotient.mk (I^k))) :
    ∃ P : Projector ρ,
      P.matrix.map (Ideal.Quotient.mk (I^k)) = A.map (Ideal.Quotient.mk (I^k)) ∧
      C.matrix * P.matrix = P.matrix ∧ P.matrix * C.matrix = P.matrix := by
  let f := Ideal.Quotient.mk (I^k)
  let B := C.matrix * A * C.matrix
  have hB : B.map f = A.map f := by
    dsimp [B]
    rw [Matrix.map_mul, Matrix.map_mul, hleft, hright]
  have hBC : C.matrix * B = B * C.matrix := by
    dsimp [B]
    simp only [← mul_assoc, C.idempotent]
    rw [mul_assoc (C.matrix * A), C.idempotent]
  have hBρ (g : Γ) : ρ g * B = B * ρ g := by
    dsimp [B]
    calc
      ρ g * (C.matrix * A * C.matrix) =
          (ρ g * C.matrix) * A * C.matrix := by simp only [mul_assoc]
      _ = (C.matrix * ρ g) * A * C.matrix := by rw [C.commutes]
      _ = C.matrix * (ρ g * A) * C.matrix := by simp only [mul_assoc]
      _ = C.matrix * (A * ρ g) * C.matrix := by rw [hcomm]
      _ = C.matrix * A * (ρ g * C.matrix) := by simp only [mul_assoc]
      _ = C.matrix * A * (C.matrix * ρ g) := by rw [C.commutes]
      _ = (C.matrix * A * C.matrix) * ρ g := by simp only [mul_assoc]
  obtain ⟨Q, hQ, hred, hQcomm⟩ := correct_commuting I k hk B (by rw [hB]; exact hid)
  have hCQ := hQcomm C.matrix hBC
  have hQρ (g : Γ) := hQcomm (ρ g) (hBρ g)
  have hQQ : Q * Q = Q := by simpa only [pow_two] using hQ
  let P : Projector ρ := {
    matrix := C.matrix * Q
    idempotent := by
      calc
        C.matrix * Q * (C.matrix * Q) = C.matrix * (Q * C.matrix) * Q := by
          simp only [mul_assoc]
        _ = C.matrix * (C.matrix * Q) * Q := by rw [← hCQ]
        _ = (C.matrix * C.matrix) * (Q * Q) := by simp only [mul_assoc]
        _ = C.matrix * Q := by rw [C.idempotent, hQQ]
    commutes := fun g => by
      calc
        ρ g * (C.matrix * Q) = (ρ g * C.matrix) * Q := by rw [mul_assoc]
        _ = (C.matrix * ρ g) * Q := by rw [C.commutes]
        _ = C.matrix * (ρ g * Q) := by rw [mul_assoc]
        _ = C.matrix * (Q * ρ g) := by rw [hQρ]
        _ = (C.matrix * Q) * ρ g := by rw [mul_assoc] }
  refine ⟨P, ?_, ?_, ?_⟩
  · change (C.matrix * Q).map f = A.map f
    rw [Matrix.map_mul, hred, hB, hleft]
  · change C.matrix * (C.matrix * Q) = C.matrix * Q
    rw [← mul_assoc, C.idempotent]
  · change (C.matrix * Q) * C.matrix = C.matrix * Q
    rw [mul_assoc, ← hCQ, ← mul_assoc, C.idempotent]

/-- An idempotent reducing to zero at any positive depth is zero.
Only adic separatedness, provided here by completeness, is used. -/
theorem eq_zero_of_idempotent_reduces_zero (I : Ideal R) [IsAdicComplete I R]
    (k : ℕ) (hk : 0 < k) (E : Matrix ι ι R) (hid : E * E = E)
    (hzero : E.map (Ideal.Quotient.mk (I^k)) = 0) : E = 0 := by
  have hmem : E ∈ I.matrix ι :=
    Ideal.matrix_monotone ι (Ideal.pow_le_self (by omega : k ≠ 0))
      ((map_eq_zero_iff (I^k) E).mp hzero)
  have hall (n : ℕ) : E ∈ (I^n).matrix ι := by
    induction n with
    | zero => simp
    | succ n ih =>
      rw [← hid, pow_succ]
      exact matrix_mul_mem _ _ ih hmem
  apply matrix_ext I
  intro n
  simp only [Matrix.map_zero, map_zero]
  exact (map_eq_zero_iff (I^n) E).mpr (hall n)

end PaperX.CornerProjectors
