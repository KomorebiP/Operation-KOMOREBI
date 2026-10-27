/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import Mathlib.NumberTheory.LSeries.HurwitzZeta
import Mathlib.Analysis.Meromorphic.Order
import Mathlib.Analysis.Complex.RemovableSingularity

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Complex
open scoped Topology

/-- The entire remainder in Mathlib's regularized Hurwitz representation. -/
def hurwitzRegularPart (a : UnitAddCircle) (s : ℂ) : ℂ :=
  HurwitzZeta.hurwitzZeta a s - (s - 1)⁻¹ * (Gammaℝ s)⁻¹

theorem hurwitzRegularPart_entire (a : UnitAddCircle) :
    Differentiable ℂ (hurwitzRegularPart a) := by
  unfold hurwitzRegularPart
  intro s
  by_cases hs : s = 1
  · subst s
    simpa only [one_div, div_eq_mul_inv, one_mul] using!
      HurwitzZeta.differentiableAt_hurwitzZeta_sub_one_div a
  · exact (HurwitzZeta.differentiableAt_hurwitzZeta a hs).sub
      (((show DifferentiableAt ℂ (fun z : ℂ => z - 1) s by fun_prop).inv (sub_ne_zero.mpr hs)).mul
        (differentiable_Gammaℝ_inv s))

theorem hurwitzZeta_meromorphicAt (a : UnitAddCircle) (s : ℂ) :
    MeromorphicAt (HurwitzZeta.hurwitzZeta a) s := by
  have he : HurwitzZeta.hurwitzZeta a = fun z => hurwitzRegularPart a z +
      (z - 1)⁻¹ * (Gammaℝ z)⁻¹ := by funext z; unfold hurwitzRegularPart; ring
  rw [he]
  exact ((hurwitzRegularPart_entire a).analyticAt s).meromorphicAt.add
    ((((MeromorphicAt.id s).sub (MeromorphicAt.const 1 s)).inv).mul
      ((differentiable_Gammaℝ_inv.analyticAt s).meromorphicAt))

/-- Positive lattice model, with argument scaled by the integer d. -/
def hurwitzLatticeModel (A : ℝ) (d : ℕ) (s : ℂ) : ℂ :=
  exp (-((d : ℂ) * s) * (Real.log A : ℂ)) *
    HurwitzZeta.hurwitzZeta (1 / 2 : ℝ) ((d : ℂ) * s)

theorem hurwitzLatticeModel_meromorphicAt (A : ℝ) (d : ℕ) (s : ℂ) :
    MeromorphicAt (hurwitzLatticeModel A d) s := by
  apply MeromorphicAt.mul
  · exact (show Differentiable ℂ (fun z : ℂ => exp (-((d : ℂ) * z) * (Real.log A : ℂ))) by
      fun_prop).analyticAt s |>.meromorphicAt
  · exact (hurwitzZeta_meromorphicAt _ _).comp_analyticAt (by fun_prop)

theorem hurwitzLatticeModel_differentiableAt {A : ℝ} {d : ℕ} (hd : 0 < d)
    {s : ℂ} (hs : s ≠ 1 / (d : ℂ)) : DifferentiableAt ℂ (hurwitzLatticeModel A d) s := by
  have hd0 : (d : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr hd.ne'
  have hds : (d : ℂ) * s ≠ 1 := by
    intro h
    apply hs
    apply (eq_div_iff hd0).mpr
    simpa only [mul_comm] using h
  apply DifferentiableAt.mul
  · fun_prop
  · exact (HurwitzZeta.differentiableAt_hurwitzZeta _ hds).comp s (by fun_prop)

theorem hurwitzLatticeModel_residue {A : ℝ} (hA : 0 < A) {d : ℕ} (hd : 0 < d) :
    Tendsto (fun s : ℂ => (s - 1 / (d : ℂ)) * hurwitzLatticeModel A d s)
      (𝓝[≠] (1 / (d : ℂ))) (𝓝 (1 / ((d : ℂ) * A))) := by
  have hd0 : (d : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr hd.ne'
  have ht : Tendsto (fun s : ℂ => (d : ℂ) * s) (𝓝[≠] (1 / (d : ℂ))) (𝓝[≠] 1) := by
    rw [tendsto_nhdsWithin_iff]
    constructor
    · simpa only [mul_one_div_cancel hd0] using
        ((show Continuous (fun s : ℂ => (d : ℂ) * s) by fun_prop).tendsto (1 / (d : ℂ))).mono_left nhdsWithin_le_nhds
    · filter_upwards [self_mem_nhdsWithin] with s hs
      change s ≠ 1 / (d : ℂ) at hs
      change (d : ℂ) * s ≠ 1
      intro h
      exact hs ((eq_div_iff hd0).mpr (by simpa only [mul_comm] using h))
  have hz := (HurwitzZeta.hurwitzZeta_residue_one (1 / 2 : ℝ)).comp ht
  have he : Tendsto (fun s : ℂ => exp (-((d : ℂ) * s) * (Real.log A : ℂ)))
      (𝓝[≠] (1 / (d : ℂ))) (𝓝 ((A : ℂ)⁻¹)) := by
    have h := (show Continuous (fun s : ℂ => exp (-((d : ℂ) * s) * (Real.log A : ℂ))) by
      fun_prop).tendsto (1 / (d : ℂ))
    have hv : exp (-((d : ℂ) * (1 / (d : ℂ))) * (Real.log A : ℂ)) = (A : ℂ)⁻¹ := by
      rw [mul_one_div_cancel hd0, neg_one_mul, exp_neg, ← ofReal_exp, Real.exp_log hA]
    rw [hv] at h
    exact h.mono_left nhdsWithin_le_nhds
  have h := (he.mul hz).const_mul (1 / (d : ℂ))
  convert h using 1
  · funext s
    simp only [Function.comp_apply, hurwitzLatticeModel]
    field_simp
  · congr 1
    field_simp

/-- A nonzero punctured residue makes the pole genuinely simple. -/
theorem meromorphicOrderAt_eq_neg_one_of_residue {f : ℂ → ℂ} {p r : ℂ}
    (hf : MeromorphicAt f p) (hd : ∀ z, z ≠ p → DifferentiableAt ℂ f z)
    (hr : r ≠ 0)
    (ht : Tendsto (fun z => (z - p) * f z) (𝓝[≠] p) (𝓝 r)) :
    meromorphicOrderAt f p = (-1 : ℤ) := by
  classical
  let g := Function.update (fun z => (z - p) * f z) p r
  have hg : AnalyticAt ℂ g p := by
    apply Complex.analyticAt_of_differentiable_on_punctured_nhds_of_continuousAt
    · filter_upwards [self_mem_nhdsWithin] with z hz
      have hz0 : z ≠ p := hz
      have he : g =ᶠ[𝓝 z] (fun w => (w - p) * f w) := by
        filter_upwards [eventually_ne_nhds hz0] with w hw
        exact Function.update_of_ne hw _ _
      exact (((differentiableAt_id.sub_const p).mul (hd z hz0))).congr_of_eventuallyEq he
    · exact continuousAt_update_same.mpr ht
  apply (meromorphicOrderAt_eq_int_iff hf).mpr
  refine ⟨g, hg, ?_, ?_⟩
  · simpa only [g, Function.update_self] using hr
  · filter_upwards [self_mem_nhdsWithin] with z hz
    have hz0 : z ≠ p := hz
    simp only [g, Function.update_of_ne hz0, zpow_neg_one, smul_eq_mul]
    field_simp

end
end Komorebi.PaperIV
