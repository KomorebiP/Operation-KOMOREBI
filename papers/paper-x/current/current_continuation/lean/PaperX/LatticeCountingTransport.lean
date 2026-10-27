import PaperX.LatticeCountingInterface
import Mathlib.Algebra.Module.ZLattice.Covolume

/-! Exact transport of lattice counts and volume to integer coordinates. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.LatticeCountingTransport
open Set MeasureTheory Module
open scoped Pointwise Topology

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E]
  (L : Submodule ℤ E) [DiscreteTopology L] [IsZLattice ℝ L]
  {ι : Type*} [Fintype ι] (b : Basis ι ℤ L)

/-- Real coordinates associated with an actual integral lattice basis. -/
def coordinates : E ≃L[ℝ] (ι → ℝ) := (b.ofZLatticeBasis ℝ L).equivFunL

/-- On lattice elements the real coordinates are exactly the integral coefficients. -/
theorem coordinates_lattice (x : L) :
    coordinates L b (x : E) = fun i => (b.equivFun x i : ℝ) := by
  ext i
  exact b.ofZLatticeBasis_repr_apply ℝ L x i

/-- The coordinate equivalence preserves the actual finite point-counting objects. -/
def latticePointsEquiv (S : Set E) :
    (S ∩ (L : Set E) : Set E) ≃
      {z : ι → ℤ // (fun i => (z i : ℝ)) ∈ coordinates L b '' S} where
  toFun x := ⟨b.equivFun ⟨x.1, x.2.2⟩,
    ⟨x.1, x.2.1, coordinates_lattice L b ⟨x.1, x.2.2⟩⟩⟩
  invFun z := ⟨(b.equivFun.symm z.1 : L), by
    constructor
    · obtain ⟨y, hy, he⟩ := z.2
      have hc : coordinates L b (b.equivFun.symm z.1 : L) = coordinates L b y := by
        rw [coordinates_lattice]
        simpa only [b.equivFun.apply_symm_apply] using he.symm
      exact (coordinates L b).injective hc ▸ hy
    · exact (b.equivFun.symm z.1).2⟩
  left_inv x := by
    apply Subtype.ext
    simp only [b.equivFun.symm_apply_apply]
  right_inv z := by
    apply Subtype.ext
    exact b.equivFun.apply_symm_apply z.1

/-- Integral lattice counts become ordinary integer-grid counts. -/
theorem lattice_count_eq_grid_count (S : Set E) :
    Nat.card (S ∩ (L : Set E) : Set E) =
      {z : ι → ℤ | (fun i => (z i : ℝ)) ∈ coordinates L b '' S}.ncard := by
  exact Nat.card_congr (latticePointsEquiv L b S)

variable [MeasurableSpace E] [BorelSpace E]

/-- The coordinate image has exactly the original volume divided by the covolume. -/
theorem volumeReal_coordinates_image {S : Set E} (hS : MeasurableSet S) :
    volume.real (coordinates L b '' S) = volume.real S / ZLattice.covolume L := by
  change (volume ((b.ofZLatticeBasis ℝ L).equivFun '' S)).toReal = _
  rw [ZLattice.volume_image_eq_volume_div_covolume' L b hS.nullMeasurableSet,
    ENNReal.toReal_div, ENNReal.toReal_ofReal (ZLattice.covolume_pos L volume).le]
  rfl

omit [MeasurableSpace E] [BorelSpace E] in
/-- Translation and real dilation commute with the lattice coordinate map. -/
theorem coordinates_affine_image (D : Set E) (a : E) (t : ℝ) :
    coordinates L b '' ((fun x => a + t • x) '' D) =
      (fun y => coordinates L b a + t • y) '' (coordinates L b '' D) := by
  rw [← Set.image_comp, ← Set.image_comp]
  congr 1
  ext x
  simp

end PaperX.LatticeCountingTransport
