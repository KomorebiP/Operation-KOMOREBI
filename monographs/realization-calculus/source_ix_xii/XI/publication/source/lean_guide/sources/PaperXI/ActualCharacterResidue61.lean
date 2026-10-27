import PaperXI.ActualCharacterType61
import PaperXI.ActualELatticeFieldJoin59

/-!
# Actual residue reduction on the theta-dependent compact group

The map is the restriction of the already constructed literal lattice residue
map. Its kernel is the actual intersection C(theta)∩U_a1. Containment in the
lattice-product group and normalization of theta by integral centralizer
matrices are explicit standard-type inputs. They do not assert C(theta)=B U_a1.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCharacterResidue61
open Matrix ValuativeRel
open ActualCharacterType61 ActualELatticeTopology60 ActualELatticeResidue59
open ActualELatticeTypeGroup59 ActualELatticeQuotient59 LatticeCongruenceTopology60
open ActualEmbeddedUniformizer58 NormalizerExtensionInducing58

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra K E]
variable (n d : Type*) [Fintype n] [DecidableEq n] [Fintype d] [DecidableEq d]
  [Nonempty d] (e : (n → E) ≃L[K] (d → K))
variable (H : Subgroup (GeneralLinearGroup d K)) (θ : H →* ℂˣ)
variable (hmodel : compactGroup K E n d e H θ ≤ matrixType K E n d e)

/-- Actual inclusion into the larger lattice-product group through the same coordinates. -/
def intoModel : compactGroup K E n d e H θ →* typeGroup K E n where
  toFun c := ⟨coordinateAut e c, hmodel c.property⟩
  map_one' := Subtype.ext ((coordinateAut e).map_one)
  map_mul' x y := Subtype.ext ((coordinateAut e).map_mul x y)

/-- Restriction of the actual Block59 residue map, not a newly supplied map. -/
def reduction : compactGroup K E n d e H θ →* GeneralLinearGroup n 𝓀[E] :=
  (ActualELatticeQuotient59.reduction K E n).comp (intoModel K E n d e H θ hmodel)

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Nonempty d] in
/-- The actual theta-dependent first subgroup is exactly the residue kernel. -/
theorem reduction_kernel : (reduction K E n d e H θ hmodel).ker = firstSubgroup K E n d e H θ := by
  ext c
  change intoModel K E n d e H θ hmodel c ∈ (ActualELatticeQuotient59.reduction K E n).ker ↔ _
  rw [ActualELatticeQuotient59.reduction_kernel]
  rfl

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Nonempty d] in
/-- Integral centralizer matrices normalizing theta lie in the constructed compact group. -/
theorem integralMatrix_mem_compactGroup
    (hB : ∀ b : GeneralLinearGroup n 𝒪[E], (coordinateAut e).symm (integralMatrix K E n b) ∈
      CharacterNormalizer61.normalizer H θ) (b : GeneralLinearGroup n 𝒪[E]) :
    (coordinateAut e).symm (integralMatrix K E n b) ∈ compactGroup K E n d e H θ := by
  refine ⟨hB b, ?_⟩
  change coordinateAut e ((coordinateAut e).symm (integralMatrix K E n b)) ∈
    ActualELatticeNormalizer59.chainStabilizer (latticeChain K E n)
  rw [MulEquiv.apply_symm_apply]
  exact integralMatrix_mem_stabilizer K E n b

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Nonempty d] in
/-- The actual integral E-units belong to the same theta-dependent compact group. -/
theorem integralUnit_mem_compactGroup
    (hB : ∀ b : GeneralLinearGroup n 𝒪[E], (coordinateAut e).symm (integralMatrix K E n b) ∈
      CharacterNormalizer61.normalizer H θ) (u : 𝒪[E]ˣ) :
    unitsEmbedding K E d (scalarMatrixEmbedding K E n d e)
      (ActualLocalUnitTopology.unitEmbedding E u) ∈ compactGroup K E n d e H θ := by
  have h := integralMatrix_mem_compactGroup K E n d e H θ hB (GeneralLinearGroup.scalar n u)
  have he : (coordinateAut e).symm (integralMatrix K E n (GeneralLinearGroup.scalar n u)) =
      unitsEmbedding K E d (scalarMatrixEmbedding K E n d e)
        (ActualLocalUnitTopology.unitEmbedding E u) := by
    apply (coordinateAut e).injective
    rw [MulEquiv.apply_symm_apply, coordinateAut_unitsEmbedding,
      ActualELatticeFieldJoin59.integralMatrix_scalar]
  exact he ▸ h

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Nonempty d] in
/-- Surjectivity follows from integral centralizer matrices, while the kernel remains only their actual intersection. -/
theorem reduction_surjective
    (hB : ∀ b : GeneralLinearGroup n 𝒪[E], (coordinateAut e).symm (integralMatrix K E n b) ∈
      CharacterNormalizer61.normalizer H θ) :
    Function.Surjective (reduction K E n d e H θ hmodel) := by
  intro x
  obtain ⟨g, hg⟩ := ActualELatticeQuotient59.reduction_surjective K E n x
  have hmem := g.property
  change (g : (n → E) ≃ₗ[K] (n → E)) ∈
    integralImage K E n ⊔ ActualELatticeTypeGroup59.congruence K E n at hmem
  rw [← SetLike.mem_coe,
    Subgroup.coe_mul_of_left_le_normalizer_right _ _ (integralImage_normalizes K E n)] at hmem
  obtain ⟨b, hb, u, hu, hbu⟩ := hmem
  obtain ⟨b0, rfl⟩ := hb
  let c : compactGroup K E n d e H θ :=
    ⟨(coordinateAut e).symm (integralMatrix K E n b0),
      integralMatrix_mem_compactGroup K E n d e H θ hB b0⟩
  let u0 : typeGroup K E n := ⟨u, (show ActualELatticeTypeGroup59.congruence K E n ≤
    typeGroup K E n from le_sup_right) hu⟩
  have hu0 : ActualELatticeQuotient59.reduction K E n u0 = 1 := by
    change u0 ∈ (ActualELatticeQuotient59.reduction K E n).ker
    rw [ActualELatticeQuotient59.reduction_kernel]
    exact hu
  have hge : g = intoModel K E n d e H θ hmodel c * u0 := by
    apply Subtype.ext
    change (g : (n → E) ≃ₗ[K] (n → E)) =
      coordinateAut e ((coordinateAut e).symm (integralMatrix K E n b0)) * u
    rw [MulEquiv.apply_symm_apply]
    exact hbu.symm
  refine ⟨c, ?_⟩
  rw [hge, map_mul, hu0, mul_one] at hg
  exact hg

omit [ValuativeRel K] [IsNonarchimedeanLocalField K] [Nonempty d] in
/-- Uniformizer conjugation preserves the same actual restricted residue matrix. -/
theorem reduction_conjugation
    (hθ : embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) ∈
      CharacterNormalizer61.normalizer H θ)
    (c : compactGroup K E n d e H θ) :
    reduction K E n d e H θ hmodel
      (conjugation (compactGroup K E n d e H θ)
        (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e))
        (uniformizer_normalizes_compactGroup K E n d e H θ hθ) c) =
      reduction K E n d e H θ hmodel c := by
  have he : intoModel K E n d e H θ hmodel
      (conjugation (compactGroup K E n d e H θ)
        (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e))
        (uniformizer_normalizes_compactGroup K E n d e H θ hθ) c) =
      uniformizerConjugation K E n (intoModel K E n d e H θ hmodel c) := by
    apply Subtype.ext
    change coordinateAut e (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e) *
      (c : GeneralLinearGroup d K) * (embeddedUniformizer K E d (scalarMatrixEmbedding K E n d e))⁻¹) =
      uniformizerAction K E n * coordinateAut e c * (uniformizerAction K E n)⁻¹
    rw [map_mul, map_mul, map_inv, coordinateAut_embeddedUniformizer]
  change ActualELatticeQuotient59.reduction K E n _ = _
  rw [he]
  exact ActualELatticeQuotient59.reduction_conjugation K E n _

end PaperXI.ActualCharacterResidue61
