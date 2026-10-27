import ZModSquareZeroLayer
import MatrixSquareZeroObstruction
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Algebra.Field.ZMod

/-! Entrywise coordinates on the actual square-zero matrix kernel. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic
open SquareZeroH2
variable (p m : ℕ) (hpm : p ∣ m) (n : Type) [Fintype n] [DecidableEq n]

def matrixDatum : Datum PUnit (Matrix n n (Upper p m)) (Matrix n n (Lower m)) where
  q := (reduction p m).mapMatrix
  squareZero := matrix_kernel_squareZero (reduction p m) (reduction_squareZero p m hpm)
  rho := 1
  lift := fun _ => 1
  lift_one := rfl
  lift_residue := by intro g; simp

theorem matrix_reduction_surjective :
    Function.Surjective (matrixDatum p m hpm n).q :=
  matrix_map_surjective (reduction p m) (reduction_surjective p m)

/-- A starting upper Frobenius exists; no multiplicative section is assumed. -/
theorem lift_lower_frobenius (Fbar : (Matrix n n (Lower m))ˣ) :
    ∃ F : (Matrix n n (Upper p m))ˣ, (matrixDatum p m hpm n).q F = (Fbar : Matrix n n (Lower m)) :=
  units_lift_across_square_zero (matrixDatum p m hpm n).q
    (matrix_reduction_surjective p m hpm n) (matrixDatum p m hpm n).squareZero Fbar

def matrixLayerEmbedding : Matrix n n (ZMod p) →+ Matrix n n (Upper p m) where
  toFun X i j := layerEmbedding p m (X i j)
  map_zero' := by ext i j; exact map_zero _
  map_add' X Y := by ext i j; exact map_add _ _ _

def matrixKernelEmbedding : Matrix n n (ZMod p) →+ (matrixDatum p m hpm n).Kernel where
  toFun X := ⟨matrixLayerEmbedding p m n X, by ext i j; exact reduction_layerEmbedding p m (X i j)⟩
  map_zero' := by apply Subtype.ext; exact map_zero _
  map_add' X Y := by apply Subtype.ext; exact map_add _ X Y

theorem matrixKernelEmbedding_bijective (hm : m ≠ 0) :
    Function.Bijective (matrixKernelEmbedding p m hpm n) := by
  constructor
  · intro X Y h
    ext i j
    apply layerEmbedding_injective p m hm
    exact congrFun (congrFun (congrArg Subtype.val h) i) j
  · intro X
    have hx : ∀ i j, ∃ z : ZMod p, layerEmbedding p m z = X.val i j := by
      intro i j
      apply (mem_kernel_iff_layerEmbedding p m _).1
      exact congrFun (congrFun X.property i) j
    choose z hz using hx
    exact ⟨z, Subtype.ext (funext fun i => funext fun j => hz i j)⟩

def matrixKernelEquiv (hm : m ≠ 0) :
    Matrix n n (ZMod p) ≃+ (matrixDatum p m hpm n).Kernel :=
  AddEquiv.ofBijective (matrixKernelEmbedding p m hpm n)
    (matrixKernelEmbedding_bijective p m hpm n hm)

def kernelCoordinates (hm : m ≠ 0) :
    (matrixDatum p m hpm n).Kernel ≃+ Matrix n n (ZMod p) :=
  (matrixKernelEquiv p m hpm n hm).symm

@[simp] theorem coordinates_embedding (hm : m ≠ 0) (X : Matrix n n (ZMod p)) :
    kernelCoordinates p m hpm n hm (matrixKernelEmbedding p m hpm n X) = X :=
  (matrixKernelEquiv p m hpm n hm).symm_apply_apply X

@[simp] theorem embedding_coordinates (hm : m ≠ 0) (X : (matrixDatum p m hpm n).Kernel) :
    matrixKernelEmbedding p m hpm n (kernelCoordinates p m hpm n hm X) = X :=
  (matrixKernelEquiv p m hpm n hm).apply_symm_apply X

omit [DecidableEq n] in
/-- A matrix times a kernel matrix acts by its reduction mod p. -/
theorem matrix_mul_layerEmbedding (A : Matrix n n (Upper p m)) (X : Matrix n n (ZMod p)) :
    A * matrixLayerEmbedding p m n X =
      matrixLayerEmbedding p m n (A.map (residue p m) * X) := by
  ext i j
  change (∑ t, A i t * layerEmbedding p m (X t j)) =
    layerEmbedding p m (∑ t, residue p m (A i t) * X t j)
  rw [map_sum]
  exact Finset.sum_congr rfl fun t _ => mul_layerEmbedding p m (A i t) (X t j)

omit [DecidableEq n] in
theorem matrix_layerEmbedding_mul (X : Matrix n n (ZMod p)) (A : Matrix n n (Upper p m)) :
    matrixLayerEmbedding p m n X * A =
      matrixLayerEmbedding p m n (X * A.map (residue p m)) := by
  ext i j
  change (∑ t, layerEmbedding p m (X i t) * A t j) =
    layerEmbedding p m (∑ t, X i t * residue p m (A t j))
  rw [map_sum]
  exact Finset.sum_congr rfl fun t _ => layerEmbedding_mul p m (A t j) (X i t)

def residualFrobenius (F : (Matrix n n (Upper p m))ˣ) : (Matrix n n (ZMod p))ˣ :=
  Units.map (residue p m).mapMatrix.toMonoidHom F

def residualAdjoint (F : (Matrix n n (Upper p m))ˣ) :
    Module.End (ZMod p) (Matrix n n (ZMod p)) where
  toFun X := (residualFrobenius p m n F : Matrix n n (ZMod p)) * X *
    (↑(residualFrobenius p m n F)⁻¹ : Matrix n n (ZMod p))
  map_add' X Y := by simp [Matrix.mul_add, Matrix.add_mul]
  map_smul' a X := by simp

theorem conjugate_embedding (F : (Matrix n n (Upper p m))ˣ) (X : Matrix n n (ZMod p)) :
    (matrixDatum p m hpm n).conjugate F (matrixKernelEmbedding p m hpm n X) =
      matrixKernelEmbedding p m hpm n (residualAdjoint p m n F X) := by
  apply Subtype.ext
  change (F : Matrix n n (Upper p m)) * matrixLayerEmbedding p m n X *
    (↑F⁻¹ : Matrix n n (Upper p m)) = _
  rw [matrix_mul_layerEmbedding, matrix_layerEmbedding_mul]
  rfl

/-- Actual upper-ring conjugation becomes the residual adjoint operator. -/
theorem conjugation_coordinates (hm : m ≠ 0) (F : (Matrix n n (Upper p m))ˣ)
    (X : (matrixDatum p m hpm n).Kernel) :
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).conjugate F X) =
      residualAdjoint p m n F (kernelCoordinates p m hpm n hm X) := by
  nth_rw 1 [← embedding_coordinates p m hpm n hm X]
  rw [conjugate_embedding, coordinates_embedding]

/-- The layer action depends only on Frobenius mod p, not its higher coefficients. -/
theorem residualAdjoint_eq_of_residualFrobenius_eq
    (F F' : (Matrix n n (Upper p m))ˣ)
    (h : residualFrobenius p m n F = residualFrobenius p m n F') :
    residualAdjoint p m n F = residualAdjoint p m n F' := by
  ext X i j
  simp only [residualAdjoint, LinearMap.coe_mk, AddHom.coe_mk, h]

end Komorebi.StrongArtin.MixedCharacteristic
