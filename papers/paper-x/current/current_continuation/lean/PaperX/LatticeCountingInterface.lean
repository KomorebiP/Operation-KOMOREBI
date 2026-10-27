import Mathlib.Analysis.BoxIntegral.UnitPartition
import Mathlib.Analysis.Convex.Topology
import Mathlib.MeasureTheory.Measure.Typeclasses.Finite

/-! A finite, dimension-correct Lipschitz frontier atlas. The quantitative
counting theorem will prove its bound from this geometric data. -/
noncomputable section
open Set MeasureTheory
open scoped Topology NNReal

namespace PaperX.LatticeCounting

structure LipschitzBoundaryAtlas (ι : Type*) [Fintype ι] (D : Set (ι → ℝ)) where
  charts : ℕ
  lip : ℝ≥0
  map : Fin charts → (Fin (Fintype.card ι - 1) → ℝ) → (ι → ℝ)
  lipschitz : ∀ j, LipschitzOnWith lip (map j) (Icc 0 1)
  covers : frontier D ⊆ ⋃ j, map j '' Icc 0 1

variable {ι : Type*} [Fintype ι]

abbrev gridCell (z : ι → ℤ) : Set (ι → ℝ) :=
  (BoxIntegral.unitPartition.box 1 z : Set (ι → ℝ))

abbrev closedGridCell (z : ι → ℤ) : Set (ι → ℝ) :=
  BoxIntegral.Box.Icc (BoxIntegral.unitPartition.box 1 z)

abbrev gridTag (z : ι → ℤ) : ι → ℝ := BoxIntegral.unitPartition.tag 1 z

/-- Closed unit cells meeting the actual topological boundary. -/
def boundaryCells (D : Set (ι → ℝ)) : Set (ι → ℤ) :=
  {z | (closedGridCell z ∩ frontier D).Nonempty}

/-- A connected cell containing a point in a set and a point outside it meets the boundary. -/
theorem connected_meets_frontier {E : Type*} [TopologicalSpace E]
    {C D : Set E} (hC : IsPreconnected C) {x y : E}
    (hx : x ∈ C) (hy : y ∈ C) (hxD : x ∈ D) (hyD : y ∉ D) :
    (C ∩ frontier D).Nonempty := by
  by_contra h
  have hdis : ∀ z ∈ C, z ∉ frontier D := by
    intro z hz hzD
    exact h ⟨z, hz, hzD⟩
  have hcover : C ⊆ interior D ∪ interior Dᶜ := by
    intro z hz
    by_cases hzD : z ∈ D
    · exact Or.inl (not_not.mp ((mem_frontier_iff_notMem_interior hzD).not.mp (hdis z hz)))
    · exact Or.inr (not_not.mp ((mem_frontier_iff_notMem_interior (s := Dᶜ) hzD).not.mp
        (by simpa using hdis z hz)))
  rcases hC.subset_or_subset isOpen_interior isOpen_interior
    (disjoint_compl_right.mono interior_subset interior_subset) hcover with hD | hDc
  · exact hyD (interior_subset (hD hy))
  · exact (interior_subset (hDc hx)) hxD

end PaperX.LatticeCounting
