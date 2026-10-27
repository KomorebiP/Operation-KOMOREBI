import PaperX.NormSignResidueCounting
import PaperX.ResidueLatticePointSums

/-! Exact decomposition of actual cone points and their sums by norm sign. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormSignGeometry
open Set NumberField NumberField.mixedEmbedding
open IdealClassQuantitative ResidueLattice
open scoped Classical Pointwise BigOperators
variable (K : Type*) [Field K] [NumberField K]

theorem signRegion_disjoint : Disjoint (signRegion K true) (signRegion K false) := by
  rw [Set.disjoint_left]
  intro x hx hy
  exact Set.disjoint_left.mp (signCone_disjoint K) hx hy

theorem signRegion_union : signRegion K true ∪ signRegion K false = coneRegion K 1 := by
  rw [signRegion, signRegion, ← Set.preimage_union, signCone_union, coneRegion_one]

theorem smul_signRegion_disjoint {t : ℝ} (ht : 0 < t) :
    Disjoint (t • signRegion K true) (t • signRegion K false) := by
  rw [Set.disjoint_left]
  intro x hx hy
  exact Set.disjoint_left.mp (signRegion_disjoint K)
    ((Set.mem_smul_set_iff_inv_smul_mem₀ ht.ne' _ _).mp hx)
    ((Set.mem_smul_set_iff_inv_smul_mem₀ ht.ne' _ _).mp hy)

theorem smul_signRegion_union (t : ℝ) :
    t • signRegion K true ∪ t • signRegion K false = t • coneRegion K 1 := by
  rw [← Set.smul_set_union, signRegion_union]

/-- The actual bounded lattice points split into the two disjoint sign portions. -/
def latticePointsSignEquiv (L : Submodule ℤ (euclidean.mixedSpace K)) {t : ℝ} (ht : 0 < t) :
    LatticePoints L (coneRegion K 1) t ≃
      LatticePoints L (signRegion K true) t ⊕ LatticePoints L (signRegion K false) t := by
  let P : Set L := {x | (x : euclidean.mixedSpace K) ∈ t • signRegion K true}
  let N : Set L := {x | (x : euclidean.mixedSpace K) ∈ t • signRegion K false}
  have hd : Disjoint P N := by
    rw [Set.disjoint_left]
    intro x hx hy
    exact Set.disjoint_left.mp (smul_signRegion_disjoint K ht) hx hy
  have he : ∀ x : L, (x : euclidean.mixedSpace K) ∈ t • coneRegion K 1 ↔ x ∈ P ∪ N := by
    intro x
    change (x : euclidean.mixedSpace K) ∈ t • coneRegion K 1 ↔
      (x : euclidean.mixedSpace K) ∈ t • signRegion K true ∪ t • signRegion K false
    rw [smul_signRegion_union]
  exact (Equiv.subtypeEquivRight he).trans (Equiv.Set.union hd)

@[simp]
theorem latticePointsSignEquiv_symm_inl_coe
    (L : Submodule ℤ (euclidean.mixedSpace K)) {t : ℝ} (ht : 0 < t)
    (x : LatticePoints L (signRegion K true) t) :
    ((latticePointsSignEquiv K L ht).symm (Sum.inl x)).1 = x.1 := rfl

@[simp]
theorem latticePointsSignEquiv_symm_inr_coe
    (L : Submodule ℤ (euclidean.mixedSpace K)) {t : ℝ} (ht : 0 < t)
    (x : LatticePoints L (signRegion K false) t) :
    ((latticePointsSignEquiv K L ht).symm (Sum.inr x)).1 = x.1 := rfl

/-- Every complex weight on the actual lattice points splits without changing
the underlying points. All three domains are finite by boundedness. -/
theorem finsum_latticePoints_sign_split
    (L : Submodule ℤ (euclidean.mixedSpace K)) [DiscreteTopology L]
    (w : L → ℂ) {t : ℝ} (ht : 0 < t) :
    (∑ᶠ x : LatticePoints L (coneRegion K 1) t, w x.1) =
      (∑ᶠ x : LatticePoints L (signRegion K true) t, w x.1) +
      (∑ᶠ x : LatticePoints L (signRegion K false) t, w x.1) := by
  let : Finite (LatticePoints L (coneRegion K 1) t) :=
    finite_latticePoints L (coneRegion_one_bounded K) t
  let : Finite (LatticePoints L (signRegion K true) t) :=
    finite_latticePoints L (signRegion_bounded K true) t
  let : Finite (LatticePoints L (signRegion K false) t) :=
    finite_latticePoints L (signRegion_bounded K false) t
  let : Fintype (LatticePoints L (coneRegion K 1) t) := Fintype.ofFinite _
  let : Fintype (LatticePoints L (signRegion K true) t) := Fintype.ofFinite _
  let : Fintype (LatticePoints L (signRegion K false) t) := Fintype.ofFinite _
  rw [finsum_eq_sum_of_fintype, finsum_eq_sum_of_fintype, finsum_eq_sum_of_fintype]
  rw [← (latticePointsSignEquiv K L ht).symm.sum_comp (fun x => w x.1),
    Fintype.sum_sum_type]
  simp only [latticePointsSignEquiv_symm_inl_coe, latticePointsSignEquiv_symm_inr_coe]

end PaperX.NormSignGeometry
