import KomorebiLSM.BasisDecoder

set_option autoImplicit false
namespace Komorebi.LSM.BasisCoordinates
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E] {m r : ℕ} {P Q : Submodule ℝ E}

/-- Columns of a subspace basis in an ambient orthonormal basis. -/
noncomputable def columns (W : OrthonormalBasis (Fin m) ℝ E)
    (U : OrthonormalBasis (Fin r) ℝ P) : Matrix (Fin m) (Fin r) ℝ :=
  LinearMap.toMatrix U.toBasis W.toBasis P.subtype

theorem columns_entry (W : OrthonormalBasis (Fin m) ℝ E)
    (U : OrthonormalBasis (Fin r) ℝ P) (i : Fin m) (j : Fin r) :
    columns W U i j = inner ℝ (W i) (U j:E) := by
  simp [columns, LinearMap.toMatrix_apply, W.repr_apply_apply]

theorem cross_eq_transpose_mul (W : OrthonormalBasis (Fin m) ℝ E)
    (U : OrthonormalBasis (Fin r) ℝ P) (V : OrthonormalBasis (Fin r) ℝ Q) :
    cross U V = (columns W V).transpose * columns W U := by
  ext i j
  rw [cross_entry, Matrix.mul_apply]
  simp only [Matrix.transpose_apply, columns_entry]
  simpa only [real_inner_comm (V i:E)] using
    (W.sum_inner_mul_inner (V i:E) (U j:E)).symm

theorem columns_action (W : OrthonormalBasis (Fin m) ℝ E)
    (U : OrthonormalBasis (Fin r) ℝ P) (y : EuclideanSpace ℝ (Fin r)) :
    (columns W U).toEuclideanLin y = W.repr (synthesis U y) :=
  matrix_action U W P.subtype y

/-- Literal ambient matrix formula for the decoder, with the ordinary matrix inverse. -/
theorem decoder_matrix_formula (W : OrthonormalBasis (Fin m) ℝ E)
    (U : OrthonormalBasis (Fin r) ℝ P) (V : OrthonormalBasis (Fin r) ℝ Q)
    (y : EuclideanSpace ℝ (Fin r)) :
    W.repr (decoder U V y) =
      (columns W U * ((columns W V).transpose * columns W U)⁻¹).toEuclideanLin y := by
  rw [← cross_eq_transpose_mul W U V]
  change W.repr (synthesis U ((cross U V)⁻¹.toEuclideanLin y)) = _
  rw [← columns_action]
  exact (congrArg (fun T : EuclideanSpace ℝ (Fin r) →ₗ[ℝ] EuclideanSpace ℝ (Fin m) => T y)
    (Matrix.toLpLin_mul_same 2 (columns W U) (cross U V)⁻¹)).symm

end Komorebi.LSM.BasisCoordinates
