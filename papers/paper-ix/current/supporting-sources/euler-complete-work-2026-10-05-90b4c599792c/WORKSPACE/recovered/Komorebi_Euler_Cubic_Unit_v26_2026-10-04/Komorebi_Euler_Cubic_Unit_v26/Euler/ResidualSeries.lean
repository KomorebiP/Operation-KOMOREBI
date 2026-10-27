module
public import Euler.SourceTranslation
public import Euler.ResidualScalars
public import Euler.EulerPackets
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma eulerPacket_natDegree_le (q : ℕ) : (eulerPacket q).natDegree ≤ 2*q := by
  induction q with
  | zero => simp
  | succ q ih =>
    rw [eulerPacket_succ]
    have h1 : (Polynomial.X-Polynomial.C (q:D)).natDegree≤1 := by
      exact (Polynomial.natDegree_sub_le _ _).trans (by simp)
    have h2 : (Polynomial.C (2:D)*Polynomial.X-Polynomial.C ((2*q+1:ℕ):D)).natDegree≤1 := by
      apply (Polynomial.natDegree_sub_le _ _).trans
      apply max_le
      · exact Polynomial.natDegree_mul_le.trans (by simp)
      · rw [Polynomial.natDegree_C]; omega
    calc
      _ ≤ ((eulerPacket q)*(Polynomial.X-Polynomial.C (q:D))).natDegree +
        (Polynomial.C (2:D)*Polynomial.X-Polynomial.C ((2*q+1:ℕ):D)).natDegree :=
        Polynomial.natDegree_mul_le
      _ ≤ ((eulerPacket q).natDegree+(Polynomial.X-Polynomial.C (q:D)).natDegree) +
        (Polynomial.C (2:D)*Polynomial.X-Polynomial.C ((2*q+1:ℕ):D)).natDegree :=
        Nat.add_le_add_right Polynomial.natDegree_mul_le _
      _ ≤ 2*(q+1) := by omega

/-- The qth summand in the integral numerator of the Euler residual. -/
def residualPacketSeries (r q : ℕ) : Series :=
  C (residualNumeratorTap r q) * ((eulerPacket q : Series)*sourceShift (-(q:D)))

lemma residualPacketSeries_restricted (r q : ℕ) : Restricted (residualPacketSeries r q) :=
  PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
    (PowerSeries.isRestricted.mul 1 (polynomial_restricted _) (sourceShift_restricted _))

lemma residualPacketSeries_coeff_uniform (r q n : ℕ) :
    ‖coeff n (residualPacketSeries r q)‖≤(1/8:ℝ)^q := by
  rw [residualPacketSeries,coeff_C_mul,norm_mul]
  exact (mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (residualNumeratorTap_norm r q)

/-- Simultaneous decay in the packet index and Taylor degree. -/
lemma residualPacketSeries_coeff_bound (r q n : ℕ) :
    ‖coeff n (residualPacketSeries r q)‖≤(1/2:ℝ)^(n+q) := by
  rw [residualPacketSeries,coeff_C_mul,coeff_mul,Finset.mul_sum]
  apply IsUltrametricDist.norm_sum_le_of_forall_le_of_nonneg (by positivity)
  rintro ⟨i,j⟩ hij
  have he : i+j=n := Finset.mem_antidiagonal.mp hij
  simp only [Polynomial.coeff_coe]
  by_cases hi : i≤2*q
  · calc
      ‖residualNumeratorTap r q*((eulerPacket q).coeff i*coeff j (sourceShift (-(q:D))))‖
        ≤ (1/8:ℝ)^q*(1/2:ℝ)^j := by
          rw [norm_mul,norm_mul]
          exact mul_le_mul (residualNumeratorTap_norm r q)
            ((mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
              (sourceShift_coeff_norm _ j)) (by positivity) (by positivity)
      _ = (1/2:ℝ)^(3*q+j) := by
        rw [pow_add,pow_mul]
        norm_num
      _ ≤ (1/2:ℝ)^(n+q) := pow_le_pow_of_le_one (by norm_num) (by norm_num) (by omega)
  · have hp : (eulerPacket q).coeff i=0 :=
      Polynomial.coeff_eq_zero_of_natDegree_lt ((eulerPacket_natDegree_le q).trans_lt (by omega))
    rw [hp,zero_mul,mul_zero,norm_zero]
    positivity

lemma residualPacketSeries_summable_coeff (r n : ℕ) :
    Summable (fun q => coeff n (residualPacketSeries r q)) := by
  apply (summable_geometric_of_lt_one (by norm_num : (0:ℝ)≤1/8)
    (by norm_num : (1/8:ℝ)<1)).of_norm_bounded
  exact fun q => residualPacketSeries_coeff_uniform r q n

/-- A real constructed restricted series: J_r = beta_r H_r, with integral coefficients. -/
def eulerResidualNumerator (r : ℕ) : Series :=
  mk fun n => ∑' q, coeff n (residualPacketSeries r q)

@[simp] lemma coeff_eulerResidualNumerator (r n : ℕ) :
    coeff n (eulerResidualNumerator r)=∑' q, coeff n (residualPacketSeries r q) := by
  simp [eulerResidualNumerator]

lemma eulerResidualNumerator_coeff_norm (r n : ℕ) :
    ‖coeff n (eulerResidualNumerator r)‖≤(1/2:ℝ)^n := by
  rw [coeff_eulerResidualNumerator]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro q
  exact (residualPacketSeries_coeff_bound r q n).trans
    (pow_le_pow_of_le_one (by norm_num) (by norm_num) (by omega))

/-- The actual infinite Euler packet sum converges as a Taylor series on all of Z_2. -/
theorem eulerResidualNumerator_restricted (r : ℕ) : Restricted (eulerResidualNumerator r) := by
  rw [restricted_iff]
  apply squeeze_zero (fun _ => norm_nonneg _) (eulerResidualNumerator_coeff_norm r)
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

lemma residualPacketSeries_reval (r q : ℕ) (x : D) :
    reval (residualPacketSeries r q) x =
      residualNumeratorTap r q * (eulerPacket q).eval x * reval eulerSource (x-(q:D)) := by
  rw [residualPacketSeries,reval_C_mul
    (PowerSeries.isRestricted.mul 1 (polynomial_restricted _) (sourceShift_restricted _)),
    reval_mul (polynomial_restricted _) (sourceShift_restricted _),
    reval_polynomial,sourceShift_reval]
  rw [← sub_eq_add_neg]
  ring

lemma residualPacketSeries_double_summable (r : ℕ) (x : D) :
    Summable (fun p : ℕ × ℕ => coeff p.2 (residualPacketSeries r p.1)*x^p.2) := by
  have hg : Summable (fun n:ℕ => (1/2:ℝ)^n) :=
    summable_geometric_of_lt_one (by norm_num) (by norm_num)
  apply (hg.mul_of_nonneg hg (fun _ => by positivity) (fun _ => by positivity)).of_norm_bounded
  rintro ⟨q,n⟩
  calc
    _ ≤ ‖coeff n (residualPacketSeries r q)‖ := by
      rw [norm_mul]
      exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)
    _ ≤ (1/2:ℝ)^(n+q) := residualPacketSeries_coeff_bound r q n
    _ = _ := by rw [pow_add,mul_comm]

/-- Evaluation commutes with the entire packet sum, by a proved double-summability bound. -/
theorem eulerResidualNumerator_reval (r : ℕ) (x : D) :
    reval (eulerResidualNumerator r) x =
      ∑' q, residualNumeratorTap r q * (eulerPacket q).eval x *
        reval eulerSource (x-(q:D)) := by
  unfold reval
  simp_rw [coeff_eulerResidualNumerator]
  have hchange (n:ℕ) :
      (∑' q, coeff n (residualPacketSeries r q))*x^n =
        ∑' q, coeff n (residualPacketSeries r q)*x^n :=
    ((residualPacketSeries_summable_coeff r n).tsum_mul_right (x^n)).symm
  simp_rw [hchange]
  have hd := residualPacketSeries_double_summable r x
  trans ∑' q, ∑' n, coeff n (residualPacketSeries r q)*x^n
  · exact hd.tsum_comm
  · apply tsum_congr
    intro q
    exact residualPacketSeries_reval r q x

/-- Original integer offsets terminate because of packet zeros, with no numerical truncation. -/
theorem eulerResidualNumerator_reval_nat (r n : ℕ) :
    reval (eulerResidualNumerator r) (n:D) =
      ∑ q ∈ Finset.range (n+1), residualNumeratorTap r q * (eulerPacket q).eval (n:D) *
        reval eulerSource ((n:D)-(q:D)) := by
  rw [eulerResidualNumerator_reval]
  apply tsum_eq_sum
  intro q hq
  have hnq : n<q := by
    simp only [Finset.mem_range,not_lt] at hq
    omega
  rw [eulerPacket_eval_nat_zero q n hnq,mul_zero,zero_mul]

end Komorebi.Euler
