import KomorebiSpace.Cofinal
import Mathlib.Topology.MetricSpace.Pseudo.Lemmas
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# What cofinal refinement does and does not preserve

Vanishing is invariant under monotone cofinal sampling for a nonnegative
nonincreasing residual profile. Without monotonicity, even cofinal sampling
can hide every nonzero residual. Raw residual norms are not invariants by fiat.
-/
namespace KomorebiSpace
namespace Profiles
open Filter
open scoped Topology

theorem schedule_tendsto_atTop (φ : ℕ → ℕ) (hφ : Monotone φ)
    (hc : Resolution.UnboundedSchedule φ) : Tendsto φ atTop atTop := by
  apply tendsto_atTop.2
  intro n
  obtain ⟨j, hj⟩ := hc n
  exact eventually_atTop.2 ⟨j, fun k hk => hj.trans (hφ hk)⟩

theorem vanish_of_sample (η : ℕ → ℝ) (hη : ∀ n, 0 ≤ η n)
    (hanti : Antitone η) (φ : ℕ → ℕ)
    (hs : Tendsto (fun n => η (φ n)) atTop (𝓝 0)) : Tendsto η atTop (𝓝 0) := by
  apply Metric.tendsto_atTop.2
  intro ε hε
  have hev : ∀ᶠ k in atTop, η (φ k) < ε := (tendsto_order.1 hs).2 ε hε
  obtain ⟨k, hk⟩ := hev.exists
  refine ⟨φ k, ?_⟩
  intro n hn
  have hlt : η n < ε := (hanti hn).trans_lt hk
  simpa only [Real.dist_eq, sub_zero, abs_of_nonneg (hη n)] using hlt

/-- Correct quantitative cofinal-invariance theorem: only a convergence property. -/
theorem cofinal_vanish_iff (η : ℕ → ℝ) (hη : ∀ n, 0 ≤ η n)
    (hanti : Antitone η) (φ : ℕ → ℕ) (hφ : Monotone φ)
    (hc : Resolution.UnboundedSchedule φ) :
    Tendsto η atTop (𝓝 0) ↔ Tendsto (fun n => η (φ n)) atTop (𝓝 0) := by
  constructor
  · intro h
    exact h.comp (schedule_tendsto_atTop φ hφ hc)
  · exact vanish_of_sample η hη hanti φ

def alternating (n : ℕ) : ℝ := if n % 2 = 0 then 0 else 1

@[simp] theorem alternating_even (n : ℕ) : alternating (2*n) = 0 := by
  have h : (2*n) % 2 = 0 := by omega
  simp [alternating, h]

@[simp] theorem alternating_odd (n : ℕ) : alternating (2*n+1) = 1 := by
  simp [alternating]

theorem sampled_alternating_vanishes :
    Tendsto (fun n => alternating (2*n)) atTop (𝓝 0) := by
  simpa only [alternating_even] using (tendsto_const_nhds : Tendsto (fun _ : ℕ => (0 : ℝ)) atTop (𝓝 0))

/-- Counterexample to unconditional residual-profile invariance under cofinal sampling. -/
theorem alternating_does_not_vanish : ¬ Tendsto alternating atTop (𝓝 0) := by
  intro h
  obtain ⟨N, hN⟩ := (Metric.tendsto_atTop.1 h) (1/2) (by norm_num)
  have hh := hN (2*N+1) (by omega)
  rw [alternating_odd] at hh
  norm_num [Real.dist_eq] at hh
end Profiles
end KomorebiSpace
