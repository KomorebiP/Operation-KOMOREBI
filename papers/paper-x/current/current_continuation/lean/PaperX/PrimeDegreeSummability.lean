import Mathlib.NumberTheory.NumberField.Basic
import Mathlib.NumberTheory.NumberField.DirichletDensity
import Mathlib.RingTheory.RamificationInertia.Basic
import Mathlib.RingTheory.Ideal.Int
import Mathlib.Analysis.PSeries

/-!
# Summability of primes of higher absolute residue degree

The prime ideals below are actual height-one prime ideals of the ring of integers.
The finite fibre bound is deduced from the ramification-inertia identity.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

namespace PaperX.PrimeDegreeSummability

open NumberField IsDedekindDomain

variable (K : Type*) [Field K] [NumberField K]

abbrev RationalPrime := {p : ℕ // p.Prime}

def primeIdeal (p : RationalPrime) : Ideal ℤ := Ideal.span {(p.1 : ℤ)}

instance primeIdeal_isPrime (p : RationalPrime) : (primeIdeal p).IsPrime :=
  (Ideal.span_singleton_prime (by exact_mod_cast p.2.ne_zero)).mpr
    (Nat.prime_iff_prime_int.mp p.2)

abbrev Above (p : RationalPrime) := (primeIdeal p).primesOver (𝓞 K)

instance aboveFintype (p : RationalPrime) : Fintype (Above K p) :=
  (Algebra.QuasiFinite.finite_primesOver (S := 𝓞 K) (primeIdeal p)).fintype

theorem card_above_le (p : RationalPrime) :
    Fintype.card (Above K p) ≤ Module.finrank ℚ K := by
  rw [← RingOfIntegers.rank, ← Ideal.sum_ramification_inertia_eq_finrank (primeIdeal p) (𝓞 K),
    Fintype.card_eq_sum_ones]
  apply Finset.sum_le_sum
  intro q _
  have : q.1.IsPrime := q.2.1
  exact Right.one_le_mul (q.1.ramificationIdx_pos ℤ) (q.1.inertiaDeg_pos ℤ)

def rationalPrimeBelow (q : HeightOneSpectrum (𝓞 K)) : RationalPrime :=
  ⟨(q.asIdeal.under ℤ).absNorm, Nat.absNorm_under_prime q.asIdeal⟩

def primeOverBelow (q : HeightOneSpectrum (𝓞 K)) : Above K (rationalPrimeBelow K q) :=
  ⟨q.asIdeal, q.isPrime, Int.liesOver_span_absNorm q.asIdeal⟩

theorem below_pow_degree (q : HeightOneSpectrum (𝓞 K)) :
    (rationalPrimeBelow K q).1 ^ q.asIdeal.inertiaDeg ℤ = q.asIdeal.absNorm := by
  have : q.asIdeal.LiesOver (Ideal.span {((rationalPrimeBelow K q).1 : ℤ)}) :=
    Int.liesOver_span_absNorm q.asIdeal
  exact Ideal.pow_inertiaDeg _ _


/-- The uniform majorant is summable on all prime ideals, indexed by the prime below. -/
theorem summable_prime_majorant :
    Summable (fun z : (p : RationalPrime) × Above K p => (z.1.1 : ℝ)⁻¹ ^ 2) := by
  apply (summable_sigma_of_nonneg (fun _ => by positivity)).mpr
  constructor
  · intro p
    exact Summable.of_finite
  · have hs : Summable (fun p : RationalPrime => (p.1 : ℝ)⁻¹ ^ 2) := by
      simpa only [inv_pow, Function.comp_def] using
        (Real.summable_nat_pow_inv.mpr (by norm_num : 1 < 2)).subtype Nat.Prime
    apply Summable.of_nonneg_of_le (fun _ => by positivity) _
      (hs.mul_left (Module.finrank ℚ K : ℝ))
    intro p
    rw [tsum_fintype]
    simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    exact mul_le_mul_of_nonneg_right (by exact_mod_cast card_above_le K p) (by positivity)

/-- The canonical prime-under map together with the prime itself loses no information. -/
theorem prime_encoding_injective : Function.Injective
    (fun q : HeightOneSpectrum (𝓞 K) =>
      (⟨rationalPrimeBelow K q, primeOverBelow K q⟩ : (p : RationalPrime) × Above K p)) := by
  intro q r h
  have h' := congrArg (fun z : (p : RationalPrime) × Above K p => z.2.1) h
  exact HeightOneSpectrum.ext h'

/-- Reciprocal squared rational primes form a summable majorant on actual prime ideals. -/
theorem summable_below_sq :
    Summable (fun q : HeightOneSpectrum (𝓞 K) => ((rationalPrimeBelow K q).1 : ℝ)⁻¹ ^ 2) := by
  have h := (summable_prime_majorant K).comp_injective (prime_encoding_injective K)
  exact h

/-- The norm formula gives the reciprocal-square estimate at each higher-degree prime. -/
theorem reciprocal_le_below_sq (q : HeightOneSpectrum (𝓞 K))
    (hq : 2 ≤ q.asIdeal.inertiaDeg ℤ) :
    (q.asIdeal.absNorm : ℝ)⁻¹ ≤ ((rationalPrimeBelow K q).1 : ℝ)⁻¹ ^ 2 := by
  rw [← below_pow_degree K q, Nat.cast_pow, inv_pow]
  have hp : 0 < ((rationalPrimeBelow K q).1 : ℝ) :=
    by exact_mod_cast (rationalPrimeBelow K q).2.pos
  apply inv_anti₀ (pow_pos hp 2)
  exact pow_le_pow_right₀ (by exact_mod_cast (rationalPrimeBelow K q).2.one_lt.le) hq

/-- Prime ideals of absolute residue degree at least two have summable reciprocal norms. -/
theorem summable_high_degree :
    Summable (fun q : {q : HeightOneSpectrum (𝓞 K) // 2 ≤ q.asIdeal.inertiaDeg ℤ} =>
      (q.1.asIdeal.absNorm : ℝ)⁻¹) := by
  apply Summable.of_nonneg_of_le (fun _ => by positivity) _
    ((summable_below_sq K).subtype (fun q => 2 ≤ q.asIdeal.inertiaDeg ℤ))
  exact fun q => reciprocal_le_below_sq K q.1 q.2

/-- Explicit global bound for the rational-prime majorant. -/
theorem tsum_prime_majorant_le :
    (∑' z : (p : RationalPrime) × Above K p, (z.1.1 : ℝ)⁻¹ ^ 2) ≤
      (Module.finrank ℚ K : ℝ) * ∑' p : RationalPrime, (p.1 : ℝ)⁻¹ ^ 2 := by
  have hs : Summable (fun p : RationalPrime => (p.1 : ℝ)⁻¹ ^ 2) := by
    simpa only [inv_pow, Function.comp_def] using
      (Real.summable_nat_pow_inv.mpr (by norm_num : 1 < 2)).subtype Nat.Prime
  rw [(summable_prime_majorant K).tsum_sigma, ← tsum_mul_left]
  apply Summable.tsum_le_tsum _ (summable_prime_majorant K).sigma
    (hs.mul_left (Module.finrank ℚ K : ℝ))
  intro p
  rw [tsum_fintype]
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  exact mul_le_mul_of_nonneg_right (by exact_mod_cast card_above_le K p) (by positivity)

/-- The higher-degree reciprocal sum is bounded by degree times the prime square series. -/
theorem tsum_high_degree_le :
    (∑' q : {q : HeightOneSpectrum (𝓞 K) // 2 ≤ q.asIdeal.inertiaDeg ℤ},
      (q.1.asIdeal.absNorm : ℝ)⁻¹) ≤
      (Module.finrank ℚ K : ℝ) * ∑' p : RationalPrime, (p.1 : ℝ)⁻¹ ^ 2 := by
  let e (q : {q : HeightOneSpectrum (𝓞 K) // 2 ≤ q.asIdeal.inertiaDeg ℤ}) :
      (p : RationalPrime) × Above K p := ⟨rationalPrimeBelow K q.1, primeOverBelow K q.1⟩
  have he : Function.Injective e := (prime_encoding_injective K).comp Subtype.val_injective
  have hsum := (summable_prime_majorant K).comp_injective he
  have hbound := tsum_comp_le_tsum_of_inj (summable_prime_majorant K) (fun _ => by positivity) he
  apply le_trans _ (hbound.trans (tsum_prime_majorant_le K))
  exact Summable.tsum_le_tsum (fun q => reciprocal_le_below_sq K q.1 q.2)
    (summable_high_degree K) hsum

/-- Divergence forces an absolute degree-one prime outside each finite exclusion. -/
theorem exists_degree_one_outside_finite
    (S : Set (HeightOneSpectrum (𝓞 K)))
    (hS : ¬ Summable (fun q : S => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ∃ q : HeightOneSpectrum (𝓞 K), q ∈ S ∧ q ∉ bad ∧ q.asIdeal.inertiaDeg ℤ = 1 := by
  classical
  by_contra h
  have hdegree (q : S) (hq : q.1 ∉ bad) : 2 ≤ q.1.asIdeal.inertiaDeg ℤ := by
    have hpos := q.1.asIdeal.inertiaDeg_pos ℤ
    have hne : q.1.asIdeal.inertiaDeg ℤ ≠ 1 := fun he => h ⟨q.1, q.2, hq, he⟩
    omega
  let B : Set S := Subtype.val ⁻¹' bad
  have hB : B.Finite := hbad.preimage Subtype.val_injective.injOn
  have hs : Summable (fun q : ↥(Bᶜ) => (q.1.1.asIdeal.absNorm : ℝ)⁻¹) := by
    let e : ↥(Bᶜ) → {q : HeightOneSpectrum (𝓞 K) // 2 ≤ q.asIdeal.inertiaDeg ℤ} :=
      fun q => ⟨q.1.1, hdegree q.1 q.2⟩
    have he : Function.Injective e := by
      intro x y hxy
      have hh := congrArg
        (fun z : {q : HeightOneSpectrum (𝓞 K) // 2 ≤ q.asIdeal.inertiaDeg ℤ} => z.1) hxy
      exact Subtype.ext (Subtype.ext hh)
    have hs := (summable_high_degree K).comp_injective he
    exact hs
  exact hS (hB.summable_compl_iff.mp hs)

/-- Infinitely many degree-one primes remain after every finite exclusion. -/
theorem infinite_degree_one_outside_finite
    (S : Set (HeightOneSpectrum (𝓞 K)))
    (hS : ¬ Summable (fun q : S => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    {q | q ∈ S ∧ q ∉ bad ∧ q.asIdeal.inertiaDeg ℤ = 1}.Infinite := by
  intro hf
  obtain ⟨q, hq, hn, hd⟩ := exists_degree_one_outside_finite K S hS
    (bad ∪ {q | q ∈ S ∧ q ∉ bad ∧ q.asIdeal.inertiaDeg ℤ = 1}) (hbad.union hf)
  have hb : q ∉ bad := fun hb => hn (Or.inl hb)
  exact hn (Or.inr ⟨hq, hb, hd⟩)

end PaperX.PrimeDegreeSummability
