module
public import Euler.ResidualRecurrence
public import Euler.RestrictedJets
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- Evaluated Hasse jets preserve subtraction of actual restricted series. -/
lemma rjet_sub {f g : Series} (hf : Restricted f) (hg : Restricted g)
    (k : ℕ) (x : D) : rjet k (f-g) x=rjet k f x-rjet k g x := by
  have h : hasseSeries k (f-g)=hasseSeries k f-hasseSeries k g := by
    ext n
    simp only [coeff_hasseSeries,map_sub,mul_sub]
  unfold rjet
  rw [h,reval_sub (restricted_hasseSeries hf k) (restricted_hasseSeries hg k)]

/-- Hasse differentiation introduces integral binomial multipliers and no loss of norm. -/
lemma rjet_norm_le_coeff_bound (f : Series) (k : ℕ) (x : D) (B : ℝ)
    (hb : ∀ n, ‖coeff n f‖≤B) : ‖rjet k f x‖≤B := by
  unfold rjet reval
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [coeff_hasseSeries,norm_mul,norm_mul]
  exact (mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)).trans
    ((mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans (hb _))

lemma residualPacket_hasse_coeff_norm (r q k n : ℕ) :
    ‖coeff n (hasseSeries k (residualPacketSeries r q))‖≤(1/8:ℝ)^q := by
  rw [coeff_hasseSeries,norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (residualPacketSeries_coeff_uniform r q (n+k))

lemma residualPacket_hasse_coeff_decay (r q k n : ℕ) :
    ‖coeff n (hasseSeries k (residualPacketSeries r q))‖≤(1/2:ℝ)^(n+k+q) := by
  rw [coeff_hasseSeries,norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (residualPacketSeries_coeff_bound r q (n+k))

/-- Uniform in BOTH the packet derivative order and the integral argument. -/
lemma residualPacket_rjet_norm (r q k : ℕ) (x : D) :
    ‖rjet k (residualPacketSeries r q) x‖≤(1/8:ℝ)^q :=
  rjet_norm_le_coeff_bound _ k x _ (residualPacketSeries_coeff_uniform r q)

lemma residualPacket_rjet_summable (r k : ℕ) (x : D) :
    Summable (fun q => rjet k (residualPacketSeries r q) x) := by
  exact (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
    (by norm_num : (1/8:ℝ)<1)).of_norm_bounded (residualPacket_rjet_norm r · k x)

/-- The differentiated Taylor/packet double sum is absolutely summable. -/
lemma residualPacket_rjet_double_summable (r k : ℕ) (x : D) :
    Summable (fun p : ℕ×ℕ =>
      (Nat.choose (p.2+k) k:D)*coeff (p.2+k) (residualPacketSeries r p.1)*x^p.2) := by
  have hg : Summable (fun n:ℕ => (1/2:ℝ)^n) :=
    summable_geometric_of_lt_one (by norm_num) (by norm_num)
  apply (hg.mul_of_nonneg hg (fun _ => by positivity) (fun _ => by positivity)).of_norm_bounded
  rintro ⟨q,n⟩
  calc
    _ ≤ ‖coeff n (hasseSeries k (residualPacketSeries r q))‖ := by
      rw [coeff_hasseSeries,norm_mul]
      exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)
    _ ≤ (1/2:ℝ)^(n+k+q) := residualPacket_hasse_coeff_decay r q k n
    _ ≤ (1/2:ℝ)^(n+q) :=
      pow_le_pow_of_le_one (by norm_num) (by norm_num) (by omega)
    _ = _ := by rw [pow_add,mul_comm]

/-- Every evaluated Hasse jet commutes with the ACTUAL infinite Euler packet sum. -/
theorem eulerResidualNumerator_rjet_sum (r k : ℕ) (x : D) :
    rjet k (eulerResidualNumerator r) x=
      ∑' q, rjet k (residualPacketSeries r q) x := by
  unfold rjet reval
  simp_rw [coeff_hasseSeries,coeff_eulerResidualNumerator]
  have hchange (n : ℕ) :
      (Nat.choose (n+k) k:D)*(∑' q, coeff (n+k) (residualPacketSeries r q))*x^n =
        ∑' q, (Nat.choose (n+k) k:D)*coeff (n+k) (residualPacketSeries r q)*x^n := by
    rw [← (residualPacketSeries_summable_coeff r (n+k)).tsum_mul_left]
    exact (((residualPacketSeries_summable_coeff r (n+k)).mul_left _).tsum_mul_right _).symm
  simp_rw [hchange]
  exact (residualPacket_rjet_double_summable r k x).tsum_comm

/-- A finite packet truncation also commutes with every evaluated Hasse jet. -/
lemma residualNumeratorTrunc_rjet (r Q k : ℕ) (x : D) :
    rjet k (residualNumeratorTrunc r Q) x=
      ∑ q ∈ Finset.range Q, rjet k (residualPacketSeries r q) x := by
  classical
  unfold rjet reval
  simp_rw [coeff_hasseSeries,residualNumeratorTrunc_coeff,Finset.mul_sum,Finset.sum_mul]
  rw [Summable.tsum_finsetSum]
  intro q _
  simpa only [coeff_hasseSeries] using
    summable_reval (restricted_hasseSeries (residualPacketSeries_restricted r q) k) x

/-- The tail bound survives arbitrary Hasse differentiation with no extra precision loss. -/
theorem residualNumeratorTrunc_rjet_error_norm (r Q k : ℕ) (x : D) :
    ‖rjet k (eulerResidualNumerator r) x-rjet k (residualNumeratorTrunc r Q) x‖≤
      (1/8:ℝ)^Q := by
  rw [← rjet_sub (eulerResidualNumerator_restricted r) (residualNumeratorTrunc_restricted r Q)]
  exact rjet_norm_le_coeff_bound _ k x _ (residualNumeratorTrunc_error_coeff_norm r Q)

/-- Complete finite packet certificates control every Hasse jet at once. -/
theorem residualNumeratorTrunc_rjet_modulus (r P Q k : ℕ) (hPQ : P≤3*Q) (x : D) :
    redPow P (rjet k (eulerResidualNumerator r) x)=
      redPow P (rjet k (residualNumeratorTrunc r Q) x) := by
  apply redPow_eq_of_norm_sub_le P
  exact (residualNumeratorTrunc_rjet_error_norm r Q k x).trans
    (one_eighth_pow_le_two_zpow P Q hPQ)

end Komorebi.Euler
