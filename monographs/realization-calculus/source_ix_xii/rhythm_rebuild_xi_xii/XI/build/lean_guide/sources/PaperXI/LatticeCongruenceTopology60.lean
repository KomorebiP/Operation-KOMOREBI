import PaperXI.LatticeMatrixTopology60
import PaperXI.PeriodicLatticeReduction60

/-!
# Topology of the full periodic-lattice congruence group

The infinite definition is preserved literally. A base-field scalar period
proves openness by finite reduction, while compactness follows from the zero
lattice stabilizer. The ambient group is actual `GL_d(K)`.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LatticeCongruenceTopology60
open Matrix Topology ActualELatticeNormalizer59 LatticeMatrixTopology60 PeriodicLatticeReduction60
variable {K V d : Type*} [Field K] [TopologicalSpace K] [IsTopologicalRing K]
  [T2Space K] [Fintype d] [DecidableEq d]
  [AddCommGroup V] [Module K V] [TopologicalSpace V] [IsTopologicalAddGroup V]
  [T2Space V]

/-- The matrix group is identified with the actual linear automorphism group. -/
def coordinateAut (e : V ≃L[K] (d → K)) :
    GeneralLinearGroup d K ≃* (V ≃ₗ[K] V) :=
  (GeneralLinearGroup.toLin.trans
    (LinearMap.GeneralLinearGroup.congrLinearEquiv e.toLinearEquiv.symm)).trans
    (LinearMap.GeneralLinearGroup.generalLinearEquiv K V)

omit [IsTopologicalRing K] [T2Space K] [IsTopologicalAddGroup V] [T2Space V] in
@[simp] theorem coordinateAut_apply (e : V ≃L[K] (d → K))
    (g : GeneralLinearGroup d K) (v : V) :
    coordinateAut e g v = matrixAction e (g : Matrix d d K) v := rfl

/-- The matrix subgroup is the exact preimage of the literal full-chain subgroup. -/
def congruence (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V) :
    Subgroup (GeneralLinearGroup d K) :=
  (firstCongruence L).comap (coordinateAut e).toMonoidHom

omit [IsTopologicalRing K] [T2Space K] [IsTopologicalAddGroup V] [T2Space V] in
theorem mem_stabilizer_iff (e : V ≃L[K] (d → K)) (L : AddSubgroup V)
    (g : GeneralLinearGroup d K) :
    g ∈ stabilizer e L ↔ ∀ v, coordinateAut e g v ∈ L ↔ v ∈ L := by
  constructor
  · rintro ⟨hg, hi⟩ v
    constructor
    · intro hv
      have h := hi _ hv
      change coordinateAut e g⁻¹ (coordinateAut e g v) ∈ L at h
      rw [map_inv] at h
      exact (coordinateAut e g).symm_apply_apply v ▸ h
    · exact hg v
  · intro h
    constructor
    · exact fun v hv => (h v).mpr hv
    · intro v hv
      apply (h (coordinateAut e g⁻¹ v)).mp
      rw [map_inv]
      change (coordinateAut e g) ((coordinateAut e g).symm v) ∈ L
      simpa only [LinearEquiv.apply_symm_apply] using hv

/-- The exact one-level condition in actual matrix coordinates. -/
def levelSet (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V) (i : ℤ) :
    Set (GeneralLinearGroup d K) :=
  {g | levelCondition L (coordinateAut e g) i}

omit [IsTopologicalRing K] [T2Space K] [IsTopologicalAddGroup V] [T2Space V] in
theorem levelSet_eq (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V) (i : ℤ) :
    levelSet e L i = (stabilizer e (L i) : Set (GeneralLinearGroup d K)) ∩
      {g | ∀ v ∈ L i, matrixAction e (g : Matrix d d K) v - v ∈ L (i + 1)} := by
  ext g
  exact and_congr (mem_stabilizer_iff e (L i) g).symm Iff.rfl

omit [T2Space K] [T2Space V] in
theorem levelSet_closed (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V) (i : ℤ)
    (hi : IsClosed (L i : Set V)) (hj : IsClosed (L (i + 1) : Set V)) :
    IsClosed (levelSet e L i) := by
  rw [levelSet_eq]
  apply IsClosed.inter
  · exact ((preserving_closed e (L i) hi).preimage Units.continuous_val).inter
      ((preserving_closed e (L i) hi).preimage Units.continuous_coe_inv)
  · simp only [Set.ofPred_forall]
    apply isClosed_iInter
    intro v
    apply isClosed_iInter
    intro _
    apply hj.preimage
    exact ((matrixAction_continuous e).comp
      (Units.continuous_val.prodMk continuous_const)).sub continuous_const

omit [T2Space K] [T2Space V] in
theorem levelSet_open (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V) (i : ℤ)
    (hi : IsCompact (L i : Set V)) (hoi : IsOpen (L i : Set V))
    (hoj : IsOpen (L (i + 1) : Set V)) : IsOpen (levelSet e L i) := by
  rw [levelSet_eq]
  apply IsOpen.inter (stabilizer_open e (L i) hi hoi)
  let f : GeneralLinearGroup d K → C(V, V) := fun g =>
    ⟨fun v => matrixAction e (g : Matrix d d K) v - v,
      ((matrixAction_continuous e).comp (continuous_const.prodMk continuous_id)).sub continuous_id⟩
  have hf : Continuous f := by
    apply ContinuousMap.continuous_of_continuous_uncurry
    exact ((matrixAction_continuous e).comp
      ((Units.continuous_val.comp continuous_fst).prodMk continuous_snd)).sub continuous_snd
  exact (ContinuousMap.isOpen_setOfPred_mapsTo hi hoj).preimage hf

omit [T2Space K] in
/-- Compactness of all levels makes literal full-chain congruence closed. -/
theorem congruence_closed (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V)
    (hL : ∀ i, IsCompact (L i : Set V)) :
    IsClosed (congruence e L : Set (GeneralLinearGroup d K)) := by
  have he : (congruence e L : Set (GeneralLinearGroup d K)) = ⋂ i, levelSet e L i := by
    ext g
    simp only [Set.mem_iInter, levelSet, Set.mem_ofPred_eq]
    constructor
    · intro h i
      exact ⟨h.1 i, h.2 i⟩
    · intro h
      exact ⟨fun i => (h i).1, fun i => (h i).2⟩
  rw [he]
  exact isClosed_iInter fun i => levelSet_closed e L i (hL i).isClosed (hL (i + 1)).isClosed

/-- A basis in level zero bounds the entire congruence group compactly. -/
theorem congruence_compact (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V)
    (hL : ∀ i, IsCompact (L i : Set V))
    (hb : ∀ j, e.symm (Pi.single j 1) ∈ L 0) :
    IsCompact (congruence e L : Set (GeneralLinearGroup d K)) := by
  apply (stabilizer_compact e (L 0) (hL 0) hb).of_isClosed_subset (congruence_closed e L hL)
  intro g hg
  exact (mem_stabilizer_iff e (L 0) g).mpr (hg.1 0)

omit [T2Space K] [T2Space V] in
/-- A positive base-field period makes the literal full-chain congruence open. -/
theorem congruence_open (e : V ≃L[K] (d → K)) (L : ℤ → AddSubgroup V)
    (hLc : ∀ i, IsCompact (L i : Set V)) (hLo : ∀ i, IsOpen (L i : Set V))
    (c : Kˣ) (r : ℕ) (hr : 0 < r)
    (hperiod : ∀ i v, (c : K) • v ∈ L (i + (r : ℤ)) ↔ v ∈ L i) :
    IsOpen (congruence e L : Set (GeneralLinearGroup d K)) := by
  have he : (congruence e L : Set (GeneralLinearGroup d K)) =
      ⋂ j : Fin r, levelSet e L (j.val : ℤ) := by
    ext g
    simp only [Set.mem_iInter, levelSet, Set.mem_ofPred_eq]
    exact mem_firstCongruence_iff_fin L c r hr hperiod (coordinateAut e g)
  rw [he]
  exact isOpen_iInter_of_finite fun j => levelSet_open e L j.val (hLc j.val) (hLo j.val)
    (hLo (j.val + 1))

end PaperXI.LatticeCongruenceTopology60
