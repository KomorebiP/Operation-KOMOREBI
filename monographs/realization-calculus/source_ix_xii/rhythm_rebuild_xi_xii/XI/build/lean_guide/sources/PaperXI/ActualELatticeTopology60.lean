import PaperXI.LatticeCongruenceTopology60
import PaperXI.ActualELatticeScalarPeriod60

/-!
# Compact open topology for the literal extension-field lattice type group

The exact Block59 lattice groups are realized in actual `GL_d(K)` through
finite continuous coordinates on `E^n`. Compactness, openness, and the open
kernel of actual residue reduction are proved. No identification with the
simple-character group of an arbitrary stratum is asserted.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeTopology60
open Matrix ValuativeRel Topology
open ActualELatticeResidue59 ActualELatticeTypeGroup59 ActualELatticeNormalizer59
open ActualELatticeFreeness59 ActualELatticeQuotient59 ActualELatticeScalarPeriod60
open LatticeMatrixTopology60 LatticeCongruenceTopology60

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra K E]
variable (n d : Type*) [Fintype n] [DecidableEq n] [Fintype d] [DecidableEq d]

local instance : T2Space K := ActualIntegralGeneralLinear.field_t2Space K
local instance : T2Space E := ActualIntegralGeneralLinear.field_t2Space E

/-- A local field has nontrivial punctured neighborhoods at zero. -/
theorem field_nhdsNE_neBot : Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ) := by
  let := IsTopologicalAddGroup.rightUniformSpace K
  have := isUniformAddGroup_of_addCommGroup (G := K)
  let : (Valued.v (R := K)).RankOne :=
    { hom' := ValuativeRel.IsRankLeOne.nonempty.some.emb (R := K).comp
        MonoidWithZeroHom.ValueGroup₀.embedding
      strictMono' := ValuativeRel.IsRankLeOne.nonempty.some.strictMono.comp
        MonoidWithZeroHom.ValueGroup₀.embedding_strictMono }
  open scoped Valued in
    infer_instance

/-- Every actual finite basis gives continuous coordinates under the compatible extension topology. -/
def coordinatesOfBasis (hK : Continuous (algebraMap K E)) (b : Module.Basis d K (n → E)) :
    (n → E) ≃L[K] (d → K) := by
  let := IsTopologicalAddGroup.rightUniformSpace K
  have := isUniformAddGroup_of_addCommGroup (G := K)
  let : (Valued.v (R := K)).RankOne :=
    { hom' := ValuativeRel.IsRankLeOne.nonempty.some.emb (R := K).comp
        MonoidWithZeroHom.ValueGroup₀.embedding
      strictMono' := ValuativeRel.IsRankLeOne.nonempty.some.strictMono.comp
        MonoidWithZeroHom.ValueGroup₀.embedding_strictMono }
  let : ContinuousSMul K E := continuousSMul_of_algebraMap K E hK
  let : FiniteDimensional K (n → E) := Module.Finite.of_basis b
  open scoped Valued in
    exact b.equivFun.toContinuousLinearEquiv

/-- Scalar multiplication gives a literal algebra embedding into actual matrices. -/
def scalarMatrixEmbedding (e : (n → E) ≃L[K] (d → K)) : E →ₐ[K] Matrix d d K :=
  LinearMap.toMatrixAlgEquiv'.toAlgHom.comp
    ((e.toLinearEquiv.conjAlgEquiv K).toAlgHom.comp (Algebra.lsmul K K (n → E)))

omit [Fintype n] [DecidableEq n] in
/-- The literal integral extension-field lattice is compact. -/
theorem integralLattice_compact : IsCompact (integralLattice E n : Set (n → E)) :=
  isCompact_pi_infinite (fun _ => IsNonarchimedeanLocalField.isCompact_closedBall E 1)

omit [DecidableEq n] in
/-- The literal integral extension-field lattice is open. -/
theorem integralLattice_open : IsOpen (integralLattice E n : Set (n → E)) := by
  change IsOpen {v : n → E | ∀ i, v i ∈ (valuation E).integer}
  simp only [Set.ofPred_forall]
  exact isOpen_iInter_of_finite fun i => (valuation E).isOpen_integer.preimage (continuous_apply i)

omit [ValuativeRel K] [TopologicalSpace K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] in
/-- Every integer translate in the actual chain is compact. -/
theorem latticeChain_compact (i : ℤ) : IsCompact (latticeChain K E n i : Set (n → E)) := by
  let a : E := (ActualLocalUnitDecomposition.uniformizer E : E) ^ (-i)
  have ha : a ≠ 0 := zpow_ne_zero _ (ActualLocalUnitDecomposition.uniformizer_ne_zero E)
  have h := (Homeomorph.smulOfNeZero a ha : (n → E) ≃ₜ (n → E)).isCompact_preimage.mpr
    (integralLattice_compact E n)
  convert h using 1
  ext v
  exact Iff.of_eq (congrArg (fun w => w ∈ integralLattice E n)
    (uniformizerAction_zpow_apply K E n (-i) v))

omit [ValuativeRel K] [TopologicalSpace K] [IsNonarchimedeanLocalField K] [DecidableEq n] in
/-- Every integer translate in the actual chain is open. -/
theorem latticeChain_open (i : ℤ) : IsOpen (latticeChain K E n i : Set (n → E)) := by
  have h := (integralLattice_open E n).preimage
    (continuous_const_smul ((ActualLocalUnitDecomposition.uniformizer E : E) ^ (-i)))
  convert h using 1
  ext v
  exact Iff.of_eq (congrArg (fun w => w ∈ integralLattice E n)
    (uniformizerAction_zpow_apply K E n (-i) v))

/-- The exact Block59 type group in actual finite `K`-matrix coordinates. -/
def matrixType (e : (n → E) ≃L[K] (d → K)) : Subgroup (GeneralLinearGroup d K) :=
  (typeGroup K E n).comap (coordinateAut e).toMonoidHom

/-- The exact Block59 first congruence group in the same coordinates. -/
def matrixCongruence (e : (n → E) ≃L[K] (d → K)) : Subgroup (GeneralLinearGroup d K) :=
  LatticeCongruenceTopology60.congruence e (latticeChain K E n)

variable [Nonempty d]

/-- Openness uses a proved base-field scalar period, not a supplied period or ramification index. -/
theorem matrixCongruence_open (e : (n → E) ≃L[K] (d → K))
    (hK : Continuous (algebraMap K E)) :
    IsOpen (matrixCongruence K E n d e : Set (GeneralLinearGroup d K)) := by
  let ι := scalarMatrixEmbedding K E n d e
  have hι := ActualEmbeddedUniformizer58.algebraEmbedding_continuous K E d ι hK
  obtain ⟨c, r, hr, hp⟩ := exists_chain_period K E n ι hι
  exact LatticeCongruenceTopology60.congruence_open e (latticeChain K E n)
    (latticeChain_compact K E n) (latticeChain_open K E n) c r hr hp

/-- The actual type group is open because it contains the proved open first congruence group. -/
theorem matrixType_open (e : (n → E) ≃L[K] (d → K))
    (hK : Continuous (algebraMap K E)) :
    IsOpen (matrixType K E n d e : Set (GeneralLinearGroup d K)) := by
  apply Subgroup.isOpen_mono (H₁ := matrixCongruence K E n d e)
  · intro g hg
    exact (show ActualELatticeTypeGroup59.congruence K E n ≤ typeGroup K E n from le_sup_right) hg
  · exact matrixCongruence_open K E n d e hK

/-- Compactness follows inside the actual compact integral-lattice stabilizer. -/
theorem matrixType_compact (e : (n → E) ≃L[K] (d → K))
    (hK : Continuous (algebraMap K E)) :
    IsCompact (matrixType K E n d e : Set (GeneralLinearGroup d K)) := by
  let : ContinuousSMul K E := continuousSMul_of_algebraMap K E hK
  let : Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ) := field_nhdsNE_neBot K
  have hc := stabilizer_compact_of_open e (integralLattice E n)
    (integralLattice_compact E n) (integralLattice_open E n)
  apply hc.of_isClosed_subset ((matrixType K E n d e).isClosed_of_isOpen (matrixType_open K E n d e hK))
  intro g hg
  apply (mem_stabilizer_iff e (integralLattice E n) g).mpr
  have h : coordinateAut e g ∈ chainStabilizer (latticeChain K E n) :=
    typeGroup_le_stabilizer K E n hg
  simpa only [latticeChain_zero] using h 0

/-- The exact first congruence group is compact as a closed subgroup of the compact type group. -/
theorem matrixCongruence_compact (e : (n → E) ≃L[K] (d → K))
    (hK : Continuous (algebraMap K E)) :
    IsCompact (matrixCongruence K E n d e : Set (GeneralLinearGroup d K)) := by
  apply (matrixType_compact K E n d e hK).of_isClosed_subset
    ((matrixCongruence K E n d e).isClosed_of_isOpen (matrixCongruence_open K E n d e hK))
  intro g hg
  exact (show ActualELatticeTypeGroup59.congruence K E n ≤ typeGroup K E n from le_sup_right) hg

/-- The compact/open result for any actual finite basis, with coordinate continuity derived. -/
theorem compact_open_of_basis (hK : Continuous (algebraMap K E))
    (b : Module.Basis d K (n → E)) :
    IsCompact (matrixType K E n d (coordinatesOfBasis K E n d hK b) : Set (GeneralLinearGroup d K)) ∧
    IsOpen (matrixType K E n d (coordinatesOfBasis K E n d hK b) : Set (GeneralLinearGroup d K)) :=
  ⟨matrixType_compact K E n d _ hK, matrixType_open K E n d _ hK⟩

/-- Finite-extension coordinates require no supplied basis or continuity of coordinates. -/
def finiteExtensionCoordinates [FiniteDimensional K E] (hK : Continuous (algebraMap K E)) :
    (n → E) ≃L[K] (Fin (Module.finrank K (n → E)) → K) :=
  coordinatesOfBasis K E n _ hK (Module.finBasis K (n → E))

omit [Fintype d] [DecidableEq d] [Nonempty d] in
/-- Every genuine finite continuous extension realizes the literal type group compact openly. -/
theorem finiteExtension_compact_open [FiniteDimensional K E] [Nonempty n]
    (hK : Continuous (algebraMap K E)) :
    IsCompact (matrixType K E n (Fin (Module.finrank K (n → E)))
      (finiteExtensionCoordinates K E n hK) : Set (GeneralLinearGroup (Fin (Module.finrank K (n → E))) K)) ∧
    IsOpen (matrixType K E n (Fin (Module.finrank K (n → E)))
      (finiteExtensionCoordinates K E n hK) : Set (GeneralLinearGroup (Fin (Module.finrank K (n → E))) K)) := by
  let : Nonempty (Fin (Module.finrank K (n → E))) := ⟨⟨0, Module.finrank_pos⟩⟩
  exact ⟨matrixType_compact K E n _ _ hK, matrixType_open K E n _ _ hK⟩

end PaperXI.ActualELatticeTopology60
