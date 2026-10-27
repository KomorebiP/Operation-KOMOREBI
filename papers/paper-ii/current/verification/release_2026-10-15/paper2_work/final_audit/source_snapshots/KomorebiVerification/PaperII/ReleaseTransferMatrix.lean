import Mathlib.LinearAlgebra.Matrix.Adjugate

/-! Shared determinant-adjugate construction and endpoint contraction.
The only inverse premise is for the scalar determinant. The power-series
specializations construct that inverse from the proved constant coefficient 1.
-/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferMatrix
universe u v w
variable {V : Type u} {P : Type v} {S : Type w}
variable [Fintype V] [DecidableEq V] [CommRing P] [CommRing S]

noncomputable def rationalMatrix (f : P →+* S) (T : Matrix V V P) (d : S) :
    Matrix V V S := d • f.mapMatrix (Matrix.adjugate T)

theorem map_mul_adjugate (f : P →+* S) (T : Matrix V V P) :
    f.mapMatrix T * f.mapMatrix (Matrix.adjugate T) =
      f (Matrix.det T) • (1 : Matrix V V S) := by
  calc
    _ = f.mapMatrix (Matrix.det T • (1 : Matrix V V P)) := by
      simpa using congrArg f.mapMatrix (Matrix.mul_adjugate T)
    _ = _ := by
      ext i j
      by_cases h : i = j <;> simp [RingHom.mapMatrix_apply, Matrix.map_apply, h]

theorem map_adjugate_mul (f : P →+* S) (T : Matrix V V P) :
    f.mapMatrix (Matrix.adjugate T) * f.mapMatrix T =
      f (Matrix.det T) • (1 : Matrix V V S) := by
  calc
    _ = f.mapMatrix (Matrix.det T • (1 : Matrix V V P)) := by
      simpa using congrArg f.mapMatrix (Matrix.adjugate_mul T)
    _ = _ := by
      ext i j
      by_cases h : i = j <;> simp [RingHom.mapMatrix_apply, Matrix.map_apply, h]

theorem mul_rationalMatrix (f : P →+* S) (T : Matrix V V P) (d : S)
    (h : d * f (Matrix.det T) = 1) :
    f.mapMatrix T * rationalMatrix f T d = 1 := by
  rw [rationalMatrix, Matrix.mul_smul, map_mul_adjugate, smul_smul, h, one_smul]

theorem rationalMatrix_mul (f : P →+* S) (T : Matrix V V P) (d : S)
    (h : d * f (Matrix.det T) = 1) :
    rationalMatrix f T d * f.mapMatrix T = 1 := by
  rw [rationalMatrix, Matrix.smul_mul, map_adjugate_mul, smul_smul, h, one_smul]

theorem denominator_smul_rationalMatrix (f : P →+* S) (T : Matrix V V P) (d : S)
    (h : f (Matrix.det T) * d = 1) :
    f (Matrix.det T) • rationalMatrix f T d = f.mapMatrix (Matrix.adjugate T) := by
  rw [rationalMatrix, smul_smul, h, one_smul]

def contract (u : V → P) (M : Matrix V V P) (v : V → P) : P :=
  ∑ i, ∑ j, u i * M i j * v j

theorem contract_map (f : P →+* S) (u v : V → P) (M : Matrix V V P) :
    contract (f ∘ u) (f.mapMatrix M) (f ∘ v) = f (contract u M v) := by
  simp [contract, map_sum, map_mul, RingHom.mapMatrix_apply, Matrix.map_apply]

omit [DecidableEq V] in
theorem mul_contract (a : P) (u v : V → P) (M : Matrix V V P) :
    a * contract u M v = contract u (a • M) v := by
  simp only [contract, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  change a * (u i * M i j * v j) = u i * (a * M i j) * v j
  ac_rfl

theorem rational_endpoint_identity (f : P →+* S) (T : Matrix V V P) (d : S)
    (h : f (Matrix.det T) * d = 1) (u v : V → P) :
    f (Matrix.det T) * contract (f ∘ u) (rationalMatrix f T d) (f ∘ v) =
      f (contract u (Matrix.adjugate T) v) := by
  rw [mul_contract, denominator_smul_rationalMatrix f T d h, contract_map]

end Komorebi.PaperII.ReleaseTransferMatrix
