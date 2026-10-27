import PaperX.LatticeCountingGrid
import PaperX.LatticeCountingTransport

/-! Quantitative counting for every fixed full lattice, uniform in translation
and real dilation. The boundary atlas is genuine geometric data. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.LatticeCountingTransport
open Set MeasureTheory Module
open scoped Pointwise Topology

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  (L : Submodule ℤ E) [DiscreteTopology L] [IsZLattice ℝ L]
  {ι : Type*} [Fintype ι] (b : Basis ι ℤ L)

/-- Exact lattice-coordinate transport yields the full translated discrepancy estimate. -/
theorem exists_lattice_discrepancy_bound {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι (coordinates L b '' D)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ (a : E) (t : ℝ), 1 ≤ t →
      |(Nat.card (((fun x => a + t • x) '' D) ∩ (L : Set E) : Set E) : ℝ) -
        t ^ Fintype.card ι * (volume.real D / ZLattice.covolume L)| ≤
          C * (t ^ (Fintype.card ι - 1) + 1) := by
  have hm : MeasurableSet (coordinates L b '' D) :=
    (coordinates L b).toHomeomorph.toMeasurableEquiv.measurableSet_image.mpr hDm
  have hb : Bornology.IsBounded (coordinates L b '' D) :=
    (coordinates L b).toContinuousLinearMap.lipschitzWith.isBounded_image hDb
  obtain ⟨C, hC, hbound⟩ := LatticeCounting.exists_grid_discrepancy_bound hm hb A
  refine ⟨C, hC, fun a t ht => ?_⟩
  have h := hbound (coordinates L b a) t ht
  rw [← coordinates_affine_image L b D a t,
    ← lattice_count_eq_grid_count L b,
    volumeReal_coordinates_image L b hDm] at h
  exact h

omit [MeasurableSpace E] [BorelSpace E] [DiscreteTopology L] [IsZLattice ℝ L] in
/-- Moving a lattice coset to the origin translates the counting region in the opposite direction. -/
def cosetPointsEquiv (D : Set E) (a : E) (t : ℝ) :
    (((fun x : E => a + x) '' (L : Set E)) ∩ (t • D) : Set E) ≃
      (((fun x => -a + t • x) '' D) ∩ (L : Set E) : Set E) where
  toFun x := ⟨x.1 - a, by
    obtain ⟨l, hl, hxl⟩ := x.2.1
    obtain ⟨d, hd, hxd⟩ := x.2.2
    change a + l = x.1 at hxl
    change t • d = x.1 at hxd
    constructor
    · refine ⟨d, hd, ?_⟩
      change -a + t • d = x.1 - a
      rw [hxd]
      simp only [sub_eq_add_neg, add_comm]
    · have he : x.1 - a = l := by rw [← hxl]; simp
      rw [he]
      exact hl⟩
  invFun x := ⟨a + x.1, by
    refine ⟨⟨x.1, x.2.2, rfl⟩, ?_⟩
    obtain ⟨d, hd, hxd⟩ := x.2.1
    change -a + t • d = x.1 at hxd
    refine ⟨d, hd, ?_⟩
    change t • d = a + x.1
    rw [← hxd]
    simp⟩
  left_inv x := by apply Subtype.ext; simp
  right_inv x := by apply Subtype.ext; simp

/-- The requested lattice-coset form, uniformly for every translate and t at least one. -/
theorem exists_coset_discrepancy_bound {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι (coordinates L b '' D)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ (a : E) (t : ℝ), 1 ≤ t →
      |(Nat.card (((fun x : E => a + x) '' (L : Set E)) ∩ (t • D) : Set E) : ℝ) -
        t ^ Fintype.card ι * (volume.real D / ZLattice.covolume L)| ≤
          C * (t ^ (Fintype.card ι - 1) + 1) := by
  obtain ⟨C, hC, hbound⟩ := exists_lattice_discrepancy_bound L b hDm hDb A
  refine ⟨C, hC, fun a t ht => ?_⟩
  rw [Nat.card_congr (cosetPointsEquiv L D a t)]
  exact hbound (-a) t ht

end PaperX.LatticeCountingTransport
