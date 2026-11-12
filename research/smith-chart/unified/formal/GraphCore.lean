import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

/-! Finite oriented circuit identities, including parallel edges and loops.
Author: Komorebi P. No connectedness, positivity or nonsingularity is assumed.
-/
namespace SmithGraphCore
open scoped BigOperators

variable {V E W K : Type*} [Fintype V] [Fintype E]
  [DecidableEq V] [DecidableEq W] [CommRing K]

def divergence (src dst : E → V) (current : E → K) (v : V) : K :=
  ∑ e, ((if src e = v then current e else 0) -
         (if dst e = v then current e else 0))

/-- Discrete integration by parts (the finite Tellegen identity). -/
theorem green (src dst : E → V) (current : E → K) (potential : V → K) :
    (∑ v, potential v * divergence src dst current v) =
      ∑ e, (potential (src e) - potential (dst e)) * current e := by
  classical
  simp_rw [divergence, Finset.mul_sum, mul_sub]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro e he
  simp [Finset.sum_sub_distrib, mul_ite, sub_mul]

/-- Sum KCL over a contraction fibre. Internal currents cancel exactly. -/
theorem contraction (src dst : E → V) (current : E → K) (quotient : V → W) (w : W) :
    (∑ v, if quotient v = w then divergence src dst current v else 0) =
      divergence (quotient ∘ src) (quotient ∘ dst) current w := by
  have h := green src dst current (fun v => if quotient v = w then (1 : K) else 0)
  simpa [divergence, sub_mul, ite_mul, Function.comp_def] using h

/- A branch contracted to a loop has no remaining divergence contribution. -/
omit [Fintype V] [Fintype E] [DecidableEq V] in
theorem wire_cancels (src dst : E → V) (current : E → K) (quotient : V → W)
    (e : E) (w : W) (hwire : quotient (src e) = quotient (dst e)) :
    (if quotient (src e) = w then current e else 0) -
      (if quotient (dst e) = w then current e else 0) = 0 := by
  rw [hwire]
  simp

/-- Contracted KCL has exactly the summed original injections. -/
theorem contraction_kcl (src dst : E → V) (current : E → K)
    (quotient : V → W) (injection : V → K)
    (hkcl : ∀ v, divergence src dst current v = injection v) (w : W) :
    divergence (quotient ∘ src) (quotient ∘ dst) current w =
      ∑ v, if quotient v = w then injection v else 0 := by
  rw [← contraction]
  simp_rw [hkcl]

/- Removing branches collapsed to loops cannot increase the storage count. -/
omit [Fintype V] [DecidableEq V] in
theorem contraction_storage_bound (src dst : E → V) (quotient : V → W)
    (storage : E → Prop) [DecidablePred storage] :
    (Finset.univ.filter (fun e => storage e ∧ quotient (src e) ≠ quotient (dst e))).card ≤
      (Finset.univ.filter storage).card := by
  apply Finset.card_le_card
  intro e he
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at *
  exact he.1

def portInjection (a b : V) (current : K) (v : V) : K :=
  (if a = v then current else 0) - (if b = v then current else 0)

/-- Tellegen's identity with only the two physical terminal injections. -/
theorem port_green (src dst : E → V) (current : E → K) (potential : V → K)
    (a b : V) (injected : K)
    (hkcl : ∀ v, divergence src dst current v = portInjection a b injected v) :
    (∑ e, (potential (src e) - potential (dst e)) * current e) =
      (potential a - potential b) * injected := by
  rw [← green]
  simp_rw [hkcl]
  simp [portInjection, mul_sub, Finset.sum_sub_distrib, mul_ite, sub_mul]

/-- Two solutions on one graph satisfy the bilinear impedance-change identity. -/
theorem impedance_change (src dst : E → V) (i j z w : E → K)
    (u v : V → K) (a b : V) (I J : K)
    (hi : ∀ n, divergence src dst i n = portInjection a b I n)
    (hj : ∀ n, divergence src dst j n = portInjection a b J n)
    (hu : ∀ e, u (src e) - u (dst e) = z e * i e)
    (hv : ∀ e, v (src e) - v (dst e) = w e * j e) :
    (∑ e, (w e - z e) * i e * j e) =
      (v a - v b) * I - (u a - u b) * J := by
  have h₁ := port_green src dst j u a b J hj
  have h₂ := port_green src dst i v a b I hi
  simp_rw [hu] at h₁
  simp_rw [hv] at h₂
  rw [← h₁, ← h₂, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro e he
  ring

end SmithGraphCore

namespace SmithPortPower
/-- Unit-source/unit-series-resistor normalization, at complex frequency. -/
theorem power_identity (v : ℂ) :
    4 * (v * star (1-v)).re = 1 - Complex.normSq (2*v-1) := by
  simp [Complex.normSq, Complex.mul_re, Complex.mul_im, Complex.sub_re,
    Complex.sub_im]
  ring

/-- The combined dissipative and same-sign reactive sensitivity budget is <= 1. -/
theorem sensitivity_budget (x y : ℝ) :
    (1-(x^2+y^2))/2 + |y| ≤ 1 := by
  nlinarith [sq_nonneg x, sq_nonneg (|y|-1), sq_abs y]

/-- The elementary rational majorant at one percent tolerance. -/
theorem one_percent_bound : ((1/100 : ℝ)/(1-1/100)) = 1/99 := by norm_num

end SmithPortPower
