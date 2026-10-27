import Komorebi.FDGaussianTransport
import Mathlib.Data.Matrix.ColumnRowPartitioned

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix MeasureTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- Pack two Euclidean vectors into disjoint coordinate blocks. -/
def pack (z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) :
    EuclideanSpace ℝ (ι ⊕ κ) := EuclideanSpace.sumEquivProd.symm z

@[simp] theorem pack_inl (z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) (i : ι) :
    pack z (Sum.inl i) = z.1 i := rfl
@[simp] theorem pack_inr (z : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) (j : κ) :
    pack z (Sum.inr j) = z.2 j := rfl

@[fun_prop] theorem measurable_pack : Measurable (pack (ι := ι) (κ := κ)) :=
  EuclideanSpace.sumEquivProd.symm.continuous.measurable

@[simp] theorem pack_add (z w : EuclideanSpace ℝ ι × EuclideanSpace ℝ κ) :
    pack (z+w) = pack z + pack w := map_add EuclideanSpace.sumEquivProd.symm z w

/-- Equality after packing is equality of the original joint measures. -/
theorem map_pack_injective :
    Function.Injective (Measure.map (pack (ι := ι) (κ := κ))) := by
  exact EuclideanSpace.sumEquivProd.symm.toHomeomorph.measurableEmbedding.map_injective

/-- Stacking rectangular matrices agrees with packing their outputs. -/
theorem matrixCLM_fromRows
    {η : Type*} [Fintype η] [DecidableEq η]
    (A : Matrix ι η ℝ) (B : Matrix κ η ℝ) (x : EuclideanSpace ℝ η) :
    matrixCLM (Matrix.fromRows A B) x = pack (matrixCLM A x, matrixCLM B x) := by
  ext i
  cases i <;> simp [matrixCLM_apply, Matrix.fromRows_mulVec]

end Komorebi.FiniteDimensionalGaussianKalman
