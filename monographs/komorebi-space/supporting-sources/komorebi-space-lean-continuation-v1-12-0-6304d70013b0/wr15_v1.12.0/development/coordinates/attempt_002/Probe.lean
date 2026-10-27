import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.ToLin

set_option autoImplicit false

/-!
# Coordinate covectors in an arbitrary full Hilbert basis

The basis is a basis of the entire correction space.  Coefficients and
covectors are finite real coordinate functions; every norm in the certificate
is the original Hilbert norm.  No nonemptiness assumption is made on the basis
index, so the zero-dimensional correction space is included.
-/

noncomputable section
universe u v w
namespace KomorebiSpace.CoordinateCovector
open Module
open scoped RealInnerProductSpace Matrix

variable {ι : Type u} [Fintype ι] [DecidableEq ι]
variable {H : Type v} [NormedAddCommGroup H] [InnerProductSpace ℝ H]

/-- Synthesis in a full, possibly nonorthonormal basis. -/
def synthesis (B : Basis ι ℝ H) (c : ι → ℝ) : H := B.equivFun.symm c

/-- The coordinate covector of a vector consists of its pairings with the basis. -/
def pairings (B : Basis ι ℝ H) (x : H) : ι → ℝ := fun i => ⟪B i, x⟫

/-- The Gram matrix uses the actual Hilbert inner product. -/
def gram (B : Basis ι ℝ H) : Matrix ι ι ℝ := fun i j => ⟪B i, B j⟫

theorem synthesis_eq_sum (B : Basis ι ℝ H) (c : ι → ℝ) :
    synthesis B c = ∑ i, c i • B i := by
  exact B.equivFun_symm_apply c

theorem synthesis_injective (B : Basis ι ℝ H) : Function.Injective (synthesis B) :=
  B.equivFun.symm.injective

theorem pairings_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) :
    pairings B (synthesis B c) = (gram B) *ᵥ c := by
  ext i
  simp [pairings, synthesis_eq_sum, gram, Matrix.mulVec, dotProduct]

theorem inner_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) (x : H) :
    ⟪synthesis B c, x⟫ = dotProduct c (pairings B x) := by
  simp [synthesis_eq_sum, pairings, dotProduct]

theorem gram_posDef (B : Basis ι ℝ H) : (gram B).PosDef := by
  refine Matrix.PosDef.of_dotProduct_mulVec_pos ?_ ?_
  · ext i j
    simp [Matrix.conjTranspose_apply, gram, real_inner_comm]
  · intro c hc
    have hz : synthesis B c ≠ 0 := by
      intro h
      apply hc
      exact B.equivFun.symm.injective (h.trans (map_zero B.equivFun.symm).symm)
    have hp := real_inner_self_pos.mpr hz
    rw [inner_synthesis, pairings_synthesis] at hp
    simpa using hp

theorem gram_isUnit (B : Basis ι ℝ H) : IsUnit (gram B) := (gram_posDef B).isUnit

theorem inverse_gram_pairings (B : Basis ι ℝ H) (x : H) :
    (gram B)⁻¹ *ᵥ pairings B x = B.equivFun x := by
  have h : pairings B x = gram B *ᵥ B.equivFun x := by
    rw [← pairings_synthesis]
    simp [synthesis]
  rw [h, Matrix.mulVec_mulVec,
    Matrix.nonsing_inv_mul _ (Matrix.isUnit_iff_isUnit_det.mp (gram_isUnit B)),
    Matrix.one_mulVec]

theorem reconstruct (B : Basis ι ℝ H) (x : H) :
    x = synthesis B ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [inverse_gram_pairings]
  simp [synthesis]

theorem norm_sq_pairings (B : Basis ι ℝ H) (x : H) :
    ‖x‖ ^ 2 = dotProduct (pairings B x) ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [← real_inner_self_eq_norm_sq]
  conv_lhs => lhs; rw [reconstruct B x]
  rw [inner_synthesis, dotProduct_comm]

end KomorebiSpace.CoordinateCovector
