module
public import CebotarevDensity.CyclotomicNormResidue
public import Mathlib.NumberTheory.NumberField.Cyclotomic.Ideal
public import Mathlib.NumberTheory.NumberField.Discriminant.Different

/-! Actual cyclotomic-compositum construction, adapted from the C1--C3
lemmas of CBirkbeck/AINTLIB Abelian.lean at commit
c62aa9dd4638d86b50f46d4000cf87157e333a6f (Apache 2.0).
No commutativity of Gal(L/K) is assumed. -/
@[expose] public section
noncomputable section
open NumberField
namespace PaperX.CrossingFields

theorem prime_dvd_cyclotomic_discr
    (E : Type*) [Field E] [NumberField E] (m : ℕ) [NeZero m]
    [IsCyclotomicExtension {m} ℚ E]
    {p : ℕ} (hp : p.Prime) (hpd : p ∣ (NumberField.discr E).natAbs) : p ∣ m := by
  by_contra hpm
  have : Fact (Nat.Prime p) := ⟨hp⟩
  have hpprime : Prime (p : ℤ) := Nat.prime_iff_prime_int.mp hp
  refine absurd (Int.ofNat_dvd_left.mpr hpd) ?_
  rw [NumberField.not_dvd_discr_iff_forall_liesOver E (𝓞 E) hpprime]
  intro P hPmax hlo
  have := hPmax.isPrime
  have := hlo
  rw [← Ideal.ramificationIdx_eq_one_iff]
  exact IsCyclotomicExtension.Rat.ramificationIdx_eq_of_not_dvd p E P hpm

/-- Discriminant coprimality supplies the full cyclotomic degree. -/
theorem cyclotomic_finrank
    (K M : Type*) [Field K] [NumberField K] [Field M] [NumberField M] [Algebra K M]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K M]
    (hcop : ((NumberField.discr K).natAbs).Coprime m) :
    Module.finrank K M = m.totient := by
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot K M
    (Set.mem_singleton m) (NeZero.ne m)
  set A : IntermediateField ℚ M := IntermediateField.adjoin ℚ {ζ} with hA
  set B : IntermediateField ℚ M := (IsScalarTower.toAlgHom ℚ K M).fieldRange with hB
  have : IsCyclotomicExtension {m} ℚ A :=
    hζ.intermediateField_adjoin_isCyclotomicExtension (K := ℚ)
  have : IsGalois ℚ A := IsCyclotomicExtension.isGalois (S := {m}) (K := ℚ) (L := A)
  have hfin : Module.finrank ℚ A = m.totient :=
    IsCyclotomicExtension.finrank A (Polynomial.cyclotomic.irreducible_rat (NeZero.pos m))
  have hsup : A ⊔ B = ⊤ := by
    have hζalg : IsAlgebraic ℚ ζ := Algebra.IsAlgebraic.isAlgebraic ζ
    have hsubalg : (IsScalarTower.toAlgHom ℚ K M).range ⊔ Algebra.adjoin ℚ {ζ}
        = (⊤ : Subalgebra ℚ M) := by
      have htop : (Algebra.adjoin K {ζ} : Subalgebra K M) = ⊤ :=
        IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ
      rw [← Algebra.Subalgebra.restrictScalars_adjoin (R := ℚ) (S := K) (s := {ζ}),
        htop, Subalgebra.restrictScalars_top]
    apply IntermediateField.toSubalgebra_injective
    rw [hA, hB, IntermediateField.sup_toSubalgebra_of_isAlgebraic_left,
      IntermediateField.adjoin_simple_toSubalgebra_of_isAlgebraic hζalg,
      AlgHom.fieldRange_toSubalgebra, IntermediateField.top_toSubalgebra, sup_comm]
    exact hsubalg
  let eB : K ≃+* B := ((IsScalarTower.toAlgHom ℚ K M : K →+* M)).rangeRestrictFieldEquiv
  have hdiscB : NumberField.discr B = NumberField.discr K :=
    (NumberField.discr_eq_discr_of_ringEquiv (f := eB)).symm
  have hcoprime : IsCoprime (NumberField.discr A) (NumberField.discr B) := by
    rw [hdiscB, Int.isCoprime_iff_gcd_eq_one, Int.gcd]
    by_contra hne
    obtain ⟨p, hp, hpdvd⟩ := Nat.exists_prime_and_dvd hne
    obtain ⟨hpa, hpb⟩ := Nat.dvd_gcd_iff.mp hpdvd
    have hpm : p ∣ m := prime_dvd_cyclotomic_discr A m hp hpa
    have hpgcd : p ∣ Nat.gcd (NumberField.discr K).natAbs m := Nat.dvd_gcd hpb hpm
    rw [hcop] at hpgcd
    exact hp.one_lt.ne' (Nat.dvd_one.mp hpgcd)
  have hld : A.LinearDisjoint B :=
    NumberField.linearDisjoint_of_isGalois_isCoprime_discr (L := M) A B hcoprime
  have hfr : Module.finrank B M = Module.finrank ℚ A := hld.finrank_right_eq_finrank hsup
  have heq : Module.finrank K M = Module.finrank B M := by
    refine Algebra.finrank_eq_of_equiv_equiv eB (RingEquiv.refl M) ?_
    ext x
    rfl
  rw [heq, hfr, hfin]


/-- The actual compositum is Galois over the original base. -/
theorem compositum_galois
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} L M] : IsGalois K M := by
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot L M
    (Set.mem_singleton m) (NeZero.ne m)
  have : FiniteDimensional K M := inferInstance
  have : Algebra.IsSeparable K M := inferInstance
  set A : IntermediateField K M := (IsScalarTower.toAlgHom K L M).fieldRange with hA
  set B : IntermediateField K M := IntermediateField.adjoin K {ζ} with hB
  have : Normal K A := Normal.of_algEquiv (AlgEquiv.ofInjectiveField (IsScalarTower.toAlgHom K L M))
  have : IsCyclotomicExtension {m} K B := hζ.intermediateField_adjoin_isCyclotomicExtension (K := K)
  have : IsGalois K B := IsCyclotomicExtension.isGalois (S := {m}) (K := K) (L := B)
  have hsup : A ⊔ B = ⊤ := by
    have hζalg : IsAlgebraic K ζ := Algebra.IsAlgebraic.isAlgebraic ζ
    have hsubalg : (IsScalarTower.toAlgHom K L M).range ⊔ Algebra.adjoin K {ζ}
        = (⊤ : Subalgebra K M) := by
      have htop : (Algebra.adjoin L {ζ} : Subalgebra L M) = ⊤ :=
        IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ
      rw [← Algebra.Subalgebra.restrictScalars_adjoin (R := K) (S := L) (s := {ζ}),
        htop, Subalgebra.restrictScalars_top]
    apply IntermediateField.toSubalgebra_injective
    rw [hA, hB, IntermediateField.sup_toSubalgebra_of_isAlgebraic_left,
      IntermediateField.adjoin_simple_toSubalgebra_of_isAlgebraic hζalg,
      AlgHom.fieldRange_toSubalgebra, IntermediateField.top_toSubalgebra]
    exact hsubalg
  have : Normal K M := by
    have h := IntermediateField.normal_sup K M A B
    rw [hsup] at h
    exact Normal.of_algEquiv (IntermediateField.topEquiv (F := K) (E := M))
  exact IsGalois.mk

/-- The literal normal restriction and cyclotomic-character pair is bijective. -/
theorem joint_restriction_bijective
    (K L M : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Field M] [NumberField M] [Algebra K L] [Algebra K M] [Algebra L M]
    [IsScalarTower K L M] [IsGalois K L] [IsGalois K M]
    (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} L M]
    (hcop : ((NumberField.discr L).natAbs).Coprime m) (ζ : M) (hζ : IsPrimitiveRoot ζ m) :
    Function.Bijective ((AlgEquiv.restrictNormalHom L).prod (hζ.autToPow K)) := by
  have : IsGalois L M := IsGalois.tower_top_of_isGalois K L M
  set Φ : Gal(M/K) →* Gal(L/K) × (ZMod m)ˣ :=
    (AlgEquiv.restrictNormalHom L).prod (hζ.autToPow K) with hΦ
  have hcard : Nat.card Gal(M/K) = Nat.card Gal(L/K) * Nat.card (ZMod m)ˣ := by
    rw [IsGalois.card_aut_eq_finrank K M, IsGalois.card_aut_eq_finrank K L,
      ← Module.finrank_mul_finrank K L M, cyclotomic_finrank L M m hcop,
      Nat.card_eq_fintype_card (α := (ZMod m)ˣ), ZMod.card_units_eq_totient]
  have hinj : Function.Injective Φ := by
    rw [injective_iff_map_eq_one]
    intro g hg
    rw [hΦ, MonoidHom.prod_apply, Prod.mk_eq_one] at hg
    obtain ⟨hL, hroot⟩ := hg
    have hζfix : g ζ = ζ := by
      have hs := hζ.autToPow_spec K g
      rw [hroot] at hs
      rw [← hs, Units.val_one]
      rcases eq_or_lt_of_le (NeZero.one_le (n := m)) with h1 | h1
      · have hm : m = 1 := h1.symm
        subst hm
        have hz : ζ = 1 := by simpa using hζ.pow_eq_one
        simp [hz]
      · rw [ZMod.val_one_eq_one_mod, Nat.mod_eq_of_lt (by omega), pow_one]
    have hLfix : ∀ x : L, g (algebraMap L M x) = algebraMap L M x := by
      intro x
      have h := g.restrictNormal_commutes L x
      have hr : g.restrictNormal L = (1 : Gal(L/K)) := hL
      rw [hr] at h
      simpa using h.symm
    have htop : Algebra.adjoin L {ζ} = (⊤ : Subalgebra L M) :=
      IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ
    apply AlgEquiv.ext
    intro x
    have hx : x ∈ Algebra.adjoin L {ζ} := htop ▸ Algebra.mem_top
    refine Algebra.adjoin_induction (hx := hx) ?_ ?_ ?_ ?_
    · intro y hy
      rw [Set.mem_singleton_iff] at hy
      subst hy
      rw [hζfix]
      rfl
    · intro t
      exact hLfix t
    · intro a b _ _ ha hb
      rw [map_add, ha, hb]
      rfl
    · intro a b _ _ ha hb
      rw [map_mul, ha, hb]
      rfl
  exact (Nat.bijective_iff_injective_and_card _).mpr ⟨hinj, by rw [hcard, Nat.card_prod]⟩

end PaperX.CrossingFields
