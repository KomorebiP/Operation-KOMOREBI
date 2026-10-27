/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.DerivativeGrowth
import KomorebiPaperIV.BranchedDirichlet

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- Exactly the simple zeros: possible multiple exceptional zeros are omitted,
as specified by the manuscript's definition. -/
abbrev SimpleZeros (f : ℂ → ℂ) := {z : ℂ // f z = 0 ∧ deriv f z ≠ 0}

def SimpleZeros.toZero {f : ℂ → ℂ} (z : SimpleZeros f) : {z : ℂ // f z = 0} :=
  ⟨z.val, z.property.1⟩

theorem SimpleZeros.toZero_injective (f : ℂ → ℂ) :
    Function.Injective (SimpleZeros.toZero (f := f)) := by
  intro a b h
  exact Subtype.ext (congrArg (fun z : {z : ℂ // f z = 0} => z.val) h)

theorem SimpleZeros.order_one {f : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z) (z : SimpleZeros f) :
    analyticOrderNatAt f z.val = 1 := by
  rw [analyticOrderNatAt, (hf z.val).analyticOrderAt_eq_one_of_zero_deriv_ne_zero
    z.property.1 z.property.2]
  rfl

theorem canonicalSignedDenominator_simple_zero_power_summable {N : ℕ} (hN : 2 ≤ N)
    {t : ℝ} (ht : 1 < t) :
    Summable (fun z : SimpleZeros (canonicalSignedDenominator N) => 1 / ‖z.val‖ ^ t) := by
  have h := (canonicalSignedDenominator_zero_power_summable_iff hN t).mpr ht
  have hi := h.comp_injective (SimpleZeros.toZero_injective (canonicalSignedDenominator N))
  change Summable (fun z : SimpleZeros (canonicalSignedDenominator N) =>
    (analyticOrderNatAt (canonicalSignedDenominator N) z.val : ℝ) / ‖z.val‖ ^ t) at hi
  convert hi using 1
  funext z
  rw [SimpleZeros.order_one (f := canonicalSignedDenominator N)
    (fun w => analyticAt_entireSigned N 0 _ _ w) z, Nat.cast_one]

theorem simple_logarithm_re {f : ℂ → ℂ} (L : SimpleZeros f → ℂ)
    (hL : ∀ z, Complex.exp (L z) = z.val) (z : SimpleZeros f) :
    (L z).re = Real.log ‖z.val‖ := by
  have h := congrArg norm (hL z)
  rw [Complex.norm_exp] at h
  rw [← h, Real.log_exp]

def derivativeZeroWeight (N q : ℕ) (z : SimpleZeros (canonicalSignedDenominator N)) : ℂ :=
  (deriv (canonicalSignedDenominator N) z.val ^ q)⁻¹

theorem derivativeZeroWeight_norm (N q : ℕ) (z : SimpleZeros (canonicalSignedDenominator N)) :
    ‖derivativeZeroWeight N q z‖ = 1 / ‖deriv (canonicalSignedDenominator N) z.val‖ ^ q := by
  simp only [derivativeZeroWeight, norm_inv, norm_pow, one_div]

/-- Every real polynomial weight is summable against the derivative decay,
including the finite exceptional simple zeros. -/
theorem derivativeZeroWeight_power_summable {N q : ℕ} (hN : 3 ≤ N) (hq : 0 < q) (t : ℝ) :
    Summable (fun z : SimpleZeros (canonicalSignedDenominator N) =>
      ‖derivativeZeroWeight N q z‖ / ‖z.val‖ ^ t) := by
  have hs := canonicalSignedDenominator_simple_zero_power_summable (show 2 ≤ N by omega)
    (show (1 : ℝ) < 2 by norm_num)
  apply hs.of_norm_bounded_eventually
  obtain ⟨R, _, hR⟩ := canonicalSignedDenominator_derivative_power_bound hN hq t
  have hf : ((fun z : SimpleZeros (canonicalSignedDenominator N) => z.val) ⁻¹'
      zeroDisk (canonicalSignedDenominator N) R).Finite :=
    (canonicalSignedDenominator_zeroDisk_finite (show 0 < N by omega) R).preimage
      Subtype.val_injective.injOn
  have hb : ∀ᶠ z : SimpleZeros (canonicalSignedDenominator N) in cofinite, R ≤ ‖z.val‖ := by
    apply eventually_cofinite.mpr
    apply hf.subset
    intro z hz
    exact ⟨(not_le.mp hz).le, z.property.1⟩
  filter_upwards [hb] with z hz
  rw [Real.norm_eq_abs, abs_of_nonneg (by positivity), derivativeZeroWeight_norm]
  exact hR z.val hz z.property.1

theorem canonicalSignedDenominator_two_derivative_norm {z : ℂ}
    (hz : canonicalSignedDenominator 2 z = 0) : ‖deriv (canonicalSignedDenominator 2) z‖ = 1 := by
  have he : canonicalSignedDenominator 2 = Complex.cos := funext
    (entireSigned_two_eq_cos (canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 2))
      (canonicalSignedRoot_pow (by norm_num : 0 < 2)))
  rw [he, Complex.deriv_cos, norm_neg]
  rw [he] at hz
  have hs := Complex.sin_sq_add_cos_sq z
  rw [hz, zero_pow (by norm_num : (2 : ℕ) ≠ 0), add_zero] at hs
  have hn := congrArg norm hs
  rw [norm_pow, norm_one] at hn
  nlinarith [norm_nonneg (Complex.sin z)]

theorem derivativeZeroWeight_two_power_summable (q : ℕ) {t : ℝ} (ht : 1 < t) :
    Summable (fun z : SimpleZeros (canonicalSignedDenominator 2) =>
      ‖derivativeZeroWeight 2 q z‖ / ‖z.val‖ ^ t) := by
  convert canonicalSignedDenominator_simple_zero_power_summable (by norm_num : 2 ≤ 2) ht using 1
  funext z
  simp only [derivativeZeroWeight_norm, canonicalSignedDenominator_two_derivative_norm z.property.1,
    one_pow, div_one]

def derivativeWeightedZeroZetaTerm (N q : ℕ)
    (L : SimpleZeros (canonicalSignedDenominator N) → ℂ)
    (z : SimpleZeros (canonicalSignedDenominator N)) (s : ℂ) : ℂ :=
  branchedDirichletTerm (derivativeZeroWeight N q) L z s

def derivativeWeightedZeroZeta (N q : ℕ)
    (L : SimpleZeros (canonicalSignedDenominator N) → ℂ) (s : ℂ) : ℂ :=
  ∑' z, derivativeWeightedZeroZetaTerm N q L z s

theorem derivativeWeightedZeroZetaTerm_eq (N q : ℕ)
    (L : SimpleZeros (canonicalSignedDenominator N) → ℂ)
    (z : SimpleZeros (canonicalSignedDenominator N)) (s : ℂ) :
    derivativeWeightedZeroZetaTerm N q L z s =
      Complex.exp (-s * L z) / deriv (canonicalSignedDenominator N) z.val ^ q := by
  unfold derivativeWeightedZeroZetaTerm branchedDirichletTerm derivativeZeroWeight
  ring

theorem derivativeWeightedZeroZeta_summable_norm {N q : ℕ} (hN : 3 ≤ N) (hq : 0 < q)
    (L : SimpleZeros (canonicalSignedDenominator N) → ℂ)
    (hL : ∀ z, Complex.exp (L z) = z.val)
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ z, |(L z).im| ≤ B) (s : ℂ) :
    Summable (fun z => ‖derivativeWeightedZeroZetaTerm N q L z s‖) := by
  apply branchedDirichlet_summable_norm (derivativeZeroWeight N q) L (fun z => ‖z.val‖)
    _ (simple_logarithm_re L hL) hB harg s (derivativeZeroWeight_power_summable hN hq s.re)
  intro z
  exact zero_norm_pos_of_value_at_zero
    (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero) z.toZero

theorem derivativeWeightedZeroZeta_two_summable_norm (q : ℕ)
    (L : SimpleZeros (canonicalSignedDenominator 2) → ℂ)
    (hL : ∀ z, Complex.exp (L z) = z.val)
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ z, |(L z).im| ≤ B) {s : ℂ} (hs : 1 < s.re) :
    Summable (fun z => ‖derivativeWeightedZeroZetaTerm 2 q L z s‖) := by
  apply branchedDirichlet_summable_norm (derivativeZeroWeight 2 q) L (fun z => ‖z.val‖)
    _ (simple_logarithm_re L hL) hB harg s (derivativeZeroWeight_two_power_summable q hs)
  intro z
  exact zero_norm_pos_of_value_at_zero
    (by rw [canonicalSignedDenominator_zero (by norm_num : 0 < 2)]; exact one_ne_zero) z.toZero

/-- Paper IV 14.8, N≥3: the actual derivative-weighted series is locally
uniformly convergent on the whole plane and has an entire sum. -/
theorem derivativeWeightedZeroZeta_entire {N q : ℕ} (hN : 3 ≤ N) (hq : 0 < q)
    (L : SimpleZeros (canonicalSignedDenominator N) → ℂ)
    (hL : ∀ z, Complex.exp (L z) = z.val)
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ z, |(L z).im| ≤ B) :
    HasSumLocallyUniformlyOn (derivativeWeightedZeroZetaTerm N q L)
      (derivativeWeightedZeroZeta N q L) univ ∧
    Differentiable ℂ (derivativeWeightedZeroZeta N q L) := by
  apply branchedDirichlet_entire (derivativeZeroWeight N q) L (fun z => ‖z.val‖)
    _ (simple_logarithm_re L hL) hB harg (derivativeZeroWeight_power_summable hN hq)
  intro z
  exact zero_norm_pos_of_value_at_zero
    (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero) z.toZero

/-- Paper IV 14.8, N=2: local uniform convergence and holomorphy on Re(s)>1,
with arbitrary bounded logarithmic arguments. -/
theorem derivativeWeightedZeroZeta_two_holomorphic (q : ℕ)
    (L : SimpleZeros (canonicalSignedDenominator 2) → ℂ)
    (hL : ∀ z, Complex.exp (L z) = z.val)
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ z, |(L z).im| ≤ B) :
    HasSumLocallyUniformlyOn (derivativeWeightedZeroZetaTerm 2 q L)
      (derivativeWeightedZeroZeta 2 q L) {s : ℂ | 1 < s.re} ∧
    DifferentiableOn ℂ (derivativeWeightedZeroZeta 2 q L) {s : ℂ | 1 < s.re} := by
  apply branchedDirichlet_halfplane (derivativeZeroWeight 2 q) L (fun z => ‖z.val‖)
    _ (simple_logarithm_re L hL) hB harg 1 (fun t ht => derivativeZeroWeight_two_power_summable q ht)
  intro z
  exact zero_norm_pos_of_value_at_zero
    (by rw [canonicalSignedDenominator_zero (by norm_num : 0 < 2)]; exact one_ne_zero) z.toZero

end
end Komorebi.PaperIV
