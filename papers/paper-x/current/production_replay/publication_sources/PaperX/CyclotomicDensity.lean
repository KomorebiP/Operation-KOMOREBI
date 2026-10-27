module
public import PaperX.CyclotomicFourier

/-! Cyclotomic Frobenius density and finite-set avoidance, with the analytic
boundary inputs constructed rather than assumed. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter Set
open PaperX.ArtinLocalFactors PaperX.CyclotomicPrimeBoundary PaperX.CyclotomicFourier
open scoped Topology
namespace PaperX.CyclotomicDensity
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

/-- Full complex Fourier inversion gives density of each individual Frobenius
class in a cyclotomic extension, for every nonzero modulus. -/
theorem cyclotomic_density (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (σ : Gal(L/K)) :
    HasDirichletDensity (classSet K L σ) ((Nat.card Gal(L/K) : ℝ)⁻¹) := by
  classical
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot K L
    (Set.mem_singleton m) (NeZero.ne m)
  have : IsMulCommutative Gal(L/K) := .of_comm fun a b ↦
    hζ.autToPow_injective (K := K) (by rw [map_mul, map_mul, mul_comm])
  let : Fintype (Character K L) := characterFintype K L
  have hterm : ∀ χ : Character K L,
      Tendsto (fun s ↦ (χ σ : ℂ)⁻¹ * (twistedPrimeSum K L χ s / (normalizer K s : ℂ)))
        (𝓝[>] 1) (𝓝 (if χ = 1 then (1 : ℂ) else 0)) := by
    intro χ
    by_cases hχ : χ = 1
    · subst χ
      simpa using trivial_prime_normalized K L
    · simpa only [ite_eq_right hχ, mul_zero] using
        (cyclotomic_twisted_prime_normalized K L m χ hχ).const_mul (χ σ : ℂ)⁻¹
  have hsum : Tendsto
      (fun s ↦ ∑ χ : Character K L,
        (χ σ : ℂ)⁻¹ * (twistedPrimeSum K L χ s / (normalizer K s : ℂ)))
      (𝓝[>] 1) (𝓝 (1 : ℂ)) := by
    simpa using tendsto_finsetSum (Finset.univ : Finset (Character K L)) (fun χ _ ↦ hterm χ)
  have hcardC : (Nat.card Gal(L/K) : ℂ) ≠ 0 := by exact_mod_cast (Nat.card_pos (α := Gal(L/K))).ne'
  have hscaled := hsum.const_mul ((Nat.card Gal(L/K) : ℂ)⁻¹)
  have hratio : Tendsto
      (fun s ↦ ((primeIdealZetaSum (classSet K L σ) s / normalizer K s : ℝ) : ℂ))
      (𝓝[>] 1) (𝓝 ((Nat.card Gal(L/K) : ℂ)⁻¹)) := by
    apply (show Tendsto _ _ (𝓝 ((Nat.card Gal(L/K) : ℂ)⁻¹)) by
      simpa only [mul_one] using hscaled).congr'
    filter_upwards [self_mem_nhdsWithin] with s hs
    have hfourier := fourier_identity K L σ hs
    rw [Complex.ofReal_div]
    have he : (∑ χ : Character K L,
        (χ σ : ℂ)⁻¹ * (twistedPrimeSum K L χ s / (normalizer K s : ℂ))) =
        (Nat.card Gal(L/K) : ℂ) * (primeIdealZetaSum (classSet K L σ) s : ℂ) /
          (normalizer K s : ℂ) := by
      simp_rw [← mul_div_assoc]
      rw [← Finset.sum_div]
      exact congrArg (· / (normalizer K s : ℂ)) hfourier
    rw [he]
    rw [← mul_div_assoc, ← mul_assoc, inv_mul_cancel₀ hcardC, one_mul]
  have hreal := (Complex.continuous_re.tendsto ((Nat.card Gal(L/K) : ℂ)⁻¹)).comp hratio
  simpa [HasDirichletDensity, Function.comp_def, normalizer, ← Complex.ofReal_inv,
    ← Complex.ofReal_natCast] using hreal

/-- Positive cyclotomic density gives infinitely many actual prime ideals. -/
theorem cyclotomic_frobenius_infinite (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (σ : Gal(L/K)) : (classSet K L σ).Infinite := by
  intro hfin
  have hd := cyclotomic_density K L m σ
  have hz := hasDirichletDensity_of_finite K hfin
  have he : (Nat.card Gal(L/K) : ℝ)⁻¹ = 0 := tendsto_nhds_unique hd hz
  have hpos : 0 < (Nat.card Gal(L/K) : ℝ)⁻¹ := inv_pos.mpr (by exact_mod_cast Nat.card_pos (α := Gal(L/K)))
  exact hpos.ne' he

/-- Occurrence outside any finite forbidden set, restricted to the constructed
cyclotomic extension. No density or boundary-limit premise is supplied. -/
theorem cyclotomic_frobenius_avoids (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (σ : Gal(L/K)) (B : Finset (Ideal (𝓞 K))) :
    ∃ p : Ideal (𝓞 K), p ∉ B ∧ p.IsPrime ∧ UnramifiedIn K L p ∧
      frobeniusClass K L p = ConjClasses.mk σ := by
  obtain ⟨p, hp, hn⟩ := (cyclotomic_frobenius_infinite K L m σ).exists_notMem_finset B
  exact ⟨p, hn, hp⟩

end PaperX.CyclotomicDensity
