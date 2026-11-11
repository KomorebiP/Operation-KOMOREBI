import SmithBoundaries
import Mathlib.Analysis.Analytic.Constructions

open scoped BigOperators

/-! Finite-sample nonuniqueness for analytic positive-real coordinate functions. -/

namespace SmithFiniteSamples

noncomputable def witness (s : Finset ℂ) (z : ℂ) : ℂ :=
  1 + (1 / (2 : ℂ) ^ (s.card + 1)) * ∏ x ∈ s, (z - x)

theorem witness_agrees {s : Finset ℂ} {z : ℂ} (hz : z ∈ s) : witness s z = 1 := by
  have hprod : (∏ x ∈ s, (z - x)) = 0 := Finset.prod_eq_zero hz (sub_self z)
  simp [witness, hprod]

theorem witness_positive {s : Finset ℂ} (hs : ∀ x ∈ s, ‖x‖ < 1)
    {z : ℂ} (hz : ‖z‖ < 1) : 0 < (witness s z).re := by
  have hprod : ‖∏ x ∈ s, (z - x)‖ ≤ (2 : ℝ) ^ s.card := by
    rw [norm_prod]
    calc
      (∏ x ∈ s, ‖z - x‖) ≤ ∏ _x ∈ s, (2 : ℝ) := by
        apply Finset.prod_le_prod (fun _ _ => norm_nonneg _)
        intro x hx
        have ht := norm_sub_le z x
        have hx' := hs x hx
        linarith
      _ = (2 : ℝ) ^ s.card := by simp
  have hnorm : ‖(1 / (2 : ℂ) ^ (s.card + 1)) * ∏ x ∈ s, (z - x)‖ ≤ (1 / 2 : ℝ) := by
    rw [norm_mul]
    have he : ‖1 / (2 : ℂ) ^ (s.card + 1)‖ = 1 / (2 : ℝ) ^ (s.card + 1) := by
      simp [norm_pow]
    rw [he]
    calc
      (1 / (2 : ℝ) ^ (s.card + 1)) * ‖∏ x ∈ s, (z - x)‖ ≤
          (1 / (2 : ℝ) ^ (s.card + 1)) * (2 : ℝ) ^ s.card := by
        exact mul_le_mul_of_nonneg_left hprod (by positivity)
      _ = 1 / 2 := by
        rw [pow_succ]
        field_simp
  have hre := (abs_le.mp (le_trans (Complex.abs_re_le_norm _) hnorm)).1
  simp only [witness, Complex.add_re, Complex.one_re]
  linarith

theorem witness_distinct (s : Finset ℂ) (hs : ∀ x ∈ s, ‖x‖ < 1) : witness s 2 ≠ 1 := by
  have hprod : (∏ x ∈ s, ((2 : ℂ) - x)) ≠ 0 := by
    apply Finset.prod_ne_zero_iff.mpr
    intro x hx
    apply sub_ne_zero.mpr
    intro he
    have hx' := hs x hx
    rw [← he] at hx'
    norm_num at hx'
  have hscale : (1 / (2 : ℂ) ^ (s.card + 1)) ≠ 0 :=
    div_ne_zero one_ne_zero (pow_ne_zero _ (by norm_num))
  intro h
  have hn : (1 / (2 : ℂ) ^ (s.card + 1)) * ∏ x ∈ s, ((2 : ℂ) - x) = 0 := by
    have h' := h
    simp only [witness] at h'
    linear_combination h'
  exact (mul_ne_zero hscale hprod) hn

theorem witness_analytic (s : Finset ℂ) (z : ℂ) : AnalyticAt ℂ (witness s) z := by
  unfold witness
  fun_prop

theorem witness_distinct_inside (s : Finset ℂ) :
    ∃ z : ℂ, ‖z‖ < 1 ∧ witness s z ≠ 1 := by
  have hball : Set.Infinite (Metric.ball (0 : ℂ) 1) := by
    apply infinite_of_mem_nhds (0 : ℂ)
    exact Metric.ball_mem_nhds _ (by norm_num)
  obtain ⟨z, hz, hznot⟩ := hball.exists_notMem_finset s
  have hz' : ‖z‖ < 1 := by simpa [Metric.mem_ball, dist_zero_right] using hz
  refine ⟨z, hz', ?_⟩
  have hprod : (∏ x ∈ s, (z - x)) ≠ 0 := by
    apply Finset.prod_ne_zero_iff.mpr
    intro x hx
    apply sub_ne_zero.mpr
    intro he
    apply hznot
    simpa [he] using hx
  have hscale : (1 / (2 : ℂ) ^ (s.card + 1)) ≠ 0 :=
    div_ne_zero one_ne_zero (pow_ne_zero _ (by norm_num))
  intro h
  have hn : (1 / (2 : ℂ) ^ (s.card + 1)) * ∏ x ∈ s, (z - x) = 0 := by
    have h' := h
    simp only [witness] at h'
    linear_combination h'
  exact (mul_ne_zero hscale hprod) hn

theorem finite_sample_nonuniqueness (s : Finset ℂ) (hs : ∀ x ∈ s, ‖x‖ < 1) :
    ∃ f g : ℂ → ℂ,
      (∀ z, AnalyticAt ℂ f z) ∧ (∀ z, AnalyticAt ℂ g z) ∧
      (∀ z, ‖z‖ < 1 → 0 < (f z).re) ∧ (∀ z, ‖z‖ < 1 → 0 < (g z).re) ∧
      (∀ z ∈ s, f z = g z) ∧ (∃ z, ‖z‖ < 1 ∧ f z ≠ g z) := by
  refine ⟨(fun _ => 1), witness s, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro z
    fun_prop
  · exact witness_analytic s
  · intro z hz
    norm_num
  · intro z hz
    exact witness_positive hs hz
  · intro z hz
    exact (witness_agrees hz).symm
  · obtain ⟨z, hz, hn⟩ := witness_distinct_inside s
    exact ⟨z, hz, Ne.symm hn⟩

end SmithFiniteSamples
