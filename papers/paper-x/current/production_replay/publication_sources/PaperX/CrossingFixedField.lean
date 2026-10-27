module
public import PaperX.CrossingFields
public import PaperX.CyclotomicDensity
public import CebotarevDensity.FixedFieldDensityBridge

/-! The twist creates an actual cyclotomic extension over a cyclic fixed field.
The gate uses root-of-unity fixers, not the subgroup fixing L. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev
namespace PaperX.CrossingFixedField
open PaperX.CrossingFields

theorem character_one_of_fixes
    (K M : Type*) [Field K] [Field M] [Algebra K M] (m : ℕ) [NeZero m]
    (ζ : M) (hζ : IsPrimitiveRoot ζ m) (g : Gal(M/K)) (hg : g ζ = ζ) :
    hζ.autToPow K g = 1 := by
  have hspec := hζ.autToPow_spec K g
  rw [hg] at hspec
  set u : (ZMod m)ˣ := hζ.autToPow K g
  have hmod : (u : ZMod m).val ≡ 1 [MOD m] := by
    have hisu : IsUnit ζ := hζ.isUnit (NeZero.ne m)
    lift ζ to Mˣ using hisu with z hz
    have hzp : IsPrimitiveRoot z m := by rwa [IsPrimitiveRoot.coe_units_iff] at hζ
    have hord : orderOf z = m := (IsPrimitiveRoot.eq_orderOf hzp).symm
    have he : z ^ (u : ZMod m).val = z ^ (1 : ℕ) := by
      apply Units.ext
      push_cast
      rwa [pow_one]
    rwa [pow_eq_pow_iff_modEq, hord] at he
  apply Units.ext
  have hc : ((u : ZMod m).val : ZMod m) = (1 : ZMod m) := by
    rw [← Nat.cast_one]
    exact (ZMod.natCast_eq_natCast_iff _ _ _).mpr hmod
  simpa using hc

/-- Order divisibility implies the required root-fixer intersection is trivial. -/
theorem crossing_meet
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]
    (m : ℕ) [NeZero m] (ζ : M) (hζ : IsPrimitiveRoot ζ m)
    (σ : Gal(L/K)) (τ : (ZMod m)ˣ) (hord : orderOf σ ∣ orderOf τ)
    (s : Gal(M/K)) (hrestr : AlgEquiv.restrictNormalHom L s = σ)
    (hchar : hζ.autToPow K s = τ)
    (hinj : Function.Injective ((AlgEquiv.restrictNormalHom L).prod (hζ.autToPow K))) :
    Subgroup.zpowers s ⊓
      (IntermediateField.adjoin K {b : M | b ^ m = 1}).fixingSubgroup = ⊥ := by
  rw [eq_bot_iff]
  intro g hg
  rw [Subgroup.mem_inf] at hg
  obtain ⟨⟨k, hk⟩, hgfix⟩ := hg
  simp only at hk
  have hgζ : g ζ = ζ :=
    (IntermediateField.mem_fixingSubgroup_iff _ g).mp hgfix ζ
      (IntermediateField.subset_adjoin K _ hζ.pow_eq_one)
  have hχg : hζ.autToPow K g = 1 := character_one_of_fixes K M m ζ hζ g hgζ
  have hτk : τ ^ k = 1 := by rw [← hchar, ← map_zpow, hk]; exact hχg
  have hσk : σ ^ k = 1 :=
    orderOf_dvd_iff_zpow_eq_one.mp
      ((Int.natCast_dvd_natCast.mpr hord).trans (orderOf_dvd_iff_zpow_eq_one.mpr hτk))
  have hrg : AlgEquiv.restrictNormalHom L g = 1 := by rw [← hk, map_zpow, hrestr, hσk]
  rw [Subgroup.mem_bot]
  apply hinj
  rw [MonoidHom.prod_apply, MonoidHom.prod_apply, hrg, hχg, map_one, map_one]

/-- A genuine adjunction/Galois-correspondence construction of M = F(mu_m). -/
theorem cyclotomic_over_fixedField
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} L M] (g : Gal(M/K))
    (hmeet : Subgroup.zpowers g ⊓
      (IntermediateField.adjoin K {b : M | b ^ m = 1}).fixingSubgroup = ⊥) :
    letI := (IntermediateField.fixedField (Subgroup.zpowers g)).isScalarTower_mid'
    IsCyclotomicExtension {m} ↥(IntermediateField.fixedField (Subgroup.zpowers g)) M := by
  set F : IntermediateField K M := IntermediateField.fixedField (Subgroup.zpowers g)
  set Kμ : IntermediateField K M := IntermediateField.adjoin K {b : M | b ^ m = 1}
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot L M
    (Set.mem_singleton m) (NeZero.ne m)
  have hadjζ : IntermediateField.adjoin K {ζ} = Kμ :=
    le_antisymm
      (IntermediateField.adjoin_le_iff.mpr (Set.singleton_subset_iff.mpr
        (IntermediateField.subset_adjoin K _ hζ.pow_eq_one)))
      (IntermediateField.adjoin_le_iff.mpr fun x hx ↦ by
        obtain ⟨i, -, rfl⟩ := hζ.eq_pow_of_pow_eq_one (Set.mem_ofPred_eq ▸ hx)
        exact pow_mem (IntermediateField.subset_adjoin K _ (Set.mem_singleton ζ)) i)
  have hsup : (F ⊔ Kμ).fixingSubgroup = ⊥ := by
    rw [IntermediateField.fixingSubgroup_sup, IntermediateField.fixingSubgroup_fixedField, hmeet]
  have htop : F ⊔ Kμ = ⊤ := by
    have h := congrArg IntermediateField.fixedField hsup
    rwa [IsGalois.fixedField_fixingSubgroup, IntermediateField.fixedField_bot] at h
  have htopF : IntermediateField.adjoin (↥F) {ζ} = ⊤ := by
    apply IntermediateField.restrictScalars_injective K
    rw [IntermediateField.restrictScalars_adjoin_eq_sup, hadjζ, htop]
    rfl
  have : Algebra.IsIntegral ↥F M := Algebra.IsIntegral.of_finite ↥F M
  have hcyc : IsCyclotomicExtension {m} ↥F (IntermediateField.adjoin (↥F) {ζ}) :=
    IsPrimitiveRoot.intermediateField_adjoin_isCyclotomicExtension (K := ↥F) hζ
  rw [htopF] at hcyc
  exact IsCyclotomicExtension.equiv (S := {m}) (A := ↥F) (f := IntermediateField.topEquiv)


/-- A root-fixer-trivial element has the expected positive-density Frobenius class,
even when the compositum Galois group is nonabelian. -/
theorem crossing_density
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} L M] (s : Gal(M/K))
    (hmeet : Subgroup.zpowers s ⊓
      (IntermediateField.adjoin K {b : M | b ^ m = 1}).fixingSubgroup = ⊥) :
    HasDirichletDensity
      {p : Ideal (𝓞 K) | p.IsPrime ∧ UnramifiedIn K M p ∧
        frobeniusClass K M p = ConjClasses.mk s}
      ((Nat.card (ConjClasses.mk s).carrier : ℝ) / Nat.card Gal(M/K)) := by
  let F : IntermediateField K M := IntermediateField.fixedField (Subgroup.zpowers s)
  have : IsScalarTower K ↥F M := F.isScalarTower_mid'
  have : IsGalois ↥F M := IsGalois.tower_top_intermediateField F
  have : IsCyclotomicExtension {m} ↥F M := cyclotomic_over_fixedField K L M m s hmeet
  let sF : Gal(M/↥F) :=
    IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers s) ⟨s, Subgroup.mem_zpowers s⟩
  apply density_lift_through_fixedField s F sF (by ext x; rfl) rfl
  simpa only [PaperX.CyclotomicFourier.classSet] using
    PaperX.CyclotomicDensity.cyclotomic_density ↥F M m sF

/-- Positive crossing density supplies prime occurrence outside every finite set. -/
theorem crossing_avoids
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} L M] (s : Gal(M/K))
    (hmeet : Subgroup.zpowers s ⊓
      (IntermediateField.adjoin K {b : M | b ^ m = 1}).fixingSubgroup = ⊥)
    (B : Finset (Ideal (𝓞 K))) :
    ∃ p : Ideal (𝓞 K), p ∉ B ∧ p.IsPrime ∧ UnramifiedIn K M p ∧
      frobeniusClass K M p = ConjClasses.mk s := by
  have hinf : Set.Infinite
      {p : Ideal (𝓞 K) | p.IsPrime ∧ UnramifiedIn K M p ∧
        frobeniusClass K M p = ConjClasses.mk s} := by
    intro hfin
    have h := tendsto_nhds_unique (crossing_density K L M m s hmeet)
      (hasDirichletDensity_of_finite K hfin)
    have : Nonempty (ConjClasses.mk s).carrier := ⟨⟨s, ConjClasses.mem_carrier_mk⟩⟩
    have hpos : (0 : ℝ) < (Nat.card (ConjClasses.mk s).carrier : ℝ) / Nat.card Gal(M/K) :=
      div_pos (by exact_mod_cast (Nat.card_pos (α := (ConjClasses.mk s).carrier)))
        (by exact_mod_cast (Nat.card_pos (α := Gal(M/K))))
    exact hpos.ne' h
  obtain ⟨p, hp, hB⟩ := hinf.exists_notMem_finset B
  exact ⟨p, hB, hp⟩

end PaperX.CrossingFixedField
