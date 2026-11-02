import CoupledFormal
import Mathlib.Analysis.Complex.LocallyUniformLimit
import Mathlib.Analysis.Normed.Ring.InfiniteSum

/-!
# Coupled functions: the local analytic bridge

The recurrence is the one in `CoupledFormal`. All analytic assertions below
are restricted to `‖z‖ ^ 2 < 2` and positive scales at most one.
No entire continuation or global growth assertion is made here.
-/

set_option autoImplicit false
set_option maxHeartbeats 800000

noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales

/-- The function associated with an ordinary odd coefficient sequence. -/
def oddSum (c : ℕ → ℝ) (z : ℂ) : ℂ := ∑' n, (c n : ℂ) * z ^ (2 * n + 1)

/-- The common open disk supplied by the coefficient majorant. -/
def localDisk : Set ℂ := {z | ‖z‖ ^ 2 < 2}

theorem oddSum_zero (c : ℕ → ℝ) : oddSum c 0 = 0 := by
  simp [oddSum]

theorem oddSum_neg (c : ℕ → ℝ) (z : ℂ) : oddSum c (-z) = -oddSum c z := by
  simp [oddSum, pow_add, pow_mul, tsum_neg]

/-- A uniform geometric majorant on each smaller ball. -/
theorem odd_series_uniform_bound {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    {R : ℝ} (hR : 0 ≤ R) {z : ℂ} (hz : z ∈ Metric.ball 0 R) (n : ℕ) :
    ‖(c n : ℂ) * z ^ (2 * n + 1)‖ ≤ R * (R ^ 2 / 2) ^ n := by
  have hzR : ‖z‖ ≤ R := (by simpa using hz : ‖z‖ < R).le
  calc
    _ ≤ ‖z‖ * (‖z‖ ^ 2 / 2) ^ n := odd_series_norm_bound hc z n
    _ ≤ R * (R ^ 2 / 2) ^ n := by
      apply mul_le_mul hzR
      · exact pow_le_pow_left₀ (by positivity)
          (div_le_div_of_nonneg_right (pow_le_pow_left₀ (norm_nonneg z) hzR 2) (by norm_num)) n
      · positivity
      · exact hR

theorem oddSum_differentiableOn_ball {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    {R : ℝ} (hR : 0 ≤ R) (hR2 : R ^ 2 < 2) :
    DifferentiableOn ℂ (oddSum c) (Metric.ball 0 R) := by
  apply Complex.differentiableOn_tsum_of_summable_norm
    ((summable_geometric_of_lt_one (by positivity : 0 ≤ R ^ 2 / 2)
      (by linarith : R ^ 2 / 2 < 1)).mul_left R)
  · intro n
    exact (differentiable_const _ |>.mul (differentiable_id.pow _)).differentiableOn
  · exact Metric.isOpen_ball
  · intro n z hz
    exact odd_series_uniform_bound hc hR hz n

/-- Every point of the disk lies in a smaller ball with a summable majorant. -/
theorem exists_local_radius {z : ℂ} (hz : z ∈ localDisk) :
    ∃ R : ℝ, 0 ≤ R ∧ R ^ 2 < 2 ∧ z ∈ Metric.ball 0 R := by
  have hs : 0 ≤ Real.sqrt 2 := Real.sqrt_nonneg _
  have hs2 : (Real.sqrt 2) ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hlt : ‖z‖ < Real.sqrt 2 := by
    dsimp [localDisk] at hz
    nlinarith [norm_nonneg z]
  obtain ⟨R, hzR, hRs⟩ := exists_between hlt
  have hR : 0 ≤ R := (norm_nonneg z).trans hzR.le
  refine ⟨R, hR, ?_, ?_⟩
  · nlinarith
  · simpa using hzR

theorem oddSum_differentiableAt {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    {z : ℂ} (hz : z ∈ localDisk) : DifferentiableAt ℂ (oddSum c) z := by
  obtain ⟨R, hR, hR2, hzR⟩ := exists_local_radius hz
  exact (oddSum_differentiableOn_ball hc hR hR2).differentiableAt
    (Metric.isOpen_ball.mem_nhds hzR)

theorem oddSum_differentiableOn {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n) :
    DifferentiableOn ℂ (oddSum c) localDisk := by
  intro z hz
  exact (oddSum_differentiableAt hc hz).differentiableWithinAt

theorem oddTerm_hasDerivAt (c : ℕ → ℝ) (n : ℕ) (z : ℂ) :
    HasDerivAt (fun w : ℂ => (c n : ℂ) * w ^ (2 * n + 1))
      ((c n : ℂ) * (2 * n + 1) * z ^ (2 * n)) z := by
  simpa [mul_assoc] using
    ((hasDerivAt_id z).pow (2 * n + 1)).const_mul (c n : ℂ)

/-- Termwise differentiation, with convergence of the differentiated series. -/
theorem oddSum_hasSum_deriv {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    {z : ℂ} (hz : z ∈ localDisk) :
    HasSum (fun n => (c n : ℂ) * (2 * n + 1) * z ^ (2 * n)) (deriv (oddSum c) z) := by
  obtain ⟨R, hR, hR2, hzR⟩ := exists_local_radius hz
  have h := Complex.hasSum_deriv_of_summable_norm
    ((summable_geometric_of_lt_one (by positivity : 0 ≤ R ^ 2 / 2)
      (by linarith : R ^ 2 / 2 < 1)).mul_left R)
    (fun n => (differentiable_const _ |>.mul (differentiable_id.pow (2 * n + 1))).differentiableOn)
    Metric.isOpen_ball (fun n w hw => odd_series_uniform_bound hc hR hw n) hzR
  convert! h using 1
  ext n
  exact (oddTerm_hasDerivAt c n z).deriv.symm

theorem oddSum_hasDerivAt {c : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    {z : ℂ} (hz : z ∈ localDisk) :
    HasDerivAt (oddSum c) (∑' n, (c n : ℂ) * (2 * n + 1) * z ^ (2 * n)) z := by
  rw [(oddSum_hasSum_deriv hc hz).tsum_eq]
  exact (oddSum_differentiableAt hc hz).hasDerivAt

/-- The two sums are defined from the existing recursively constructed coefficients. -/
def U (s : Scales) : ℂ → ℂ := oddSum (fun n => (s.coefficients n).1)

def V (s : Scales) : ℂ → ℂ := oddSum (fun n => (s.coefficients n).2)

theorem coefficient_bounds_left (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) (n : ℕ) :
    0 ≤ (s.coefficients n).1 ∧ (s.coefficients n).1 ≤ (1 / 2 : ℝ) ^ n :=
  ⟨(s.coefficients_positive hs n).1.le, (s.coefficients_le_geometric hs hsmall n).1⟩

theorem coefficient_bounds_right (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) (n : ℕ) :
    0 ≤ (s.coefficients n).2 ∧ (s.coefficients n).2 ≤ (1 / 2 : ℝ) ^ n :=
  ⟨(s.coefficients_positive hs n).2.le, (s.coefficients_le_geometric hs hsmall n).2⟩

theorem coupled_differentiableOn (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) :
    DifferentiableOn ℂ s.U localDisk ∧ DifferentiableOn ℂ s.V localDisk :=
  ⟨oddSum_differentiableOn (s.coefficient_bounds_left hs hsmall),
    oddSum_differentiableOn (s.coefficient_bounds_right hs hsmall)⟩

theorem mul_mem_localDisk {x z : ℂ} (hx : ‖x‖ ≤ 1) (hz : z ∈ localDisk) :
    x * z ∈ localDisk := by
  have hle : ‖x * z‖ ≤ ‖z‖ := by
    rw [norm_mul]
    nlinarith [norm_nonneg z]
  exact lt_of_le_of_lt (pow_le_pow_left₀ (norm_nonneg _) hle 2) hz

/-- The absolutely convergent Cauchy product, in the recurrence's finite indexing. -/
theorem oddSum_mul_eq {c d : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    (hd : ∀ n, 0 ≤ d n ∧ d n ≤ (1 / 2 : ℝ) ^ n)
    {x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (hx1 : x ≤ 1) (hy1 : y ≤ 1)
    {z : ℂ} (hz : z ∈ localDisk) :
    oddSum c ((x : ℂ) * z) * oddSum d ((y : ℂ) * z) =
      ∑' n, ((∑ i : Fin (n + 1),
        x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) * c i.val * d (n - i.val) : ℝ) : ℂ) *
        z ^ (2 * n + 2) := by
  have hxz := mul_mem_localDisk (x := (x : ℂ))
    (by simpa only [Complex.norm_of_nonneg hx] using hx1) hz
  have hyz := mul_mem_localDisk (x := (y : ℂ))
    (by simpa only [Complex.norm_of_nonneg hy] using hy1) hz
  unfold oddSum
  rw [tsum_mul_tsum_eq_tsum_sum_range_of_summable_norm
    (odd_series_norm_summable hc _ hxz) (odd_series_norm_summable hd _ hyz)]
  apply tsum_congr
  intro n
  rw [← Fin.sum_univ_eq_sum_range]
  simp only [Complex.ofReal_sum, Finset.sum_mul, Complex.ofReal_mul, Complex.ofReal_pow]
  apply Finset.sum_congr rfl
  intro i _
  have hi : i.val ≤ n := by omega
  have he : (2 * i.val + 1) + (2 * (n - i.val) + 1) = 2 * n + 2 := by omega
  simp only [mul_pow]
  calc
    _ = (x : ℂ) ^ (2 * i.val + 1) * (y : ℂ) ^ (2 * (n - i.val) + 1) *
        (c i.val : ℂ) * (d (n - i.val) : ℂ) *
        (z ^ (2 * i.val + 1) * z ^ (2 * (n - i.val) + 1)) := by ring
    _ = _ := by rw [← pow_add, he]

/-- The denominator in the recurrence is nonzero, including at the first step. -/
theorem nextCoefficient_mul_denominator (x y : ℝ) (f : ℕ → ℝ × ℝ) (n : ℕ) :
    nextCoefficient x y f n * (2 * (n : ℝ) + 3) =
      ∑ i : Fin (n + 1), x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) *
        (f i.val).1 * (f (n - i.val)).2 := by
  exact div_mul_cancel₀ _ (by positivity)

/-- A local analytic equation follows from the coefficient recurrence and Cauchy product. -/
theorem oddSum_deriv_eq_of_recurrence {c d e : ℕ → ℝ}
    (hc : ∀ n, 0 ≤ c n ∧ c n ≤ (1 / 2 : ℝ) ^ n)
    (hd : ∀ n, 0 ≤ d n ∧ d n ≤ (1 / 2 : ℝ) ^ n)
    (he : ∀ n, 0 ≤ e n ∧ e n ≤ (1 / 2 : ℝ) ^ n)
    {x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (hx1 : x ≤ 1) (hy1 : y ≤ 1)
    (he0 : e 0 = 1)
    (hrec : ∀ n, e (n + 1) = nextCoefficient x y (fun j => (c j, d j)) n)
    {z : ℂ} (hz : z ∈ localDisk) :
    deriv (oddSum e) z = 1 + oddSum c ((x : ℂ) * z) * oddSum d ((y : ℂ) * z) := by
  rw [← (oddSum_hasSum_deriv he hz).tsum_eq,
    (oddSum_hasSum_deriv he hz).summable.tsum_eq_zero_add]
  simp only [he0, Complex.ofReal_one, Nat.cast_zero, mul_zero, zero_add, pow_zero, mul_one]
  rw [oddSum_mul_eq hc hd hx hy hx1 hy1 hz]
  congr 1
  apply tsum_congr
  intro n
  rw [hrec]
  have h := congrArg (fun t : ℝ => (t : ℂ))
    (nextCoefficient_mul_denominator x y (fun j => (c j, d j)) n)
  simp only [Complex.ofReal_mul, Complex.ofReal_add, Complex.ofReal_ofNat,
    Complex.ofReal_natCast] at h
  convert congrArg (fun t : ℂ => t * z ^ (2 * n + 2)) h using 1
  push_cast
  ring

theorem coupled_local_equations (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1)
    {z : ℂ} (hz : z ∈ localDisk) :
    deriv s.U z = 1 + s.U ((s.q : ℂ) * z) * s.V ((s.r : ℂ) * z) ∧
    deriv s.V z = 1 + s.U ((s.a : ℂ) * z) * s.V ((s.b : ℂ) * z) := by
  have h0 := s.coefficients_zero
  constructor
  · apply oddSum_deriv_eq_of_recurrence (s.coefficient_bounds_left hs hsmall)
      (s.coefficient_bounds_right hs hsmall) (s.coefficient_bounds_left hs hsmall)
      hs.1.le hs.2.1.le hsmall.1 hsmall.2.1
    · exact congrArg Prod.fst h0
    · intro n
      exact congrArg Prod.fst (s.coefficients_solution.2 n)
    · exact hz
  · apply oddSum_deriv_eq_of_recurrence (s.coefficient_bounds_left hs hsmall)
      (s.coefficient_bounds_right hs hsmall) (s.coefficient_bounds_right hs hsmall)
      hs.2.2.1.le hs.2.2.2.le hsmall.2.2.1 hsmall.2.2.2
    · exact congrArg Prod.snd h0
    · intro n
      exact congrArg Prod.snd (s.coefficients_solution.2 n)
    · exact hz

/-- The normalized analytic solution on the common disk, including both equations. -/
theorem coupled_local_solution (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) :
    s.U 0 = 0 ∧ s.V 0 = 0 ∧
      ∀ z ∈ localDisk,
        HasDerivAt s.U (1 + s.U ((s.q : ℂ) * z) * s.V ((s.r : ℂ) * z)) z ∧
        HasDerivAt s.V (1 + s.U ((s.a : ℂ) * z) * s.V ((s.b : ℂ) * z)) z := by
  refine ⟨oddSum_zero _, oddSum_zero _, ?_⟩
  intro z hz
  have hU := oddSum_differentiableAt (s.coefficient_bounds_left hs hsmall) hz
  have hV := oddSum_differentiableAt (s.coefficient_bounds_right hs hsmall) hz
  exact ⟨(s.coupled_local_equations hs hsmall hz).1 ▸ hU.hasDerivAt,
    (s.coupled_local_equations hs hsmall hz).2 ▸ hV.hasDerivAt⟩

theorem coupled_initial_derivatives (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) :
    deriv s.U 0 = 1 ∧ deriv s.V 0 = 1 := by
  have h := s.coupled_local_equations hs hsmall (z := 0) (by norm_num [localDisk])
  simpa only [mul_zero, U, V, oddSum_zero, zero_mul, add_zero] using h

theorem coupled_odd (s : Scales) (z : ℂ) : s.U (-z) = -s.U z ∧ s.V (-z) = -s.V z :=
  ⟨oddSum_neg _ _, oddSum_neg _ _⟩

end Komorebi.SpecialFunctions.Coupled.Scales
