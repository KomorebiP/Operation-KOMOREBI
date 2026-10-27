import PaperXI.ActualCharacterIdentification61
import PaperXI.ActualCharacterResidue61
import PaperXI.ActualCuspidalCandidate105

/-! Conditional character-normalizer dictionary, followed by literal instances.
No canonical simple-stratum group is introduced or identified by assumption. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.NormalizerDictionary110

section Groups
variable {G : Type*} [Group G]
variable (N U₀ U₁ J₁ B : Subgroup G) (I : Set G)

/-- Cancellation inside U₁ identifies the normalizer intersection from support. -/
theorem inf_eq_of_support
    (hJ : J₁ ≤ U₁) (hJN : J₁ ≤ N)
    (hNI : ∀ g, g ∈ N → g ∈ I)
    (hI : ∀ g, g ∈ I → ∃ a : J₁, ∃ b : B, ∃ c : J₁,
      (a : G) * (b : G) * (c : G) = g)
    (hBU : B ⊓ U₁ ≤ J₁) : N ⊓ U₁ = J₁ := by
  apply le_antisymm
  · intro g hg
    obtain ⟨a, b, c, he⟩ := hI g (hNI g hg.1)
    have hb : (b : G) = (a : G)⁻¹ * g * (c : G)⁻¹ := by
      rw [← he]
      group
    have hbU : (b : G) ∈ U₁ := by
      rw [hb]
      exact U₁.mul_mem (U₁.mul_mem (U₁.inv_mem (hJ a.property)) hg.2)
        (U₁.inv_mem (hJ c.property))
    rw [← he]
    exact J₁.mul_mem (J₁.mul_mem a.property (hBU ⟨b.property, hbU⟩)) c.property
  · exact le_inf hJN hJ

/-- The compact intersection is the join of its integral centralizer and J₁. -/
theorem compact_eq_sup_of_support
    (hU : U₁ ≤ U₀) (hJ : J₁ ≤ U₁) (hJN : J₁ ≤ N)
    (hNI : ∀ g, g ∈ N → g ∈ I)
    (hI : ∀ g, g ∈ I → ∃ a : J₁, ∃ b : B, ∃ c : J₁,
      (a : G) * (b : G) * (c : G) = g)
    (hB₀ : B ⊓ U₀ ≤ N) : N ⊓ U₀ = (B ⊓ U₀) ⊔ J₁ := by
  apply le_antisymm
  · intro g hg
    obtain ⟨a, b, c, he⟩ := hI g (hNI g hg.1)
    have hb : (b : G) = (a : G)⁻¹ * g * (c : G)⁻¹ := by
      rw [← he]
      group
    have hbU : (b : G) ∈ U₀ := by
      rw [hb]
      exact U₀.mul_mem (U₀.mul_mem (U₀.inv_mem (hU (hJ a.property))) hg.2)
        (U₀.inv_mem (hU (hJ c.property)))
    rw [← he]
    exact ((B ⊓ U₀) ⊔ J₁).mul_mem
      (((B ⊓ U₀) ⊔ J₁).mul_mem (Subgroup.mem_sup_right a.property)
        (Subgroup.mem_sup_left ⟨b.property, hbU⟩))
      (Subgroup.mem_sup_right c.property)
  · exact sup_le (le_inf hB₀ inf_le_right) (le_inf hJN (hJ.trans hU))

/-- U₁ normal in U₀ implies its normalizer intersection is normal in the compact part. -/
theorem compact_le_normalizer_inf (hnormal : U₀ ≤ Subgroup.normalizer (U₁ : Set G)) :
    N ⊓ U₀ ≤ Subgroup.normalizer ((N ⊓ U₁ : Subgroup G) : Set G) :=
  (inf_le_inf N.le_normalizer hnormal).trans Subgroup.inf_normalizer_le_normalizer_inf

/-- After the dictionary equality, normalization of J₁ requires no extra arithmetic axiom. -/
theorem compact_le_normalizer_of_inf_eq
    (hnormal : U₀ ≤ Subgroup.normalizer (U₁ : Set G)) (he : N ⊓ U₁ = J₁) :
    N ⊓ U₀ ≤ Subgroup.normalizer (J₁ : Set G) := by
  rw [← he]
  exact compact_le_normalizer_inf N U₀ U₁ hnormal

/-- A product presentation follows from U₁ normality and the support dictionary. -/
theorem mem_compact_iff_product
    (hU : U₁ ≤ U₀) (hJ : J₁ ≤ U₁) (hJN : J₁ ≤ N)
    (hNI : ∀ g, g ∈ N → g ∈ I)
    (hI : ∀ g, g ∈ I → ∃ a : J₁, ∃ b : B, ∃ c : J₁,
      (a : G) * (b : G) * (c : G) = g)
    (hBU : B ⊓ U₁ ≤ J₁) (hB₀ : B ⊓ U₀ ≤ N)
    (hnormal : U₀ ≤ Subgroup.normalizer (U₁ : Set G)) (g : G) :
    g ∈ N ⊓ U₀ ↔ ∃ b : (B ⊓ U₀ : Subgroup G), ∃ j : J₁, (b : G) * (j : G) = g := by
  have he := inf_eq_of_support N U₁ J₁ B I hJ hJN hNI hI hBU
  have hn := compact_le_normalizer_of_inf_eq N U₀ U₁ J₁ hnormal he
  constructor
  · intro hg
    obtain ⟨a, b, c, habc⟩ := hI g (hNI g hg.1)
    have hb : (b : G) = (a : G)⁻¹ * g * (c : G)⁻¹ := by
      rw [← habc]
      group
    have hbU : (b : G) ∈ U₀ := by
      rw [hb]
      exact U₀.mul_mem (U₀.mul_mem (U₀.inv_mem (hU (hJ a.property))) hg.2)
        (U₀.inv_mem (hU (hJ c.property)))
    have hbN : (b : G) ∈ N := hB₀ ⟨b.property, hbU⟩
    have hbinv : (b : G)⁻¹ ∈ Subgroup.normalizer (J₁ : Set G) :=
      hn ⟨N.inv_mem hbN, U₀.inv_mem hbU⟩
    have hj : (b : G)⁻¹ * (a : G) * (b : G) * (c : G) ∈ J₁ := by
      apply J₁.mul_mem _ c.property
      simpa only [inv_inv] using
        (Subgroup.mem_normalizer_iff.mp hbinv (a : G)).mp a.property
    refine ⟨⟨b, ⟨b.property, hbU⟩⟩, ⟨_, hj⟩, ?_⟩
    change (b : G) * ((b : G)⁻¹ * (a : G) * (b : G) * (c : G)) = g
    rw [← habc]
    group
  · rintro ⟨b, j, rfl⟩
    exact ⟨N.mul_mem (hB₀ b.property) (hJN j.property),
      U₀.mul_mem b.property.2 (hU (hJ j.property))⟩

end Groups

section Actual
open Matrix ValuativeRel ActualCharacterType61 ActualELatticeTopology60
open ActualELatticeNormalizer59 ActualELatticeTypeGroup59 LatticeCongruenceTopology60
open ActualELatticeResidue59
variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- Actual U₁ normality is proved from the original chain, independently of hmodel. -/
theorem chainGroup_le_normalizer_congruence :
    chainGroup F E m n e ≤ Subgroup.normalizer (matrixCongruence F E m n e : Set (GL n F)) := by
  intro g hg
  apply Subgroup.mem_normalizer_iff.mpr
  intro x
  change coordinateAut e x ∈ firstCongruence (latticeChain F E m) ↔
    coordinateAut e (g * x * g⁻¹) ∈ firstCongruence (latticeChain F E m)
  rw [map_mul, map_mul, map_inv]
  exact Subgroup.mem_normalizer_iff.mp
    (stabilizer_normalizes_firstCongruence (latticeChain F E m) hg) (coordinateAut e x)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- The actual first subgroup's ambient image is literally N(theta) intersect U₁. -/
theorem firstSubgroup_ambient_image :
    (firstSubgroup F E m n e D θ).map (compactGroup F E m n e D θ).subtype =
      CharacterNormalizer61.normalizer D θ ⊓ matrixCongruence F E m n e := by
  rw [firstSubgroup, Subgroup.subgroupOf_map_subtype]
  change matrixCongruence F E m n e ⊓
    (CharacterNormalizer61.normalizer D θ ⊓ chainGroup F E m n e) = _
  apply le_antisymm
  · exact fun _ h => ⟨h.2.1, h.1⟩
  · exact fun _ h => ⟨h.2, h.1, matrixCongruence_le_chainGroup F E m n e h.2⟩

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- The embedding used in ActualIntersection108 has this same literal ambient range. -/
theorem firstSubgroup_embedding_range :
    ((compactGroup F E m n e D θ).subtype.comp
      (firstSubgroup F E m n e D θ).subtype).range =
      CharacterNormalizer61.normalizer D θ ⊓ matrixCongruence F E m n e := by
  rw [MonoidHom.range_comp, Subgroup.range_subtype]
  exact firstSubgroup_ambient_image F E m n e D θ

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- Actual first-subgroup normality follows from chain congruence, without a residue model. -/
theorem firstSubgroup_normal : (firstSubgroup F E m n e D θ).Normal := by
  apply Subgroup.normal_subgroupOf_iff_le_normalizer_inf.mpr
  change compactGroup F E m n e D θ ≤ Subgroup.normalizer
    (matrixCongruence F E m n e ⊓ compactGroup F E m n e D θ : Set (GL n F))
  have hn := compact_le_normalizer_inf (CharacterNormalizer61.normalizer D θ)
    (chainGroup F E m n e) (matrixCongruence F E m n e)
    (chainGroup_le_normalizer_congruence F E m n e)
  rw [← firstSubgroup_ambient_image F E m n e D θ,
    firstSubgroup, Subgroup.subgroupOf_map_subtype] at hn
  exact hn

/-- The literal integral centralizer in the same ambient matrix coordinates. -/
def integralCentralizer : Subgroup (GL n F) :=
  (ActualELatticeResidue59.integralImage F E m).comap (coordinateAut e).toMonoidHom

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- The actual lattice type is exactly its integral centralizer joined with U₁. -/
theorem matrixType_eq_integral_sup :
    matrixType F E m n e = integralCentralizer F E m n e ⊔ matrixCongruence F E m n e := by
  change ((ActualELatticeResidue59.integralImage F E m ⊔
    ActualELatticeTypeGroup59.congruence F E m).comap (coordinateAut e).toMonoidHom) = _
  exact (coordinateAut e).comapSubgroup.map_sup _ _

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Integral centralizer matrices preserve the original full periodic chain. -/
theorem integralCentralizer_le_chainGroup :
    integralCentralizer F E m n e ≤ chainGroup F E m n e := by
  intro g hg
  obtain ⟨b, hb⟩ := hg
  change ActualELatticeResidue59.integralMatrix F E m b = coordinateAut e g at hb
  change coordinateAut e g ∈ chainStabilizer (latticeChain F E m)
  rw [← hb]
  exact integralMatrix_mem_stabilizer F E m b

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [IsNonarchimedeanLocalField E] [Nonempty n] in
/-- The existing integral pair-normalization premise supplies actual B₀≤N(theta). -/
theorem integralCentralizer_le_character_normalizer
    (hB : ∀ b : GL m 𝒪[E], (coordinateAut e).symm
      (ActualELatticeResidue59.integralMatrix F E m b) ∈ CharacterNormalizer61.normalizer D θ) :
    integralCentralizer F E m n e ≤ CharacterNormalizer61.normalizer D θ := by
  intro g hg
  obtain ⟨b, hb⟩ := hg
  have he : g = (coordinateAut e).symm (ActualELatticeResidue59.integralMatrix F E m b) := by
    apply (coordinateAut e).injective
    rw [MulEquiv.apply_symm_apply]
    exact hb.symm
  rw [he]
  exact hB b

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [Fintype n] [DecidableEq n] [Nonempty n] in
/-- An extension-linear matrix preserves the chain exactly when it and its inverse are integral. -/
theorem restrict_mem_chain_iff (g : GL m E) :
    restrictScalarMatrix F E m g ∈ chainStabilizer (latticeChain F E m) ↔
    g ∈ ActualIntegralGeneralLinear.integralSubgroup E m := by
  have single_mem (j : m) : Pi.single j (1 : E) ∈ integralLattice E m := by
    intro i
    simp only [Pi.single_apply]
    split_ifs <;> simp
  have entries (a : GL m E)
      (ha : restrictScalarMatrix F E m a ∈ chainStabilizer (latticeChain F E m)) :
      ∀ i j, a i j ∈ (valuation E).integer := by
    intro i j
    have hv := (ha 0 (Pi.single j 1)).mpr (by simpa using single_mem j)
    rw [latticeChain_zero] at hv
    have hi := hv i
    simpa [restrictScalarMatrix_apply, Matrix.mulVec, dotProduct, Pi.single_apply] using hi
  constructor
  · intro hg
    apply (ActualIntegralGeneralLinear.mem_integralSubgroup E m g).mpr
    refine ⟨entries g hg, entries g⁻¹ ?_⟩
    simpa only [map_inv] using (chainStabilizer (latticeChain F E m)).inv_mem hg
  · rintro ⟨u, rfl⟩
    exact integralMatrix_mem_stabilizer F E m u

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- The full literal field centralizer intersects the chain group in its integral image. -/
theorem centralizer_inf_chain :
    (ActualCuspidalCandidate105.centralizerMap F E m n e).range ⊓
      chainGroup F E m n e = integralCentralizer F E m n e := by
  ext g
  constructor
  · rintro ⟨⟨y, hy⟩, h0⟩
    have hcoord : restrictScalarMatrix F E m y = coordinateAut e g := by
      have h := congrArg (coordinateAut e) hy
      change coordinateAut e ((coordinateAut e).symm (restrictScalarMatrix F E m y)) =
        coordinateAut e g at h
      rwa [MulEquiv.apply_symm_apply] at h
    have hy0 : restrictScalarMatrix F E m y ∈ chainStabilizer (latticeChain F E m) := by
      rw [hcoord]
      exact h0
    obtain ⟨u, hu⟩ := (restrict_mem_chain_iff F E m y).mp hy0
    change coordinateAut e g ∈ integralImage F E m
    refine ⟨u, ?_⟩
    change restrictScalarMatrix F E m (ActualIntegralGeneralLinear.embedding E m u) =
      coordinateAut e g
    rw [hu, hcoord]
  · intro hg
    obtain ⟨u, hu⟩ := hg
    change integralMatrix F E m u = coordinateAut e g at hu
    constructor
    · refine ⟨ActualIntegralGeneralLinear.embedding E m u, ?_⟩
      apply (coordinateAut e).injective
      change coordinateAut e ((coordinateAut e).symm
        (restrictScalarMatrix F E m (ActualIntegralGeneralLinear.embedding E m u))) =
        coordinateAut e g
      rw [MulEquiv.apply_symm_apply]
      exact hu
    · change coordinateAut e g ∈ chainStabilizer (latticeChain F E m)
      rw [← hu]
      exact integralMatrix_mem_stabilizer F E m u

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Its intersection with full chain congruence is the explicit transported residue kernel. -/
theorem centralizer_inf_congruence :
    (ActualCuspidalCandidate105.centralizerMap F E m n e).range ⊓
      matrixCongruence F E m n e =
    (ActualResidueGeneralLinear.reduction E m).ker.map
      ((ActualCuspidalCandidate105.centralizerMap F E m n e).comp
        (ActualIntegralGeneralLinear.embedding E m)) := by
  ext g
  constructor
  · intro hg
    have h0 : g ∈ integralCentralizer F E m n e := by
      rw [← centralizer_inf_chain F E m n e]
      exact ⟨hg.1, matrixCongruence_le_chainGroup F E m n e hg.2⟩
    obtain ⟨u, hu⟩ := h0
    change integralMatrix F E m u = coordinateAut e g at hu
    have hu1 : integralMatrix F E m u ∈ ActualELatticeTypeGroup59.congruence F E m := by
      rw [hu]
      exact hg.2
    refine ⟨u, (integralMatrix_mem_congruence_iff F E m u).mp hu1, ?_⟩
    apply (coordinateAut e).injective
    change coordinateAut e ((coordinateAut e).symm
      (restrictScalarMatrix F E m (ActualIntegralGeneralLinear.embedding E m u))) =
      coordinateAut e g
    rw [MulEquiv.apply_symm_apply]
    exact hu
  · rintro ⟨u, hu, hug⟩
    constructor
    · exact ⟨ActualIntegralGeneralLinear.embedding E m u, hug⟩
    · have hcoord : integralMatrix F E m u = coordinateAut e g := by
        have h := congrArg (coordinateAut e) hug
        change coordinateAut e ((coordinateAut e).symm
          (restrictScalarMatrix F E m (ActualIntegralGeneralLinear.embedding E m u))) =
          coordinateAut e g at h
        rwa [MulEquiv.apply_symm_apply] at h
      change coordinateAut e g ∈ ActualELatticeTypeGroup59.congruence F E m
      rw [← hcoord]
      exact (integralMatrix_mem_congruence_iff F E m u).mpr hu

variable (J₁ B : Subgroup (GL n F))
variable (hJ : J₁ ≤ matrixCongruence F E m n e)
  (hJN : J₁ ≤ CharacterNormalizer61.normalizer D θ)
  (hθsupport : ∀ g : GL n F,
    NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
    ∃ a : J₁, ∃ b : B, ∃ c : J₁, (a : GL n F) * (b : GL n F) * (c : GL n F) = g)
include hJ hJN hθsupport

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- The actual image dictionary uses the proved normalizer-to-character-support implication. -/
theorem actual_first_eq
    (hBU : B ⊓ matrixCongruence F E m n e ≤ J₁) :
    (firstSubgroup F E m n e D θ).map (compactGroup F E m n e D θ).subtype = J₁ := by
  rw [firstSubgroup_ambient_image F E m n e D θ]
  exact inf_eq_of_support (CharacterNormalizer61.normalizer D θ)
    (matrixCongruence F E m n e) J₁ B
    {g | NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g}
    hJ hJN (fun _ hg => CharacterNormalizer61.character_intertwinedAt D θ hg) hθsupport hBU

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- The image dictionary also identifies the subgroup inside the original compact carrier. -/
theorem actual_first_subgroup_eq
    (hBU : B ⊓ matrixCongruence F E m n e ≤ J₁) :
    firstSubgroup F E m n e D θ = J₁.subgroupOf (compactGroup F E m n e D θ) := by
  have hJC : J₁ ≤ compactGroup F E m n e D θ :=
    le_inf hJN (hJ.trans (matrixCongruence_le_chainGroup F E m n e))
  apply Subgroup.map_injective (compactGroup F E m n e D θ).subtype_injective
  rw [actual_first_eq F E m n e D θ J₁ B hJ hJN hθsupport hBU,
    Subgroup.map_subgroupOf_eq_of_le hJC]

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- Compact-group equality is derived from support and integral centralizer normalization. -/
theorem actual_compact_eq_sup
    (hB₀ : B ⊓ chainGroup F E m n e ≤ CharacterNormalizer61.normalizer D θ) :
    compactGroup F E m n e D θ = (B ⊓ chainGroup F E m n e) ⊔ J₁ :=
  compact_eq_sup_of_support (CharacterNormalizer61.normalizer D θ)
    (chainGroup F E m n e) (matrixCongruence F E m n e) J₁ B
    {g | NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g}
    (matrixCongruence_le_chainGroup F E m n e) hJ hJN
    (fun _ hg => CharacterNormalizer61.character_intertwinedAt D θ hg) hθsupport hB₀

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
/-- The support dictionary and actual U₁ normality yield the compact product formula. -/
theorem actual_compact_product
    (hBU : B ⊓ matrixCongruence F E m n e ≤ J₁)
    (hB₀ : B ⊓ chainGroup F E m n e ≤ CharacterNormalizer61.normalizer D θ)
    (g : GL n F) :
    g ∈ compactGroup F E m n e D θ ↔
      ∃ b : (B ⊓ chainGroup F E m n e : Subgroup (GL n F)),
      ∃ j : J₁, (b : GL n F) * (j : GL n F) = g :=
  mem_compact_iff_product (CharacterNormalizer61.normalizer D θ)
    (chainGroup F E m n e) (matrixCongruence F E m n e) J₁ B
    {g | NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g}
    (matrixCongruence_le_chainGroup F E m n e) hJ hJN
    (fun _ hg => CharacterNormalizer61.character_intertwinedAt D θ hg) hθsupport hBU hB₀
    (chainGroup_le_normalizer_congruence F E m n e) g

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- The lattice-product containment hmodel follows once the actual integral factor is identified. -/
theorem actual_model_le
    (hB₀ : B ⊓ chainGroup F E m n e ≤ CharacterNormalizer61.normalizer D θ)
    (hBtype : B ⊓ chainGroup F E m n e ≤ matrixType F E m n e) :
    compactGroup F E m n e D θ ≤ matrixType F E m n e := by
  rw [actual_compact_eq_sup F E m n e D θ J₁ B hJ hJN hθsupport hB₀]
  apply sup_le hBtype
  exact hJ.trans (fun _ hg =>
    (show ActualELatticeTypeGroup59.congruence F E m ≤ typeGroup F E m from le_sup_right) hg)

omit hθsupport [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Specializing the centralizer removes the extra lattice-model containment premise. -/
theorem actual_model_from_centralizer
    (hθcentralizer : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ a : J₁, ∃ b : (ActualCuspidalCandidate105.centralizerMap F E m n e).range,
      ∃ c : J₁, (a : GL n F) * (b : GL n F) * (c : GL n F) = g)
    (hB : ∀ b : GL m 𝒪[E], (coordinateAut e).symm (integralMatrix F E m b) ∈
      CharacterNormalizer61.normalizer D θ) :
    compactGroup F E m n e D θ ≤ matrixType F E m n e := by
  apply actual_model_le F E m n e D θ J₁
    (ActualCuspidalCandidate105.centralizerMap F E m n e).range hJ hJN hθcentralizer
  · rw [centralizer_inf_chain F E m n e]
    exact integralCentralizer_le_character_normalizer F E m n e D θ hB
  · rw [centralizer_inf_chain F E m n e, matrixType_eq_integral_sup F E m n e]
    exact le_sup_left

omit hθsupport [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- The remaining intersection hypothesis is only containment of the concrete residue kernel. -/
theorem actual_first_from_residue
    (hθcentralizer : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ a : J₁, ∃ b : (ActualCuspidalCandidate105.centralizerMap F E m n e).range,
      ∃ c : J₁, (a : GL n F) * (b : GL n F) * (c : GL n F) = g)
    (hresidue : (ActualResidueGeneralLinear.reduction E m).ker.map
      ((ActualCuspidalCandidate105.centralizerMap F E m n e).comp
        (ActualIntegralGeneralLinear.embedding E m)) ≤ J₁) :
    firstSubgroup F E m n e D θ = J₁.subgroupOf (compactGroup F E m n e D θ) := by
  apply actual_first_subgroup_eq F E m n e D θ J₁
    (ActualCuspidalCandidate105.centralizerMap F E m n e).range hJ hJN hθcentralizer
  rw [centralizer_inf_congruence F E m n e]
  exact hresidue

omit hθsupport [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Canonical support expressed through J₁ gives the existing candidate's compact support bound. -/
theorem character_support_compact
    (hθcentralizer : ∀ g : GL n F,
      NormalizerIntertwining60.IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g →
      ∃ a : J₁, ∃ b : (ActualCuspidalCandidate105.centralizerMap F E m n e).range,
      ∃ c : J₁, (a : GL n F) * (b : GL n F) * (c : GL n F) = g)
    (g : GL n F)
    (hg : NormalizerIntertwining60.IntertwinedAt D
      (MonomialInduction.scalarRepresentation θ) g) :
    ∃ j₁ j₂ : compactGroup F E m n e D θ, ∃ y : GL m E,
      g = (j₁ : GL n F) * ActualCuspidalCandidate105.centralizerMap F E m n e y *
        (j₂ : GL n F) := by
  have hJC : J₁ ≤ compactGroup F E m n e D θ :=
    le_inf hJN (hJ.trans (matrixCongruence_le_chainGroup F E m n e))
  obtain ⟨a, b, c, he⟩ := hθcentralizer g hg
  obtain ⟨y, hy⟩ := b.property
  refine ⟨⟨a, hJC a.property⟩, ⟨c, hJC c.property⟩, y, ?_⟩
  change g = (a : GL n F) * ActualCuspidalCandidate105.centralizerMap F E m n e y * (c : GL n F)
  rw [hy]
  exact he.symm

end Actual
end PaperXI.NormalizerDictionary110
