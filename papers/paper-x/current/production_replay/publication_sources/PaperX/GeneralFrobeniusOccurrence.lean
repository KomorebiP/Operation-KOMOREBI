module
public import PaperX.CrossingFixedField
public import PaperX.FrobeniusTowerProjection
public import Mathlib.NumberTheory.PrimesCongruentOne
public import Mathlib.RingTheory.ZMod.UnitsCyclic

/-! Qualitative general Chebotarev occurrence from one auxiliary cyclotomic
crossing per conjugacy class. This does not assert the exact general density. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev
namespace PaperX.GeneralFrobeniusOccurrence

/-- The auxiliary prime and twist are constructed, not supplied. Only the
elementary theorem on primes congruent to one is needed. -/
theorem exists_admissible_twist
    (L : Type*) [Field L] [NumberField L] (n : ℕ) (hn : n ≠ 0) :
    ∃ m : ℕ, m.Prime ∧ ((NumberField.discr L).natAbs).Coprime m ∧
      ∃ τ : (ZMod m)ˣ, n ∣ orderOf τ := by
  obtain ⟨m, hm, hlarge, hmod⟩ :=
    Nat.exists_prime_gt_modEq_one ((NumberField.discr L).natAbs + 2) hn
  have hdiscpos : 0 < (NumberField.discr L).natAbs :=
    Int.natAbs_pos.mpr (NumberField.discr_ne_zero L)
  have hcop : ((NumberField.discr L).natAbs).Coprime m := by
    apply Nat.Coprime.symm
    apply hm.coprime_iff_not_dvd.mpr
    intro hd
    have hle := Nat.le_of_dvd hdiscpos hd
    omega
  have : Fact m.Prime := ⟨hm⟩
  have : IsCyclic (ZMod m)ˣ := ZMod.isCyclic_units_prime hm
  obtain ⟨τ, hτ⟩ := IsCyclic.exists_ofOrder_eq_natCard (α := (ZMod m)ˣ)
  have hn_div : n ∣ m - 1 := (Nat.modEq_iff_dvd' hm.pos).mp hmod.symm
  refine ⟨m, hm, hcop, τ, ?_⟩
  rw [hτ, Nat.card_eq_fintype_card, ZMod.card_units_eq_totient, Nat.totient_prime hm]
  exact hn_div

/-- Finite-set avoidance for every actual finite Galois extension of number fields.
No abelian, cyclotomic, density, cancellation, or occurrence premise is supplied. -/
theorem general_frobenius_avoids
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (σ : Gal(L/K)) (B : Finset (Ideal (𝓞 K))) :
    ∃ p : Ideal (𝓞 K), p ∉ B ∧ p.IsPrime ∧ UnramifiedIn K L p ∧
      frobeniusClass K L p = ConjClasses.mk σ := by
  classical
  obtain ⟨m, hm, hcop, τ, hτ⟩ := exists_admissible_twist L (orderOf σ)
    (orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)).ne'
  have : NeZero m := ⟨hm.ne_zero⟩
  let M := CyclotomicField m L
  have : IsGalois K M := PaperX.CrossingFields.compositum_galois K L M m
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot L M
    (Set.mem_singleton m) (NeZero.ne m)
  have hbij := PaperX.CrossingFields.joint_restriction_bijective K L M m hcop ζ hζ
  obtain ⟨s, hs⟩ := hbij.surjective (σ, τ)
  have hrestr : AlgEquiv.restrictNormalHom L s = σ := congrArg Prod.fst hs
  have hchar : hζ.autToPow K s = τ := congrArg Prod.snd hs
  have hmeet := PaperX.CrossingFixedField.crossing_meet K L M m ζ hζ σ τ hτ
    s hrestr hchar hbij.injective
  obtain ⟨p, hB, hp, hunrM, hfr⟩ :=
    PaperX.CrossingFixedField.crossing_avoids K L M m s hmeet B
  have := hp
  exact ⟨p, hB, hp, PaperX.FrobeniusTowerProjection.unramified_descend K L M p hunrM,
    PaperX.FrobeniusTowerProjection.frobeniusClass_project K L M σ s hrestr p hunrM hfr⟩

/-- Each prescribed Frobenius conjugacy class occurs infinitely often. -/
theorem general_frobenius_infinite
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (σ : Gal(L/K)) :
    Set.Infinite {p : Ideal (𝓞 K) | p.IsPrime ∧ UnramifiedIn K L p ∧
      frobeniusClass K L p = ConjClasses.mk σ} := by
  classical
  intro hfin
  obtain ⟨p, hp, hrest⟩ := general_frobenius_avoids K L σ hfin.toFinset
  exact hp (hfin.mem_toFinset.mpr hrest)


/-- The exact conjugacy-class shape needed by the prime-ideal API. -/
theorem infinite_setOf_frobenius_class
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (C : ConjClasses Gal(L/K)) :
    Set.Infinite {p : Ideal (𝓞 K) | p.IsPrime ∧ UnramifiedIn K L p ∧
      frobeniusClass K L p = C} := by
  obtain ⟨σ, rfl⟩ := ConjClasses.mk_surjective C
  exact general_frobenius_infinite K L σ

end PaperX.GeneralFrobeniusOccurrence
