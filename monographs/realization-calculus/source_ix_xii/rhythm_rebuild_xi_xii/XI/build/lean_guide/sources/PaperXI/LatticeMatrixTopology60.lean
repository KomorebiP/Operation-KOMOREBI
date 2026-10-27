import PaperXI.ActualELatticeQuotient59
import Mathlib.Topology.CompactOpen
import Mathlib.Topology.Algebra.Module.FiniteDimension

/-!
# Compact open lattice stabilizers in actual matrix coordinates

A finite continuous basis transports a literal compact open additive lattice
into the given local field's matrix group. Compactness uses a basis contained
in the lattice. No equality with a simple-character group is asserted.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LatticeMatrixTopology60
open Matrix Topology

variable {K V d : Type*} [Field K] [TopologicalSpace K] [IsTopologicalRing K]
  [T2Space K] [Fintype d] [DecidableEq d]
  [AddCommGroup V] [Module K V] [TopologicalSpace V] [T2Space V]

/-- Actual matrix action in the supplied finite continuous coordinates. -/
def matrixAction (e : V ≃L[K] (d → K)) (M : Matrix d d K) (v : V) : V :=
  e.symm (M *ᵥ e v)

omit [T2Space K] [DecidableEq d] [T2Space V] in
@[fun_prop] theorem matrixAction_continuous (e : V ≃L[K] (d → K)) :
    Continuous (fun p : Matrix d d K × V => matrixAction e p.1 p.2) := by
  unfold matrixAction
  apply e.symm.continuous.comp
  apply continuous_pi
  intro i
  simp only [Matrix.mulVec, dotProduct]
  fun_prop

/-- The actual endomorphism monoid preserving the literal lattice. -/
def preserving (e : V ≃L[K] (d → K)) (L : AddSubgroup V) : Submonoid (Matrix d d K) where
  carrier := {M | ∀ v ∈ L, matrixAction e M v ∈ L}
  one_mem' := by intro v hv; simpa [matrixAction] using hv
  mul_mem' := by
    intro M N hM hN v hv
    have h := hM (matrixAction e N v) (hN v hv)
    simpa [matrixAction, Matrix.mulVec_mulVec] using h

/-- The stabilizer is the unit group of the literal preserving monoid. -/
def stabilizer (e : V ≃L[K] (d → K)) (L : AddSubgroup V) :
    Subgroup (GeneralLinearGroup d K) := (preserving e L).units

omit [T2Space K] [T2Space V] in
/-- Preserving a closed lattice is a closed condition on actual matrices. -/
theorem preserving_closed (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hL : IsClosed (L : Set V)) : IsClosed (preserving e L : Set (Matrix d d K)) := by
  change IsClosed {M : Matrix d d K | ∀ v, v ∈ L → matrixAction e M v ∈ L}
  simp only [Set.ofPred_forall]
  apply isClosed_iInter
  intro v
  apply isClosed_iInter
  intro _
  exact hL.preimage ((matrixAction_continuous e).comp (continuous_id.prodMk continuous_const))

omit [T2Space K] [T2Space V] in
/-- Compact-open continuity makes preservation of a compact open lattice open. -/
theorem preserving_open (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V)) (ho : IsOpen (L : Set V)) :
    IsOpen (preserving e L : Set (Matrix d d K)) := by
  let f : Matrix d d K → C(V, V) := fun M =>
    ⟨matrixAction e M, (matrixAction_continuous e).comp (continuous_const.prodMk continuous_id)⟩
  have hf : Continuous f := ContinuousMap.continuous_of_continuous_uncurry f
    (matrixAction_continuous e)
  exact (ContinuousMap.isOpen_setOfPred_mapsTo hc ho).preimage hf

omit [T2Space K] in
/-- A basis inside the lattice gives a compact set containing all preserving matrices. -/
theorem preserving_compact (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V))
    (hb : ∀ i, e.symm (Pi.single i 1) ∈ L) :
    IsCompact (preserving e L : Set (Matrix d d K)) := by
  let C : Set (d → K) := e '' (L : Set V)
  have hC : IsCompact C := hc.image e.continuous
  have hP : IsCompact (Set.pi Set.univ (fun _ : d => C)) := isCompact_univ_pi (fun _ => hC)
  have hT : IsCompact (Matrix.transpose '' Set.pi Set.univ (fun _ : d => C)) :=
    hP.image continuous_id.matrix_transpose
  apply hT.of_isClosed_subset (preserving_closed e L hc.isClosed)
  intro M hM
  refine ⟨Mᵀ, ?_, Matrix.transpose_transpose M⟩
  intro i _
  refine ⟨matrixAction e M (e.symm (Pi.single i 1)), hM _ (hb i), ?_⟩
  simp only [matrixAction, ContinuousLinearEquiv.apply_symm_apply, Matrix.mulVec_single_one]
  rfl

omit [IsTopologicalRing K] [T2Space K] [T2Space V] in
/-- Every finite basis can be uniformly moved into an open lattice by a nonzero base scalar. -/
theorem exists_scaled_basis [ContinuousSMul K V] [Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ)]
    (e : V ≃L[K] (d → K)) (L : AddSubgroup V) (ho : IsOpen (L : Set V)) :
    ∃ c : Kˣ, ∀ i, (c : K) • e.symm (Pi.single i 1) ∈ L := by
  have he : ∀ᶠ c : K in nhds (0 : K), ∀ i, c • e.symm (Pi.single i 1) ∈ L := by
    rw [Filter.eventually_all]
    intro i
    exact (continuous_id.smul continuous_const).continuousAt.preimage_mem_nhds
      (ho.mem_nhds (by simp))
  have he' : ∀ᶠ c : K in nhdsWithin (0 : K) {0}ᶜ, ∀ i, c • e.symm (Pi.single i 1) ∈ L :=
    he.filter_mono nhdsWithin_le_nhds
  have hn : ∀ᶠ c : K in nhdsWithin (0 : K) {0}ᶜ, c ≠ 0 := by
    exact Filter.Eventually.mono (self_mem_nhdsWithin : {0}ᶜ ∈ nhdsWithin (0 : K) {0}ᶜ)
      (fun _ h => h)
  obtain ⟨c, hc, hci⟩ := (hn.and he').exists
  exact ⟨Units.mk0 c hc, hci⟩

omit [T2Space K] in
/-- Openness supplies the required bounded basis, so no integral-basis premise remains. -/
theorem preserving_compact_of_open [ContinuousSMul K V]
    [Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ)]
    (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V)) (ho : IsOpen (L : Set V)) :
    IsCompact (preserving e L : Set (Matrix d d K)) := by
  obtain ⟨c, hb⟩ := exists_scaled_basis e L ho
  let C : Set (d → K) := (fun v : V => e ((↑c⁻¹ : K) • v)) '' (L : Set V)
  have hC : IsCompact C := hc.image (e.continuous.comp (continuous_const.smul continuous_id))
  have hP : IsCompact (Set.pi Set.univ (fun _ : d => C)) := isCompact_univ_pi (fun _ => hC)
  have hT : IsCompact (Matrix.transpose '' Set.pi Set.univ (fun _ : d => C)) :=
    hP.image continuous_id.matrix_transpose
  apply hT.of_isClosed_subset (preserving_closed e L hc.isClosed)
  intro M hM
  refine ⟨Mᵀ, ?_, Matrix.transpose_transpose M⟩
  intro i _
  refine ⟨matrixAction e M ((c : K) • e.symm (Pi.single i 1)), hM _ (hb i), ?_⟩
  simp only [matrixAction, map_smul, ContinuousLinearEquiv.apply_symm_apply, Matrix.mulVec_smul,
    Matrix.mulVec_single_one, smul_smul, Units.inv_mul, one_smul]
  rfl

/-- The literal lattice stabilizer is compact in actual `GL_d(K)`. -/
theorem stabilizer_compact (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V))
    (hb : ∀ i, e.symm (Pi.single i 1) ∈ L) :
    IsCompact (stabilizer e L : Set (GeneralLinearGroup d K)) :=
  Submonoid.units_isCompact (preserving_compact e L hc hb)

omit [T2Space K] [T2Space V] in
/-- The same literal stabilizer is open in actual `GL_d(K)`. -/
theorem stabilizer_open (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V)) (ho : IsOpen (L : Set V)) :
    IsOpen (stabilizer e L : Set (GeneralLinearGroup d K)) :=
  Submonoid.isOpen_units (preserving_open e L hc ho)

/-- Every compact open additive lattice has compact matrix stabilizer. -/
theorem stabilizer_compact_of_open [ContinuousSMul K V]
    [Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ)]
    (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (hc : IsCompact (L : Set V)) (ho : IsOpen (L : Set V)) :
    IsCompact (stabilizer e L : Set (GeneralLinearGroup d K)) :=
  Submonoid.units_isCompact (preserving_compact_of_open e L hc ho)

end PaperXI.LatticeMatrixTopology60
