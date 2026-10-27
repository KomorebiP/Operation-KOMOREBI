module
public import PaperX.EulerLogBoundary
public import PaperX.ConstructedArtinBoundary

/-! Actual cyclotomic nontrivial-character prime sums have finite complex
right boundary limits. No occurrence or density premise is used. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter Set
open PaperX.ArtinLocalFactors PaperX.ArtinFactorization
open PaperX.FrobeniusArtinDomination
open scoped Topology
namespace PaperX.CyclotomicPrimeBoundary

variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

abbrev UPrime := UnramifiedPrime K L
def primeNorm (p : UPrime K L) : ℕ := Ideal.absNorm p.1
def characterWeight (χ : Character K L) (p : UPrime K L) : ℂ :=
  χ (frobeniusClass K L p.1).out

theorem primeNorm_two_le (p : UPrime K L) : 2 ≤ primeNorm K L p :=
  prime_norm_two_le K ⟨p.1, p.2.1, p.2.2.ne_bot⟩

theorem characterWeight_norm (χ : Character K L) (p : UPrime K L) :
    ‖characterWeight K L χ p‖ = 1 :=
  (((Units.coeHom ℂ).comp χ).isOfFinOrder
    (isOfFinOrder_of_finite (frobeniusClass K L p.1).out)).norm_eq_one

theorem primeNorm_summable (s : ℝ) (hs : 1 < s) :
    Summable (fun p : UPrime K L ↦ (primeNorm K L p : ℝ) ^ (-s)) := by
  let j : UPrime K L → NonzeroIdeal K := fun p ↦ ⟨p.1, p.2.2.ne_bot⟩
  have hj : Function.Injective j := fun _ _ h ↦ Subtype.ext (congrArg (fun x : NonzeroIdeal K ↦ x.1) h)
  have h := (hasSum_nonzeroIdeal_absNorm_cpow K (s := (s : ℂ)) hs).summable.norm.comp_injective hj
  apply h.congr
  intro p
  have hp : 0 < Ideal.absNorm p.1 := lt_of_lt_of_le (by norm_num) (primeNorm_two_le K L p)
  simp [j, primeNorm, Complex.norm_natCast_cpow_of_pos hp]

def twistedPrimeSum (χ : Character K L) (s : ℝ) : ℂ :=
  EulerLogBoundary.primeSum (primeNorm K L) (characterWeight K L χ) s

theorem twistedPrimeSum_summable (χ : Character K L) {s : ℝ} (hs : 1 < s) :
    Summable (fun p : UPrime K L ↦ (χ (frobeniusClass K L p.1).out : ℂ) *
      (Ideal.absNorm p.1 : ℂ) ^ (-(s : ℂ))) :=
  EulerLogBoundary.summable_term (primeNorm K L) (characterWeight K L χ)
    (primeNorm_two_le K L) (characterWeight_norm K L χ) (primeNorm_summable K L) hs

theorem cyclotomic_twisted_prime_boundary (m : ℕ) [NeZero m]
    [IsCyclotomicExtension {m} K L] (χ : Character K L) (hχ : χ ≠ 1) :
    ∃ w : ℂ, Tendsto (twistedPrimeSum K L χ) (𝓝[>] 1) (𝓝 w) := by
  obtain ⟨v, hv, hlimit⟩ :=
    PaperX.ConstructedArtinBoundary.cyclotomic_artin_boundary_nonzero K L m χ hχ
  apply EulerLogBoundary.primeSum_boundary_of_euler_boundary (primeNorm K L)
    (characterWeight K L χ) (primeNorm_two_le K L) (characterWeight_norm K L χ)
    (primeNorm_summable K L) hv
  apply hlimit.congr'
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact (eulerProduct_eq_series K L χ (s := (s : ℂ)) hs).symm

def normalizer (s : ℝ) : ℝ := primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) s

omit [NumberField L] [IsGalois K L] in
theorem inverse_normalizer_limit :
    Tendsto (fun s ↦ ((normalizer K s)⁻¹ : ℝ)) (𝓝[>] 1) (𝓝 0) :=
  tendsto_inv_atTop_zero.comp (primeIdealZetaSum_univ_tendsto_atTop K)

theorem cyclotomic_twisted_prime_normalized (m : ℕ) [NeZero m]
    [IsCyclotomicExtension {m} K L] (χ : Character K L) (hχ : χ ≠ 1) :
    Tendsto (fun s ↦ twistedPrimeSum K L χ s / (normalizer K s : ℂ))
      (𝓝[>] 1) (𝓝 0) := by
  obtain ⟨w, hw⟩ := cyclotomic_twisted_prime_boundary K L m χ hχ
  have hi : Tendsto (fun s ↦ ((normalizer K s : ℂ))⁻¹) (𝓝[>] 1) (𝓝 0) := by
    simpa [Function.comp_def] using (Complex.continuous_ofReal.tendsto 0).comp (inverse_normalizer_limit K)
  simpa only [div_eq_mul_inv, mul_zero] using hw.mul hi

end PaperX.CyclotomicPrimeBoundary
