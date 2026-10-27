import PaperX.LatticeCountingDiscrepancy
import PaperX.IntegerCellFiniteCharts
import Mathlib.MeasureTheory.Measure.Lebesgue.EqHaar

noncomputable section
open Set MeasureTheory
open scoped Topology NNReal symmDiff Pointwise

namespace PaperX.LatticeCounting
variable {ι : Type*} [Fintype ι]

omit [Fintype ι] in
theorem closedGridCell_eq (z : ι → ℤ) :
    closedGridCell z = IntegerCellBounds.closedCell z := by
  simp [closedGridCell, BoxIntegral.Box.Icc_def, IntegerCellBounds.closedCell,
    BoxIntegral.unitPartition.box]

omit [Fintype ι] in
theorem boundaryCells_eq (D : Set (ι → ℝ)) :
    boundaryCells D = IntegerCellBounds.touching (frontier D) := by
  simp [boundaryCells, IntegerCellBounds.touching, closedGridCell_eq]

omit [Fintype ι] in
theorem gridTag_eq (z : ι → ℤ) : gridTag z = fun i => (z i : ℝ) + 1 := by
  funext i
  simp [gridTag, BoxIntegral.unitPartition.tag_apply]

omit [Fintype ι] in
/-- Counting upper-right cell tags agrees exactly with counting integer vectors. -/
theorem ncard_upper_tags_eq (D : Set (ι → ℝ)) :
    {z : ι → ℤ | gridTag z ∈ D}.ncard =
      {z : ι → ℤ | (fun i => (z i : ℝ)) ∈ D}.ncard := by
  apply Set.ncard_congr (fun z _ => z + 1)
  · intro z hz
    simpa [gridTag_eq, Int.cast_add] using hz
  · intro z w hz hw h
    exact add_right_cancel h
  · intro z hz
    refine ⟨z - 1, ?_, sub_add_cancel z 1⟩
    simpa [gridTag_eq, Int.cast_sub] using hz

/-- The actual standard integer-lattice discrepancy is bounded by boundary cells. -/
theorem integer_discrepancy_le_touching {D : Set (ι → ℝ)}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (hB : (IntegerCellBounds.touching (frontier D)).Finite) :
    |({z : ι → ℤ | (fun i => (z i : ℝ)) ∈ D}.ncard : ℝ) - volume.real D| ≤
      (IntegerCellBounds.touching (frontier D)).ncard := by
  have hS : {z : ι → ℤ | gridTag z ∈ D}.Finite := by
    simpa [gridTag_eq] using
      IntegerCellBounds.finite_upper_tags_of_isBounded hDb
  have h := discrepancy_le_boundary_cells hDm hDb hS.toFinset hB.toFinset
    (by intro z; simp) (by intro z hz; simpa [boundaryCells_eq] using hz)
  rw [← Set.ncard_eq_toFinset_card _ hS, ← Set.ncard_eq_toFinset_card _ hB,
    ncard_upper_tags_eq] at h
  exact h

omit [Fintype ι] in
/-- Translation and nonzero dilation carry the entire topological boundary. -/
theorem frontier_affine_image (D : Set (ι → ℝ)) (a : ι → ℝ) (t : ℝ) (ht : t ≠ 0) :
    frontier ((fun x => a + t • x) '' D) =
      (fun x => a + t • x) '' frontier D := by
  let e := (Homeomorph.smulOfNeZero t ht : (ι → ℝ) ≃ₜ (ι → ℝ)).trans
    (Homeomorph.addLeft a)
  exact (e.image_frontier D).symm

theorem measurableSet_affine_image {D : Set (ι → ℝ)} (hD : MeasurableSet D)
    (a : ι → ℝ) (t : ℝ) (ht : t ≠ 0) :
    MeasurableSet ((fun x => a + t • x) '' D) := by
  let e := (Homeomorph.smulOfNeZero t ht : (ι → ℝ) ≃ₜ (ι → ℝ)).trans
    (Homeomorph.addLeft a)
  exact e.toMeasurableEquiv.measurableSet_image.mpr hD

theorem isBounded_affine_image {D : Set (ι → ℝ)} (hD : Bornology.IsBounded D)
    (a : ι → ℝ) (t : ℝ) : Bornology.IsBounded ((fun x => a + t • x) '' D) := by
  have hf : LipschitzWith ‖t‖₊ (fun x : ι → ℝ => a + t • x) := by
    exact LipschitzWith.of_dist_le_mul fun x y => by
      simpa only [dist_eq_norm, add_sub_add_left_eq_sub, ← smul_sub, norm_smul, coe_nnnorm] using
        (le_refl (‖t‖ * ‖x - y‖))
  exact hf.isBounded_image hD

theorem volumeReal_affine_image (D : Set (ι → ℝ)) (a : ι → ℝ) (t : ℝ) (ht : 0 ≤ t) :
    volume.real ((fun x => a + t • x) '' D) =
      t ^ Fintype.card ι * volume.real D := by
  have heq : (fun x => a + t • x) '' D = (fun y => a + y) '' (t • D) := by
    rw [← image_smul, image_image]
  rw [heq, Measure.real, image_add_left, measure_preimage_add,
    volume.addHaar_smul_of_nonneg ht]
  simp [ENNReal.toReal_mul, ENNReal.toReal_ofReal (pow_nonneg ht _),
    Measure.real]

/-- Every bounded measurable region with a finite Lipschitz frontier atlas has
uniform translated standard-lattice discrepancy of surface order. -/
theorem exists_grid_discrepancy_bound {D : Set (ι → ℝ)}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LipschitzBoundaryAtlas ι D) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ (a : ι → ℝ) (t : ℝ), 1 ≤ t →
      |({z : ι → ℤ | (fun i => (z i : ℝ)) ∈ (fun x => a + t • x) '' D}.ncard : ℝ) -
        t ^ Fintype.card ι * volume.real D| ≤ C * (t ^ (Fintype.card ι - 1) + 1) := by
  let C : ℝ := (A.charts : ℝ) * 3 ^ (Fintype.card ι - 1) *
    (2 * Nat.ceil ((A.lip : ℝ) + 1) + 3) ^ Fintype.card ι
  have hC : 0 ≤ C := by dsimp [C]; positivity
  refine ⟨C, hC, ?_⟩
  intro a t ht
  have ht0 : 0 ≤ t := by linarith
  have htne : t ≠ 0 := by linarith
  have hcov : frontier ((fun x => a + t • x) '' D) ⊆
      ⋃ j, (fun x => a + t • A.map j x) '' Icc 0 1 := by
    rw [frontier_affine_image D a t htne]
    rintro y ⟨x, hx, rfl⟩
    obtain ⟨j, hj⟩ := mem_iUnion.mp (A.covers hx)
    obtain ⟨z, hz, rfl⟩ := hj
    exact mem_iUnion.mpr ⟨j, mem_image_of_mem _ hz⟩
  obtain ⟨hfin, hcount⟩ := IntegerCellBounds.touching_finite_charts_polynomial_bound
    (frontier ((fun x => a + t • x) '' D)) A.map A.lip A.lipschitz a t ht hcov
  have hdisc := integer_discrepancy_le_touching (measurableSet_affine_image hDm a t htne)
    (isBounded_affine_image hDb a t) hfin
  rw [volumeReal_affine_image D a t ht0] at hdisc
  refine hdisc.trans ((show _ ≤ C * t ^ (Fintype.card ι - 1) by
    simpa [C] using hcount).trans ?_)
  exact mul_le_mul_of_nonneg_left (le_add_of_nonneg_right zero_le_one) hC

end PaperX.LatticeCounting
