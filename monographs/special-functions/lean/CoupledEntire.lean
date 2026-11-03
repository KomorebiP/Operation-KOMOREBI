import CoupledAnalytic

/-!
# Entire coupled functions under strict contraction

The recurrence and the sums are unchanged from Blocks 01 and 02. The new
mechanism propagates absolute convergence using the recurrence denominator
and the absolutely convergent Cauchy product.
-/

set_option autoImplicit false
set_option maxHeartbeats 1000000

noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales

/-- The finite Cauchy-product coefficient at a fixed evaluation point. -/
def oddConvolution (c d : ℕ → ℝ) (x y : ℝ) (z : ℂ) (n : ℕ) : ℂ :=
  ∑ i ∈ Finset.range (n + 1),
    ((c i : ℂ) * ((x : ℂ) * z) ^ (2 * i + 1)) *
      ((d (n - i) : ℂ) * ((y : ℂ) * z) ^ (2 * (n - i) + 1))

theorem oddConvolution_eq (c d : ℕ → ℝ) (x y : ℝ) (z : ℂ) (n : ℕ) :
    oddConvolution c d x y z n =
      ((∑ i : Fin (n + 1), x ^ (2 * i.val + 1) * y ^ (2 * (n - i.val) + 1) *
        c i.val * d (n - i.val) : ℝ) : ℂ) * z ^ (2 * n + 2) := by
  unfold oddConvolution
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

/-- The recurrence relates the next series term to the finite Cauchy product. -/
theorem next_term_mul_denominator (c d : ℕ → ℝ) (x y : ℝ) (z : ℂ) (n : ℕ) :
    ((nextCoefficient x y (fun j => (c j, d j)) n : ℂ) * z ^ (2 * (n + 1) + 1)) *
      ((2 * (n : ℝ) + 3 : ℝ) : ℂ) = z * oddConvolution c d x y z n := by
  have h := congrArg (fun t : ℝ => (t : ℂ))
    (nextCoefficient_mul_denominator x y (fun j => (c j, d j)) n)
  rw [oddConvolution_eq]
  calc
    _ = ((nextCoefficient x y (fun j => (c j, d j)) n : ℂ) *
        ((2 * (n : ℝ) + 3 : ℝ) : ℂ)) * z ^ (2 * (n + 1) + 1) := by ring
    _ = _ := by rw [← Complex.ofReal_mul, h]; ring

/-- No summability or positivity is assumed in this pointwise norm estimate. -/
theorem next_term_norm_le (c d : ℕ → ℝ) (x y : ℝ) (z : ℂ) (n : ℕ) :
    ‖(nextCoefficient x y (fun j => (c j, d j)) n : ℂ) * z ^ (2 * (n + 1) + 1)‖ ≤
      ‖z‖ * ‖oddConvolution c d x y z n‖ := by
  have h := congrArg norm (next_term_mul_denominator c d x y z n)
  have hd : 0 ≤ 2 * (n : ℝ) + 3 := by positivity
  simp only [norm_mul, Complex.norm_of_nonneg hd] at h
  have hn : 0 ≤ ‖(nextCoefficient x y (fun j => (c j, d j)) n : ℂ) *
      z ^ (2 * (n + 1) + 1)‖ := norm_nonneg _
  have hden : (1 : ℝ) ≤ 2 * (n : ℝ) + 3 := by
    have := Nat.cast_nonneg (α := ℝ) n
    linarith
  calc
    _ = _ * (1 : ℝ) := (mul_one _).symm
    _ ≤ _ * (2 * (n : ℝ) + 3) := mul_le_mul_of_nonneg_left hden hn
    _ = _ := by simpa only [norm_mul] using h

/-- Convergence at the two contracted arguments implies convergence of the
coefficient series one recurrence step outward. -/
theorem odd_series_bootstrap {c d e : ℕ → ℝ} {x y : ℝ} (z : ℂ)
    (hrec : ∀ n, e (n + 1) = nextCoefficient x y (fun j => (c j, d j)) n)
    (hc : Summable (fun n => ‖(c n : ℂ) * ((x : ℂ) * z) ^ (2 * n + 1)‖))
    (hd : Summable (fun n => ‖(d n : ℂ) * ((y : ℂ) * z) ^ (2 * n + 1)‖)) :
    Summable (fun n => ‖(e n : ℂ) * z ^ (2 * n + 1)‖) := by
  have hconv : Summable (fun n => ‖oddConvolution c d x y z n‖) := by
    simpa only [oddConvolution] using
      (summable_norm_sum_mul_range_of_summable_norm (R := ℂ)
        (f := fun n => (c n : ℂ) * ((x : ℂ) * z) ^ (2 * n + 1))
        (g := fun n => (d n : ℂ) * ((y : ℂ) * z) ^ (2 * n + 1)) hc hd)
  have htail : Summable (fun n => ‖(e (n + 1) : ℂ) * z ^ (2 * (n + 1) + 1)‖) := by
    apply Summable.of_nonneg_of_le (fun n => norm_nonneg _) _ (hconv.mul_left ‖z‖)
    intro n
    rw [hrec]
    exact next_term_norm_le c d x y z n
  exact (summable_nat_add_iff 1).mp htail

/-- Absolute convergence of both constructed odd coefficient series. -/
def NormConverges (s : Scales) (z : ℂ) : Prop :=
  Summable (fun n => ‖((s.coefficients n).1 : ℂ) * z ^ (2 * n + 1)‖) ∧
  Summable (fun n => ‖((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)‖)

theorem coefficient_series_bootstrap (s : Scales) (z : ℂ)
    (hq : s.NormConverges ((s.q : ℂ) * z))
    (hr : s.NormConverges ((s.r : ℂ) * z))
    (ha : s.NormConverges ((s.a : ℂ) * z))
    (hb : s.NormConverges ((s.b : ℂ) * z)) : s.NormConverges z := by
  constructor
  · apply odd_series_bootstrap z _ hq.1 hr.2
    intro n
    exact congrArg Prod.fst (s.coefficients_solution.2 n)
  · apply odd_series_bootstrap z _ ha.1 hb.2
    intro n
    exact congrArg Prod.snd (s.coefficients_solution.2 n)

/-- The largest of the four labeled positive scales. -/
def maxScale (s : Scales) : ℝ := max (max s.q s.r) (max s.a s.b)

theorem maxScale_bounds (s : Scales) :
    s.q ≤ s.maxScale ∧ s.r ≤ s.maxScale ∧ s.a ≤ s.maxScale ∧ s.b ≤ s.maxScale :=
  ⟨(le_max_left _ _).trans (le_max_left _ _),
    (le_max_right _ _).trans (le_max_left _ _),
    (le_max_left _ _).trans (le_max_right _ _),
    (le_max_right _ _).trans (le_max_right _ _)⟩

theorem maxScale_lt_one (s : Scales)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : s.maxScale < 1 :=
  max_lt (max_lt hstrict.1 hstrict.2.1) (max_lt hstrict.2.2.1 hstrict.2.2.2)

/-- Convergence on every level of the contraction ladder. The estimate uses
multiplication by Q^n, avoiding any division by a possibly zero radius. -/
theorem coefficient_series_on_ladder (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1)
    {Q : ℝ} (hQ : 0 ≤ Q) (hscales : s.q ≤ Q ∧ s.r ≤ Q ∧ s.a ≤ Q ∧ s.b ≤ Q)
    (n : ℕ) (z : ℂ) (hz : ‖z‖ * Q ^ n ≤ 1) : s.NormConverges z := by
  induction n generalizing z with
  | zero =>
    have hnorm : ‖z‖ ≤ 1 := by simpa using hz
    exact s.coefficient_series_absolutely_convergent hs hsmall z (by nlinarith [norm_nonneg z])
  | succ n ih =>
    have harg {t : ℝ} (ht : 0 ≤ t) (htQ : t ≤ Q) :
        ‖(t : ℂ) * z‖ * Q ^ n ≤ 1 := by
      rw [norm_mul, Complex.norm_of_nonneg ht]
      calc
        _ ≤ (Q * ‖z‖) * Q ^ n := mul_le_mul_of_nonneg_right
          (mul_le_mul_of_nonneg_right htQ (norm_nonneg z)) (pow_nonneg hQ _)
        _ = ‖z‖ * Q ^ (n + 1) := by rw [pow_succ]; ring
        _ ≤ 1 := hz
    exact s.coefficient_series_bootstrap z
      (ih _ (harg hs.1.le hscales.1)) (ih _ (harg hs.2.1.le hscales.2.1))
      (ih _ (harg hs.2.2.1.le hscales.2.2.1))
      (ih _ (harg hs.2.2.2.le hscales.2.2.2))

/-- Strict contraction promotes the previously local absolute convergence to
every complex point, for the same coefficient sequences. -/
theorem coefficient_series_entire (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (z : ℂ) : s.NormConverges z := by
  have hQ0 : 0 ≤ s.maxScale := hs.1.le.trans s.maxScale_bounds.1
  have hlim : Filter.Tendsto (fun n : ℕ => ‖z‖ * s.maxScale ^ n)
      Filter.atTop (nhds 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hQ0 (s.maxScale_lt_one hstrict)).const_mul ‖z‖
  obtain ⟨n, hn⟩ := (hlim.eventually_lt_const (by norm_num : (0 : ℝ) < 1)).exists
  exact s.coefficient_series_on_ladder hs
    ⟨hstrict.1.le, hstrict.2.1.le, hstrict.2.2.1.le, hstrict.2.2.2.le⟩
    hQ0 s.maxScale_bounds n z hn.le

/-- A summable positive-radius majorant controls each smaller complex point. -/
theorem odd_term_norm_le_radius (c : ℕ → ℝ) {R : ℝ} (hR : 0 ≤ R)
    {z : ℂ} (hz : ‖z‖ ≤ R) (n : ℕ) :
    ‖(c n : ℂ) * z ^ (2 * n + 1)‖ ≤
      ‖(c n : ℂ) * (R : ℂ) ^ (2 * n + 1)‖ := by
  simp only [norm_mul, norm_pow, Complex.norm_of_nonneg hR]
  exact mul_le_mul_of_nonneg_left
    (pow_le_pow_left₀ (norm_nonneg z) hz _) (norm_nonneg _)

theorem oddSum_differentiableOn_of_radius {c : ℕ → ℝ} {R : ℝ} (hR : 0 ≤ R)
    (hc : Summable (fun n => ‖(c n : ℂ) * (R : ℂ) ^ (2 * n + 1)‖)) :
    DifferentiableOn ℂ (oddSum c) (Metric.ball 0 R) := by
  apply Complex.differentiableOn_tsum_of_summable_norm hc
  · intro n
    exact (differentiable_const _ |>.mul (differentiable_id.pow _)).differentiableOn
  · exact Metric.isOpen_ball
  · intro n z hz
    exact odd_term_norm_le_radius c hR (show ‖z‖ < R by simpa using hz).le n

theorem oddSum_hasSum_deriv_of_radius {c : ℕ → ℝ} {R : ℝ} (hR : 0 ≤ R)
    (hc : Summable (fun n => ‖(c n : ℂ) * (R : ℂ) ^ (2 * n + 1)‖))
    {z : ℂ} (hz : ‖z‖ < R) :
    HasSum (fun n => (c n : ℂ) * (2 * n + 1) * z ^ (2 * n)) (deriv (oddSum c) z) := by
  have h := Complex.hasSum_deriv_of_summable_norm hc
    (fun n => (differentiable_const _ |>.mul (differentiable_id.pow (2 * n + 1))).differentiableOn)
    Metric.isOpen_ball
    (fun n w hw => odd_term_norm_le_radius c hR (show ‖w‖ < R by simpa using hw).le n)
    (show z ∈ Metric.ball 0 R by simpa using hz)
  convert! h using 1
  ext n
  exact (oddTerm_hasDerivAt c n z).deriv.symm

theorem oddSum_entire_of_norm_summable {c : ℕ → ℝ}
    (hc : ∀ z : ℂ, Summable (fun n => ‖(c n : ℂ) * z ^ (2 * n + 1)‖)) :
    Differentiable ℂ (oddSum c) := by
  intro z
  have h := oddSum_differentiableOn_of_radius (c := c)
    (R := ‖z‖ + 1) (by positivity) (hc (‖z‖ + 1 : ℝ))
  exact h.differentiableAt (Metric.isOpen_ball.mem_nhds (by simp))

theorem coupled_entire (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    Differentiable ℂ s.U ∧ Differentiable ℂ s.V :=
  ⟨oddSum_entire_of_norm_summable (fun z => (s.coefficient_series_entire hs hstrict z).1),
    oddSum_entire_of_norm_summable (fun z => (s.coefficient_series_entire hs hstrict z).2)⟩

theorem oddSum_hasSum_deriv_entire {c : ℕ → ℝ}
    (hc : ∀ z : ℂ, Summable (fun n => ‖(c n : ℂ) * z ^ (2 * n + 1)‖)) (z : ℂ) :
    HasSum (fun n => (c n : ℂ) * (2 * n + 1) * z ^ (2 * n)) (deriv (oddSum c) z) :=
  oddSum_hasSum_deriv_of_radius (R := ‖z‖ + 1) (by positivity)
    (hc (‖z‖ + 1 : ℝ)) (lt_add_one ‖z‖)

/-- The shifted differentiated term is exactly the finite Cauchy coefficient. -/
theorem next_derivative_term_eq (c d : ℕ → ℝ) (x y : ℝ) (z : ℂ) (n : ℕ) :
    (nextCoefficient x y (fun j => (c j, d j)) n : ℂ) *
      (2 * (n + 1) + 1) * z ^ (2 * (n + 1)) = oddConvolution c d x y z n := by
  rw [oddConvolution_eq]
  have h := congrArg (fun t : ℝ => (t : ℂ))
    (nextCoefficient_mul_denominator x y (fun j => (c j, d j)) n)
  simp only [Complex.ofReal_mul, Complex.ofReal_add, Complex.ofReal_ofNat,
    Complex.ofReal_natCast] at h
  convert congrArg (fun t : ℂ => t * z ^ (2 * n + 2)) h using 1
  ring

theorem oddSum_entire_equation {c d e : ℕ → ℝ}
    (he : ∀ w : ℂ, Summable (fun n => ‖(e n : ℂ) * w ^ (2 * n + 1)‖))
    {x y : ℝ} (he0 : e 0 = 1)
    (hrec : ∀ n, e (n + 1) = nextCoefficient x y (fun j => (c j, d j)) n)
    (z : ℂ)
    (hc : Summable (fun n => ‖(c n : ℂ) * ((x : ℂ) * z) ^ (2 * n + 1)‖))
    (hd : Summable (fun n => ‖(d n : ℂ) * ((y : ℂ) * z) ^ (2 * n + 1)‖)) :
    deriv (oddSum e) z = 1 + oddSum c ((x : ℂ) * z) * oddSum d ((y : ℂ) * z) := by
  have hprod : oddSum c ((x : ℂ) * z) * oddSum d ((y : ℂ) * z) =
      ∑' n, oddConvolution c d x y z n :=
    tsum_mul_tsum_eq_tsum_sum_range_of_summable_norm
      (f := fun n => (c n : ℂ) * ((x : ℂ) * z) ^ (2 * n + 1))
      (g := fun n => (d n : ℂ) * ((y : ℂ) * z) ^ (2 * n + 1)) hc hd
  have hsum := oddSum_hasSum_deriv_entire he z
  rw [← hsum.tsum_eq, hsum.summable.tsum_eq_zero_add]
  simp only [he0, Complex.ofReal_one, Nat.cast_zero, mul_zero, zero_add, pow_zero, mul_one]
  rw [hprod]
  congr 1
  apply tsum_congr
  intro n
  rw [hrec]
  simpa only [Nat.cast_add, Nat.cast_one] using next_derivative_term_eq c d x y z n

theorem coupled_entire_equations (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (z : ℂ) :
    deriv s.U z = 1 + s.U ((s.q : ℂ) * z) * s.V ((s.r : ℂ) * z) ∧
    deriv s.V z = 1 + s.U ((s.a : ℂ) * z) * s.V ((s.b : ℂ) * z) := by
  have h0 := s.coefficients_zero
  constructor
  · apply oddSum_entire_equation (fun w => (s.coefficient_series_entire hs hstrict w).1)
      (congrArg Prod.fst h0) _ z
      (s.coefficient_series_entire hs hstrict _).1 (s.coefficient_series_entire hs hstrict _).2
    intro n
    exact congrArg Prod.fst (s.coefficients_solution.2 n)
  · apply oddSum_entire_equation (fun w => (s.coefficient_series_entire hs hstrict w).2)
      (congrArg Prod.snd h0) _ z
      (s.coefficient_series_entire hs hstrict _).1 (s.coefficient_series_entire hs hstrict _).2
    intro n
    exact congrArg Prod.snd (s.coefficients_solution.2 n)

/-- The constructed pair is an entire normalized solution, without a gluing
choice or a hypothesis that the infinite sums already solve the equations. -/
theorem coupled_entire_solution (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.U 0 = 0 ∧ s.V 0 = 0 ∧
      ∀ z : ℂ,
        HasDerivAt s.U (1 + s.U ((s.q : ℂ) * z) * s.V ((s.r : ℂ) * z)) z ∧
        HasDerivAt s.V (1 + s.U ((s.a : ℂ) * z) * s.V ((s.b : ℂ) * z)) z := by
  refine ⟨oddSum_zero _, oddSum_zero _, ?_⟩
  intro z
  have hd := s.coupled_entire hs hstrict
  exact ⟨(s.coupled_entire_equations hs hstrict z).1 ▸ (hd.1 z).hasDerivAt,
    (s.coupled_entire_equations hs hstrict z).2 ▸ (hd.2 z).hasDerivAt⟩

end Komorebi.SpecialFunctions.Coupled.Scales
