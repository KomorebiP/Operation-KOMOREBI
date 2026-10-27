import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Topology.Semicontinuity.Basic
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-!
# Exactification from summable movement and vanishing residual

Completeness, lower semicontinuity and nonnegativity are explicit hypotheses.
No assertion of uniqueness follows from residual zero alone.
-/
universe u
namespace KomorebiSpace
namespace Exactification
open Filter
open scoped Topology
variable {M : Type u} [PseudoMetricSpace M]

/-- Lower semicontinuity is sufficient to preserve a vanishing residual at a limit. -/
theorem residual_zero_of_limit (ω : M → ℝ) (hω : ∀ x, 0 ≤ ω x)
    (hlsc : LowerSemicontinuous ω) {f : ℕ → M} {x : M}
    (hx : Tendsto f atTop (𝓝 x))
    (hv : Tendsto (fun n => ω (f n)) atTop (𝓝 0)) : ω x = 0 := by
  apply le_antisymm _ (hω x)
  apply le_of_forall_pos_le_add
  intro ε hε
  have hev : ∀ᶠ n in atTop, ω (f n) ≤ ε :=
    ((tendsto_order.1 hv).2 ε hε).mono fun _ h => le_of_lt h
  have hm : ω x ≤ ε := (hlsc.isClosed_preimage ε).mem_of_tendsto hx hev
  simpa only [zero_add] using hm

/-- General exactification, with an explicit a posteriori tail estimate. -/
theorem summable_exactification [CompleteSpace M]
    (ω : M → ℝ) (hω : ∀ x, 0 ≤ ω x) (hlsc : LowerSemicontinuous ω)
    (f : ℕ → M) (b : ℕ → ℝ) (hb : Summable b)
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ b n)
    (hv : Tendsto (fun n => ω (f n)) atTop (𝓝 0)) :
    ∃ x, Tendsto f atTop (𝓝 x) ∧ ω x = 0 ∧
      ∀ n, dist (f n) x ≤ ∑' k, b (n+k) := by
  have hc : CauchySeq f := cauchySeq_of_dist_le_of_summable b hstep hb
  obtain ⟨x, hx⟩ := cauchySeq_tendsto_of_complete hc
  exact ⟨x, hx, residual_zero_of_limit ω hω hlsc hx hv,
    dist_le_tsum_of_dist_le_of_tendsto b hstep hb hx⟩

/-- Prefix product Q₀=1, Qₙ₊₁=qₙQₙ. -/
def productRate (q : ℕ → ℝ) : ℕ → ℝ
  | 0 => 1
  | n+1 => q n * productRate q n

theorem productRate_nonneg (q : ℕ → ℝ) (hq : ∀ n, 0 ≤ q n) :
    ∀ n, 0 ≤ productRate q n := by
  intro n
  induction n with
  | zero => norm_num [productRate]
  | succ n ih => exact mul_nonneg (hq n) ih

omit [PseudoMetricSpace M] in
theorem variable_decay (ω : M → ℝ) (f : ℕ → M) (q : ℕ → ℝ)
    (hq : ∀ n, 0 ≤ q n)
    (hdec : ∀ n, ω (f (n+1)) ≤ q n * ω (f n)) :
    ∀ n, ω (f n) ≤ productRate q n * ω (f 0) := by
  intro n
  induction n with
  | zero => simp [productRate]
  | succ n ih =>
    calc
      ω (f (n+1)) ≤ q n * ω (f n) := hdec n
      _ ≤ q n * (productRate q n * ω (f 0)) := mul_le_mul_of_nonneg_left ih (hq n)
      _ = productRate q (n+1) * ω (f 0) := by simp [productRate, mul_assoc]

/-- Variable cancellation factors: no fixed geometric rate is required. -/
theorem variable_exactification [CompleteSpace M]
    (ω : M → ℝ) (hω : ∀ x, 0 ≤ ω x) (hlsc : LowerSemicontinuous ω)
    (f : ℕ → M) (q C : ℕ → ℝ)
    (hq : ∀ n, 0 ≤ q n) (hC : ∀ n, 0 ≤ C n)
    (hdec : ∀ n, ω (f (n+1)) ≤ q n * ω (f n))
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ C n * ω (f n))
    (hQ : Tendsto (productRate q) atTop (𝓝 0))
    (hs : Summable (fun n => C n * productRate q n)) :
    ∃ x, Tendsto f atTop (𝓝 x) ∧ ω x = 0 ∧
      ∀ n, dist (f n) x ≤ ∑' k, (C (n+k) * productRate q (n+k)) * ω (f 0) := by
  have hbound := variable_decay ω f q hq hdec
  have hv : Tendsto (fun n => ω (f n)) atTop (𝓝 0) := by
    apply squeeze_zero (fun n => hω (f n)) hbound
    simpa using hQ.mul_const (ω (f 0))
  refine summable_exactification ω hω hlsc f
    (fun n => (C n * productRate q n) * ω (f 0)) (hs.mul_right _) ?_ hv
  intro n
  calc
    dist (f n) (f (n+1)) ≤ C n * ω (f n) := hstep n
    _ ≤ C n * (productRate q n * ω (f 0)) := mul_le_mul_of_nonneg_left (hbound n) (hC n)
    _ = (C n * productRate q n) * ω (f 0) := (mul_assoc _ _ _).symm

omit [PseudoMetricSpace M] in
theorem geometric_decay (ω : M → ℝ) (f : ℕ → M) (q : ℝ) (hq : 0 ≤ q)
    (hdec : ∀ n, ω (f (n+1)) ≤ q * ω (f n)) :
    ∀ n, ω (f n) ≤ q^n * ω (f 0) := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    calc
      ω (f (n+1)) ≤ q * ω (f n) := hdec n
      _ ≤ q * (q^n * ω (f 0)) := mul_le_mul_of_nonneg_left ih hq
      _ = q^(n+1) * ω (f 0) := by rw [pow_succ]; ring

/-- A posteriori error estimate relative to the residual at level n. -/
theorem geometric_limit_bound (ω : M → ℝ) (f : ℕ → M) (q C : ℝ)
    (hq₀ : 0 ≤ q) (hq₁ : q < 1) (hC : 0 ≤ C)
    (hdec : ∀ n, ω (f (n+1)) ≤ q * ω (f n))
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ C * ω (f n))
    {x : M} (hx : Tendsto f atTop (𝓝 x)) (n : ℕ) :
    dist (f n) x ≤ (C / (1-q)) * ω (f n) := by
  let g : ℕ → M := fun k => f (n+k)
  have hg : Tendsto g atTop (𝓝 x) := by
    simpa only [g, Function.comp_def, Nat.add_comm] using hx.comp (tendsto_add_atTop_nat n)
  have hd : ∀ k, ω (g (k+1)) ≤ q * ω (g k) := by
    intro k; exact hdec (n+k)
  have hb := geometric_decay ω g q hq₀ hd
  have hs : Summable (fun k : ℕ => C * (q^k * ω (f n))) :=
    ((summable_geometric_of_lt_one hq₀ hq₁).mul_right _).mul_left _
  have hst : ∀ k, dist (g k) (g (k+1)) ≤ C * (q^k * ω (f n)) := by
    intro k
    exact (hstep (n+k)).trans (mul_le_mul_of_nonneg_left (hb k) hC)
  have hh := dist_le_tsum_of_dist_le_of_tendsto₀
    (fun k : ℕ => C * (q^k * ω (f n))) hst hs hg
  have hsum : (∑' k : ℕ, C * (q^k * ω (f n))) = (C / (1-q)) * ω (f n) := by
    rw [tsum_mul_left, tsum_mul_right, tsum_geometric_of_lt_one hq₀ hq₁]
    simp [div_eq_mul_inv, mul_assoc]
  simpa only [g, Nat.add_zero, hsum] using hh

/-- Geometric exactification plus the residual-based tail bound. -/
theorem geometric_exactification [CompleteSpace M]
    (ω : M → ℝ) (hω : ∀ x, 0 ≤ ω x) (hlsc : LowerSemicontinuous ω)
    (f : ℕ → M) (q C : ℝ)
    (hq₀ : 0 ≤ q) (hq₁ : q < 1) (hC : 0 ≤ C)
    (hdec : ∀ n, ω (f (n+1)) ≤ q * ω (f n))
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ C * ω (f n)) :
    ∃ x, Tendsto f atTop (𝓝 x) ∧ ω x = 0 ∧
      ∀ n, dist (f n) x ≤ (C / (1-q)) * ω (f n) := by
  have hb := geometric_decay ω f q hq₀ hdec
  have hv : Tendsto (fun n => ω (f n)) atTop (𝓝 0) := by
    apply squeeze_zero (fun n => hω (f n)) hb
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hq₀ hq₁).mul_const (ω (f 0))
  have hs : Summable (fun n : ℕ => C * (q^n * ω (f 0))) :=
    ((summable_geometric_of_lt_one hq₀ hq₁).mul_right _).mul_left _
  have hst : ∀ n, dist (f n) (f (n+1)) ≤ C * (q^n * ω (f 0)) := by
    intro n
    exact (hstep n).trans (mul_le_mul_of_nonneg_left (hb n) hC)
  obtain ⟨x, hx, hw, _⟩ := summable_exactification ω hω hlsc f _ hs hst hv
  exact ⟨x, hx, hw, geometric_limit_bound ω f q C hq₀ hq₁ hC hdec hstep hx⟩

end Exactification

namespace PathIndependence
open Filter
open scoped Topology
variable {M : Type u} [MetricSpace M]

theorem limits_equal_of_distance_vanishes {f g : ℕ → M} {x y : M}
    (hf : Tendsto f atTop (𝓝 x)) (hg : Tendsto g atTop (𝓝 y))
    (hfg : Tendsto (fun n => dist (f n) (g n)) atTop (𝓝 0)) : x = y := by
  exact dist_eq_zero.mp (tendsto_nhds_unique (hf.dist hg) hfg)

theorem limits_equal_of_budget {f g : ℕ → M} {x y : M} (b : ℕ → ℝ)
    (hf : Tendsto f atTop (𝓝 x)) (hg : Tendsto g atTop (𝓝 y))
    (hbudget : ∀ n, dist (f n) (g n) ≤ b n)
    (hb : Tendsto b atTop (𝓝 0)) : x = y := by
  apply limits_equal_of_distance_vanishes hf hg
  exact squeeze_zero (fun _ => dist_nonneg) hbudget hb
end PathIndependence
end KomorebiSpace
