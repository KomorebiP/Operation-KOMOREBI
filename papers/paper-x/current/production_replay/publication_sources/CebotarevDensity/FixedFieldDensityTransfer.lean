/-
Density transfer through the actual cyclic fixed field. The proof combines an
exact degree-one sum with a proved zero-density error, not an exact equality
for the full relative prime sum. Cyclic density remains an explicit input.
-/
module
public import CebotarevDensity.FixedFieldMainTerm

@[expose] public section
noncomputable section
open Filter NumberField Topology Set
namespace Chebotarev.FixedFieldDensityTransfer
open FixedFieldMainTerm FixedFieldSumTools

variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L] (σ : Gal(L/K))

/-- Disjointly partition the relative prime sum into its main term and error. -/
theorem relative_sum_partition {s : ℝ} (hs : 1 < s) :
    primeIdealZetaSum (relativeSet K L σ) s =
      primeIdealZetaSum (goodSet K L σ) s +
      primeIdealZetaSum (relativeSet K L σ \ goodSet K L σ) s := by
  have hsub : goodSet K L σ ⊆ relativeSet K L σ := fun _ h ↦ h.1
  have hunion : goodSet K L σ ∪ (relativeSet K L σ \ goodSet K L σ) = relativeSet K L σ :=
    Set.union_sdiff_cancel hsub
  have h := primeIdealZetaSum_union_of_disjoint
    (S := goodSet K L σ) (T := relativeSet K L σ \ goodSet K L σ) Set.disjoint_sdiff_right hs
  rwa [hunion] at h

/-- Zero-density discarded primes do not change the density of the good relative fibre. -/
theorem good_density {δ : ℝ} (hT : HasDirichletDensity (relativeSet K L σ) δ) :
    HasDirichletDensity (goodSet K L σ) δ := by
  have h := hT.sub (error_density_zero K L σ)
  rw [sub_zero] at h
  refine h.congr' ?_
  filter_upwards [self_mem_nhdsWithin] with s hs
  rw [relative_sum_partition K L σ hs, add_div]
  ring

/-- The full density-transfer formula. The degree-one count and error control are proved,
while the density of the cyclic extension remains a genuine input. -/
theorem density_transfer {δ : ℝ} (hT : HasDirichletDensity (relativeSet K L σ) δ) :
    HasDirichletDensity (baseSet K L σ)
      (((orderOf σ : ℝ) * Nat.card (ConjClasses.mk σ).carrier / Nat.card Gal(L/K)) * δ) := by
  have hg := good_density K L σ hT
  have hrat := prime_normalizer_ratio K (↥(IntermediateField.fixedField (Subgroup.zpowers σ)))
  have hprod := hg.mul hrat
  rw [mul_one] at hprod
  have hG : Tendsto (fun s : ℝ ↦ primeIdealZetaSum (goodSet K L σ) s /
      primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) s) (𝓝[>] 1) (𝓝 δ) := by
    refine hprod.congr' ?_
    filter_upwards [(primeIdealZetaSum_univ_tendsto_atTop (↥(IntermediateField.fixedField (Subgroup.zpowers σ)))).eventually_gt_atTop 0,
      (primeIdealZetaSum_univ_tendsto_atTop K).eventually_gt_atTop 0] with s hE hK
    field_simp
  have hc : multiplicity K L σ ≠ 0 := (multiplicity_pos K L σ).ne'
  have hbase : HasDirichletDensity (baseSet K L σ) (δ / multiplicity K L σ) := by
    refine (hG.div_const (multiplicity K L σ)).congr' ?_
    filter_upwards [self_mem_nhdsWithin,
      (primeIdealZetaSum_univ_tendsto_atTop K).eventually_gt_atTop 0] with s hs hK
    rw [main_term K L σ hs]
    field_simp
  have hN : (Nat.card Gal(L/K) : ℝ) ≠ 0 := by exact_mod_cast (Nat.card_pos (α := Gal(L/K))).ne'
  have heq : δ / multiplicity K L σ =
      (((orderOf σ : ℝ) * Nat.card (ConjClasses.mk σ).carrier / Nat.card Gal(L/K)) * δ) := by
    unfold FixedFieldMainTerm.multiplicity
    field_simp
  rwa [heq] at hbase

/-- Inserting cyclic density gives the conjugacy-class density with the correct factor. -/
theorem conjugacy_density_of_cyclic_density
    (hcyc : HasDirichletDensity (relativeSet K L σ) (orderOf σ : ℝ)⁻¹) :
    HasDirichletDensity (baseSet K L σ)
      ((Nat.card (ConjClasses.mk σ).carrier : ℝ) / Nat.card Gal(L/K)) := by
  have h := density_transfer K L σ hcyc
  have hf : (orderOf σ : ℝ) ≠ 0 := by
    exact_mod_cast (orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)).ne'
  have heq : ((orderOf σ : ℝ) * Nat.card (ConjClasses.mk σ).carrier / Nat.card Gal(L/K)) *
      (orderOf σ : ℝ)⁻¹ = (Nat.card (ConjClasses.mk σ).carrier : ℝ) / Nat.card Gal(L/K) := by
    field_simp
  rwa [heq] at h

/-- Positive conjugacy-class density yields infinitude, still conditional on cyclic density. -/
theorem infinite_base_of_cyclic_density
    (hcyc : HasDirichletDensity (relativeSet K L σ) (orderOf σ : ℝ)⁻¹) :
    (baseSet K L σ).Infinite := by
  intro hfin
  have h := tendsto_nhds_unique (conjugacy_density_of_cyclic_density K L σ hcyc)
    (hasDirichletDensity_of_finite K hfin)
  have : Nonempty (ConjClasses.mk σ).carrier := ⟨⟨σ, ConjClasses.mem_carrier_mk⟩⟩
  have hpos : (0 : ℝ) < (Nat.card (ConjClasses.mk σ).carrier : ℝ) / Nat.card Gal(L/K) :=
    div_pos (by exact_mod_cast (Nat.card_pos (α := (ConjClasses.mk σ).carrier)))
      (by exact_mod_cast (Nat.card_pos (α := Gal(L/K))))
  exact hpos.ne' h

/-- Avoid every finite forbidden family of prime ideals; the remaining cyclic input is explicit. -/
theorem exists_prime_outside_of_cyclic_density
    (hcyc : HasDirichletDensity (relativeSet K L σ) (orderOf σ : ℝ)⁻¹)
    (B : Finset (Ideal (𝓞 K))) :
    ∃ p : Ideal (𝓞 K), p ∉ B ∧ p.IsPrime ∧ UnramifiedIn K L p ∧
      frobeniusClass K L p = ConjClasses.mk σ := by
  obtain ⟨p, hp, hB⟩ := (infinite_base_of_cyclic_density K L σ hcyc).exists_notMem_finset B
  exact ⟨p, hB, hp⟩

end Chebotarev.FixedFieldDensityTransfer
