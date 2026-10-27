module
public import Euler.EulerSource
public import Mathlib.Analysis.Normed.Group.Tannery
@[expose] public section
noncomputable section
set_option maxHeartbeats 800000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma norm_two : ‖(2:D)‖=(1/2:ℝ) := by
  have h := PadicInt.norm_p (p:=2)
  norm_num at h ⊢
  exact h

lemma norm_two_weight (w : ℕ → D) (n : ℕ) :
    ‖(2:D)^n*w n‖≤(1/2:ℝ)^n := by
  rw [norm_mul,norm_pow,norm_two]
  exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

lemma summable_two_weight (w : ℕ → D) : Summable (fun n => (2:D)^n*w n) := by
  exact (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/2)
    (by norm_num : (1/2:ℝ)<1)).of_norm_bounded (norm_two_weight w)

lemma restricted_rescale_two (f : Series) : Restricted (rescale (2:D) f) := by
  rw [restricted_iff]
  simp only [coeff_rescale]
  apply squeeze_zero (fun _ => norm_nonneg _) (norm_two_weight (fun n => coeff n f))
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

/-- Integral coefficients after a translation of a geometrically weighted series. -/
def translatedTwoWeight (w : ℕ → D) (a : D) (n : ℕ) : D :=
  ∑' m, (2:D)^m * ((n+m).choose n:D) * w (n+m) * a^m

/-- This defines translation through convergent coefficient sums, not formal substitution
at a nonzero constant. -/
def translatedTwoSeries (w : ℕ → D) (a : D) : Series :=
  rescale (2:D) (mk (translatedTwoWeight w a))

@[simp] lemma coeff_translatedTwoSeries (w : ℕ → D) (a : D) (n : ℕ) :
    coeff n (translatedTwoSeries w a) = (2:D)^n * translatedTwoWeight w a n := by
  simp [translatedTwoSeries]

lemma translatedTwoSeries_restricted (w : ℕ → D) (a : D) :
    Restricted (translatedTwoSeries w a) := restricted_rescale_two _

lemma summable_translation_double (w : ℕ → D) (a x : D) :
    Summable (fun p : ℕ × ℕ =>
      (2:D)^(p.1+p.2)*((p.1+p.2).choose p.1:D)*w (p.1+p.2)*x^p.1*a^p.2) := by
  have hg : Summable (fun n : ℕ => (1/2:ℝ)^n) :=
    summable_geometric_of_lt_one (by norm_num) (by norm_num)
  apply (hg.mul_of_nonneg hg (fun _ => by positivity) (fun _ => by positivity)).of_norm_bounded
  rintro ⟨n,m⟩
  calc
    _ = ‖(2:D)^(n+m) * (((n+m).choose n:D)*w (n+m)*x^n*a^m)‖ := by congr 1; ring
    _ ≤ (1/2:ℝ)^(n+m) := norm_two_weight (fun _ => _) (n+m)
    _ = _ := pow_add _ _ _

/-- General diagonal regrouping used to justify the translated infinite binomial sum. -/
lemma tsum_antidiagonal_of_summable {f : ℕ × ℕ → D} (hf : Summable f) :
    (∑' p, f p) = ∑' n, ∑ p ∈ Finset.antidiagonal n, f p := by
  let e := (Finset.HasAntidiagonal.sigmaAntidiagonalEquivProd :
    (Σ n:ℕ, ↥(Finset.antidiagonal n)) ≃ ℕ × ℕ)
  rw [← e.tsum_eq f]
  have hs : Summable (fun p : Σ n:ℕ, ↥(Finset.antidiagonal n) => f (e p)) := e.summable_iff.mpr hf
  rw [hs.tsum_sigma' (fun _ => (hasSum_fintype _).summable)]
  apply tsum_congr
  intro n
  rw [tsum_fintype]
  change (∑ b : ↥(Finset.antidiagonal n), f b.val) = _
  exact Finset.sum_coe_sort (Finset.antidiagonal n) f

/-- Translation is compatible with actual analytic evaluation on the entire dyadic disc. -/
theorem translatedTwoSeries_reval (w : ℕ → D) (a x : D) :
    reval (translatedTwoSeries w a) x = reval (rescale (2:D) (mk w)) (x+a) := by
  let f : ℕ × ℕ → D := fun p =>
    (2:D)^(p.1+p.2)*((p.1+p.2).choose p.1:D)*w (p.1+p.2)*x^p.1*a^p.2
  have hf : Summable f := summable_translation_double w a x
  have hh (n : ℕ) :
      coeff n (translatedTwoSeries w a)*x^n = ∑' m, f (n,m) := by
    rw [coeff_translatedTwoSeries,translatedTwoWeight]
    have hs := summable_two_weight (fun m => ((n+m).choose n:D)*w (n+m)*a^m)
    simp only [← mul_assoc] at hs
    rw [← hs.tsum_mul_left ((2:D)^n), ← (hs.mul_left ((2:D)^n)).tsum_mul_right (x^n)]
    apply tsum_congr
    intro m
    dsimp [f]
    rw [pow_add]
    ring
  unfold reval
  simp_rw [hh]
  rw [← hf.tsum_prod,tsum_antidiagonal_of_summable hf]
  apply tsum_congr
  intro n
  simp only [coeff_rescale,coeff_mk]
  have he : ∑ p ∈ Finset.antidiagonal n, f p =
      (2:D)^n*w n*∑ i ∈ Finset.range (n+1), x^i*a^(n-i)*(n.choose i:D) := by
    rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    have hin : i≤n := by simpa only [Finset.mem_range,Nat.lt_succ_iff] using hi
    dsimp [f]
    rw [Nat.add_sub_of_le hin]
    ring
  rw [he,← add_pow]

end Komorebi.Euler
