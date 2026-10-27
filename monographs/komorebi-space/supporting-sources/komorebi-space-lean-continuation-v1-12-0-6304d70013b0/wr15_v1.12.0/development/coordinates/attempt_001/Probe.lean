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

end KomorebiSpace.CoordinateCovector
