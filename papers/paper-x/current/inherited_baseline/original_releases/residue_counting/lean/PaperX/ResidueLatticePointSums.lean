import PaperX.ResidueLatticeFibers
import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Finprod
import Mathlib.Analysis.Normed.Module.Ball.Pointwise

/-! Exact identification of residue-weighted counts with sums over actual lattice points. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ResidueLattice
open Set Module MeasureTheory
open scoped Pointwise BigOperators

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  (L₀ L : Submodule ℤ E)

/-- The exact residue-weighted count, using actual points in every fiber. -/
def weightedFiberCount [Fintype (Residues L₀ L)] (D : Set E) (w : Residues L₀ L → ℂ) (t : ℝ) : ℂ :=
  ∑ c, w c * (fiberCount L₀ L D c t : ℂ)

/-- The actual points of a lattice lying in the dilated region. -/
abbrev LatticePoints (D : Set E) (t : ℝ) := {x : L // (x : E) ∈ t • D}

/-- The quotient fiber of the bounded-point map is exactly the original residue fiber. -/
def pointFiberEquiv (D : Set E) (t : ℝ) (c : Residues L₀ L) :
    {x : LatticePoints L D t // (Submodule.Quotient.mk x.1 : Residues L₀ L) = c} ≃
    {x : L // (Submodule.Quotient.mk x : Residues L₀ L) = c ∧ (x : E) ∈ t • D} where
  toFun x := ⟨x.1.1, x.2, x.1.2⟩
  invFun x := ⟨⟨x.1, x.2.2⟩, x.2.1⟩
  left_inv _x := rfl
  right_inv _x := rfl

/-- An actual finite sum of residue weights over the points, independent of a chosen enumeration. -/
def latticePointSum (D : Set E) (w : Residues L₀ L → ℂ) (t : ℝ) : ℂ :=
  ∑ᶠ x : LatticePoints L D t, w (Submodule.Quotient.mk x.1)

variable [FiniteDimensional ℝ E] [DiscreteTopology L]

/-- A bounded region contains only finitely many points of the discrete lattice. -/
theorem finite_latticePoints {D : Set E} (hDb : Bornology.IsBounded D) (t : ℝ) :
    Finite (LatticePoints L D t) := by
  have hs : (t • D ∩ (L : Set E)).Finite :=
    Metric.finite_isBounded_inter_isClosed DiscreteTopology.isDiscrete
      (hDb.smul₀ t) (AddSubgroup.isClosed_of_discrete (H := L.toAddSubgroup))
  let : Finite (t • D ∩ (L : Set E) : Set E) := hs.to_subtype
  exact Finite.of_injective
    (fun x : LatticePoints L D t => (⟨x.1.1, x.2, x.1.2⟩ : (t • D ∩ (L : Set E) : Set E)))
    (by
      intro x y h
      apply Subtype.ext
      apply Subtype.ext
      exact congrArg (fun z : (t • D ∩ (L : Set E) : Set E) => z.1) h)

variable [Fintype (Residues L₀ L)]

/-- The finite residue decomposition is exactly the sum over the actual lattice points. -/
theorem weightedFiberCount_eq_pointSum {D : Set E} (hDb : Bornology.IsBounded D)
    (w : Residues L₀ L → ℂ) (t : ℝ) :
    weightedFiberCount L₀ L D w t = latticePointSum L₀ L D w t := by
  classical
  let : Finite (LatticePoints L D t) := finite_latticePoints L hDb t
  let : Fintype (LatticePoints L D t) := Fintype.ofFinite (LatticePoints L D t)
  unfold weightedFiberCount latticePointSum
  rw [finsum_eq_sum_of_fintype, ← Fintype.sum_fiberwise
    (fun x : LatticePoints L D t => (Submodule.Quotient.mk x.1 : Residues L₀ L))]
  apply Finset.sum_congr rfl
  intro c _
  have he := Nat.card_congr (pointFiberEquiv L₀ L D t c)
  change Nat.card _ = fiberCount L₀ L D c t at he
  rw [← he, Nat.card_eq_fintype_card]
  conv_rhs =>
    arg 2
    ext x
    rw [x.2]
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  exact mul_comm _ _

end PaperX.ResidueLattice
