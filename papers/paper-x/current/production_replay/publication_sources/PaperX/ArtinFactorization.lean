module

public import PaperX.ArtinLocalFactors
public import PaperX.RamifiedResidueClosure

/-!
# Global abelian Artin factorization with the actual ramified correction

The products below are indexed by actual prime ideals, not a supplied list.
The proof uses absolute convergence, contraction of prime ideals, the finite
local character-product identity and the finite ramified set. No density or
Frobenius-occurrence premise is used. The Euler-product rearrangements adapt
CBirkbeck/AINTLIB ZetaProduct.lean at commit
c62aa9dd4638d86b50f46d4000cf87157e333a6f, with the old residue bridge's exact
arithmetic coefficient definition retained.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter
open scoped Topology
open PaperX.ArtinLocalFactors PaperX.FrobeniusArtinDomination
namespace PaperX.ArtinFactorization

abbrev Prime (K : Type*) [Field K] [NumberField K] :=
  {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥}

abbrev UnramifiedPrime (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] :=
  {p : Ideal (𝓞 K) // p.IsPrime ∧ UnramifiedIn K L p}

abbrev UnramifiedTop (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] :=
  {P : Ideal (𝓞 L) // P.IsPrime ∧ P ≠ ⊥ ∧ UnramifiedIn K L (P.under (𝓞 K))}

/-- Precisely the top-field primes whose contraction ramifies in the extension. -/
abbrev RamifiedTop (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] :=
  {P : Ideal (𝓞 L) // P.IsPrime ∧ P ≠ ⊥ ∧ ¬ UnramifiedIn K L (P.under (𝓞 K))}

/-- Euler factor at a genuine ideal norm. -/
def factor (L : Type*) [Field L] [NumberField L] (P : Ideal (𝓞 L)) (s : ℂ) : ℂ :=
  (1 - (Ideal.absNorm P : ℂ) ^ (-s))⁻¹

private theorem norm_one_sub_inv_sub_one_le {y : ℂ} (hy : ‖y‖ ≤ 1 / 2) :
    ‖(1 - y)⁻¹ - 1‖ ≤ 2 * ‖y‖ := by
  have hn : (1 : ℂ) - y ≠ 0 := sub_ne_zero.mpr (by rintro rfl; norm_num at hy)
  have heq : (1 - y)⁻¹ - 1 = y * (1 - y)⁻¹ := by field_simp; ring
  rw [heq, norm_mul]
  have hlb : (2 : ℝ)⁻¹ ≤ ‖(1 : ℂ) - y‖ := by
    have ht := norm_sub_norm_le (1 : ℂ) y
    rw [norm_one] at ht
    linarith
  have hi : ‖(1 - y)⁻¹‖ ≤ 2 := by
    rw [norm_inv, show (2 : ℝ) = (2⁻¹ : ℝ)⁻¹ by norm_num]
    exact inv_anti₀ (by norm_num) hlb
  rw [mul_comm 2 ‖y‖]
  exact mul_le_mul_of_nonneg_left hi (norm_nonneg _)

theorem prime_norm_two_le (L : Type*) [Field L] [NumberField L] (P : Prime L) :
    2 ≤ Ideal.absNorm P.1 := by
  have h0 : Ideal.absNorm P.1 ≠ 0 := fun h ↦ P.2.2 (Ideal.absNorm_eq_zero_iff.mp h)
  have h1 : Ideal.absNorm P.1 ≠ 1 := fun h ↦ P.2.1.ne_top (Ideal.absNorm_eq_one_iff.mp h)
  omega

private theorem norm_prime_power_le_half (L : Type*) [Field L] [NumberField L]
    {s : ℂ} (hs : 1 < s.re) (P : Prime L) :
    ‖(Ideal.absNorm P.1 : ℂ) ^ (-s)‖ ≤ 1 / 2 := by
  have h2 := prime_norm_two_le L P
  have hpos : 0 < Ideal.absNorm P.1 := by omega
  rw [Complex.norm_natCast_cpow_of_pos hpos, Complex.neg_re]
  have hb2 : (2 : ℝ) ≤ (Ideal.absNorm P.1 : ℝ) := by exact_mod_cast h2
  have hb1 : (1 : ℝ) ≤ (Ideal.absNorm P.1 : ℝ) := one_le_two.trans hb2
  calc (Ideal.absNorm P.1 : ℝ) ^ (-s.re)
      ≤ (Ideal.absNorm P.1 : ℝ) ^ (-1 : ℝ) :=
        Real.rpow_le_rpow_of_exponent_le hb1 (by linarith)
    _ = ((Ideal.absNorm P.1 : ℝ))⁻¹ := Real.rpow_neg_one _
    _ ≤ (2 : ℝ)⁻¹ := by rw [inv_le_inv₀ (by linarith) (by norm_num)]; exact hb2
    _ = 1 / 2 := by norm_num

private theorem summable_prime_shift (L : Type*) [Field L] [NumberField L]
    {s : ℂ} (hs : 1 < s.re) : Summable fun P : Prime L ↦ ‖factor L P.1 s - 1‖ := by
  have hall := (hasSum_nonzeroIdeal_absNorm_cpow L hs).summable.norm
  have hp : Summable fun P : Prime L ↦ ‖(Ideal.absNorm P.1 : ℂ) ^ (-s)‖ :=
    hall.comp_injective (i := fun P : Prime L ↦ (⟨P.1, P.2.2⟩ : NonzeroIdeal L))
      (fun _ _ h ↦ Subtype.ext (congrArg (fun x : NonzeroIdeal L ↦ x.1) h))
  exact Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _)
    (fun P ↦ norm_one_sub_inv_sub_one_le (norm_prime_power_le_half L hs P)) (hp.mul_left 2)

private theorem hasProd_all (L : Type*) [Field L] [NumberField L]
    {s : ℂ} (hs : 1 < s.re) :
    HasProd (fun P : Prime L ↦ factor L P.1 s) (NumberField.dedekindZeta L s) := by
  have hm : Multipliable fun P : Prime L ↦ factor L P.1 s := by
    simpa using multipliable_one_add_of_summable
      (f := fun P : Prime L ↦ factor L P.1 s - 1) (summable_prime_shift L hs)
  rw [dedekindZeta_eq_tprod_primeIdeal L hs]
  exact hm.hasProd

private theorem multipliable_restricted (L : Type*) [Field L] [NumberField L]
    {s : ℂ} (hs : 1 < s.re) (p : Prime L → Prop) :
    Multipliable fun P : {P : Prime L // p P} ↦ factor L P.1.1 s := by
  have h := (summable_prime_shift L hs).subtype p
  simpa using multipliable_one_add_of_summable
    (f := fun P : {P : Prime L // p P} ↦ factor L P.1.1 s - 1) h

theorem summable_artin_shift (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    Summable fun p : UnramifiedPrime K L ↦
      ‖(1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹ - 1‖ := by
  have hall := (hasSum_nonzeroIdeal_absNorm_cpow K hs).summable.norm
  have hp : Summable fun p : UnramifiedPrime K L ↦ ‖(Ideal.absNorm p.1 : ℂ) ^ (-s)‖ :=
    hall.comp_injective
      (i := fun p : UnramifiedPrime K L ↦ (⟨p.1, p.2.2.ne_bot⟩ : NonzeroIdeal K))
      (fun _ _ h ↦ Subtype.ext (congrArg (fun x : NonzeroIdeal K ↦ x.1) h))
  have hshift : Summable fun p : UnramifiedPrime K L ↦
      ‖(1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹ - 1‖ := by
    refine Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _) (fun p ↦ ?_) (hp.mul_left 2)
    have hn : ‖(χ (frobeniusClass K L p.1).out : ℂ)‖ = 1 :=
      (((Units.coeHom ℂ).comp χ).isOfFinOrder
        (isOfFinOrder_of_finite (frobeniusClass K L p.1).out)).norm_eq_one
    have hy : ‖(χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s)‖ ≤ 1 / 2 := by
      rw [norm_mul, hn, one_mul]
      exact norm_prime_power_le_half K hs ⟨p.1, p.2.1, p.2.2.ne_bot⟩
    simpa only [norm_mul, hn, one_mul] using norm_one_sub_inv_sub_one_le hy
  exact hshift

private theorem multipliable_artin (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    Multipliable fun p : UnramifiedPrime K L ↦
      (1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹ := by
  have hall := (hasSum_nonzeroIdeal_absNorm_cpow K hs).summable.norm
  have hp : Summable fun p : UnramifiedPrime K L ↦ ‖(Ideal.absNorm p.1 : ℂ) ^ (-s)‖ :=
    hall.comp_injective
      (i := fun p : UnramifiedPrime K L ↦ (⟨p.1, p.2.2.ne_bot⟩ : NonzeroIdeal K))
      (fun _ _ h ↦ Subtype.ext (congrArg (fun x : NonzeroIdeal K ↦ x.1) h))
  have hshift : Summable fun p : UnramifiedPrime K L ↦
      ‖(1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹ - 1‖ := by
    refine Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _) (fun p ↦ ?_) (hp.mul_left 2)
    have hn : ‖(χ (frobeniusClass K L p.1).out : ℂ)‖ = 1 :=
      (((Units.coeHom ℂ).comp χ).isOfFinOrder
        (isOfFinOrder_of_finite (frobeniusClass K L p.1).out)).norm_eq_one
    have hy : ‖(χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s)‖ ≤ 1 / 2 := by
      rw [norm_mul, hn, one_mul]
      exact norm_prime_power_le_half K hs ⟨p.1, p.2.1, p.2.2.ne_bot⟩
    simpa only [norm_mul, hn, one_mul] using norm_one_sub_inv_sub_one_le hy
  simpa using multipliable_one_add_of_summable
    (f := fun p : UnramifiedPrime K L ↦
      (1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹ - 1) hshift

private def underPrime (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (P : UnramifiedTop K L) : UnramifiedPrime K L :=
  ⟨P.1.under (𝓞 K), by have := P.2.1; exact inferInstance, P.2.2.2⟩

private def fibreUnderEquiv (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] (p : UnramifiedPrime K L) :
    {P : UnramifiedTop K L // underPrime K L P = p} ≃
      {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p.1 ∧ P ≠ ⊥} where
  toFun P := ⟨P.1.1, P.1.2.1, ⟨by
    have h := congrArg Subtype.val P.2
    change P.1.1.under (𝓞 K) = p.1 at h
    exact h.symm⟩, P.1.2.2.1⟩
  invFun Q := ⟨⟨Q.1, Q.2.1, Q.2.2.2, by
    have := Q.2.1; have := Q.2.2.1
    rw [← Q.2.2.1.over]; exact p.2.2⟩, Subtype.ext Q.2.2.1.over.symm⟩
  left_inv _ := by ext; rfl
  right_inv _ := by ext; rfl

private def flattenUnramified (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] :
    {P : Prime L // UnramifiedIn K L (P.1.under (𝓞 K))} ≃ UnramifiedTop K L where
  toFun P := ⟨P.1.1, P.1.2.1, P.1.2.2, P.2⟩
  invFun P := ⟨⟨P.1, P.2.1, P.2.2.1⟩, P.2.2.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

private def flattenRamified (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] :
    {P : Prime L // ¬ UnramifiedIn K L (P.1.under (𝓞 K))} ≃ RamifiedTop K L where
  toFun P := ⟨P.1.1, P.1.2.1, P.1.2.2, P.2⟩
  invFun P := ⟨⟨P.1, P.2.1, P.2.2.1⟩, P.2.2.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

set_option backward.isDefEq.respectTransparency false in
/-- The full unramified part is the product of all actual Artin series. -/
theorem unramified_product (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    [IsMulCommutative Gal(L/K)] {s : ℂ} (hs : 1 < s.re) :
    (∏' P : UnramifiedTop K L, factor L P.1 s) = ∏' χ : Character K L, seriesC K L χ s := by
  classical
  let : Fintype (Character K L) := Fintype.ofFinite _
  let F : Ideal (𝓞 L) → ℂ := fun P ↦ factor L P s
  let G : UnramifiedPrime K L → ℂ := fun p ↦ ∏' χ : Character K L,
    (1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹
  have hm : Multipliable fun P : UnramifiedTop K L ↦ F P.1 :=
    (Equiv.multipliable_iff (flattenUnramified K L).symm).mpr
      (multipliable_restricted L hs (fun P ↦ UnramifiedIn K L (P.1.under (𝓞 K))))
  have hfib : ∀ p : UnramifiedPrime K L,
      HasProd (fun P : {P : UnramifiedTop K L // underPrime K L P = p} ↦ F P.1.1) (G p) := by
    intro p
    have : p.1.IsPrime := p.2.1
    have : p.1.IsMaximal := p.2.1.isMaximal p.2.2.ne_bot
    have : Finite (p.1.primesOver (𝓞 L)) :=
      (IsDedekindDomain.primesOver_finite p.1 (𝓞 L)).to_subtype
    have : Finite {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p.1 ∧ P ≠ ⊥} :=
      Finite.of_injective
        (fun P : {P : Ideal (𝓞 L) // P.IsPrime ∧ P.LiesOver p.1 ∧ P ≠ ⊥} ↦
          (⟨P.1, P.2.1, P.2.2.1⟩ : p.1.primesOver (𝓞 L)))
        (fun _ _ h ↦ Subtype.ext (by simpa using h))
    have : Finite {P : UnramifiedTop K L // underPrime K L P = p} :=
      Finite.of_equiv _ (fibreUnderEquiv K L p).symm
    have hval : (∏' P : {P : UnramifiedTop K L // underPrime K L P = p}, F P.1.1) = G p := by
      dsimp only [G]
      rw [← local_factorization K L p.1 p.2.2 s]
      exact (fibreUnderEquiv K L p).tprod_eq (fun Q ↦ factor L Q.1 s)
    rw [← hval]
    exact (Multipliable.of_finite).hasProd
  have hprod : HasProd G (∏' P : UnramifiedTop K L, F P.1) :=
    ((Equiv.sigmaFiberEquiv (underPrime K L)).hasProd_iff.mpr hm.hasProd).sigma hfib
  rw [← hprod.tprod_eq]
  simp only [G]
  simp_rw [tprod_fintype]
  rw [Multipliable.tprod_finsetProd (s := (Finset.univ : Finset (Character K L)))
    (f := fun χ : Character K L ↦ fun p : UnramifiedPrime K L ↦
      (1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹)
    (fun χ _ ↦ multipliable_artin K L χ hs)]
  exact Finset.prod_congr rfl fun χ _ ↦ eulerProduct_eq_series K L χ hs

/-- The ramified top-field set is finite, by contraction to the finite ramified
base set and finiteness of the primes over each nonzero base prime. -/
instance finiteRamifiedTop (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] : Finite (RamifiedTop K L) := by
  classical
  have : Finite {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ UnramifiedIn K L p} :=
    (finite_ramifiedIn K L).to_subtype
  have : ∀ p : {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ UnramifiedIn K L p},
      Finite (p.1.primesOver (𝓞 L)) := fun p ↦ by
    have : p.1.IsPrime := p.2.1
    have : p.1.IsMaximal := p.2.1.isMaximal p.2.2.1
    exact (IsDedekindDomain.primesOver_finite p.1 (𝓞 L)).to_subtype
  refine Finite.of_injective
    (fun P : RamifiedTop K L ↦
      (show Σ p : {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ UnramifiedIn K L p},
          p.1.primesOver (𝓞 L) from
        by
          have := P.2.1
          exact ⟨⟨P.1.under (𝓞 K), inferInstance,
            Ideal.under_ne_bot (A := 𝓞 K) P.2.2.1, P.2.2.2⟩,
              ⟨P.1, P.2.1, Ideal.over_under (A := 𝓞 K) (P := P.1)⟩⟩))
    (fun a b h ↦ Subtype.ext (by simpa using congrArg (fun x ↦ (x.2 : Ideal (𝓞 L))) h))

/-- The correction is constructed from all, and only, actual ramified-above primes. -/
def ramifiedCorrection (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] (s : ℂ) : ℂ :=
  ∏' P : RamifiedTop K L, factor L P.1 s

/-- Global factorization. No factorization premise, norm list, or prime occurrence
hypothesis is present. -/
theorem zeta_factorization (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    [IsMulCommutative Gal(L/K)] {s : ℂ} (hs : 1 < s.re) :
    NumberField.dedekindZeta L s =
      (∏' χ : Character K L, seriesC K L χ s) * ramifiedCorrection K L s := by
  let f : Prime L → ℂ := fun P ↦ factor L P.1 s
  let S : Set (Prime L) := {P | UnramifiedIn K L (P.1.under (𝓞 K))}
  have hU := (multipliable_restricted L hs (fun P ↦ UnramifiedIn K L (P.1.under (𝓞 K)))).hasProd
  have hR := (multipliable_restricted L hs (fun P ↦ ¬ UnramifiedIn K L (P.1.under (𝓞 K)))).hasProd
  have heq := ((hU.mul_compl (f := f) (s := S) hR).unique (hasProd_all L hs)).symm
  have hUf : (∏' P : {P : Prime L // UnramifiedIn K L (P.1.under (𝓞 K))},
      factor L P.1.1 s) = ∏' P : UnramifiedTop K L, factor L P.1 s :=
    Equiv.tprod_eq (flattenUnramified K L) (fun P ↦ factor L P.1 s)
  have hRf : (∏' P : {P : Prime L // ¬ UnramifiedIn K L (P.1.under (𝓞 K))},
      factor L P.1.1 s) = ramifiedCorrection K L s :=
    Equiv.tprod_eq (flattenRamified K L) (fun P ↦ factor L P.1 s)
  rw [hUf, hRf, unramified_product K L hs] at heq
  exact heq

/-- The finite correction's genuine arithmetic norm function. -/
def ramifiedNorm (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] (P : RamifiedTop K L) : ℕ :=
  Ideal.absNorm P.1

theorem ramifiedNorm_two_le (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] (P : RamifiedTop K L) :
    2 ≤ ramifiedNorm K L P := prime_norm_two_le L ⟨P.1, P.2.1, P.2.2.1⟩

/-- The actual ramified correction has a finite nonzero limit at one. -/
theorem ramifiedCorrection_limit_nonzero (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] :
    ∃ r : ℂ, r ≠ 0 ∧
      Tendsto (fun s : ℝ ↦ ramifiedCorrection K L (s : ℂ)) (𝓝[>] (1 : ℝ)) (𝓝 r) := by
  classical
  let : Fintype (RamifiedTop K L) := Fintype.ofFinite _
  let q := ramifiedNorm K L
  refine ⟨PaperX.RamifiedResidueClosure.correctionBoundary q,
    PaperX.RamifiedResidueClosure.correctionBoundary_ne_zero q (ramifiedNorm_two_le K L), ?_⟩
  have h := PaperX.RamifiedResidueClosure.correction_limit q (ramifiedNorm_two_le K L)
  change Tendsto (fun s : ℝ ↦ ∏ P : RamifiedTop K L, factor L P.1 (s : ℂ))
    (𝓝[>] (1 : ℝ)) (𝓝 (PaperX.RamifiedResidueClosure.correctionBoundary q)) at h
  simpa only [ramifiedCorrection, tprod_fintype] using h

end PaperX.ArtinFactorization
