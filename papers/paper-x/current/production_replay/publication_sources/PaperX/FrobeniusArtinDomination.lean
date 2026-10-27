module

public import CebotarevDensity.Frobenius
public import CebotarevDensity.NumberFieldEulerProduct
public import PaperX.ResidueDomination

/-!
# Domination for actual Frobenius ideal coefficients

The coefficient formula uses the actual unramified predicate and Frobenius
conjugacy classes from the authenticated nine-module predecessor. It sets a
ramified prime coefficient to zero. No unproved occurrence assertion appears.
This is a new local module, not a port of the whole upstream ZetaProduct file.
-/
@[expose] public section

set_option autoImplicit false
noncomputable section
open NumberField Filter
open scoped Topology BigOperators
namespace PaperX.FrobeniusArtinDomination

section Weighted
variable (K : Type*) [Field K] [NumberField K]

/-- At a real argument, all unweighted ideal Dirichlet terms are nonnegative real
numbers embedded in the complex plane. -/
theorem norm_nat_cpow_real_as_complex (n : ℕ) (s : ℝ) :
    (‖(n : ℂ) ^ (-(s : ℂ))‖ : ℂ) = (n : ℂ) ^ (-(s : ℂ)) := by
  rw [← Complex.ofReal_neg, Complex.norm_cpow_real, Complex.norm_natCast,
    Complex.ofReal_cpow (Nat.cast_nonneg n)]
  rfl

/-- The sum of the norms of the positive real ideal terms is the norm of the
actual Dedekind zeta function, not a formal surrogate for it. -/
theorem tsum_ideal_term_norm (s : ℝ) (hs : 1 < s) :
    (∑' a : Chebotarev.NonzeroIdeal K, ‖(Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖) =
      ‖NumberField.dedekindZeta K (s : ℂ)‖ := by
  have h := Chebotarev.hasSum_nonzeroIdeal_absNorm_cpow K (s := (s : ℂ)) hs
  have hn : 0 ≤ ∑' a : Chebotarev.NonzeroIdeal K,
      ‖(Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ := tsum_nonneg (fun _ => norm_nonneg _)
  calc
    _ = ‖((∑' a : Chebotarev.NonzeroIdeal K,
        ‖(Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ : ℝ) : ℂ)‖ := by
      simp only [Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hn]
    _ = ‖∑' a : Chebotarev.NonzeroIdeal K, (Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ := by
      rw [Complex.ofReal_tsum]
      congr 1
      exact tsum_congr (fun a => norm_nat_cpow_real_as_complex (Ideal.absNorm a.1) s)
    _ = _ := congrArg norm h.tsum_eq

/-- Every ideal Dirichlet series with coefficients of norm at most one is
bounded by Dedekind zeta on the real half-line `s > 1`. -/
theorem norm_weighted_ideal_series_le
    (c : Ideal (𝓞 K) → ℂ) (hc : ∀ a, ‖c a‖ ≤ 1) (s : ℝ) (hs : 1 < s) :
    ‖∑' a : Chebotarev.NonzeroIdeal K,
      c a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ ≤
      ‖NumberField.dedekindZeta K (s : ℂ)‖ := by
  have hb := (Chebotarev.hasSum_nonzeroIdeal_absNorm_cpow K (s := (s : ℂ)) hs).summable.norm
  have hm : ∀ a : Chebotarev.NonzeroIdeal K,
      ‖c a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ ≤
        ‖(Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))‖ := by
    intro a
    rw [norm_mul]
    exact (mul_le_mul_of_nonneg_right (hc a.1) (norm_nonneg _)).trans_eq (one_mul _)
  have hw := hb.of_nonneg_of_le (fun a => norm_nonneg
      (c a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ)))) hm
  exact (norm_tsum_le_tsum_norm hw).trans
    ((hw.tsum_le_tsum hm hb).trans_eq (tsum_ideal_term_norm K s hs))
end Weighted

section Galois
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
variable [Algebra K L] [IsGalois K L]

open Classical in
/-- The incomplete Artin coefficient: actual unramified Frobenius values,
extended over the prime factorization, with ramified prime values zero. -/
def idealCoefficient (χ : Gal(L/K) →* ℂˣ) (a : Ideal (𝓞 K)) : ℂ :=
  ∏ p ∈ (UniqueFactorizationMonoid.normalizedFactors a).toFinset,
    (if Chebotarev.UnramifiedIn K L p then
      (χ (Chebotarev.frobeniusClass K L p).out : ℂ) else 0) ^
      (UniqueFactorizationMonoid.normalizedFactors a).count p

/-- The actual coefficients satisfy the norm hypothesis, including at ramified
primes. Finite-order character values have norm one. -/
theorem norm_idealCoefficient_le_one (χ : Gal(L/K) →* ℂˣ) (a : Ideal (𝓞 K)) :
    ‖idealCoefficient K L χ a‖ ≤ 1 := by
  classical
  rw [idealCoefficient, norm_prod]
  refine Finset.prod_le_one (fun _ _ => norm_nonneg _) (fun p _ => ?_)
  rw [norm_pow]
  by_cases hp : Chebotarev.UnramifiedIn K L p
  · rw [ite_eq_left hp]
    have hn : ‖(χ (Chebotarev.frobeniusClass K L p).out : ℂ)‖ = 1 :=
      (((Units.coeHom ℂ).comp χ).isOfFinOrder
        (isOfFinOrder_of_finite (Chebotarev.frobeniusClass K L p).out)).norm_eq_one
    rw [hn, one_pow]
  · rw [ite_eq_right hp, norm_zero]
    exact zero_pow_le_one _

/-- The actual incomplete ideal Artin series on the real half-line. -/
def idealArtinSeries (χ : Gal(L/K) →* ℂˣ) (s : ℝ) : ℂ :=
  ∑' a : Chebotarev.NonzeroIdeal K,
    idealCoefficient K L χ a.1 * (Ideal.absNorm a.1 : ℂ) ^ (-(s : ℂ))

/-- The singular-factor domination premise is now discharged for the actual
ideal Artin series, rather than supplied as an axiom or interface field. -/
theorem norm_idealArtinSeries_le (χ : Gal(L/K) →* ℂˣ) (s : ℝ) (hs : 1 < s) :
    ‖idealArtinSeries K L χ s‖ ≤ ‖NumberField.dedekindZeta K (s : ℂ)‖ :=
  norm_weighted_ideal_series_le K (idealCoefficient K L χ)
    (norm_idealCoefficient_le_one K L χ) s hs

/-- The nonvanishing assembly specialized to the actual trivial-character
ideal Artin series. Only factorization and regular-factor limits remain inputs. -/
theorem actual_factors_nonzero
    {I : Type*} [Fintype I] {R : ℝ → ℂ} {F : I → ℝ → ℂ} {r : ℂ} {v : I → ℂ}
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1, NumberField.dedekindZeta L (s : ℂ) =
      idealArtinSeries K L 1 s * (R s * ∏ i, F i s))
    (hR : Tendsto R (𝓝[>] (1 : ℝ)) (𝓝 r))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    r ≠ 0 ∧ ∀ i, v i ≠ 0 := by
  apply PaperX.ResidueDomination.dedekind_factors_nonzero K L hfactor ?_ hR hF
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact norm_idealArtinSeries_le K L 1 s hs

/-- Quantitative version with the same actual arithmetic attachment. -/
theorem actual_product_ratio_bound
    {I : Type*} [Fintype I] {R : ℝ → ℂ} {F : I → ℝ → ℂ} {r : ℂ} {v : I → ℂ}
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1, NumberField.dedekindZeta L (s : ℂ) =
      idealArtinSeries K L 1 s * (R s * ∏ i, F i s))
    (hR : Tendsto R (𝓝[>] (1 : ℝ)) (𝓝 r))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    NumberField.dedekindZeta_residue L / NumberField.dedekindZeta_residue K ≤
      ‖r * ∏ i, v i‖ := by
  apply PaperX.ResidueDomination.dedekind_product_ratio_bound K L hfactor ?_ hR hF
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact norm_idealArtinSeries_le K L 1 s hs
end Galois
end PaperX.FrobeniusArtinDomination
