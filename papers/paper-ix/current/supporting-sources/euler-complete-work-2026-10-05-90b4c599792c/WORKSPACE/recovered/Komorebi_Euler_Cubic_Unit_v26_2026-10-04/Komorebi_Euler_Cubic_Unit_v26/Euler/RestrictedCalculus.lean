module
public import Euler.RestrictedEvaluation
public import Mathlib.Analysis.Calculus.Deriv.Basic
public import Mathlib.Topology.MetricSpace.Contracting
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open Filter PowerSeries
open scoped Topology

lemma norm_pow_sub_le (x y : D) (n : ℕ) : ‖x^n-y^n‖ ≤ ‖x-y‖ := by
  obtain ⟨u,hu⟩ := sub_dvd_pow_sub_pow x y n
  rw [hu, norm_mul]
  exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)

/-- Integral second-order Taylor remainder for every monomial. -/
lemma pow_succ_second_remainder (n : ℕ) (x y : D) :
    ∃ u : D, y^(n+1)-x^(n+1)-(n+1:D)*x^n*(y-x)=(y-x)^2*u := by
  induction n with
  | zero => exact ⟨0, by simp⟩
  | succ n ih =>
    obtain ⟨u,hu⟩ := ih
    refine ⟨y*u+(n+1:D)*x^n, ?_⟩
    calc
      y^(n+1+1)-x^(n+1+1)-(↑(n+1)+1:D)*x^(n+1)*(y-x)
          = y*(y^(n+1)-x^(n+1)-(n+1:D)*x^n*(y-x))
              +(n+1:D)*x^n*(y-x)^2 := by
                simp only [pow_succ, Nat.cast_add, Nat.cast_one]
                ring
      _ = (y-x)^2*(y*u+(n+1:D)*x^n) := by rw [hu]; ring

lemma norm_pow_second_le (n : ℕ) (x y : D) :
    ‖y^n-x^n-(n:D)*x^(n-1)*(y-x)‖ ≤ ‖y-x‖^2 := by
  cases n with
  | zero => simp
  | succ n =>
    obtain ⟨u,hu⟩ := pow_succ_second_remainder n x y
    simp only [Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one]
    rw [hu, norm_mul, norm_pow]
    exact mul_le_of_le_one_right (sq_nonneg _) (PadicInt.norm_le_one _)

/-- Every integral restricted series is 1-Lipschitz on the closed unit disc. -/
theorem reval_lipschitz {f : PowerSeries D} (hf : Restricted f) (x y : D) :
    ‖reval f x-reval f y‖ ≤ ‖x-y‖ := by
  rw [reval, reval, ← (summable_reval hf x).tsum_sub (summable_reval hf y)]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [← mul_sub, norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (norm_pow_sub_le x y n)

lemma continuous_reval {f : PowerSeries D} (hf : Restricted f) : Continuous (reval f) := by
  have hl : LipschitzWith 1 (reval f) := by
    apply LipschitzWith.of_dist_le_mul
    intro x y
    simpa only [dist_eq_norm, NNReal.coe_one, one_mul] using reval_lipschitz hf x y
  exact hl.continuous

lemma summable_first_jet {f : PowerSeries D} (hf : Restricted f) (x : D) :
    Summable (fun n => coeff n f*((n:D)*x^(n-1))) := summable_weighted hf _

lemma first_jet_tsum {f : PowerSeries D} (hf : Restricted f) (x : D) :
    (∑' n, coeff n f*((n:D)*x^(n-1)))=rjet 1 f x := by
  rw [← (summable_first_jet hf x).sum_add_tsum_nat_add 1]
  simp only [Finset.sum_range_one, Nat.cast_zero, zero_mul, mul_zero, zero_add,
    Nat.add_sub_cancel, Nat.cast_add, Nat.cast_one, rjet, reval, coeff_hasseSeries,
    Nat.choose_one_right]
  apply tsum_congr
  intro n
  ring

/-- Full analytic first-order error: valid on every pair of dyadic arguments. -/
theorem reval_first_order_error {f : PowerSeries D} (hf : Restricted f) (x y : D) :
    ‖reval f y-reval f x-(y-x)*rjet 1 f x‖ ≤ ‖y-x‖^2 := by
  have hsum : HasSum (fun n => coeff n f*(y^n-x^n-(n:D)*x^(n-1)*(y-x)))
      (reval f y-reval f x-(y-x)*rjet 1 f x) := by
    have h1 := (hasSum_reval hf y).sub (hasSum_reval hf x)
    have h2 := (summable_first_jet hf x).hasSum.mul_left (y-x)
    rw [first_jet_tsum hf x] at h2
    convert h1.sub h2 using 1 <;> first | rfl | (ext n; ring)
  rw [← hsum.tsum_eq]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [norm_mul]
  exact (mul_le_of_le_one_left (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (norm_pow_second_le n x y)

/-- On Q_2 the series is used only where the unit-disc summation is proved. -/
def qeval (f : PowerSeries D) (x : ℚ_[2]) : ℚ_[2] :=
  ∑' n, ((coeff n f : D) : ℚ_[2])*x^n

lemma coe_reval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    (reval f x : ℚ_[2])=qeval f (x:ℚ_[2]) := by
  have h := (hasSum_reval hf x).map (PadicInt.Coe.ringHom : D →+* ℚ_[2])
    PadicInt.isOpenEmbedding_coe.continuous
  change HasSum (fun n => ((coeff n f*x^n : D) : ℚ_[2]))
    ((reval f x : D) : ℚ_[2]) at h
  simpa only [PadicInt.coe_mul, PadicInt.coe_pow, qeval] using h.tsum_eq.symm


/-- The evaluated first Hasse coefficient is the GENUINE analytic derivative in Q_2. -/
theorem hasDerivAt_qeval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    HasDerivAt (qeval f) ((rjet 1 f x : D) : ℚ_[2]) (x : ℚ_[2]) := by
  rw [hasDerivAt_iff_tendsto]
  apply squeeze_zero' (Eventually.of_forall (fun y => mul_nonneg (inv_nonneg.mpr (norm_nonneg _)) (norm_nonneg _)))
    (g := fun y : ℚ_[2] => ‖y-(x:ℚ_[2])‖)
  · filter_upwards [Metric.ball_mem_nhds (x:ℚ_[2]) (by norm_num : (0:ℝ)<1)] with y hy
    have hd : ‖y-(x:ℚ_[2])‖<1 := by simpa only [Metric.mem_ball, dist_eq_norm] using hy
    have hunit : ‖y‖≤1 := by
      calc
        ‖y‖ = ‖(y-(x:ℚ_[2]))+(x:ℚ_[2])‖ := by rw [sub_add_cancel]
        _ ≤ max ‖y-(x:ℚ_[2])‖ ‖(x:ℚ_[2])‖ := IsUltrametricDist.norm_add_le_max _ _
        _ ≤ 1 := max_le hd.le x.2
    let yy : D := ⟨y,hunit⟩
    have he := reval_first_order_error hf x yy
    change ‖((reval f yy-reval f x-(yy-x)*rjet 1 f x : D):ℚ_[2])‖ ≤
      ‖((yy-x:D):ℚ_[2])‖^2 at he
    simp only [PadicInt.coe_sub, PadicInt.coe_mul, coe_reval hf] at he
    have hrem : ‖qeval f y-qeval f (x:ℚ_[2])-
        (y-(x:ℚ_[2])) • ((rjet 1 f x:D):ℚ_[2])‖ ≤ ‖y-(x:ℚ_[2])‖^2 := he
    calc
      _ ≤ ‖y-(x:ℚ_[2])‖⁻¹ * ‖y-(x:ℚ_[2])‖^2 :=
        mul_le_mul_of_nonneg_left hrem (inv_nonneg.mpr (norm_nonneg _))
      _ = ‖y-(x:ℚ_[2])‖ := by
        by_cases hz : ‖y-(x:ℚ_[2])‖=0
        · simp [hz]
        · field_simp
  · have hc : Continuous (fun y : ℚ_[2] => ‖y-(x:ℚ_[2])‖) := continuous_norm.comp (continuous_id.sub continuous_const)
    have h := hc.tendsto (x:ℚ_[2])
    simpa only [sub_self, norm_zero] using h

lemma deriv_qeval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    deriv (qeval f) (x:ℚ_[2])=((rjet 1 f x:D):ℚ_[2]) :=
  (hasDerivAt_qeval hf x).deriv

end Komorebi.Euler
