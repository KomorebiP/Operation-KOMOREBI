import PaperXI.CharacterNormalizer61
import PaperXI.ActualELatticeTopology60

/-!
# The compact lattice part of an actual character normalizer

This group depends on the actual subgroup-character pair. It is not the larger
literal lattice-product group from Block59. Its first subgroup is its actual
intersection with adjacent-lattice congruence, never an equality with all U1.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCharacterType61
open Matrix ValuativeRel Topology
open ActualELatticeNormalizer59 ActualELatticeResidue59 ActualELatticeTypeGroup59
open ActualELatticeQuotient59 ActualELatticeTopology60 LatticeMatrixTopology60
open LatticeCongruenceTopology60 ActualEmbeddedUniformizer58

section Chain
variable {F V : Type*} [Field F] [AddCommGroup V] [Module F V]

/-- The chain shift normalizes the full chain stabilizer, for positive and negative powers. -/
theorem power_normalizes_chainStabilizer (t : V ≃ₗ[F] V) (L : AddSubgroup V) (r : ℤ) :
    t ^ r ∈ Subgroup.normalizer (chainStabilizer (K := F) (periodicChain t L) : Set (V ≃ₗ[F] V)) := by
  have shift (r i : ℤ) (v : V) :
      (t ^ r) v ∈ periodicChain t L i ↔ v ∈ periodicChain t L (i - r) := by
    simpa only [sub_add_cancel] using periodicChain_shift t L r (i - r) v
  have step (r : ℤ) (g : V ≃ₗ[F] V) (hg : g ∈ chainStabilizer (K := F) (periodicChain t L)) :
      t ^ r * g * (t ^ r)⁻¹ ∈ chainStabilizer (K := F) (periodicChain t L) := by
    intro i v
    change (t ^ r) (g ((t ^ r)⁻¹ v)) ∈ periodicChain t L i ↔ _
    rw [shift, hg (i - r)]
    simpa [zpow_neg, sub_eq_add_neg] using shift (-r) (i - r) v
  apply Subgroup.mem_normalizer_iff.mpr
  intro g
  constructor
  · exact step r g
  · intro hg
    have h := step (-r) (t ^ r * g * (t ^ r)⁻¹) hg
    simpa [zpow_neg, mul_assoc] using h
end Chain

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra K E]
variable (n d : Type*) [Fintype n] [DecidableEq n] [Fintype d] [DecidableEq d]
  [Nonempty d] (e : (n → E) ≃L[K] (d → K))

local instance : T2Space K := ActualIntegralGeneralLinear.field_t2Space K
local instance : T2Space E := ActualIntegralGeneralLinear.field_t2Space E

/-- The full actual lattice-chain stabilizer in matrix coordinates. -/
def chainGroup : Subgroup (GeneralLinearGroup d K) :=
  (chainStabilizer (latticeChain K E n)).comap (coordinateAut e).toMonoidHom

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- Full-chain congruence lies in the full-chain stabilizer. -/
theorem matrixCongruence_le_chainGroup : matrixCongruence K E n d e ≤ chainGroup K E n d e :=
  fun _ h => h.1

/-- The full chain stabilizer is open. -/
theorem chainGroup_open (hK : Continuous (algebraMap K E)) :
    IsOpen (chainGroup K E n d e : Set (GeneralLinearGroup d K)) :=
  Subgroup.isOpen_mono (matrixCongruence_le_chainGroup K E n d e)
    (matrixCongruence_open K E n d e hK)

/-- The full chain stabilizer is compact, inside the zero-lattice stabilizer. -/
theorem chainGroup_compact (hK : Continuous (algebraMap K E)) :
    IsCompact (chainGroup K E n d e : Set (GeneralLinearGroup d K)) := by
  let : ContinuousSMul K E := continuousSMul_of_algebraMap K E hK
  let : Filter.NeBot (nhdsWithin (0 : K) {0}ᶜ) := field_nhdsNE_neBot K
  apply (stabilizer_compact_of_open e (integralLattice E n)
    (integralLattice_compact E n) (integralLattice_open E n)).of_isClosed_subset
    ((chainGroup K E n d e).isClosed_of_isOpen (chainGroup_open K E n d e hK))
  intro g hg
  apply (mem_stabilizer_iff e (integralLattice E n) g).mpr
  have h : coordinateAut e g ∈ chainStabilizer (latticeChain K E n) := hg
  simpa only [latticeChain_zero] using h 0

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [ValuativeRel E] [IsNonarchimedeanLocalField E]
  [Fintype n] [DecidableEq n] [Nonempty d] in
/-- Every embedded extension-field unit acts by its literal scalar linear operator. -/
theorem coordinateAut_unitsEmbedding (a : Eˣ) :
    coordinateAut e (unitsEmbedding K E d (scalarMatrixEmbedding K E n d e) a) =
      ActualELatticeFreeness59.scalarAction K E n a := by
  apply LinearEquiv.ext
  intro v
  change e.symm ((LinearMap.toMatrix' ((e.toLinearEquiv.conjAlgEquiv K)
    ((Algebra.lsmul K K (n → E)) (a : E)))) *ᵥ e v) = _
  rw [LinearMap.toMatrix'_mulVec]
  change e.symm (e ((a : E) • e.symm (e v))) = (a : E) • v
  simp only [ContinuousLinearEquiv.symm_apply_apply]

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- The embedded extension uniformizer acts by the exact inherited scalar operator. -/
theorem coordinateAut_embeddedUniformizer :
    coordinateAut e (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e)) =
      uniformizerAction K E n := by
  apply LinearEquiv.ext
  intro v
  change e.symm ((LinearMap.toMatrix' ((e.toLinearEquiv.conjAlgEquiv K)
    ((Algebra.lsmul K K (n → E)) (ActualLocalUnitDecomposition.uniformizer E : E)))) *ᵥ e v) = _
  rw [LinearMap.toMatrix'_mulVec]
  change e.symm (e ((ActualLocalUnitDecomposition.uniformizer E : E) • e.symm (e v))) =
    (ActualLocalUnitDecomposition.uniformizer E : E) • v
  simp only [ContinuousLinearEquiv.symm_apply_apply]

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- The actual embedded uniformizer normalizes the full chain stabilizer. -/
theorem uniformizer_normalizes_chainGroup :
    embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ∈
      Subgroup.normalizer (chainGroup K E n d e : Set (GeneralLinearGroup d K)) := by
  apply Subgroup.mem_normalizer_iff.mpr
  intro g
  change coordinateAut e g ∈ chainStabilizer (latticeChain K E n) ↔
    coordinateAut e (_ * g * _) ∈ chainStabilizer (latticeChain K E n)
  rw [map_mul, map_mul, map_inv, coordinateAut_embeddedUniformizer]
  exact Subgroup.mem_normalizer_iff.mp
    (by simpa only [zpow_one, latticeChain] using
      power_normalizes_chainStabilizer (uniformizerAction K E n) (integralLattice E n) 1)
    (coordinateAut e g)

variable (H : Subgroup (GeneralLinearGroup d K)) (θ : H →* ℂˣ)

/-- The actual theta-dependent compact group, using the graph normalizer. -/
def compactGroup : Subgroup (GeneralLinearGroup d K) :=
  CharacterNormalizer61.compactPart H θ (chainGroup K E n d e)

/-- Its first subgroup is the literal intersection, not the whole adjacent-lattice group. -/
def firstSubgroup : Subgroup (compactGroup K E n d e H θ) :=
  (matrixCongruence K E n d e).subgroupOf (compactGroup K E n d e H θ)

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- The actual character domain lies in its compact group when it preserves the chain. -/
theorem domain_le_compactGroup (hH : H ≤ chainGroup K E n d e) :
    H ≤ compactGroup K E n d e H θ :=
  le_inf (CharacterNormalizer61.domain_le_normalizer H θ) hH

/-- Compactness and openness now refer to the actual character-normalizer intersection. -/
theorem compactGroup_compact_open (hK : Continuous (algebraMap K E))
    (hH : IsOpen (H : Set (GeneralLinearGroup d K))) :
    IsCompact (compactGroup K E n d e H θ : Set (GeneralLinearGroup d K)) ∧
    IsOpen (compactGroup K E n d e H θ : Set (GeneralLinearGroup d K)) :=
  CharacterNormalizer61.compactPart_compact_open H θ (chainGroup K E n d e) hH
    (chainGroup_compact K E n d e hK) (chainGroup_open K E n d e hK)

/-- The genuine intersection subgroup is open inside the compact group. -/
theorem firstSubgroup_open (hK : Continuous (algebraMap K E)) :
    IsOpen (firstSubgroup K E n d e H θ : Set (compactGroup K E n d e H θ)) :=
  (matrixCongruence_open K E n d e hK).preimage continuous_subtype_val

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Fintype n] [DecidableEq n] [Nonempty d] in
/-- Pair-normalization of theta makes the same embedded uniformizer normalize its compact part. -/
theorem uniformizer_normalizes_compactGroup
    (hθ : embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ∈
      CharacterNormalizer61.normalizer H θ) :
    embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ∈
      Subgroup.normalizer (compactGroup K E n d e H θ : Set (GeneralLinearGroup d K)) :=
  Subgroup.inf_normalizer_le_normalizer_inf
    ⟨(CharacterNormalizer61.normalizer H θ).le_normalizer hθ,
      uniformizer_normalizes_chainGroup K E n d e⟩

end PaperXI.ActualCharacterType61
