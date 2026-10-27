module

public import PaperX.FrobeniusArtinDomination
public import Mathlib.GroupTheory.FiniteAbelian.Duality
public import Mathlib.RingTheory.RootsOfUnity.Complex
public import Mathlib.RingTheory.RootsOfUnity.AlgebraicallyClosed
public import Mathlib.Analysis.Complex.Polynomial.Basic

/-!
# Actual Artin Euler products and local abelian factorization

The arithmetic coefficients are exactly those of the retained residue bridge.
The character-product and local-factor arguments adapt the corresponding
constructions in CBirkbeck/AINTLIB, ZetaProduct.lean, pinned at
c62aa9dd4638d86b50f46d4000cf87157e333a6f. This is a scoped local implementation,
not a claim that the full upstream module has been ported.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Finset
open PaperX.FrobeniusArtinDomination
namespace PaperX.ArtinLocalFactors

abbrev Character (K L : Type*) [Field K] [Field L] [Algebra K L] := Gal(L/K) →* ℂˣ

/-- The same arithmetic series, now on the complex half-plane. -/
def seriesC (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) (s : ℂ) : ℂ :=
  ∑' a : NonzeroIdeal K, idealCoefficient K L χ a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-s)

theorem seriesC_real (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) (s : ℝ) :
    seriesC K L χ (s : ℂ) = idealArtinSeries K L χ s := rfl

open Classical in
theorem coefficient_eq_map_prod
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) (a : Ideal (𝓞 K)) :
    idealCoefficient K L χ a =
      ((UniqueFactorizationMonoid.normalizedFactors a).map
        (fun p ↦ if UnramifiedIn K L p then (χ (frobeniusClass K L p).out : ℂ)
          else 0)).prod := by
  rw [idealCoefficient, Finset.prod_multiset_map_count]

open Classical in
theorem coefficient_prime
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L)
    (p : Ideal (𝓞 K)) [p.IsPrime] (hp : p ≠ ⊥) :
    idealCoefficient K L χ p =
      if UnramifiedIn K L p then (χ (frobeniusClass K L p).out : ℂ) else 0 := by
  rw [coefficient_eq_map_prod, UniqueFactorizationMonoid.normalizedFactors_irreducible
    (Ideal.prime_of_isPrime hp ‹_›).irreducible, normalize_eq, Multiset.map_singleton,
    Multiset.prod_singleton]

theorem coefficient_mul
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L)
    {a b : Ideal (𝓞 K)} (ha : a ≠ ⊥) (hb : b ≠ ⊥) :
    idealCoefficient K L χ (a * b) =
      idealCoefficient K L χ a * idealCoefficient K L χ b := by
  rw [coefficient_eq_map_prod, coefficient_eq_map_prod, coefficient_eq_map_prod,
    UniqueFactorizationMonoid.normalizedFactors_mul ha hb, Multiset.map_add, Multiset.prod_add]

theorem coefficient_one
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) :
    idealCoefficient K L χ ⊤ = 1 := by
  rw [coefficient_eq_map_prod, ← Ideal.one_eq_top,
    UniqueFactorizationMonoid.normalizedFactors_one, Multiset.map_zero, Multiset.prod_zero]

/-- Absolute convergence on the open half-plane for the actual ideal series. -/
theorem series_summable
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    Summable fun a : NonzeroIdeal K ↦
      idealCoefficient K L χ a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-s) := by
  apply Summable.of_norm
  refine Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _) (fun a ↦ ?_)
    (hasSum_nonzeroIdeal_absNorm_cpow K hs).summable.norm
  rw [norm_mul]
  exact mul_le_of_le_one_left (norm_nonneg _) (norm_idealCoefficient_le_one K L χ a.1)

/-- Euler product over the actual unramified primes; ramified coefficients are zero. -/
theorem eulerProduct_eq_series
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    (∏' p : {p : Ideal (𝓞 K) // p.IsPrime ∧ UnramifiedIn K L p},
      (1 - (χ (frobeniusClass K L p.1).out : ℂ) *
        (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹) = seriesC K L χ s := by
  classical
  rw [seriesC, ← weighted_eulerProduct_eq_tsum K hs (idealCoefficient K L χ)
    (coefficient_one K L χ) (fun {a b} ha hb ↦ coefficient_mul K L χ ha hb)
    (norm_idealCoefficient_le_one K L χ)]
  let g : {p : Ideal (𝓞 K) // p.IsPrime ∧ UnramifiedIn K L p} →
      {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥} := fun p ↦ ⟨p.1, p.2.1, p.2.2.ne_bot⟩
  let f : {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥} → ℂ := fun p ↦
      (1 - idealCoefficient K L χ p.1 * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹
  have hg : Function.Injective g := fun _ _ h ↦ Subtype.ext (congrArg (fun x : {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥} ↦ x.1) h)
  have hsupp : Function.mulSupport f ⊆ Set.range g := by
    intro p hp
    simp only [Function.mem_mulSupport, f] at hp
    have := p.2.1
    have hu : UnramifiedIn K L p.1 := by
      by_contra hn
      apply hp
      rw [coefficient_prime K L χ p.1 p.2.2, ite_eq_right hn, zero_mul, sub_zero, inv_one]
    exact ⟨⟨p.1, p.2.1, hu⟩, rfl⟩
  change _ = ∏' p, f p
  rw [← hg.tprod_eq hsupp]
  refine tprod_congr fun p ↦ ?_
  have := p.2.1
  simp only [f, g]
  rw [coefficient_prime K L χ p.1 p.2.2.ne_bot, ite_eq_left p.2.2]

section FiniteCharacters

private theorem prod_one_sub_nthRoots (f : ℕ) (hf : 0 < f) (Y : ℂ) :
    ∏ ζ ∈ Polynomial.nthRootsFinset f (1 : ℂ), (1 - ζ * Y) = 1 - Y ^ f := by
  rw [← (Complex.isPrimitiveRoot_exp f hf.ne').pow_sub_pow_eq_prod_sub_mul 1 Y hf, one_pow]

private def charEval {G : Type*} [CommGroup G] [Finite G] (σ : G) :
    (G →* ℂˣ) →* ℂˣ := (CommGroup.monoidHomMonoidHomEquiv G ℂ).symm σ

private theorem charEval_apply {G : Type*} [CommGroup G] [Finite G] (σ : G) (χ : G →* ℂˣ) :
    charEval σ χ = χ σ := by rw [charEval, CommGroup.monoidHomMonoidHomEquiv_symm_apply_apply]

private theorem charEval_ker_card {G : Type*} [CommGroup G] [Finite G] (σ : G) :
    Nat.card (charEval σ).ker = Nat.card G / orderOf σ := by
  have h1 : (charEval σ).ker = (MonoidHom.domRestrictHom (Subgroup.zpowers σ) ℂˣ).ker := by
    ext χ
    simp only [MonoidHom.mem_ker, MonoidHom.domRestrictHom_apply, MonoidHom.domRestrict_eq_one_iff]
    refine ⟨fun h y hy ↦ ?_, fun h ↦ ?_⟩
    · rw [charEval_apply] at h
      obtain ⟨n, rfl⟩ := Subgroup.mem_zpowers_iff.mp hy
      rw [map_zpow, h, one_zpow]
    · rw [charEval_apply]
      exact h σ (Subgroup.mem_zpowers σ)
  rw [h1, CommGroup.card_domRestrictHom_ker]
  have hp : 0 < orderOf σ := orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)
  have heq : Nat.card G = Nat.card (G ⧸ Subgroup.zpowers σ) * orderOf σ := by
    rw [Subgroup.card_eq_card_quotient_mul_card_subgroup (Subgroup.zpowers σ), Nat.card_zpowers]
  rw [heq, Nat.mul_div_cancel _ hp]

/-- The finite abelian character product, with the exact uniform fibre multiplicity. -/
theorem character_product {G : Type*} [CommGroup G] [Finite G] [Fintype (G →* ℂˣ)]
    (σ : G) (Y : ℂ) :
    ∏ χ : G →* ℂˣ, (1 - (χ σ : ℂ) * Y) =
      (1 - Y ^ orderOf σ) ^ (Nat.card G / orderOf σ) := by
  classical
  let f := orderOf σ
  have hf : 0 < f := orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)
  let ev : (G →* ℂˣ) →* ℂ := (Units.coeHom ℂ).comp (charEval σ)
  have hev : ∀ χ : G →* ℂˣ, ev χ = (χ σ : ℂ) := fun χ ↦ by
    change ((charEval σ) χ : ℂ) = (χ σ : ℂ)
    rw [charEval_apply]
  have hfib : #{χ : G →* ℂˣ | ev χ = 1} = Nat.card (charEval σ).ker := by
    rw [Nat.card_eq_fintype_card, ← Fintype.card_coe]
    refine Fintype.card_congr (Equiv.subtypeEquivRight fun χ ↦ ?_)
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, MonoidHom.mem_ker, hev]
    rw [Units.val_eq_one, ← charEval_apply σ χ]
  have hunif : ∀ c ∈ Set.range ev,
      #{χ : G →* ℂˣ | ev χ = c} = Nat.card (charEval σ).ker := by
    intro c hc
    rw [MonoidHom.card_fiber_eq_of_mem_range ev hc (⟨1, map_one _⟩ : (1 : ℂ) ∈ Set.range ev), hfib]
  let t := Polynomial.nthRootsFinset f (1 : ℂ)
  have hmaps : ∀ χ ∈ (Finset.univ : Finset (G →* ℂˣ)), ev χ ∈ t := by
    intro χ _
    rw [Polynomial.mem_nthRootsFinset hf, hev, ← Units.val_pow_eq_pow_val,
      ← map_pow, pow_orderOf_eq_one, map_one, Units.val_one]
  have hsub : Finset.univ.image ev ⊆ t := by
    intro c hc
    obtain ⟨χ, _, rfl⟩ := Finset.mem_image.mp hc
    exact hmaps χ (Finset.mem_univ χ)
  have hcard : Nat.card G = (Finset.univ.image ev).card * Nat.card (charEval σ).ker := by
    have h := Finset.card_eq_sum_card_image ev (Finset.univ : Finset (G →* ℂˣ))
    rw [show (Finset.univ : Finset (G →* ℂˣ)).card = Nat.card (G →* ℂˣ) by
      rw [Nat.card_eq_fintype_card, Finset.card_univ],
      CommGroup.card_monoidHom_of_hasEnoughRootsOfUnity] at h
    rw [h, Finset.sum_congr rfl (fun c hc ↦ hunif c ?_), Finset.sum_const, smul_eq_mul]
    obtain ⟨χ, _, rfl⟩ := Finset.mem_image.mp hc
    exact Set.mem_range_self χ
  have himgcard : (Finset.univ.image ev).card = f := by
    have hdvd : f ∣ Nat.card G := orderOf_dvd_natCard σ
    have hk : Nat.card (charEval σ).ker = Nat.card G / f := charEval_ker_card σ
    rw [hk] at hcard
    exact Nat.eq_of_mul_eq_mul_right (hk ▸ Nat.card_pos)
      (by rw [← hcard, Nat.mul_div_cancel' hdvd])
  have himg : Finset.univ.image ev = t := Finset.eq_of_subset_of_card_le hsub
    (by rw [himgcard, (Complex.isPrimitiveRoot_exp f hf.ne').card_nthRootsFinset])
  have hfiber := Finset.prod_fiberwise_of_maps_to' (s := (Finset.univ : Finset (G →* ℂˣ)))
    (t := t) (g := ev) (f := fun c : ℂ ↦ 1 - c * Y) hmaps
  have hleft : ∏ χ : G →* ℂˣ, (1 - (χ σ : ℂ) * Y) =
      ∏ χ : G →* ℂˣ, (1 - ev χ * Y) := Finset.prod_congr rfl fun χ _ ↦ by rw [hev]
  rw [hleft, ← hfiber]
  have hinner : ∀ c ∈ t,
      (∏ _χ ∈ {χ ∈ (Finset.univ : Finset (G →* ℂˣ)) | ev χ = c}, (1 - c * Y)) =
        (1 - c * Y) ^ Nat.card (charEval σ).ker := by
    intro c hc
    have hr : c ∈ Set.range ev := by
      rw [← himg] at hc
      obtain ⟨χ, _, rfl⟩ := Finset.mem_image.mp hc
      exact Set.mem_range_self χ
    rw [Finset.prod_const, hunif c hr]
  rw [Finset.prod_congr rfl hinner, charEval_ker_card σ, Finset.prod_pow,
    prod_one_sub_nthRoots f hf Y]
end FiniteCharacters

private theorem cpow_neg_norm_eq_pow {a b : ℕ} (f : ℕ) (s : ℂ) (h : b = a ^ f) :
    (b : ℂ) ^ (-s) = ((a : ℂ) ^ (-s)) ^ f := by
  rw [h, Nat.cast_pow, ← Complex.natCast_cpow_natCast_mul, Complex.cpow_nat_mul]

set_option backward.isDefEq.respectTransparency false in
/-- Local factorization at a supplied actual unramified prime. -/
theorem local_factorization
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] [IsMulCommutative Gal(L/K)]
    (p : Ideal (𝓞 K)) [p.IsPrime] (hu : UnramifiedIn K L p) (s : ℂ) :
    (∏' P : {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥},
      (1 - (Ideal.absNorm P.1 : ℂ) ^ (-s))⁻¹) =
    ∏' χ : Character K L,
      (1 - (χ (frobeniusClass K L p).out : ℂ) * (Ideal.absNorm p : ℂ) ^ (-s))⁻¹ := by
  classical
  let : CommGroup Gal(L/K) := { mul_comm := mul_comm' }
  let σ : Gal(L/K) := (frobeniusClass K L p).out
  let Y : ℂ := (Ideal.absNorm p : ℂ) ^ (-s)
  let f : ℕ := orderOf σ
  let : Fintype (Gal(L/K) →* ℂˣ) := Fintype.ofFinite _
  have hf : 0 < f := orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)
  have hcount : Nat.card {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥}
      = Nat.card Gal(L/K) / f := by
    have h := card_primesAbove_mul_orderOf_eq K L σ (frobeniusClass K L p)
      (Quotient.out_eq _) p hu rfl
    exact (Nat.div_eq_of_eq_mul_left hf h.symm).symm
  have hright : (∏' χ : Character K L, (1 - (χ σ : ℂ) * Y)⁻¹) =
      ((1 - Y ^ f) ^ (Nat.card Gal(L/K) / f))⁻¹ := by
    rw [tprod_fintype, Finset.prod_inv_distrib, character_product σ Y]
  have hpbot : p ≠ ⊥ := hu.ne_bot
  have : p.IsMaximal := ‹p.IsPrime›.isMaximal hpbot
  have : Finite (p.primesOver (𝓞 L)) := (IsDedekindDomain.primesOver_finite p (𝓞 L)).to_subtype
  have : Finite {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥} :=
    Finite.of_injective
      (fun P : {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥} ↦
        (⟨P.1, P.2.1, P.2.2.1⟩ : p.primesOver (𝓞 L)))
      (fun _ _ h ↦ Subtype.ext (by simpa using h))
  let : Fintype {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥} := Fintype.ofFinite _
  have hterm : ∀ P : {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p ∧ P ≠ ⊥},
      (1 - (Ideal.absNorm P.1 : ℂ) ^ (-s))⁻¹ = (1 - Y ^ f)⁻¹ := by
    intro P
    have := P.2.1
    have hlo : P.1.LiesOver p := P.2.2.1
    have : P.1.IsMaximal := P.2.1.isMaximal P.2.2.2
    have : P.1.LiesOver (P.1.under (𝓞 K)) := Ideal.over_under (A := 𝓞 K) (P := P.1)
    have : (P.1.under (𝓞 K)).IsMaximal := hlo.over ▸ (inferInstance : p.IsMaximal)
    have hdeg : P.1.inertiaDeg (𝓞 K) = f := by
      rw [Ideal.inertiaDeg_eq_of_isMaximal (P.1.under (𝓞 K)) P.1]
      exact finrank_residue_eq_orderOf K L σ (frobeniusClass K L p) (Quotient.out_eq _)
        p hu rfl P.1 hlo
    have hnorm : Ideal.absNorm P.1 = Ideal.absNorm p ^ f := by
      rw [← Ideal.absNorm_pow_inertiaDeg p P.1, hdeg]
    rw [cpow_neg_norm_eq_pow f s hnorm]
  change _ = ∏' χ : Character K L, (1 - (χ σ : ℂ) * Y)⁻¹
  rw [tprod_congr hterm, tprod_fintype, Finset.prod_const, Finset.card_univ,
    ← Nat.card_eq_fintype_card, hcount, hright, inv_pow]

end PaperX.ArtinLocalFactors
