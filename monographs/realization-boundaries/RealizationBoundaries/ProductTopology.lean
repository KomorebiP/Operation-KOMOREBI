import RealizationBoundaries.FiniteQuotients
import Mathlib.Topology.Algebra.Category.ProfiniteGrp.Basic
import Mathlib.Topology.Algebra.Group.Subgroup

/-! # Product topology and density in the genuine infinite ambient group -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

instance coordinateTopology (p : Prime) : TopologicalSpace (Coordinate p) := ⊥
instance coordinateDiscrete (p : Prime) : DiscreteTopology (Coordinate p) := ⟨rfl⟩

/-- The unrestricted product of all finite prime coordinates is a profinite additive group. -/
def ambientProfinite : ProfiniteAddGrp := ProfiniteAddGrp.of Ambient

/-- Every finite-support vector is an actual point of the infinite product, and these
points meet every nonempty open set in the product topology. -/
theorem finiteSupport_dense : Dense (finiteSupport : Set Ambient) := by
  apply dense_iff_inter_open.mpr
  intro U hU hne
  obtain ⟨x, hx⟩ := hne
  obtain ⟨J, fJ, hJ1, hJ2⟩ := isOpen_pi_iff.mp hU x hx
  refine ⟨cut J x, ?_, cut_mem_finiteSupport J x⟩
  apply hJ2
  intro p hp
  rw [cut_apply_mem J x p hp]
  exact (hJ1 p hp).2

/-- Every subgroup containing D is dense, independently of a presentation or selector. -/
theorem intermediate_dense (H : AddSubgroup Ambient) (hD : finiteSupport ≤ H) :
    Dense (H : Set Ambient) := finiteSupport_dense.mono hD

theorem preimage_dense (W : Submodule ℚ TailSpace) : Dense (preimage W : Set Ambient) :=
  intermediate_dense _ (finiteSupport_le_preimage W)

theorem preimage_denseRange (W : Submodule ℚ TailSpace) :
    DenseRange (fun x : preimage W => x.val) := by
  have hr : Set.range (fun x : preimage W => x.val) = (preimage W : Set Ambient) := by
    ext x
    constructor
    · rintro ⟨y, rfl⟩
      exact y.property
    · intro hx
      exact ⟨⟨x, hx⟩, rfl⟩
  change Dense (Set.range (fun x : preimage W => x.val))
  rw [hr]
  exact preimage_dense W

/-- Coordinate restriction on the whole ambient product. -/
def ambientCoordinates (m : ℕ) : Ambient →+ DivisorCoordinates m where
  toFun x p := x p.val
  map_zero' := rfl
  map_add' _ _ := rfl

theorem ambientCoordinates_continuous (m : ℕ) : Continuous (ambientCoordinates m) :=
  continuous_pi fun p => continuous_apply p.val

@[simp] theorem ambientCoordinates_subtype (W : Submodule ℚ TailSpace)
    (m : ℕ) (x : preimage W) : ambientCoordinates m x.val = coordinateMap W m x := rfl

/-- Finite products of discrete divisor coordinates are discrete. -/
theorem divisorCoordinates_discrete {m : ℕ} (hm : 0 < m) :
    DiscreteTopology (DivisorCoordinates m) := by
  let : Finite (DivisorPrime m) := divisorPrime_finite hm
  infer_instance

/-- At positive multipliers, every canonical congruence kernel is open. -/
theorem coordinateMap_kernel_open (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    IsOpen ((coordinateMap W m).ker : Set (preimage W)) := by
  let := divisorCoordinates_discrete hm
  have hc : Continuous (coordinateMap W m) :=
    (ambientCoordinates_continuous m).comp continuous_subtype_val
  exact hc.isOpen_preimage _ (isOpen_discrete {0})

theorem multiples_open (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    IsOpen (multiples W m : Set (preimage W)) := by
  rw [← coordinateMap_ker W hm]
  exact coordinateMap_kernel_open W hm

end RealizationBoundaries
