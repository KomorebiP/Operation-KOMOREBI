module

public import PaperX.ArtinFactorization
public import PaperX.CyclotomicGoodBoundary

/-!
# Restoring finitely removed Artin factors

The auxiliary norm-residue series omits every modulus prime. This module
proves the Euler-product identity restoring exactly those omitted primes that
are unramified in L/K. They form an actual finite set, and each correction
factor has a finite nonzero boundary value. No bad-prime list is supplied.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter
open PaperX.ArtinLocalFactors PaperX.ArtinFactorization
open PaperX.FrobeniusArtinDomination PaperX.CyclotomicGoodBoundary
open scoped Topology
namespace PaperX.FiniteArtinRestore

abbrev GoodPrime (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) :=
  {p : UnramifiedPrime K L // (Ideal.absNorm p.1).Coprime m}

abbrev OmittedPrime (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) :=
  {p : UnramifiedPrime K L // ¬ (Ideal.absNorm p.1).Coprime m}

instance omittedFinite (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) [NeZero m] : Finite (OmittedPrime K L m) :=
  have : Finite {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ (Ideal.absNorm p).Coprime m} :=
    (finite_badPrimes K m).to_subtype
  Finite.of_injective (fun p : OmittedPrime K L m ↦
    (⟨p.1.1, p.1.2.1, p.1.2.2.ne_bot, p.2⟩ :
      {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ (Ideal.absNorm p).Coprime m}))
    (fun _ _ h ↦ Subtype.ext (Subtype.ext (congrArg (fun p :
      {p : Ideal (𝓞 K) // p.IsPrime ∧ p ≠ ⊥ ∧ ¬ (Ideal.absNorm p).Coprime m} ↦ p.1) h)))

theorem goodCoefficient_one (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) :
    goodCoefficient K L m χ ⊤ = 1 := by
  simp [goodCoefficient, coefficient_one]

theorem goodCoefficient_mul (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L)
    {I J : Ideal (𝓞 K)} (hI : I ≠ ⊥) (hJ : J ≠ ⊥) :
    goodCoefficient K L m χ (I * J) = goodCoefficient K L m χ I * goodCoefficient K L m χ J := by
  classical
  simp only [goodCoefficient, map_mul Ideal.absNorm I J, Nat.coprime_mul_iff_left,
    coefficient_mul K L χ hI hJ]
  split_ifs <;> simp_all

theorem norm_goodCoefficient_le_one (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) (I : Ideal (𝓞 K)) :
    ‖goodCoefficient K L m χ I‖ ≤ 1 := by
  classical
  by_cases hc : (Ideal.absNorm I).Coprime m
  · simpa only [goodCoefficient, ite_eq_left hc] using norm_idealCoefficient_le_one K L χ I
  · simp [goodCoefficient, hc]

def artinFactor (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (χ : Character K L) (p : UnramifiedPrime K L) (s : ℂ) : ℂ :=
  (1 - (χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹

/-- Euler product of the actual good coefficients, for any Galois extension. -/
theorem good_eulerProduct (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    (∏' p : GoodPrime K L m, artinFactor K L χ p.1 s) = goodSeries K L m χ s := by
  classical
  rw [goodSeries, ← weighted_eulerProduct_eq_tsum K hs (goodCoefficient K L m χ)
    (goodCoefficient_one K L m χ) (fun {I J} hI hJ ↦ goodCoefficient_mul K L m χ hI hJ)
    (norm_goodCoefficient_le_one K L m χ)]
  let g : GoodPrime K L m → Prime K := fun p ↦ ⟨p.1.1, p.1.2.1, p.1.2.2.ne_bot⟩
  let f : Prime K → ℂ := fun p ↦
    (1 - goodCoefficient K L m χ p.1 * (Ideal.absNorm p.1 : ℂ) ^ (-s))⁻¹
  have hg : Function.Injective g := fun _ _ h ↦ Subtype.ext (Subtype.ext
    (congrArg (fun p : Prime K ↦ p.1) h))
  have hsupp : Function.mulSupport f ⊆ Set.range g := by
    intro p hp
    have := p.2.1
    have hc : (Ideal.absNorm p.1).Coprime m := by
      by_contra hn
      apply hp
      simp only [f, goodCoefficient, ite_eq_right hn, zero_mul, sub_zero, inv_one]
    have hu : UnramifiedIn K L p.1 := by
      by_contra hn
      apply hp
      simp only [f, goodCoefficient, ite_eq_left hc, coefficient_prime K L χ p.1 p.2.2,
        ite_eq_right hn, zero_mul, sub_zero, inv_one]
    exact ⟨⟨⟨p.1, p.2.1, hu⟩, hc⟩, rfl⟩
  change _ = ∏' p, f p
  rw [← hg.tprod_eq hsupp]
  refine tprod_congr fun p ↦ ?_
  have := p.1.2.1
  simp only [f, g, goodCoefficient, ite_eq_left p.2,
    coefficient_prime K L χ p.1.1 p.1.2.2.ne_bot, ite_eq_left p.1.2.2, artinFactor]

def omittedCorrection (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) (s : ℂ) : ℂ :=
  ∏' p : OmittedPrime K L m, artinFactor K L χ p.1 s

/-- The original Artin series, with only ramified primes removed, is recovered
from the good series by the exact finite unramified-modulus correction. -/
theorem restore_series (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) [NeZero m]
    (χ : Character K L) {s : ℂ} (hs : 1 < s.re) :
    seriesC K L χ s = goodSeries K L m χ s * omittedCorrection K L m χ s := by
  let f : UnramifiedPrime K L → ℂ := fun p ↦ artinFactor K L χ p s
  let S : Set (UnramifiedPrime K L) := {p | (Ideal.absNorm p.1).Coprime m}
  have hG : Multipliable fun p : GoodPrime K L m ↦ f p.1 := by
    have h := (summable_artin_shift K L χ hs).subtype (fun p ↦ (Ideal.absNorm p.1).Coprime m)
    simpa using multipliable_one_add_of_summable
      (f := fun p : GoodPrime K L m ↦ f p.1 - 1) h
  have hB : Multipliable fun p : OmittedPrime K L m ↦ f p.1 := Multipliable.of_finite
  have h := (hG.hasProd.mul_compl (f := f) (s := S) hB.hasProd).tprod_eq
  change (∏' p : UnramifiedPrime K L, artinFactor K L χ p s) =
    (∏' p : GoodPrime K L m, artinFactor K L χ p.1 s) * omittedCorrection K L m χ s at h
  rw [good_eulerProduct K L m χ hs] at h
  exact (eulerProduct_eq_series K L χ hs).symm.trans h

/-- Character-twisted omitted Euler factors have nonzero denominators at one. -/
theorem artinFactor_at_one_nonzero (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (χ : Character K L) (p : UnramifiedPrime K L) : artinFactor K L χ p 1 ≠ 0 := by
  have hq : 2 ≤ Ideal.absNorm p.1 := prime_norm_two_le K ⟨p.1, p.2.1, p.2.2.ne_bot⟩
  have hn : ‖(χ (frobeniusClass K L p.1).out : ℂ)‖ = 1 :=
    (((Units.coeHom ℂ).comp χ).isOfFinOrder
      (isOfFinOrder_of_finite (frobeniusClass K L p.1).out)).norm_eq_one
  apply inv_ne_zero
  apply sub_ne_zero.mpr
  intro heq
  have hlt : ‖(χ (frobeniusClass K L p.1).out : ℂ) * (Ideal.absNorm p.1 : ℂ) ^ (-(1 : ℂ))‖ < 1 := by
    rw [norm_mul, hn, one_mul, Complex.cpow_neg_one, norm_inv, Complex.norm_natCast]
    apply inv_lt_one_of_one_lt₀
    exact_mod_cast (show 1 < Ideal.absNorm p.1 by omega)
  rw [← heq, norm_one] at hlt
  exact lt_irrefl _ hlt

theorem artinFactor_continuousAt_one (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    (χ : Character K L) (p : UnramifiedPrime K L) :
    ContinuousAt (fun s : ℝ ↦ artinFactor K L χ p (s : ℂ)) 1 := by
  have hq : (Ideal.absNorm p.1 : ℂ) ≠ 0 :=
    Nat.cast_ne_zero.mpr (mt Ideal.absNorm_eq_zero_iff.mp p.2.2.ne_bot)
  have hpow : ContinuousAt (fun s : ℝ ↦ (Ideal.absNorm p.1 : ℂ) ^ (-(s : ℂ))) 1 :=
    (continuousAt_const_cpow hq).comp Complex.continuous_ofReal.continuousAt.neg
  have hden : (1 : ℂ) - (χ (frobeniusClass K L p.1).out : ℂ) *
      (Ideal.absNorm p.1 : ℂ) ^ (-(1 : ℂ)) ≠ 0 :=
    fun hz ↦ artinFactor_at_one_nonzero K L χ p (inv_eq_zero.mpr hz)
  exact (continuousAt_const.sub (continuousAt_const.mul hpow)).inv₀ hden

/-- The complete finite omitted set, not a chosen sublist, has a nonzero limit. -/
theorem omittedCorrection_limit (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L] (m : ℕ) [NeZero m]
    (χ : Character K L) :
    omittedCorrection K L m χ 1 ≠ 0 ∧
      Tendsto (fun s : ℝ ↦ omittedCorrection K L m χ (s : ℂ))
        (𝓝[>] 1) (𝓝 (omittedCorrection K L m χ 1)) := by
  classical
  let : Fintype (OmittedPrime K L m) := Fintype.ofFinite _
  constructor
  · rw [omittedCorrection, tprod_fintype]
    exact Finset.prod_ne_zero_iff.mpr fun p _ ↦ artinFactor_at_one_nonzero K L χ p.1
  · have h := (tendsto_finsetProd Finset.univ (fun p : OmittedPrime K L m ↦
      fun _ ↦ (artinFactor_continuousAt_one K L χ p.1).tendsto)).mono_left (nhdsWithin_le_nhds (s := Set.Ioi (1 : ℝ)))
    simpa only [omittedCorrection, tprod_fintype, Complex.ofReal_one] using h

/-- Actual finite boundary limits of the original incomplete cyclotomic Artin
series, with every extra omitted unramified factor restored. -/
theorem cyclotomic_boundary_limit (K L : Type*) [Field K] [NumberField K]
    [Field L] [NumberField L] [Algebra K L] [IsGalois K L]
    [IsMulCommutative Gal(L/K)] (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (χ : Character K L) (hχ : χ ≠ 1) :
    ∃ v : ℂ, Tendsto (fun s : ℝ ↦ seriesC K L χ (s : ℂ)) (𝓝[>] 1) (𝓝 v) := by
  obtain ⟨v, hv⟩ := goodSeries_boundary_limit K L m χ hχ
  refine ⟨v * omittedCorrection K L m χ 1,
    (hv.mul (omittedCorrection_limit K L m χ).2).congr' ?_⟩
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact (restore_series K L m χ (s := (s : ℂ)) (show 1 < (s : ℂ).re from hs)).symm

end PaperX.FiniteArtinRestore
