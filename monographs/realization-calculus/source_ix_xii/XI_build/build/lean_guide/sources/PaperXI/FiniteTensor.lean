import Mathlib.LinearAlgebra.PiTensorProduct.Basis
import Mathlib.LinearAlgebra.PiTensorProduct.Finite
import Mathlib.RepresentationTheory.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank

/-! Actual tensor products indexed by an arbitrary finite family, with their
external product actions. The empty family retains its scalar tensor unit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteTensor
open TensorProduct

variable {ι K : Type*} [Field K] {H V : ι → Type*}
variable [∀ i, Monoid (H i)] [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]

/-- The external tensor representation, on Mathlib's actual multiple tensor product. -/
def representation (σ : ∀ i, Representation K (H i) (V i)) :
    Representation K (∀ i, H i) (PiTensorProduct K V) where
  toFun h := PiTensorProduct.map (fun i => σ i (h i))
  map_one' := by simp
  map_mul' h k := by
    simpa using PiTensorProduct.map_mul
      (fun i => σ i (h i)) (fun i => σ i (k i))

@[simp] theorem representation_tprod (σ : ∀ i, Representation K (H i) (V i))
    (h : ∀ i, H i) (v : ∀ i, V i) :
    representation σ h (PiTensorProduct.tprod K v) =
      PiTensorProduct.tprod K (fun i => σ i (h i) (v i)) :=
  PiTensorProduct.map_tprod _ _

/-- The actual tensor dimension is the product of the actual factor dimensions. -/
theorem finrank [Fintype ι] [∀ i, FiniteDimensional K (V i)] :
    Module.finrank K (PiTensorProduct K V) = ∏ i, Module.finrank K (V i) := by
  classical
  let b := Basis.piTensorProduct (fun i => Module.finBasis K (V i))
  rw [Module.finrank_eq_card_basis b]
  simp only [Fintype.card_pi, Fintype.card_fin]

/-- In particular, the empty family has dimension one. -/
theorem finrank_empty [Fintype ι] [IsEmpty ι] [∀ i, FiniteDimensional K (V i)] :
    Module.finrank K (PiTensorProduct K V) = 1 := by
  rw [finrank]
  simp

/-- A product of nonzero finite-dimensional factors is nonzero, including the empty family. -/
theorem nontrivial [Fintype ι] [∀ i, FiniteDimensional K (V i)] [∀ i, Nontrivial (V i)] :
    Nontrivial (PiTensorProduct K V) := by
  apply Module.nontrivial_of_finrank_pos (R := K)
  rw [finrank]
  exact Finset.prod_pos (fun i _ => Module.finrank_pos)

/-- The empty tensor equivalence intertwines the external action with the identity. -/
theorem empty_action [IsEmpty ι] (σ : ∀ i, Representation K (H i) (V i))
    (h : ∀ i, H i) (x : PiTensorProduct K V) : representation σ h x = x := by
  have hh : h = 1 := Subsingleton.elim _ _
  rw [hh, map_one]
  rfl

/-- Multiplying every factor by a scalar multiplies its tensor by their product. -/
theorem scalar_map [Fintype ι] (c : ι → K) :
    PiTensorProduct.map (fun i => c i • (LinearMap.id : V i →ₗ[K] V i)) =
      (∏ i, c i) • LinearMap.id := by
  apply PiTensorProduct.ext
  ext v
  simp only [LinearMap.compMultilinearMap_apply, PiTensorProduct.map_tprod,
    LinearMap.smul_apply, LinearMap.id_apply]
  exact (PiTensorProduct.tprod K).map_smul_univ c v

end PaperXI.FiniteTensor
