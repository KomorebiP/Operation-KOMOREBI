import Mathlib.Analysis.ConstantSpeed
import Mathlib.Topology.Order.IntermediateValue

/-! # Arclength parameterization of continuous rectifiable complex paths
This constructs a Lipschitz path on the unit interval from bounded variation,
with exact recovery through the monotone cumulative-length map. -/

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseArcLength
open Set
open scoped NNReal ENNReal

/-- Unit metric speed controls distances, including noninjective paths. -/
theorem unitSpeed_lipschitz {g : ℝ → ℂ} {s : Set ℝ}
    (hg : HasUnitSpeedOn g s) : LipschitzOnWith 1 g s := by
  apply LipschitzOnWith.of_dist_le_mul
  intro x hx y hy
  rcases le_total x y with hxy | hyx
  · have hb := hg.hasLocallyBoundedVariationOn x y hx hy
    have hd := hb.dist_le (show x ∈ s ∩ Icc x y from ⟨hx, le_rfl, hxy⟩)
      (show y ∈ s ∩ Icc x y from ⟨hy, hxy, le_rfl⟩)
    rw [hg hx hy] at hd
    simpa only [NNReal.coe_one, one_mul, ENNReal.toReal_ofReal (sub_nonneg.mpr hxy),
      Real.dist_eq, abs_of_nonpos (sub_nonpos.mpr hxy), neg_sub] using hd
  · have hb := hg.hasLocallyBoundedVariationOn y x hy hx
    have hd := hb.dist_le (show y ∈ s ∩ Icc y x from ⟨hy, le_rfl, hyx⟩)
      (show x ∈ s ∩ Icc y x from ⟨hx, hyx, le_rfl⟩)
    rw [hg hy hx] at hd
    simpa only [NNReal.coe_one, one_mul, ENNReal.toReal_ofReal (sub_nonneg.mpr hyx),
      Real.dist_eq, abs_of_nonneg (sub_nonneg.mpr hyx), dist_comm] using hd

def geometricLength (f : ℝ → ℂ) : ℝ := (eVariationOn f (Icc (0:ℝ) 1)).toReal

def arcMap (f : ℝ → ℂ) : ℝ → ℝ := variationOnFromTo f (Icc 0 1) 0

def arcPath (f : ℝ → ℂ) : ℝ → ℂ := naturalParameterization f (Icc 0 1) 0

def unitIntervalPath (f : ℝ → ℂ) (s : ℝ) : ℂ := arcPath f (geometricLength f * s)

@[simp] theorem arcMap_zero (f : ℝ → ℂ) : arcMap f 0 = 0 := by
  simp only [arcMap, variationOnFromTo.self]

@[simp] theorem arcMap_one (f : ℝ → ℂ) : arcMap f 1 = geometricLength f := by
  rw [arcMap, variationOnFromTo.eq_of_le f (Icc 0 1) (by norm_num : (0:ℝ) ≤ 1)]
  simp only [inter_self, geometricLength]

theorem arcMap_monotone {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1)) :
    MonotoneOn (arcMap f) (Icc (0:ℝ) 1) :=
  variationOnFromTo.monotoneOn hf.locallyBoundedVariationOn (by norm_num)

theorem arcMap_continuous {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) : ContinuousOn (arcMap f) (Icc (0:ℝ) 1) := by
  intro x hx
  exact (hf.continuousWithinAt_variationOnFromTo_iff (by norm_num) hx).mpr (hc x hx)

theorem arcMap_image {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) :
    arcMap f '' Icc (0:ℝ) 1 = Icc 0 (geometricLength f) := by
  simpa only [arcMap_zero, arcMap_one] using
    (arcMap_continuous hf hc).image_Icc_of_monotoneOn (by norm_num) (arcMap_monotone hf)

/-- Reconstruction is pointwise equality in the genuine metric complex plane. -/
theorem arcPath_recovers {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (s : ℝ) (hs : s ∈ Icc (0:ℝ) 1) : arcPath f (arcMap f s) = f s := by
  exact edist_eq_zero.mp
    (edist_naturalParameterization_eq_zero hf.locallyBoundedVariationOn (by norm_num) hs)

theorem arcPath_unitSpeed {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) :
    HasUnitSpeedOn (arcPath f) (Icc 0 (geometricLength f)) := by
  have h := has_unit_speed_naturalParameterization f hf.locallyBoundedVariationOn
    (show (0:ℝ) ∈ Icc (0:ℝ) 1 by norm_num)
  change HasUnitSpeedOn (arcPath f) (arcMap f '' Icc (0:ℝ) 1) at h
  rwa [arcMap_image hf hc] at h

theorem scale_image (L : ℝ) (hL : 0 ≤ L) :
    (fun s : ℝ ↦ L * s) '' Icc (0:ℝ) 1 = Icc 0 L := by
  have hm : MonotoneOn (fun s : ℝ ↦ L * s) (Icc (0:ℝ) 1) :=
    fun _ _ _ _ hxy ↦ mul_le_mul_of_nonneg_left hxy hL
  simpa only [mul_zero, mul_one] using
    (continuous_const.mul continuous_id).continuousOn.image_Icc_of_monotoneOn
      (by norm_num : (0:ℝ) ≤ 1) hm

theorem unitIntervalPath_lipschitz {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) :
    LipschitzOnWith ⟨geometricLength f, ENNReal.toReal_nonneg⟩
      (unitIntervalPath f) (Icc (0:ℝ) 1) := by
  have hg := unitSpeed_lipschitz (arcPath_unitSpeed hf hc)
  have hmap : MapsTo (fun s : ℝ ↦ geometricLength f * s) (Icc (0:ℝ) 1)
      (Icc 0 (geometricLength f)) := by
    intro s hs
    rw [← scale_image (geometricLength f) ENNReal.toReal_nonneg]
    exact mem_image_of_mem _ hs
  apply LipschitzOnWith.of_dist_le_mul
  intro x hx y hy
  calc
    dist (unitIntervalPath f x) (unitIntervalPath f y) ≤
        dist (geometricLength f * x) (geometricLength f * y) := by
      simpa only [NNReal.coe_one, one_mul, unitIntervalPath] using
        hg.dist_le_mul _ (hmap hx) _ (hmap hy)
    _ = geometricLength f * dist x y := by
      rw [dist_eq_norm, ← mul_sub, norm_mul, Real.norm_of_nonneg ENNReal.toReal_nonneg,
        dist_eq_norm]

@[simp] theorem unitIntervalPath_zero {f : ℝ → ℂ}
    (hf : BoundedVariationOn f (Icc (0:ℝ) 1)) : unitIntervalPath f 0 = f 0 := by
  simpa only [unitIntervalPath, mul_zero, arcMap_zero] using arcPath_recovers hf 0 (by norm_num)

@[simp] theorem unitIntervalPath_one {f : ℝ → ℂ}
    (hf : BoundedVariationOn f (Icc (0:ℝ) 1)) : unitIntervalPath f 1 = f 1 := by
  simpa only [unitIntervalPath, mul_one, arcMap_one] using arcPath_recovers hf 1 (by norm_num)

theorem unitIntervalPath_closed {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hclosed : f 1 = f 0) : unitIntervalPath f 1 = unitIntervalPath f 0 := by
  rw [unitIntervalPath_one hf, unitIntervalPath_zero hf, hclosed]

/-- The arclength construction preserves the trace, even when length is zero. -/
theorem unitIntervalPath_image {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) :
    unitIntervalPath f '' Icc (0:ℝ) 1 = f '' Icc (0:ℝ) 1 := by
  have hcomp : (arcPath f ∘ arcMap f) '' Icc (0:ℝ) 1 = f '' Icc (0:ℝ) 1 := by
    apply image_congr
    intro s hs
    exact arcPath_recovers hf s hs
  rw [image_comp, arcMap_image hf hc] at hcomp
  change (arcPath f ∘ (fun s : ℝ ↦ geometricLength f * s)) '' Icc (0:ℝ) 1 = _
  rw [image_comp, scale_image _ ENNReal.toReal_nonneg]
  exact hcomp

/-- Total geometric variation is preserved by the constructed reparameterization. -/
theorem unitIntervalPath_variation {f : ℝ → ℂ} (hf : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1)) :
    eVariationOn (unitIntervalPath f) (Icc (0:ℝ) 1) = eVariationOn f (Icc (0:ℝ) 1) := by
  have hm : MonotoneOn (fun s : ℝ ↦ geometricLength f * s) (Icc (0:ℝ) 1) :=
    fun _ _ _ _ hxy ↦ mul_le_mul_of_nonneg_left hxy ENNReal.toReal_nonneg
  change eVariationOn (arcPath f ∘ (fun s : ℝ ↦ geometricLength f * s)) (Icc (0:ℝ) 1) = _
  rw [eVariationOn.comp_eq_of_monotoneOn _ _ hm, scale_image _ ENNReal.toReal_nonneg]
  have hu := arcPath_unitSpeed hf hc
  have hvar := hu (show (0:ℝ) ∈ Icc 0 (geometricLength f) from ⟨le_rfl, ENNReal.toReal_nonneg⟩)
    (show geometricLength f ∈ Icc 0 (geometricLength f) from ⟨ENNReal.toReal_nonneg, le_rfl⟩)
  simpa only [inter_self, NNReal.coe_one, one_mul, sub_zero,
    geometricLength, ENNReal.ofReal_toReal hf] using hvar

end Komorebi.PaperII.ReleaseArcLength
