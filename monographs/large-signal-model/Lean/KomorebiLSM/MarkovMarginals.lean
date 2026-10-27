import KomorebiLSM.MarkovMinorization

/-! P86: actual Markov marginal iterates satisfy the geometric stability bound
because minorization contracts the common-kernel part of each comparison. -/
set_option autoImplicit false
namespace Komorebi.LSM.MarkovStability
open MeasureTheory ProbabilityTheory SequentialLowerCertificate MeasureTVCalculus
open scoped ENNReal
variable {X : Type*} [MeasurableSpace X]

/-- The literal recursively composed one-time laws. -/
noncomputable def marginal (P : Kernel X X) (ν0 : Measure X) : ℕ → Measure X
  | 0 => ν0
  | n+1 => P ∘ₘ marginal P ν0 n

instance marginal_probability (P : Kernel X X) [IsMarkovKernel P]
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (n : ℕ) : IsProbabilityMeasure (marginal P ν0 n) := by
  induction n with
  | zero => exact inferInstanceAs (IsProbabilityMeasure ν0)
  | succ n ih =>
    have := ih
    exact inferInstanceAs (IsProbabilityMeasure (P ∘ₘ marginal P ν0 n))

/-- The actual one-step recurrence, derived by adding a common-P continuation
and then changing the conditional kernel under the second current law. -/
theorem marginal_step (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (ρ Δ : ℝ)
    (hρ0 : 0≤ρ) (hρ1 : ρ≤1) (hmin : Minorized P ρ reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (n : ℕ) :
    lawTV (marginal P ν0 (n+1)) (marginal Q η0 (n+1))≤
      (1-ρ)*lawTV (marginal P ν0 n) (marginal Q η0 n)+Δ :=
  (lawTV_triangle (P ∘ₘ marginal P ν0 n) (P ∘ₘ marginal Q η0 n) (Q ∘ₘ marginal Q η0 n)).trans
    (add_le_add (minorization_contraction P reference ρ hρ0 hρ1 hmin (marginal P ν0 n) (marginal Q η0 n))
      (comp_measure_uniform_change (marginal Q η0 n) P Q Δ hΔ))

/-- The source's closed geometric error budget, including n=0 and rho=1. -/
noncomputable def marginalBudget (ρ Δ e0 : ℝ) (n : ℕ) : ℝ :=
  (1-ρ)^n*e0+Δ*(1-(1-ρ)^n)/ρ

omit [MeasurableSpace X] in
theorem marginalBudget_succ (ρ Δ e0 : ℝ) (hρ : ρ≠0) (n : ℕ) :
    (1-ρ)*marginalBudget ρ Δ e0 n+Δ=marginalBudget ρ Δ e0 (n+1) := by
  unfold marginalBudget
  rw [pow_succ]
  field_simp
  ring

/-- Full geometric bound for the actual one-time marginal measures. -/
theorem marginal_bound (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (ρ Δ : ℝ)
    (hρ0 : 0<ρ) (hρ1 : ρ≤1) (hmin : Minorized P ρ reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (n : ℕ) :
    lawTV (marginal P ν0 n) (marginal Q η0 n)≤
      min 1 ((1-ρ)^n*lawTV ν0 η0+Δ*(1-(1-ρ)^n)/ρ) := by
  apply le_min (lawTV_le_one _ _)
  change lawTV (marginal P ν0 n) (marginal Q η0 n)≤marginalBudget ρ Δ (lawTV ν0 η0) n
  induction n with
  | zero => simp [marginal,marginalBudget]
  | succ n ih =>
    calc lawTV (marginal P ν0 (n+1)) (marginal Q η0 (n+1))≤
        (1-ρ)*lawTV (marginal P ν0 n) (marginal Q η0 n)+Δ :=
          marginal_step P Q reference ρ Δ hρ0.le hρ1 hmin hΔ ν0 η0 n
      _ ≤ (1-ρ)*marginalBudget ρ Δ (lawTV ν0 η0) n+Δ :=
        add_le_add (mul_le_mul_of_nonneg_left ih (sub_nonneg.mpr hρ1)) le_rfl
      _ = marginalBudget ρ Δ (lawTV ν0 η0) (n+1) :=
        marginalBudget_succ ρ Δ (lawTV ν0 η0) (ne_of_gt hρ0) n

/-- Complete refresh rho=1 removes every initial discrepancy after one step. -/
theorem marginal_bound_refresh (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (Δ : ℝ)
    (hmin : Minorized P 1 reference) (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 η0 : Measure X) [IsProbabilityMeasure ν0] [IsProbabilityMeasure η0] (n : ℕ) :
    lawTV (marginal P ν0 (n+1)) (marginal Q η0 (n+1))≤min 1 Δ := by
  apply le_min (lawTV_le_one _ _)
  simpa only [sub_self,zero_mul,zero_add] using
    marginal_step P Q reference 1 Δ (by norm_num) le_rfl hmin hΔ ν0 η0 n

/-- A common initial law has a uniform all-time one-marginal budget. -/
theorem marginal_same_initial_uniform (P Q : Kernel X X) [IsMarkovKernel P] [IsMarkovKernel Q]
    (reference : Measure X) [IsProbabilityMeasure reference] (ρ Δ : ℝ)
    (hρ0 : 0<ρ) (hρ1 : ρ≤1) (hΔ0 : 0≤Δ) (hmin : Minorized P ρ reference)
    (hΔ : ∀ x,lawTV (P x) (Q x)≤Δ)
    (ν0 : Measure X) [IsProbabilityMeasure ν0] (n : ℕ) :
    lawTV (marginal P ν0 n) (marginal Q ν0 n)≤min 1 (Δ/ρ) := by
  apply (marginal_bound P Q reference ρ Δ hρ0 hρ1 hmin hΔ ν0 ν0 n).trans
  apply min_le_min le_rfl
  simp only [lawTV_self,mul_zero,zero_add]
  apply (div_le_div_iff_of_pos_right hρ0).2
  have hn : 0≤(1-ρ)^n := pow_nonneg (sub_nonneg.mpr hρ1) n
  nlinarith

end Komorebi.LSM.MarkovStability
