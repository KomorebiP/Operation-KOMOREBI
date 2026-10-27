import ReleaseRectifiable
import ReleaseArcLength

/-! # Constructed integral cycles from continuous rectifiable closed curves
The geometric total variation and trace are preserved by the construction.
Identification of integral-norm velocity length with geometric total variation,
and invariance of classical contour integrals, are separate obligations. -/

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseRectifiableCycle
open Set
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseRectifiable
open Komorebi.PaperII.ReleaseArcLength

/-- A finite family of genuinely continuous bounded-variation closed paths
produces an integral cycle by arclength and coordinatewise differentiation. -/
def cycleOfRectifiable (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) : IntegralCycle :=
  cycleOfLipschitz n (fun i ↦ unitIntervalPath (f i))
    (fun i ↦ ⟨geometricLength (f i), ENNReal.toReal_nonneg⟩)
    (fun i ↦ by simpa only [uIcc_of_le (by norm_num : (0:ℝ) ≤ 1)] using
      unitIntervalPath_lipschitz (hv i) (hc i))
    (fun i ↦ unitIntervalPath_closed (hv i) (hclosed i))

theorem curve_cycleOfRectifiable (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) (s : ℝ) (hs : s ∈ Icc (0:ℝ) 1) :
    (cycleOfRectifiable n f hv hc hclosed).curve i s = unitIntervalPath (f i) s := by
  apply curve_cycleOfLipschitz
  simpa only [uIcc_of_le (by norm_num : (0:ℝ) ≤ 1)] using hs

/-- Each curve preserves the complete geometric trace. -/
theorem image_curve_cycleOfRectifiable (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) :
    (cycleOfRectifiable n f hv hc hclosed).curve i '' Icc (0:ℝ) 1 =
      f i '' Icc (0:ℝ) 1 := by
  calc
    _ = unitIntervalPath (f i) '' Icc (0:ℝ) 1 :=
      image_congr (fun s hs ↦ curve_cycleOfRectifiable n f hv hc hclosed i s hs)
    _ = _ := unitIntervalPath_image (hv i) (hc i)

/-- The actual integral cycle has the union of the original traces. -/
theorem trace_cycleOfRectifiable (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) :
    (cycleOfRectifiable n f hv hc hclosed).trace =
      {z | ∃ i : Fin n, z ∈ f i '' Icc (0:ℝ) 1} := by
  ext z
  change (∃ i s, s ∈ uIcc (0:ℝ) 1 ∧
    (cycleOfRectifiable n f hv hc hclosed).curve i s = z) ↔ _
  simp only [uIcc_of_le (by norm_num : (0:ℝ) ≤ 1)]
  constructor
  · rintro ⟨i,s,hs,hz⟩
    refine ⟨i, ?_⟩
    rw [← image_curve_cycleOfRectifiable n f hv hc hclosed i]
    exact ⟨s,hs,hz⟩
  · rintro ⟨i,hz⟩
    rw [← image_curve_cycleOfRectifiable n f hv hc hclosed i] at hz
    obtain ⟨s,hs,hz⟩ := hz
    exact ⟨i,s,hs,hz⟩

/-- Geometric length of every reconstructed curve, expressed as variation,
is exactly the original geometric length. This theorem does not identify the
separately defined velocity-integral length. -/
theorem variation_curve_cycleOfRectifiable (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) :
    eVariationOn ((cycleOfRectifiable n f hv hc hclosed).curve i) (Icc (0:ℝ) 1) =
      eVariationOn (f i) (Icc (0:ℝ) 1) := by
  calc
    _ = eVariationOn (unitIntervalPath (f i)) (Icc (0:ℝ) 1) :=
      eVariationOn.eq_of_eqOn (fun s hs ↦ curve_cycleOfRectifiable n f hv hc hclosed i s hs)
    _ = _ := unitIntervalPath_variation (hv i) (hc i)

end Komorebi.PaperII.ReleaseRectifiableCycle
