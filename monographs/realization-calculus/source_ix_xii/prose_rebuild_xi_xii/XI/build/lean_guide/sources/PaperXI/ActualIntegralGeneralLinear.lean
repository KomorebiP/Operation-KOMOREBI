import PaperXI.ActualResidueGeneralLinear
import PaperXI.QuotientRepresentation
import PaperXI.SmoothDegreeQuotient
import PaperXI.FiniteRepresentation
import Mathlib.Topology.Algebra.Group.Matrix
import Mathlib.Topology.Algebra.Ring.Compact

/-!
# The actual compact open integral subgroup of `GL_n(K)`

The subgroup is the image of `GL_n(𝒪[K])` in the given local field's matrix
group. Its compactness, openness and actual residue quotient are derived from
the entrywise maps. Inflation therefore gives smooth irreducible actions on
this actual subgroup from actual irreducible finite residue representations.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualIntegralGeneralLinear

open Matrix ValuativeRel Topology
open ActualResidueGeneralLinear

variable (K : Type*) [Field K] [ValuativeRel K]
variable (n : Type*) [Fintype n] [DecidableEq n]

/-- Entrywise inclusion into the actual ambient general linear group. -/
def embedding : GeneralLinearGroup n 𝒪[K] →* GeneralLinearGroup n K :=
  GeneralLinearGroup.map (valuation K).integer.subtype

@[simp] theorem embedding_apply (g : GeneralLinearGroup n 𝒪[K]) (i j : n) :
    embedding K n g i j = (g i j : K) := rfl

theorem embedding_injective : Function.Injective (embedding K n) := by
  intro g h he
  apply GeneralLinearGroup.ext
  intro i j
  apply Subtype.ext
  exact congrArg (fun A : GeneralLinearGroup n K => A i j) he

/-- The actual integral subgroup inside `GL_n(K)`. -/
def integralSubgroup : Subgroup (GeneralLinearGroup n K) := (embedding K n).range

/-- Integral matrices are identified with their actual ambient subgroup. -/
def integralEquiv : GeneralLinearGroup n 𝒪[K] ≃* integralSubgroup K n :=
  MonoidHom.ofInjective (embedding_injective K n)

@[simp] theorem integralEquiv_coe (g : GeneralLinearGroup n 𝒪[K]) :
    (integralEquiv K n g : GeneralLinearGroup n K) = embedding K n g := rfl

@[simp] theorem embedding_integralEquiv_symm (g : integralSubgroup K n) :
    embedding K n ((integralEquiv K n).symm g) = g :=
  congrArg Subtype.val ((integralEquiv K n).apply_symm_apply g)

/-- Membership is exactly integrality of both the matrix and its inverse. -/
theorem mem_integralSubgroup (g : GeneralLinearGroup n K) :
    g ∈ integralSubgroup K n ↔
      (∀ i j, g i j ∈ (valuation K).integer) ∧
      (∀ i j, g⁻¹ i j ∈ (valuation K).integer) := by
  constructor
  · rintro ⟨h, rfl⟩
    exact ⟨fun i j => (h i j).property, fun i j => (h⁻¹ i j).property⟩
  · rintro ⟨hg, hi⟩
    let A : Matrix n n 𝒪[K] := fun i j => ⟨g i j, hg i j⟩
    let B : Matrix n n 𝒪[K] := fun i j => ⟨g⁻¹ i j, hi i j⟩
    have hA : A.map ((valuation K).integer.subtype) = (g : Matrix n n K) := rfl
    have hB : B.map ((valuation K).integer.subtype) =
        ((g⁻¹ : GeneralLinearGroup n K) : Matrix n n K) := rfl
    have hab : A * B = 1 := by
      apply Matrix.map_injective Subtype.val_injective
      change (RingHom.mapMatrix (valuation K).integer.subtype) (A * B) =
        (RingHom.mapMatrix (valuation K).integer.subtype) 1
      rw [map_mul, map_one]
      exact g.mul_inv
    have hba : B * A = 1 := by
      apply Matrix.map_injective Subtype.val_injective
      change (RingHom.mapMatrix (valuation K).integer.subtype) (B * A) =
        (RingHom.mapMatrix (valuation K).integer.subtype) 1
      rw [map_mul, map_one]
      exact g.inv_mul
    exact ⟨⟨A, B, hab, hba⟩, Units.ext hA⟩

variable [TopologicalSpace K] [IsNonarchimedeanLocalField K]

theorem field_t2Space : T2Space K := by
  let := IsTopologicalAddGroup.rightUniformSpace K
  have := isUniformAddGroup_of_addCommGroup (G := K)
  infer_instance

local instance : T2Space K := field_t2Space K

omit [IsNonarchimedeanLocalField K] in
theorem embedding_isEmbedding : IsEmbedding (embedding K n) :=
  (IsEmbedding.subtypeVal : IsEmbedding ((valuation K).integer.subtype)).generalLinearGroup_map

omit [IsNonarchimedeanLocalField K] in
theorem embedding_continuous : Continuous (embedding K n) :=
  (embedding_isEmbedding K n).continuous

omit [IsNonarchimedeanLocalField K] in
theorem integralEquiv_symm_continuous : Continuous (integralEquiv K n).symm := by
  apply (embedding_isEmbedding K n).continuous_iff.mpr
  have he : embedding K n ∘ (integralEquiv K n).symm =
      (Subtype.val : integralSubgroup K n → GeneralLinearGroup n K) := by
    funext g
    exact embedding_integralEquiv_symm K n g
  rw [he]
  exact continuous_subtype_val

/-- Compactness is inherited from finite matrices over the actual compact
integer ring and the topology on units. -/
theorem integralSubgroup_compact : IsCompact (integralSubgroup K n : Set (GeneralLinearGroup n K)) := by
  let : CompactSpace 𝒪[K] := inferInstance
  let : CompactSpace (Matrix n n 𝒪[K]) := inferInstanceAs (CompactSpace (n → n → 𝒪[K]))
  let : T1Space (Matrix n n 𝒪[K]) := inferInstance
  let : ContinuousMul (Matrix n n 𝒪[K]) := inferInstance
  let : CompactSpace (GeneralLinearGroup n 𝒪[K]) := inferInstance
  exact isCompact_range (embedding_continuous K n)

/-- Integrality of a matrix and its inverse are open entrywise conditions. -/
theorem integralSubgroup_open : IsOpen (integralSubgroup K n : Set (GeneralLinearGroup n K)) := by
  let U : Submonoid (Matrix n n K) := (valuation K).integer.matrix.toSubmonoid
  have he : (integralSubgroup K n : Set (GeneralLinearGroup n K)) =
      (U.units : Set (GeneralLinearGroup n K)) := by
    ext g
    exact mem_integralSubgroup K n g
  rw [he]
  apply Submonoid.isOpen_units
  exact (Valuation.isOpen_integer (v := valuation K)).matrix

/-- Literal residue reduction on the actual subgroup of the ambient group. -/
def reductionOnSubgroup : integralSubgroup K n →* GeneralLinearGroup n 𝓀[K] :=
  (reduction K n).comp (integralEquiv K n).symm.toMonoidHom

@[simp] theorem reductionOnSubgroup_integralEquiv (g : GeneralLinearGroup n 𝒪[K]) :
    reductionOnSubgroup K n (integralEquiv K n g) = reduction K n g := by
  simp [reductionOnSubgroup]

theorem reductionOnSubgroup_surjective : Function.Surjective (reductionOnSubgroup K n) :=
  (reduction_surjective K n).comp (integralEquiv K n).symm.surjective

/-- The congruence kernel is given by entrywise congruence to the identity. -/
theorem mem_reduction_kernel (g : GeneralLinearGroup n 𝒪[K]) :
    g ∈ (reduction K n).ker ↔
      ∀ i j, g i j - (1 : Matrix n n 𝒪[K]) i j ∈ IsLocalRing.maximalIdeal 𝒪[K] := by
  change reduction K n g = 1 ↔ _
  rw [GeneralLinearGroup.ext_iff]
  simp only [reduction_apply, GeneralLinearGroup.coe_one]
  apply forall_congr'
  intro i
  apply forall_congr'
  intro j
  rw [← IsLocalRing.residue_eq_zero_iff, map_sub, sub_eq_zero]
  simp [Matrix.one_apply]

/-- The principal congruence kernel is open in the actual integral group. -/
theorem reduction_kernel_open : IsOpen ((reduction K n).ker : Set (GeneralLinearGroup n 𝒪[K])) := by
  have he : ((reduction K n).ker : Set (GeneralLinearGroup n 𝒪[K])) =
      ⋂ i, ⋂ j, {g : GeneralLinearGroup n 𝒪[K] |
        g i j - (1 : Matrix n n 𝒪[K]) i j ∈ IsLocalRing.maximalIdeal 𝒪[K]} := by
    ext g
    simp only [Set.mem_iInter, Set.mem_ofPred_eq]
    exact mem_reduction_kernel K n g
  rw [he]
  apply isOpen_iInter_of_finite
  intro i
  apply isOpen_iInter_of_finite
  intro j
  apply (IsLocalRing.isOpen_maximalIdeal 𝒪[K]).preimage
  fun_prop

theorem reductionOnSubgroup_kernel_open :
    IsOpen ((reductionOnSubgroup K n).ker : Set (integralSubgroup K n)) :=
  (reduction_kernel_open K n).preimage (integralEquiv_symm_continuous K n)

/-- The actual principal-congruence quotient is the full finite residue
general linear group, by the proved surjectivity of entrywise reduction. -/
def residueQuotientEquiv :
    integralSubgroup K n ⧸ (reductionOnSubgroup K n).ker ≃* GeneralLinearGroup n 𝓀[K] :=
  QuotientGroup.quotientKerEquivOfSurjective (reductionOnSubgroup K n)
    (reductionOnSubgroup_surjective K n)

theorem finite_residue_quotient :
    Finite (integralSubgroup K n ⧸ (reductionOnSubgroup K n).ker) :=
  Finite.of_injective (residueQuotientEquiv K n) (residueQuotientEquiv K n).injective

variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (σ : Representation ℂ (GeneralLinearGroup n 𝓀[K]) V)

/-- Inflation on the actual ambient integral subgroup, using its literal
entrywise residue quotient. -/
def inflated : Representation ℂ (integralSubgroup K n) V :=
  σ.comp (reductionOnSubgroup K n)

@[simp] theorem inflated_integralEquiv (g : GeneralLinearGroup n 𝒪[K]) :
    inflated K n σ (integralEquiv K n g) = σ (reduction K n g) := by
  simp [inflated]

/-- Irreducibility is preserved by the proved surjective actual residue map. -/
theorem inflated_irreducible [Representation.IsIrreducible σ] :
    Representation.IsIrreducible (inflated K n σ) :=
  (QuotientRepresentation.irreducible_comp_iff (reductionOnSubgroup K n)
    (reductionOnSubgroup_surjective K n) σ).mpr inferInstance

/-- The open principal-congruence kernel fixes every vector after inflation. -/
theorem inflated_isSmooth : SmoothDegreeQuotient.IsSmooth (inflated K n σ) := by
  intro v
  apply Subgroup.isOpen_mono (H₁ := (reductionOnSubgroup K n).ker) _
    (reductionOnSubgroup_kernel_open K n)
  intro g hg
  change σ (reductionOnSubgroup K n g) v = v
  rw [show reductionOnSubgroup K n g = 1 from hg, map_one]
  rfl

/-- Finite dimension follows from the actual finite residue group and
irreducibility of its supplied representation. -/
theorem inflated_finiteDimensional [Representation.IsIrreducible σ] :
    FiniteDimensional ℂ V := FiniteRepresentation.finiteDimensional σ

end PaperXI.ActualIntegralGeneralLinear
