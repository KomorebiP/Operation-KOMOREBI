/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SimplePoleParts

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

theorem polePrincipalPart_scaled_general (a : ℂ → ℕ → ℂ) (r : ℕ) {ρ z : ℂ} (hz : 1-z/ρ ≠ 0) :
    (1-z/ρ) ^ r * polePrincipalPart a r ρ z =
      ∑ k ∈ Finset.range r, a ρ (k+1) * (1-z/ρ) ^ (r-1-k) := by
  unfold polePrincipalPart poleTerm
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro k hk
  have hk' : k+1 ≤ r := Finset.mem_range.mp hk
  have hpow : (1-z/ρ) ^ r = (1-z/ρ) ^ (r-(k+1)) * (1-z/ρ) ^ (k+1) := by
    rw [← pow_add, Nat.sub_add_cancel hk']
  rw [hpow, show r-1-k = r-(k+1) by omega]
  field_simp

theorem polePrincipalPart_scaled_limit (a : ℂ → ℕ → ℂ) {r : ℕ} (hr : 0 < r)
    {ρ : ℂ} (hρ : ρ ≠ 0) :
    Tendsto (fun z => (1-z/ρ) ^ r * polePrincipalPart a r ρ z) (𝓝[≠] ρ) (𝓝 (a ρ r)) := by
  let P : ℂ → ℂ := fun z => ∑ k ∈ Finset.range r, a ρ (k+1) * (1-z/ρ) ^ (r-1-k)
  have hc : ContinuousAt P ρ := by dsimp [P]; fun_prop
  have heval : P ρ = a ρ r := by
    simp only [P, div_self hρ, sub_self]
    rw [Finset.sum_eq_single (r-1)]
    · simp [show r-1+1 = r by omega]
    · intro k hk hkne
      have hpow : r-1-k ≠ 0 := by have := Finset.mem_range.mp hk; omega
      simp [hpow]
    · intro hn
      exact (hn (Finset.mem_range.mpr (by omega))).elim
  have hlim : Tendsto P (𝓝[≠] ρ) (𝓝 (P ρ)) := hc.tendsto.mono_left nhdsWithin_le_nhds
  rw [heval] at hlim
  apply hlim.congr'
  filter_upwards [self_mem_nhdsWithin] with z hz
  have ht : 1-z/ρ ≠ 0 := by
    intro h
    exact hz ((div_eq_one_iff_eq hρ).mp (sub_eq_zero.mp h).symm)
  exact (polePrincipalPart_scaled_general a r ht).symm

/-- Any principal part satisfying the manuscript's O(1) condition has the
same leading Laurent coefficient as the constructed analytic principal part. -/
theorem principalPart_leading_coefficient {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {ρ : ℂ} (hρ : ρ ≠ 0) (hfρ : f ρ = 0) (hd : deriv f ρ ≠ 0)
    {r : ℕ} (hr : 0 < r) (a : ℂ → ℕ → ℂ)
    (hb : ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ, ‖(f z ^ r)⁻¹ - polePrincipalPart a r ρ z‖ ≤ C) :
    a ρ r = ((-ρ * deriv f ρ) ^ r)⁻¹ := by
  have ht : Tendsto (fun z : ℂ => 1-z/ρ) (𝓝[≠] ρ) (𝓝 0) := by
    have hc : ContinuousAt (fun z : ℂ => 1-z/ρ) ρ := by fun_prop
    simpa [hρ] using hc.tendsto.mono_left nhdsWithin_le_nhds
  have hn := (poleNumerator_analyticAt hf hρ hd r).continuousAt.tendsto.comp ht
  have hnum : Tendsto (fun z : ℂ => (1-z/ρ)^r * (f z ^ r)⁻¹) (𝓝[≠] ρ)
      (𝓝 (((-ρ * deriv f ρ) ^ r)⁻¹)) := by
    simp only [poleNumerator, sub_zero, mul_one, dslope_same] at hn
    apply hn.congr'
    filter_upwards [self_mem_nhdsWithin] with z hz
    have htz : 1-z/ρ ≠ 0 := by
      intro h
      exact hz ((div_eq_one_iff_eq hρ).mp (sub_eq_zero.mp h).symm)
    rw [poleNumerator_identity hfρ hρ hz r]
    rw [← mul_assoc, mul_inv_cancel₀ (pow_ne_zero r htz), one_mul]
    rfl
  have hzero : Tendsto (fun z : ℂ => (1-z/ρ)^r) (𝓝[≠] ρ) (𝓝 0) := by simpa [hr.ne'] using ht.pow r
  have hrem := hzero.zero_mul_isBoundedUnder_le hb
  have hdiff := hnum.sub (polePrincipalPart_scaled_limit a hr hρ)
  have hEq : ((-ρ * deriv f ρ) ^ r)⁻¹ - a ρ r = 0 :=
    tendsto_nhds_unique hdiff (by simpa only [mul_sub] using hrem)
  exact (sub_eq_zero.mp hEq).symm

end
end Komorebi.PaperIV
