module
public import Euler.SourceScalars
public import Mathlib.Analysis.Normed.Ring.InfiniteSum
@[expose] public section
noncomputable section
set_option maxHeartbeats 800000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma summable_four_weight (w : ℕ → D) : Summable (fun n => (4:D)^n*w n) := by
  have h := summable_reval (restricted_rescale_four (mk w)) 1
  simpa only [coeff_rescale, coeff_mk, one_pow, mul_one] using h

lemma summable_sourceTap_weight (w : ℕ → D) :
    Summable (fun q => sourceTap q*w q) := by
  simpa only [sourceTap, mul_assoc] using summable_four_weight (fun q => sourceScalar q*w q)

/-- Newton expansion of (9^(x+1)-1)/(8(x+1)), assembled as a true infinite power series. -/
def sourceNumerator : Series := mk fun n =>
  ∑' q, sourceTap q*(descPochhammer D q).coeff n

@[simp] lemma coeff_sourceNumerator (n : ℕ) :
    coeff n sourceNumerator = ∑' q, sourceTap q*(descPochhammer D q).coeff n := by
  simp [sourceNumerator]

lemma sourceNumerator_coeff_four (n : ℕ) :
    coeff n sourceNumerator = (4:D)^n *
      ∑' m, (4:D)^m*(sourceScalar (m+n)*(descPochhammer D (m+n)).coeff n) := by
  rw [coeff_sourceNumerator]
  have hs := summable_sourceTap_weight (fun q => (descPochhammer D q).coeff n)
  have hz : ∑ q ∈ Finset.range n, sourceTap q*(descPochhammer D q).coeff n = 0 := by
    apply Finset.sum_eq_zero
    intro q hq
    rw [Polynomial.coeff_eq_zero_of_natDegree_lt (by simpa using Finset.mem_range.mp hq), mul_zero]
  rw [← hs.sum_add_tsum_nat_add n, hz, zero_add]
  simp_rw [sourceTap, pow_add]
  rw [← (summable_four_weight (fun m => sourceScalar (m+n)*(descPochhammer D (m+n)).coeff n)).tsum_mul_left (4^n)]
  apply tsum_congr
  intro m
  ring

theorem sourceNumerator_restricted : Restricted sourceNumerator := by
  apply restricted_of_four_tail sourceNumerator 0
    (fun n => ∑' m, (4:D)^m*(sourceScalar (m+n)*(descPochhammer D (m+n)).coeff n))
  intro n
  simpa using sourceNumerator_coeff_four n

/-- Absolute summability justifying the Newton/Taylor double-sum interchange. -/
lemma summable_source_double (x : D) :
    Summable (fun p : ℕ × ℕ => sourceTap p.1*(descPochhammer D p.1).coeff p.2*x^p.2) := by
  have hg : Summable (fun n : ℕ => (1/2:ℝ)^n) :=
    summable_geometric_of_lt_one (by norm_num) (by norm_num)
  apply (hg.mul_of_nonneg hg (fun _ => by positivity) (fun _ => by positivity)).of_norm_bounded
  rintro ⟨q,n⟩
  by_cases hn : n ≤ q
  · calc
      ‖sourceTap q*(descPochhammer D q).coeff n*x^n‖
          ≤ ‖sourceTap q‖ := by
            rw [norm_mul, norm_mul]
            exact (mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)).trans
              (mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _))
      _ ≤ (1/4:ℝ)^q := sourceTap_norm_bound q
      _ = (1/2:ℝ)^(q+q) := by rw [pow_add, ← mul_pow]; norm_num
      _ ≤ (1/2:ℝ)^(q+n) := pow_le_pow_of_le_one (by norm_num) (by norm_num) (by omega)
      _ = (1/2:ℝ)^q*(1/2:ℝ)^n := pow_add _ _ _
  · rw [Polynomial.coeff_eq_zero_of_natDegree_lt (by simpa using Nat.lt_of_not_ge hn)]
    simp only [mul_zero, zero_mul, norm_zero]
    positivity

lemma polynomial_eval_tsum (p : Polynomial D) (x : D) :
    (∑' n, p.coeff n*x^n) = p.eval x := by
  rw [tsum_eq_sum (s:=Finset.range (p.natDegree+1))]
  · exact (Polynomial.eval_eq_sum_range x).symm
  · intro n hn
    rw [Polynomial.coeff_eq_zero_of_natDegree_lt (by
      simp only [Finset.mem_range, not_lt] at hn
      omega), zero_mul]

/-- The constructed Taylor series evaluates to the full Newton packet sum. -/
theorem sourceNumerator_reval (x : D) :
    reval sourceNumerator x =
      ∑' q, sourceTap q*(descPochhammer D q).eval x := by
  unfold reval
  simp_rw [coeff_sourceNumerator]
  have hchange (n : ℕ) :
      (∑' q, sourceTap q*(descPochhammer D q).coeff n)*x^n =
      ∑' q, sourceTap q*(descPochhammer D q).coeff n*x^n :=
    ((summable_sourceTap_weight (fun q => (descPochhammer D q).coeff n)).tsum_mul_right (x^n)).symm
  simp_rw [hchange]
  have hd : Summable (Function.uncurry (fun q n : ℕ =>
      sourceTap q*(descPochhammer D q).coeff n*x^n)) := summable_source_double x
  trans ∑' q, ∑' n, sourceTap q*(descPochhammer D q).coeff n*x^n
  · exact hd.tsum_comm
  · apply tsum_congr
    intro q
    have hp : Summable (fun n => (descPochhammer D q).coeff n*x^n) := by
      apply summable_of_ne_finset_zero (s:=Finset.range (q+1))
      intro n hn
      rw [Polynomial.coeff_eq_zero_of_natDegree_lt (by
        simp only [Finset.mem_range, not_lt] at hn
        simpa using (show q<n by omega)), zero_mul]
    simp_rw [mul_assoc]
    rw [hp.tsum_mul_left, polynomial_eval_tsum]

/-- Integer rows terminate for mathematical reasons, not a chosen numeric cutoff. -/
theorem sourceNumerator_reval_nat (n : ℕ) :
    reval sourceNumerator (n:D) =
      ∑ q ∈ Finset.range (n+1), sourceTap q*(descPochhammer D q).eval (n:D) := by
  rw [sourceNumerator_reval]
  apply tsum_eq_sum
  intro q hq
  rw [descPochhammer_eval_coe_nat_of_lt (R:=D) (by
    simp only [Finset.mem_range, not_lt] at hq
    omega), mul_zero]

@[simp] theorem sourceNumerator_const : coeff 0 sourceNumerator=1 := by
  rw [coeff_sourceNumerator, tsum_eq_single 0]
  · simp
  · intro q hq
    have h : (descPochhammer D q).coeff 0=0 := by
      rw [Polynomial.coeff_zero_eq_eval_zero]
      exact descPochhammer_ne_zero_eval_zero D hq
    rw [h,mul_zero]

lemma sourceNumerator_red_coeff (n : ℕ) :
    red (coeff n sourceNumerator) = if n=0 then 1 else 0 := by
  by_cases hn : n=0
  · subst n
    rw [sourceNumerator_const]
    simp
  · rw [sourceNumerator_coeff_four]
    simp [hn]

end Komorebi.Euler
