import Komorebi.SufficientResolution.MetricRepresentatives
import Komorebi.SufficientResolution.ObstructionTransport

/-!
# Quantitative transport on the existing obstruction quotients

The induced algebraic presentation map is not replaced. A supplied whole-local-map
bound makes it bounded for the actual quotient norms. A bounded reverse map is a
separate requirement for quantitative reflection.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MetricObstructionTransport

open Globalization Globalization.PresentationMap
open OrthogonalResolution HilbertGlobalization MetricObstruction MetricRepresentatives

variable {G V W G' V' W' : Type*}
variable [AddCommGroup G] [Module ℝ G] [AddCommGroup G'] [Module ℝ G']
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup V'] [InnerProductSpace ℝ V']
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable [NormedAddCommGroup W'] [NormedSpace ℝ W']
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)
variable (A' : G' →ₗ[ℝ] V') (delta' : V' →L[ℝ] W')
variable [(LinearMap.range A).HasOrthogonalProjection] [delta.ker.HasOrthogonalProjection]
variable (f : PresentationMap A delta.toLinearMap A' delta'.toLinearMap)

/-- A bound on the whole local map descends to the actual obstruction quotient. -/
theorem obstructionMap_norm_le (h : delta.toLinearMap.comp A = 0)
    (C : ℝ) (hL : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖)
    (z : ObstructionSpace A delta.toLinearMap) : ‖f.obstructionMap z‖ ≤ C * ‖z‖ := by
  let v := minimumRepresentative A delta h z
  have hv : obstructionClass A delta.toLinearMap v = z := class_minimumRepresentative A delta h z
  calc
    ‖f.obstructionMap z‖ = ‖obstructionClass A' delta'.toLinearMap (f.kernelMap v)‖ := by
      rw [← hv, f.obstructionMap_class]
    _ ≤ ‖f.kernelMap v‖ := Submodule.Quotient.norm_mk_le _ _
    _ ≤ C * ‖z‖ := by
      change ‖f.localMap (v : V)‖ ≤ C * ‖z‖
      have hb := hL (v : V)
      rw [← minimumRepresentative_norm A delta h z]
      exact hb

/-- The old obstruction map, now bundled as a bounded linear map. -/
def boundedObstructionMap (h : delta.toLinearMap.comp A = 0)
    (C : ℝ) (hL : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖) :
    ObstructionSpace A delta.toLinearMap →L[ℝ] ObstructionSpace A' delta'.toLinearMap :=
  f.obstructionMap.mkContinuous C (obstructionMap_norm_le A delta A' delta' f h C hL)

theorem boundedObstructionMap_apply (h : delta.toLinearMap.comp A = 0)
    (C : ℝ) (hL : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖)
    (z : ObstructionSpace A delta.toLinearMap) :
    boundedObstructionMap A delta A' delta' f h C hL z = f.obstructionMap z := rfl

theorem boundedObstructionMap_opNorm (h : delta.toLinearMap.comp A = 0)
    (C : ℝ) (hC : 0 ≤ C) (hL : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖) :
    ‖boundedObstructionMap A delta A' delta' f h C hL‖ ≤ C :=
  ContinuousLinearMap.opNorm_le_bound _ hC (obstructionMap_norm_le A delta A' delta' f h C hL)

theorem obstructionMap_distance (h : delta.toLinearMap.comp A = 0)
    (C : ℝ) (hL : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖)
    (z w : ObstructionSpace A delta.toLinearMap) :
    dist (f.obstructionMap z) (f.obstructionMap w) ≤ C * dist z w := by
  simp only [dist_eq_norm, ← map_sub]
  exact obstructionMap_norm_le A delta A' delta' f h C hL (z-w)

variable [(LinearMap.range A').HasOrthogonalProjection] [delta'.ker.HasOrthogonalProjection]

theorem harmonic_transport_formula (h : delta.toLinearMap.comp A = 0)
    (h' : delta'.toLinearMap.comp A' = 0) (z : ObstructionSpace A delta.toLinearMap) :
    (quotientToHarmonic A' delta' h' (f.obstructionMap z) : V') =
      obstruction (LinearMap.range A') delta'.ker
        (f.localMap (minimumRepresentative A delta h z : V)) := by
  conv_lhs => rw [← class_minimumRepresentative A delta h z, f.obstructionMap_class]
  rfl

omit [(LinearMap.range A).HasOrthogonalProjection] [delta.ker.HasOrthogonalProjection] in
/-- Forward continuity does not imply reflection; a reverse-map certificate supplies it. -/
theorem reverse_bound (h' : delta'.toLinearMap.comp A' = 0)
    (g : PresentationMap A' delta'.toLinearMap A delta.toLinearMap)
    (M : ℝ) (hg : ∀ v : V', ‖g.localMap v‖ ≤ M * ‖v‖)
    (hgf : g.obstructionMap.comp f.obstructionMap = LinearMap.id)
    (z : ObstructionSpace A delta.toLinearMap) :
    ‖z‖ ≤ M * ‖f.obstructionMap z‖ := by
  have he : g.obstructionMap (f.obstructionMap z) = z := LinearMap.congr_fun hgf z
  rw [← he]
  conv_rhs => rw [he]
  exact obstructionMap_norm_le A' delta' A delta g h' M hg (f.obstructionMap z)

theorem two_sided_bound (h : delta.toLinearMap.comp A = 0)
    (h' : delta'.toLinearMap.comp A' = 0)
    (g : PresentationMap A' delta'.toLinearMap A delta.toLinearMap)
    (C M : ℝ) (hM : 0 < M)
    (hf : ∀ v : V, ‖f.localMap v‖ ≤ C * ‖v‖)
    (hg : ∀ v : V', ‖g.localMap v‖ ≤ M * ‖v‖)
    (hgf : g.obstructionMap.comp f.obstructionMap = LinearMap.id)
    (z : ObstructionSpace A delta.toLinearMap) :
    ‖z‖ / M ≤ ‖f.obstructionMap z‖ ∧ ‖f.obstructionMap z‖ ≤ C * ‖z‖ := by
  refine ⟨(div_le_iff₀ hM).mpr ?_, obstructionMap_norm_le A delta A' delta' f h C hf z⟩
  simpa only [mul_comm] using reverse_bound A delta A' delta' f h' g M hg hgf z

end Komorebi.SufficientResolution.MetricObstructionTransport
