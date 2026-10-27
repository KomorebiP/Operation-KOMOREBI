/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.PoleRemoval
import Mathlib.Analysis.Complex.RemovableSingularity

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

def poleNumerator (f : ℂ → ℂ) (ρ : ℂ) (r : ℕ) (t : ℂ) : ℂ :=
  (((-ρ) * dslope f ρ (ρ * (1-t))) ^ r)⁻¹

def canonicalPoleCoefficient (f : ℂ → ℂ) (r : ℕ) (ρ : ℂ) (ℓ : ℕ) : ℂ :=
  analyticTaylorCoefficient (poleNumerator f ρ r) (r-ℓ)

theorem poleNumerator_analyticAt {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {ρ : ℂ} (hρ : ρ ≠ 0) (hd : deriv f ρ ≠ 0) (r : ℕ) : AnalyticAt ℂ (poleNumerator f ρ r) 0 := by
  have hg : Differentiable ℂ (dslope f ρ) := differentiableOn_univ.mp
    ((Complex.differentiableOn_dslope (s := univ) (by simp)).mpr hf.differentiableOn)
  have ha : AnalyticAt ℂ (fun t : ℂ => (-ρ) * dslope f ρ (ρ * (1-t))) 0 := by
    apply analyticAt_const.fun_mul
    exact (hg.analyticAt _).comp (by fun_prop)
  apply (ha.pow r).inv
  change (((-ρ) * dslope f ρ (ρ * (1-(0:ℂ)))) ^ r) ≠ 0
  simp only [sub_zero, mul_one, dslope_same]
  exact pow_ne_zero r (mul_ne_zero (neg_ne_zero.mpr hρ) hd)

theorem canonicalPoleCoefficient_leading (f : ℂ → ℂ) (ρ : ℂ) (r : ℕ) :
    canonicalPoleCoefficient f r ρ r = ((-ρ * deriv f ρ) ^ r)⁻¹ := by
  simp [canonicalPoleCoefficient, analyticTaylorCoefficient, poleNumerator, dslope_same]

theorem poleNumerator_identity {f : ℂ → ℂ} {ρ z : ℂ} (hfρ : f ρ = 0) (hρ : ρ ≠ 0)
    (hz : z ≠ ρ) (r : ℕ) :
    (f z ^ r)⁻¹ = ((1-z/ρ) ^ r)⁻¹ * poleNumerator f ρ r (1-z/ρ) := by
  have ht : 1-z/ρ ≠ 0 := by
    intro h
    exact hz ((div_eq_one_iff_eq hρ).mp (sub_eq_zero.mp h).symm)
  have harg : ρ * (1 - (1-z/ρ)) = z := by field_simp; ring
  have he : f z = (1-z/ρ) * ((-ρ) * dslope f ρ z) := by
    have h := sub_smul_dslope_of_zero hfρ z
    simp only [smul_eq_mul] at h
    rw [← h]
    field_simp
    ring
  rw [poleNumerator, harg, he, mul_pow, mul_inv]

theorem polePrincipalPart_scaled (h : ℂ → ℂ) (r : ℕ) {ρ z : ℂ} (hz : 1-z/ρ ≠ 0) :
    (1-z/ρ) ^ r * polePrincipalPart (fun _ ℓ => analyticTaylorCoefficient h (r-ℓ)) r ρ z =
      ∑ i ∈ Finset.range r, analyticTaylorCoefficient h i * (1-z/ρ) ^ i := by
  classical
  unfold polePrincipalPart poleTerm
  rw [Finset.mul_sum]
  have he : (∑ k ∈ Finset.range r, (1-z/ρ) ^ r *
      (analyticTaylorCoefficient h (r-(k+1)) * ((1-z/ρ) ^ (k+1))⁻¹)) =
      ∑ k ∈ Finset.range r, analyticTaylorCoefficient h (r-1-k) * (1-z/ρ) ^ (r-1-k) := by
    apply Finset.sum_congr rfl
    intro k hk
    have hk' : k+1 ≤ r := Finset.mem_range.mp hk
    have hpow : (1-z/ρ) ^ r = (1-z/ρ) ^ (r-(k+1)) * (1-z/ρ) ^ (k+1) := by
      rw [← pow_add, Nat.sub_add_cancel hk']
    have hidx : r-(k+1) = r-1-k := by omega
    rw [hpow]
    rw [← hidx]
    field_simp
  rw [he]
  exact Finset.sum_range_reflect (fun i => analyticTaylorCoefficient h i * (1-z/ρ) ^ i) r

/-- Simple zeros produce the complete principal parts and the exact leading
coefficient; the local boundedness is proved from analytic Taylor division. -/
theorem canonicalPoleCoefficient_local_bound {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {ρ : ℂ} (hρ : ρ ≠ 0) (hfρ : f ρ = 0) (hd : deriv f ρ ≠ 0) (r : ℕ) :
    ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ,
      ‖(f z ^ r)⁻¹ - polePrincipalPart (canonicalPoleCoefficient f r) r ρ z‖ ≤ C := by
  let h := poleNumerator f ρ r
  obtain ⟨F, hF, he⟩ := (poleNumerator_analyticAt hf hρ hd r).exists_eventuallyEq_sum_add_pow_mul r
  have ht : Tendsto (fun z : ℂ => 1-z/ρ) (𝓝[≠] ρ) (𝓝 0) := by
    have hc : ContinuousAt (fun z : ℂ => 1-z/ρ) ρ := by fun_prop
    simpa [hρ] using hc.tendsto.mono_left nhdsWithin_le_nhds
  have hbound : ∀ᶠ z in 𝓝[≠] ρ, ‖F (1-z/ρ)‖ ≤ ‖F 0‖ + 1 :=
    (hF.continuousAt.norm.tendsto.comp ht).eventually (eventually_le_nhds (by linarith))
  refine ⟨‖F 0‖+1, ?_⟩
  filter_upwards [ht.eventually he, hbound, self_mem_nhdsWithin] with z hz hb hzρ
  have hzne : z ≠ ρ := hzρ
  have htz : 1-z/ρ ≠ 0 := by
    intro hh
    exact hzne ((div_eq_one_iff_eq hρ).mp (sub_eq_zero.mp hh).symm)
  have hp := polePrincipalPart_scaled h r htz
  have hpc : (1-z/ρ) ^ r * polePrincipalPart (canonicalPoleCoefficient f r) r ρ z =
      ∑ i ∈ Finset.range r, analyticTaylorCoefficient h i * (1-z/ρ) ^ i := by
    simpa only [polePrincipalPart, canonicalPoleCoefficient, h] using hp
  have hh : (f z ^ r)⁻¹ - polePrincipalPart (canonicalPoleCoefficient f r) r ρ z = F (1-z/ρ) := by
    rw [poleNumerator_identity hfρ hρ hzne r, hz]
    simp only [smul_eq_mul]
    have hsum : (∑ i ∈ Finset.range r, ((1-z/ρ) ^ i / (i.factorial : ℂ)) * iteratedDeriv i (poleNumerator f ρ r) 0) =
        (1-z/ρ) ^ r * polePrincipalPart (canonicalPoleCoefficient f r) r ρ z := by
      rw [hpc]
      apply Finset.sum_congr rfl
      intro i _
      dsimp [analyticTaylorCoefficient, h]
      ring
    rw [hsum]
    field_simp
    ring
  rw [hh]
  exact hb

end
end Komorebi.PaperIV
