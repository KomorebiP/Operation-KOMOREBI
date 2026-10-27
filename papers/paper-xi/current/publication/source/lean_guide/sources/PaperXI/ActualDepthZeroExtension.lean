import PaperXI.ActualIntegralGeneralLinear
import PaperXI.ActualLocalUnitDecomposition
import PaperXI.CentralExtensionInductionConsequences

/-!
# Actual depth-zero inducing data extended by the scalar uniformizer

The subgroup, degree, free central direction and smooth inducing representation
are constructed from the given local field. The supplied finite representation
is inflated through literal residue reduction. Induced irreducibility is a
separate theorem: no Mackey vanishing is assumed in this construction.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualDepthZeroExtension

open Matrix ValuativeRel
open ActualIntegralGeneralLinear ActualLocalUnitTopology ActualLocalUnitDecomposition

variable (K : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K]
variable (n : Type*) [Fintype n] [DecidableEq n]

/-- Normalized valuation of the actual determinant. -/
def determinantDegree : GeneralLinearGroup n K →* Multiplicative ℤ :=
  (degree K).comp GeneralLinearGroup.det

/-- The scalar matrix of the chosen actual uniformizer. -/
def scalarUniformizer : GeneralLinearGroup n K :=
  GeneralLinearGroup.scalar n (uniformizerUnit K)

theorem scalarUniformizer_central (g : GeneralLinearGroup n K) :
    Commute (scalarUniformizer K n) g := GeneralLinearGroup.scalar_commute _ _

@[simp] theorem determinantDegree_embedding (g : GeneralLinearGroup n 𝒪[K]) :
    determinantDegree K n (embedding K n g) = 1 := by
  change degree K (GeneralLinearGroup.det (GeneralLinearGroup.map _ g)) = 1
  rw [GeneralLinearGroup.map_det]
  exact degree_unitEmbedding K (GeneralLinearGroup.det g)

theorem integralSubgroup_le_degree_kernel :
    integralSubgroup K n ≤ (determinantDegree K n).ker := by
  rintro g ⟨a, rfl⟩
  exact determinantDegree_embedding K n a

@[simp] theorem determinantDegree_scalarUniformizer :
    determinantDegree K n (scalarUniformizer K n) =
      Multiplicative.ofAdd (Fintype.card n : ℤ) := by
  simp [determinantDegree, scalarUniformizer, GeneralLinearGroup.det_scalar]
  change Multiplicative.ofAdd ((Fintype.card n) • (1 : ℤ)) = _
  simp

variable [Nonempty n]

/-- No nonzero scalar uniformizer power is integral and integrally invertible. -/
theorem scalarUniformizer_free :
    ∀ r : ℤ, scalarUniformizer K n ^ r ∈ integralSubgroup K n → r = 0 := by
  apply CentralExtensionInducing.hfree_from_degree _ (determinantDegree K n)
    (integralSubgroup_le_degree_kernel K n)
  rw [determinantDegree_scalarUniformizer]
  intro h
  have hcard : (Fintype.card n : ℤ) = 0 := congrArg Multiplicative.toAdd h
  exact (Nat.ne_of_gt (Fintype.card_pos)).elim (Int.ofNat_eq_zero.mp hcard)

/-- The actual subgroup obtained by adjoining the scalar uniformizer. -/
abbrev extendedSubgroup : Subgroup (GeneralLinearGroup n K) :=
  CentralExtensionInducing.extendedSubgroup (integralSubgroup K n)
    (scalarUniformizer K n) (scalarUniformizer_central K n)

omit [Nonempty n] in
theorem integral_le_extended : integralSubgroup K n ≤ extendedSubgroup K n :=
  CentralExtensionInducing.le_extendedSubgroup _ _ _

omit [TopologicalSpace K] [IsNonarchimedeanLocalField K] [Nonempty n] in
/-- Every scalar integer-ring unit is already in the integral subgroup. -/
theorem scalar_unit_mem_integral (u : 𝒪[K]ˣ) :
    GeneralLinearGroup.scalar n (unitEmbedding K u) ∈ integralSubgroup K n := by
  refine ⟨GeneralLinearGroup.scalar n u, ?_⟩
  exact GeneralLinearGroup.map_scalar _ _

omit [Nonempty n] in
/-- The subgroup is precisely the scalar extension `Kˣ GL_n(𝒪[K])`. -/
theorem extendedSubgroup_eq_scalar_sup :
    extendedSubgroup K n = integralSubgroup K n ⊔ (GeneralLinearGroup.scalar n).range := by
  rw [extendedSubgroup, CentralExtensionInducing.extendedSubgroup_eq_sup]
  apply le_antisymm
  · apply sup_le le_sup_left
    apply Subgroup.zpowers_le.mpr
    exact (show (GeneralLinearGroup.scalar n).range ≤
      integralSubgroup K n ⊔ (GeneralLinearGroup.scalar n).range from le_sup_right)
      (show scalarUniformizer K n ∈ (GeneralLinearGroup.scalar n).range
      from ⟨uniformizerUnit K, rfl⟩)
  · apply sup_le le_sup_left
    rintro g ⟨a, rfl⟩
    obtain ⟨⟨u, r⟩, rfl⟩ := (ActualLocalUnitDecomposition.normalFormEquiv K).surjective a
    rw [normalFormEquiv_apply, map_mul, map_zpow]
    exact Subgroup.mul_mem _
      ((show integralSubgroup K n ≤ integralSubgroup K n ⊔
        Subgroup.zpowers (scalarUniformizer K n) from le_sup_left)
        (scalar_unit_mem_integral K n u))
      ((show Subgroup.zpowers (scalarUniformizer K n) ≤ integralSubgroup K n ⊔
        Subgroup.zpowers (scalarUniformizer K n) from le_sup_right)
        (Subgroup.zpow_mem _ (Subgroup.mem_zpowers _) r.toAdd))

omit [Nonempty n] in
theorem extendedSubgroup_open :
    IsOpen (extendedSubgroup K n : Set (GeneralLinearGroup n K)) :=
  CentralExtensionInducing.extendedSubgroup_isOpen _ _ _ (integralSubgroup_open K n)

/-- Inclusion of the actual integral subgroup into the actual extended subgroup. -/
abbrev inclusion : integralSubgroup K n →* extendedSubgroup K n :=
  CentralExtensionInducing.subgroupInclusion _ _ _

variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (σ : Representation ℂ (GeneralLinearGroup n 𝓀[K]) V) (c : ℂˣ)

/-- Extend the actual residue inflation with the prescribed uniformizer scalar. -/
abbrev extendedRepresentation : Representation ℂ (extendedSubgroup K n) V :=
  CentralExtensionInducing.extendedRepresentation _ _ _ (scalarUniformizer_free K n)
    (inflated K n σ) c

@[simp] theorem extendedRepresentation_restrict (j : integralSubgroup K n) :
    extendedRepresentation K n σ c (inclusion K n j) = inflated K n σ j :=
  CentralExtensionInducing.extendedRepresentation_restrict _ _ _ _ _ _ _

theorem extendedRepresentation_irreducible [Representation.IsIrreducible σ] :
    Representation.IsIrreducible (extendedRepresentation K n σ c) := by
  let := inflated_irreducible K n σ
  exact CentralExtensionInducing.extendedRepresentation_irreducible _ _ _ _ _ _

theorem extendedRepresentation_smooth :
    SmoothDegreeQuotient.IsSmooth (extendedRepresentation K n σ c) :=
  CentralExtensionInducing.extendedRepresentation_smooth _ _ _ _ _ _
    (integralSubgroup_open K n) (inflated_isSmooth K n σ)

/-- Actual algebraic compact induction from the open extended integral subgroup. -/
abbrev inducedRepresentation :=
  CentralExtensionInductionConsequences.inducedRepresentation (integralSubgroup K n)
    (scalarUniformizer K n) (scalarUniformizer_central K n) (scalarUniformizer_free K n)
    (inflated K n σ) c

theorem induced_smooth : SmoothDegreeQuotient.IsSmooth (inducedRepresentation K n σ c) :=
  CentralExtensionInductionConsequences.induced_isSmooth _ _ _ _ _ _
    (integralSubgroup_open K n) (inflated_isSmooth K n σ)

theorem induced_nontrivial [Nontrivial V] :
    Nontrivial (Representation.IndV (extendedSubgroup K n).subtype
      (extendedRepresentation K n σ c)) :=
  CentralExtensionInductionConsequences.induced_nontrivial _ _ _ _ _ _

theorem induced_scalar : inducedRepresentation K n σ c (scalarUniformizer K n) =
    (c : ℂ) • LinearMap.id :=
  CentralExtensionInductionConsequences.induced_central_scalar _ _ _ _ _ _

end PaperXI.ActualDepthZeroExtension
