module

public import KomorebiPhysics.TensorAtlas

/-!
Added finite entanglement test infrastructure for the tensor-atlas block.
A finite nonnegative mixture of product rank-one states has positive partial
transpose. The proof is by explicit entries and positive finite summation.
The example module supplies a negative quadratic pairing for the Bell state.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.EntanglementWitness
open scoped BigOperators Matrix Kronecker ComplexOrder
open MixedTransfer
variable {m n : Type*}

/-- Partial transpose on the second factor, explicitly in matrix indices. -/
def partialTransposeRight (ρ : Matrix (m × n) (m × n) ℂ) : Matrix (m × n) (m × n) ℂ :=
  fun x y => ρ (x.1,y.2) (y.1,x.2)

/-- Partial transposition commutes with finite summation. -/
theorem partialTranspose_sum {K : Type*} [Fintype K]
    (ρ : K → Matrix (m × n) (m × n) ℂ) :
    partialTransposeRight (∑ k, ρ k) = ∑ k, partialTransposeRight (ρ k) := by
  ext x y
  simp only [partialTransposeRight, Matrix.sum_apply]

/-- Real weights are not changed by partial transposition. -/
theorem partialTranspose_smul (w : ℝ) (ρ : Matrix (m × n) (m × n) ℂ) :
    partialTransposeRight (w • ρ) = w • partialTransposeRight ρ := rfl

/-- The partial transpose of a product pure state is another actual pure
state, with the second vector conjugated. -/
theorem partialTranspose_pureProduct (u : m → ℂ) (v : n → ℂ) :
    partialTransposeRight (pureState u ⊗ₖ pureState v) =
      pureState (fun x : m × n => u x.1 * star (v x.2)) := by
  ext x y
  simp only [partialTransposeRight, Matrix.kroneckerMap_apply, pureState,
    Matrix.vecMulVec_apply, Pi.star_apply, star_mul, star_star]
  ring

/-- A finite nonnegative sum of product pure states, with arbitrary unnormalized
local vectors. Excluding this larger cone also excludes normalized convex mixtures. -/
def HasFiniteProductDecomposition (ρ : Matrix (m × n) (m × n) ℂ) : Prop :=
  ∃ k : ℕ, ∃ w : Fin k → ℝ, ∃ u : Fin k → m → ℂ, ∃ v : Fin k → n → ℂ,
    (∀ r, 0 ≤ w r) ∧ ρ = ∑ r, w r • (pureState (u r) ⊗ₖ pureState (v r))

/-- Every explicitly finite product decomposition has positive partial
transpose. This is proved, not included as a decomposition field. -/
theorem partialTranspose_posSemidef_of_decomposition [Fintype m] [Fintype n]
    (ρ : Matrix (m × n) (m × n) ℂ) (hρ : HasFiniteProductDecomposition ρ) :
    (partialTransposeRight ρ).PosSemidef := by
  obtain ⟨k,w,u,v,hw,hρ⟩ := hρ
  rw [hρ, partialTranspose_sum]
  apply Matrix.posSemidef_sum Finset.univ
  intro r _
  rw [partialTranspose_smul, partialTranspose_pureProduct]
  exact (pureState_posSemidef _).smul (hw r)

/-- An exact failure of partial-transpose positivity rules out every such
finite mixture, not just a single tensor-product factorization. -/
theorem no_decomposition_of_partialTranspose_not_posSemidef [Fintype m] [Fintype n]
    (ρ : Matrix (m × n) (m × n) ℂ) (hρ : ¬ (partialTransposeRight ρ).PosSemidef) :
    ¬ HasFiniteProductDecomposition ρ :=
  fun h => hρ (partialTranspose_posSemidef_of_decomposition ρ h)

end KomorebiPhysics.EntanglementWitness
