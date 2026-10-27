import PaperX.LatticeCountingInterface
import Mathlib.Analysis.Convex.PathConnected

noncomputable section
open Set MeasureTheory
open scoped Topology NNReal symmDiff

namespace PaperX.LatticeCounting
variable {ι : Type*} [Fintype ι]

/-- Unit cells selected by their lattice tags. -/
def cellUnion (s : Finset (ι → ℤ)) : Set (ι → ℝ) := ⋃ z ∈ s, gridCell z

theorem measurableSet_cellUnion (s : Finset (ι → ℤ)) : MeasurableSet (cellUnion s) := by
  apply Finset.measurableSet_biUnion
  intro z hz
  exact (BoxIntegral.unitPartition.box 1 z).measurableSet_coe

theorem isBounded_cellUnion (s : Finset (ι → ℤ)) : Bornology.IsBounded (cellUnion s) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [cellUnion]
  | insert z s hz ih =>
    simpa [cellUnion] using (BoxIntegral.unitPartition.box 1 z).isBounded.union ih

theorem volumeReal_gridCell (z : ι → ℤ) : volume.real (gridCell z) = 1 := by
  simp [Measure.real, gridCell, BoxIntegral.unitPartition.volume_box]

theorem volumeReal_cellUnion (s : Finset (ι → ℤ)) : volume.real (cellUnion s) = s.card := by
  have hd : (↑s : Set (ι → ℤ)).PairwiseDisjoint gridCell := by
    intro z hz w hw hzw
    exact BoxIntegral.unitPartition.disjoint.mp hzw
  have hm : ∀ z ∈ s, MeasurableSet (gridCell z) := by
    intro z hz
    exact (BoxIntegral.unitPartition.box 1 z).measurableSet_coe
  have hf : ∀ z ∈ s, volume (gridCell z) ≠ ⊤ := by
    intro z hz
    simp [gridCell, BoxIntegral.unitPartition.volume_box]
  rw [cellUnion, measureReal_biUnion_finset hd hm hf]
  simp [volumeReal_gridCell]

omit [Fintype ι] in
theorem tag_mem_closedGridCell (z : ι → ℤ) : gridTag z ∈ closedGridCell z :=
  BoxIntegral.Box.coe_subset_Icc (BoxIntegral.unitPartition.tag_mem 1 z)

omit [Fintype ι] in
theorem preconnected_closedGridCell (z : ι → ℤ) : IsPreconnected (closedGridCell z) := by
  exact (convex_Icc _ _).isPreconnected

omit [Fintype ι] in
theorem cellUnion_symmDiff_subset_boundary_union {D : Set (ι → ℝ)}
    (s b : Finset (ι → ℤ)) (hs : ∀ z, z ∈ s ↔ gridTag z ∈ D)
    (hb : ∀ z, z ∈ boundaryCells D → z ∈ b) :
    cellUnion s ∆ D ⊆ cellUnion b := by
  intro x hx
  rcases hx with ⟨hxU, hxD⟩ | ⟨hxD, hxU⟩
  · obtain ⟨z, hzs, hxz⟩ := mem_iUnion₂.mp hxU
    have hzb : z ∈ b := hb z (connected_meets_frontier (preconnected_closedGridCell z)
      (tag_mem_closedGridCell z) (BoxIntegral.Box.coe_subset_Icc hxz) ((hs z).mp hzs) hxD)
    exact mem_iUnion₂.mpr ⟨z, hzb, hxz⟩
  · let z := BoxIntegral.unitPartition.index 1 x
    have hxz : x ∈ gridCell z := BoxIntegral.unitPartition.mem_box_iff_index.mpr rfl
    have hznot : gridTag z ∉ D := by
      intro hzD
      exact hxU (mem_iUnion₂.mpr ⟨z, (hs z).mpr hzD, hxz⟩)
    have hzb : z ∈ b := hb z (connected_meets_frontier (preconnected_closedGridCell z)
      (BoxIntegral.Box.coe_subset_Icc hxz) (tag_mem_closedGridCell z) hxD hznot)
    exact mem_iUnion₂.mpr ⟨z, hzb, hxz⟩

/-- The discrepancy is bounded by the number of unit cells meeting the boundary.
The bound follows from an actual partition and exact unit-cell volumes. -/
theorem discrepancy_le_boundary_cells {D : Set (ι → ℝ)} (hD : MeasurableSet D)
    (hDb : Bornology.IsBounded D) (s b : Finset (ι → ℤ))
    (hs : ∀ z, z ∈ s ↔ gridTag z ∈ D)
    (hb : ∀ z, z ∈ boundaryCells D → z ∈ b) :
    |(s.card : ℝ) - volume.real D| ≤ b.card := by
  rw [← volumeReal_cellUnion s, ← volumeReal_cellUnion b]
  refine (abs_measureReal_sub_le_measureReal_symmDiff'
    (measurableSet_cellUnion s).nullMeasurableSet hD.nullMeasurableSet
    (isBounded_cellUnion s).measure_lt_top.ne hDb.measure_lt_top.ne).trans ?_
  exact measureReal_mono (cellUnion_symmDiff_subset_boundary_union s b hs hb)
    (isBounded_cellUnion b).measure_lt_top.ne

end PaperX.LatticeCounting
