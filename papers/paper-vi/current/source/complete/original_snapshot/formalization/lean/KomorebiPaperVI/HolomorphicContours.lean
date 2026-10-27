import KomorebiPaperVI.ContourNaturality
import Mathlib.Topology.Instances.Matrix
import Mathlib.Analysis.Analytic.Basic

/-! Author: Komorebi P. Holomorphic input supplies integrability on common resolvent circles.
The canonical finite-dimensional construction and its local Cauchy-circle independence
are supplied by HolomorphicFinite. -/
namespace KomorebiPaperVI.HolomorphicContours
open Set Complex
open KomorebiPaperVI.ContourNaturality
set_option backward.isDefEq.respectTransparency false
variable {I J K : Type*} [Fintype I] [Fintype J] [Fintype K] [DecidableEq I] [DecidableEq J]

omit [Fintype J] [Fintype K] [DecidableEq J] in
theorem resolvent_continuousAt (A : Matrix I I ℂ) (z : ℂ) (hz : IsUnit (Matrix.scalar I z-A)) :
    ContinuousAt (ContourNaturality.resolvent A) z := by
  have hd : (Matrix.scalar I z-A).det ≠ 0 :=
    (Matrix.isUnit_iff_isUnit_det _).mp hz |>.ne_zero
  have hi : ContinuousAt Ring.inverse (Matrix.scalar I z-A).det := by
    rw [Ring.inverse_eq_inv']
    exact continuousAt_inv₀ hd
  have hc : Continuous (fun w : ℂ => Matrix.scalar I w-A) := by
    apply continuous_matrix
    intro i j
    simp only [Matrix.sub_apply,Matrix.scalar_apply,Matrix.diagonal_apply]
    split_ifs <;> fun_prop
  change ContinuousAt (fun w : ℂ => (Matrix.scalar I w-A)⁻¹) z
  exact (continuousAt_matrix_inv _ hi).comp (x := z) hc.continuousAt

omit [Fintype J] [Fintype K] [DecidableEq J] in
theorem holomorphic_circle_integrable (A : Matrix I I ℂ) (f : ℂ → ℂ) (U : Set ℂ)
    (hf : AnalyticOnNhd ℂ f U) (c : ℂ) (r : ℝ) (hr : 0 ≤ r)
    (hc : Metric.sphere c r ⊆ U)
    (hA : ∀ z∈Metric.sphere c r,IsUnit (Matrix.scalar I z-A)) (i j : I) :
    CircleIntegrable (fun z => f z*ContourNaturality.resolvent A z i j) c r := by
  apply ContinuousOn.circleIntegrable hr
  apply (hf.continuousOn.mono hc).mul
  intro z hz
  have ht := resolvent_continuousAt A z (hA z hz)
  exact ((continuous_apply j).continuousAt.comp ((continuous_apply i).continuousAt.comp ht)).continuousWithinAt

theorem holomorphic_common_contour_naturality (C : Matrix J I ℂ) (A : Matrix I I ℂ) (B : Matrix J J ℂ)
    (h : C*A=B*C) (f : ℂ → ℂ) (U : Set ℂ) (hf : AnalyticOnNhd ℂ f U)
    (c : K → ℂ) (r : K → ℝ) (hr : ∀ k,0 ≤ r k)
    (hc : ∀ k,Metric.sphere (c k) (r k) ⊆ U)
    (hA : ∀ k z,z∈Metric.sphere (c k) (r k) → IsUnit (Matrix.scalar I z-A))
    (hB : ∀ k z,z∈Metric.sphere (c k) (r k) → IsUnit (Matrix.scalar J z-B)) :
    C*calculus A f c r=calculus B f c r*C :=
  common_contour_naturality C A B h f c r hr hA hB
    (fun k i j => holomorphic_circle_integrable A f U hf (c k) (r k) (hr k) (hc k) (hA k) i j)
    (fun k i j => holomorphic_circle_integrable B f U hf (c k) (r k) (hr k) (hc k) (hB k) i j)

end KomorebiPaperVI.HolomorphicContours
