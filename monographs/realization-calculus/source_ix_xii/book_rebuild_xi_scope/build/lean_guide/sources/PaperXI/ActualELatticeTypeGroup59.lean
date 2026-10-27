import PaperXI.ActualELatticeNormalizer59
import PaperXI.ActualELatticeResidue59

/-!
# The actual lattice-product type group

The lattice and its first congruence subgroup are literal subgroups of
`Aut_K(E^n)`. The centralizer integral matrices normalize congruence, and their
intersection with congruence is exactly their residue kernel.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeTypeGroup59
open Matrix ValuativeRel
open ActualELatticeNormalizer59 ActualELatticeResidue59

variable (K E : Type*) [Field K] [Field E] [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n]
variable [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]

/-- Actual multiplication by the chosen extension-field uniformizer. -/
def uniformizerAction : (n → E) ≃ₗ[K] (n → E) :=
  (LinearEquiv.smulOfNeZero E (n → E) (ActualLocalUnitDecomposition.uniformizer E : E)
    (ActualLocalUnitDecomposition.uniformizer_ne_zero E)).restrictScalars K

omit [Fintype n] [DecidableEq n] in
@[simp] theorem uniformizerAction_apply (v : n → E) :
    uniformizerAction K E n v = (ActualLocalUnitDecomposition.uniformizer E : E) • v := rfl

/-- Every level is an actual scalar translate of the integral lattice. -/
def latticeChain : ℤ → AddSubgroup (n → E) :=
  periodicChain (uniformizerAction K E n) (integralLattice E n)

omit [Fintype n] [DecidableEq n] in
@[simp] theorem latticeChain_zero : latticeChain K E n 0 = integralLattice E n := by
  ext v
  simp [latticeChain, periodicChain]

omit [Fintype n] [DecidableEq n] in
@[simp] theorem latticeChain_one : latticeChain K E n 1 = nextLattice E n := by
  ext v
  change (uniformizerAction K E n ^ (-(1 : ℤ))) v ∈ integralLattice E n ↔ _
  rw [zpow_neg_one, mem_nextLattice]
  constructor
  · intro hv
    exact ⟨(uniformizerAction K E n)⁻¹ v, hv,
      (uniformizerAction K E n).apply_symm_apply v⟩
  · rintro ⟨w, hw, he⟩
    change uniformizerAction K E n w = v at he
    rw [← he]
    change (uniformizerAction K E n).symm (uniformizerAction K E n w) ∈ _
    rwa [LinearEquiv.symm_apply_apply]

omit [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- Integral extension-linear automorphisms preserve the integral lattice. -/
theorem integralMatrix_preserves_iff (g : GeneralLinearGroup n 𝒪[E]) (v : n → E) :
    integralMatrix K E n g v ∈ integralLattice E n ↔ v ∈ integralLattice E n := by
  constructor
  · intro hv
    have h := integralMatrix_preserves K E n g⁻¹ _ hv
    simpa [← LinearEquiv.mul_apply, ← map_mul] using h
  · exact integralMatrix_preserves K E n g v

/-- The field uniformizer centralizes the literal extension-linear matrices. -/
theorem integralMatrix_commute (g : GeneralLinearGroup n 𝒪[E]) :
    Commute (integralMatrix K E n g) (uniformizerAction K E n) := by
  apply LinearEquiv.ext
  intro v
  change ((GeneralLinearGroup.toLin (ActualIntegralGeneralLinear.embedding E n g)).toLinearEquiv)
      ((ActualLocalUnitDecomposition.uniformizer E : E) • v) = _
  exact map_smul _ _ _

/-- Hence integral extension-linear matrices preserve every chain level. -/
theorem integralMatrix_mem_stabilizer (g : GeneralLinearGroup n 𝒪[E]) :
    integralMatrix K E n g ∈ chainStabilizer (latticeChain K E n) := by
  intro i v
  change (uniformizerAction K E n ^ (-i)) (integralMatrix K E n g v) ∈ integralLattice E n ↔ _
  have hc := (integralMatrix_commute K E n g).zpow_right (-i)
  rw [← LinearEquiv.mul_apply, ← hc.eq, LinearEquiv.mul_apply]
  exact integralMatrix_preserves_iff K E n g _

/-- The literal adjacent-lattice congruence group in `Aut_K(E^n)`. -/
def congruence : Subgroup ((n → E) ≃ₗ[K] (n → E)) :=
  firstCongruence (latticeChain K E n)

/-- Integral extension-linear matrices normalize the actual congruence group. -/
theorem integralImage_normalizes : integralImage K E n ≤
    Subgroup.normalizer (congruence K E n : Set ((n → E) ≃ₗ[K] (n → E))) := by
  rintro g ⟨h, rfl⟩
  exact stabilizer_normalizes_firstCongruence (latticeChain K E n)
    (integralMatrix_mem_stabilizer K E n h)

/-- First congruence for an extension-linear matrix is exactly residue identity. -/
theorem integralMatrix_mem_congruence_iff (g : GeneralLinearGroup n 𝒪[E]) :
    integralMatrix K E n g ∈ congruence K E n ↔
      g ∈ (ActualResidueGeneralLinear.reduction E n).ker := by
  rw [reduction_kernel_iff K E n]
  constructor
  · intro hg v hv
    have h := hg.2 0 v (by simpa using hv)
    simpa using h
  · intro hg
    refine ⟨integralMatrix_mem_stabilizer K E n g, ?_⟩
    intro i v hv
    have hi : (uniformizerAction K E n ^ (-i)) v ∈ integralLattice E n := hv
    have h := hg _ hi
    have hc := (integralMatrix_commute K E n g).zpow_right (-i)
    have he : integralMatrix K E n g ((uniformizerAction K E n ^ (-i)) v) -
        (uniformizerAction K E n ^ (-i)) v =
        (uniformizerAction K E n ^ (-i)) (integralMatrix K E n g v - v) := by
      rw [map_sub, ← LinearEquiv.mul_apply, hc.eq, LinearEquiv.mul_apply]
    rw [he, ← latticeChain_one K E n] at h
    have ht := (periodicChain_shift (uniformizerAction K E n) (integralLattice E n)
      i 1 ((uniformizerAction K E n ^ (-i)) (integralMatrix K E n g v - v))).mpr h
    have hcancel : (uniformizerAction K E n ^ i)
        ((uniformizerAction K E n ^ (-i)) (integralMatrix K E n g v - v)) =
        integralMatrix K E n g v - v := by
      rw [← LinearEquiv.mul_apply, ← zpow_add, add_neg_cancel, zpow_zero]
      rfl
    rw [hcancel] at ht
    simpa only [latticeChain, add_comm 1 i] using ht

/-- On the literal integral image, the congruence intersection is the residue kernel. -/
theorem congruence_subgroupOf_integralImage :
    (congruence K E n).subgroupOf (integralImage K E n) = (residueAction K E n).ker := by
  ext g
  obtain ⟨h, rfl⟩ := (integralImageEquiv K E n).surjective g
  change integralMatrix K E n h ∈ congruence K E n ↔ _
  rw [integralMatrix_mem_congruence_iff]
  simp [residueAction]

/-- The actual centralizer-integral-times-congruence subgroup. -/
def typeGroup : Subgroup ((n → E) ≃ₗ[K] (n → E)) :=
  integralImage K E n ⊔ congruence K E n

end PaperXI.ActualELatticeTypeGroup59
