module

public import KomorebiPhysics.CornerReconstruction
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum

/-!
Exact two-by-two witnesses for Chapter 7.  They demonstrate that the finite
pointwise algebra has only the zero derivation while the full matrix algebra
has genuinely nonzero inner derivations and curvature.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.CornerExamples

open KomorebiPaperVII
open CornerDerivation CornerCurvature CornerReconstruction
open scoped BigOperators Matrix

abbrev Idx := Fin 2
abbrev Mat2 := Matrix Idx Idx ℂ

/-- Diagonal Hermitian generator. -/
def K : Mat2 := !![(0:ℂ), 0; 0, 1]

/-- Hermitian off-diagonal matrix. -/
def L : Mat2 := !![(0:ℂ), 1; 1, 0]

/-- A second Hermitian observable. -/
def Z : Mat2 := !![(1:ℂ), 0; 0, -1]

/-- Exact coordinate packet family. -/
def coordinatePackets : PacketFamily Mat2 Idx where
  proj i := Matrix.single i i 1
  mul_proj := by
    intro i j
    by_cases h : i = j
    · subst j
      simp
    · simp [h, Matrix.single_mul_single_of_ne _ _ _ _ h]
  sum_proj := Matrix.sum_single_one

@[simp] theorem coordinate_proj_zero : coordinatePackets.proj 0 = !![(1:ℂ),0;0,0] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [coordinatePackets]

@[simp] theorem coordinate_proj_one : coordinatePackets.proj 1 = !![(0:ℂ),0;0,1] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [coordinatePackets]

theorem K_hermitian : K.conjTranspose = K := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [K, Matrix.conjTranspose_apply]

theorem L_hermitian : L.conjTranspose = L := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [L, Matrix.conjTranspose_apply]

theorem Z_hermitian : Z.conjTranspose = Z := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [Z, Matrix.conjTranspose_apply]

/-- The full matrix derivation is genuinely nonzero. -/
theorem delta_K_L_exact :
    delta K L = !![(0:ℂ), -Complex.I; Complex.I, 0] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [delta, K, L, Matrix.mul_apply, Fin.sum_univ_two]

theorem delta_K_L_nonzero : delta K L ≠ 0 := by
  rw [delta_K_L_exact]
  intro h
  have he := congrArg (fun M : Mat2 => M 0 1) h
  norm_num at he

/-- This exact witness separates the matrix corner algebra from the pointwise no-go. -/
theorem nonzero_finite_matrix_derivation : ∃ X : Mat2, delta K X ≠ 0 :=
  ⟨L, delta_K_L_nonzero⟩

/-- The curvature matrix is nonzero in the same model. -/
theorem curvature_K_L_exact :
    curvature K L = !![(0:ℂ), -Complex.I; Complex.I, 0] := by
  change delta K L = _
  exact delta_K_L_exact

theorem curvature_K_L_nonzero : curvature K L ≠ 0 := by
  rw [curvature_K_L_exact]
  intro h
  have he := congrArg (fun M : Mat2 => M 0 1) h
  norm_num at he

theorem curvature_K_L_hermitian : (curvature K L).conjTranspose = curvature K L :=
  curvature_hermitian K L K_hermitian L_hermitian

/-- A concrete nonzero curvature action. -/
theorem curvature_action_on_Z_exact :
    delta (curvature K L) Z = !![(0:ℂ), -2; -2, 0] := by
  rw [curvature_K_L_exact]
  have hI : (Complex.I : ℂ) * (Complex.I + Complex.I) = -2 := by
    rw [mul_add, Complex.I_mul_I]
    norm_num
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [delta, Z, Matrix.mul_apply, Fin.sum_univ_two]
  all_goals exact hI

theorem curvature_action_on_Z_nonzero : delta (curvature K L) Z ≠ 0 := by
  rw [curvature_action_on_Z_exact]
  intro h
  have he := congrArg (fun M : Mat2 => M 0 1) h
  norm_num at he

/-- The commutator of the two derivations is exactly the curvature action. -/
theorem derivation_commutator_on_Z :
    delta K (delta L Z) - delta L (delta K Z) = delta (curvature K L) Z :=
  derivation_commutator K L Z

/-- Star compatibility is nontrivial on the nonzero witness. -/
theorem delta_K_L_hermitian : (delta K L).conjTranspose = delta K L :=
  delta_preserves_hermitian K L K_hermitian L_hermitian

/-- The finite integration-by-parts identity on a nonzero triple. -/
theorem exact_trace_ibp :
    Matrix.trace (delta K L * Z) = - Matrix.trace (L * delta K Z) :=
  trace_integration_by_parts K L Z

/-- A nonzero instance of trace integration by parts, used to test the sign. -/
theorem exact_trace_ibp_nonzero_left :
    Matrix.trace (delta K L * delta K L) = 2 := by
  rw [delta_K_L_exact]
  norm_num [Matrix.trace, Matrix.mul_apply, Fin.sum_univ_two]

theorem exact_trace_ibp_nonzero_right :
    Matrix.trace (L * delta K (delta K L)) = -2 := by
  rw [delta_K_L_exact]
  norm_num [delta, K, L, Matrix.trace, Matrix.mul_apply, Fin.sum_univ_two, Complex.I_mul_I]

/-- Coordinate `(0,1)` differentiated corner is exactly `-i E_{01}`. -/
theorem offdiag_corner_exact :
    corner coordinatePackets (delta K L) 0 1 = Matrix.single 0 1 (-Complex.I) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [corner, coordinatePackets, delta, K, L, Matrix.single_apply,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- Coordinate `(1,0)` differentiated corner is the conjugate route. -/
theorem reverse_corner_exact :
    corner coordinatePackets (delta K L) 1 0 = Matrix.single 1 0 Complex.I := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [corner, coordinatePackets, delta, K, L, Matrix.single_apply,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- The diagonal differentiated corners vanish in this example. -/
theorem diagonal_corner_zero_00 : corner coordinatePackets (delta K L) 0 0 = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [corner, coordinatePackets, delta, K, L, Matrix.single_apply,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- The second diagonal differentiated corner also vanishes. -/
theorem diagonal_corner_zero_11 : corner coordinatePackets (delta K L) 1 1 = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [corner, coordinatePackets, delta, K, L, Matrix.single_apply,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- The exact path theorem reconstructs the nonzero `(0,1)` corner. -/
theorem offdiag_path_expansion :
    corner coordinatePackets (delta K L) 0 1 =
      Complex.I • (∑ c, pathTerm coordinatePackets K L 0 c 1) :=
  corner_delta_path coordinatePackets K L 0 1

/-- Every corner reconstructs the same nonzero derivative matrix. -/
theorem exact_corner_reconstruction :
    (∑ a, ∑ b, corner coordinatePackets (delta K L) a b) =
      !![(0:ℂ), -Complex.I; Complex.I, 0] := by
  rw [reconstruct_delta, delta_K_L_exact]

/-- The pointwise theorem specializes to two complex coordinates exactly. -/
theorem two_point_no_go
    (D : PointwiseNoGo.PointAlgebra Idx →ₗ[ℂ] PointwiseNoGo.PointAlgebra Idx)
    (hD : PointwiseNoGo.IsDerivation D) : D = 0 :=
  PointwiseNoGo.finite_source_no_go D hD

end KomorebiPhysics.CornerExamples
