import PaperXI.OnePlusIntersection110
import Mathlib.NumberTheory.LocalField.Basic
import Mathlib.LinearAlgebra.Matrix.Ideal
import Mathlib.Topology.Algebra.LinearTopology
import Mathlib.Topology.Algebra.OpenSubgroup
import Mathlib.Topology.Algebra.Group.Matrix
import Mathlib.Topology.Algebra.ValuativeRel.ValuativeTopology

/-! A common open ideal in an actual coordinate integral matrix order.
The ideal lives in the integral order, not the full field matrix algebra. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CoordinateDeepIdeal111
open Matrix Topology Filter
open scoped Topology

section MatrixNeighborhood
variable {R m : Type*} [Ring R] [TopologicalSpace R]
  [IsTopologicalRing R] [IsLinearTopology R R] [Fintype m] [DecidableEq m]

def uncurryHomeomorph : Matrix m m R ≃ₜ ((m × m) → R) where
  toFun x p := x p.1 p.2
  invFun x i j := x (i,j)
  left_inv _ := rfl
  right_inv _ := rfl
  continuous_toFun := by fun_prop
  continuous_invFun := by fun_prop

/-- Every actual matrix zero-neighborhood contains matrices over one open
coefficient ideal. This constructs an ideal of the integral matrix ring. -/
theorem exists_open_matrix_ideal_subset (U : Set (Matrix m m R))
    (hU : U ∈ 𝓝 0) : ∃ I : Ideal R, IsOpen (I : Set R) ∧
      (I.matrix m : Set (Matrix m m R)) ⊆ U := by
  have hpre : (uncurryHomeomorph (R := R) (m := m)).symm ⁻¹' U ∈
      𝓝 (0 : (m × m) → R) :=
    (uncurryHomeomorph (R := R) (m := m)).symm.continuous.continuousAt hU
  rw [nhds_pi] at hpre
  obtain ⟨⟨s, I⟩, ⟨_, hI⟩, hsub⟩ :=
    (IsLinearTopology.hasBasis_open_ideal (R := R)).pi_self.mem_iff.mp hpre
  refine ⟨I, hI, ?_⟩
  intro x hx
  exact hsub (fun p _ => hx p.1 p.2)

omit [IsTopologicalRing R] [IsLinearTopology R R] in
theorem matrix_ideal_open (I : Ideal R) (hI : IsOpen (I : Set R)) :
    IsOpen (I.matrix m : Set (Matrix m m R)) := by
  have he : (I.matrix m : Set (Matrix m m R)) =
      ⋂ i, ⋂ j, {x : Matrix m m R | x i j ∈ I} := by ext x; simp
  rw [he]
  apply isOpen_iInter_of_finite
  intro i
  apply isOpen_iInter_of_finite
  intro j
  exact hI.preimage ((continuous_apply j).comp (continuous_apply i))

end MatrixNeighborhood

section CompactOrder
variable {R m : Type*} [Ring R] [TopologicalSpace R] [IsTopologicalRing R]
  [IsLinearTopology R R] [CompactSpace R] [Fintype m] [DecidableEq m]

/-- Containment and finiteness are constructed from openness inside the literal
compact integral matrix order, rather than supplied as hypotheses. -/
theorem exists_common_ideal_finite (L M : AddSubgroup (Matrix m m R))
    (hL : IsOpen (L : Set (Matrix m m R)))
    (hM : IsOpen (M : Set (Matrix m m R))) :
    ∃ I : Ideal R, IsOpen (I : Set R) ∧
      (I.matrix m).toAddSubgroup ≤ L ⊓ M ∧
      Finite (L ⧸ (I.matrix m).toAddSubgroup.addSubgroupOf L) := by
  let : CompactSpace (Matrix m m R) := inferInstanceAs (CompactSpace (m → m → R))
  obtain ⟨I, hI, hsub⟩ := exists_open_matrix_ideal_subset (R := R) (m := m)
    (↑(L ⊓ M) : Set (Matrix m m R))
    ((hL.inter hM).mem_nhds (by exact ⟨L.zero_mem, M.zero_mem⟩))
  refine ⟨I, hI, hsub, ?_⟩
  exact AddSubgroup.quotient_finite_of_isOpen' L _ hL
    ((matrix_ideal_open I hI).preimage continuous_subtype_val)

end CompactOrder
end PaperXI.CoordinateDeepIdeal111
