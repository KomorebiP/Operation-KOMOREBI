import KomorebiSpace.HolonomyViews
import KomorebiSpace.KernelProjectionBounds

set_option autoImplicit false

/-!
# Derived orthogonal anchor repair for finite-dimensional holonomy

This instantiates the finite-dimensional kernel bound on the actual rooted
loop differential. The anchor correction and its finite gain are constructed,
not supplied as hypotheses. Vertex and edge products keep their old maximum
norms; only the individual fiber now has an inner-product norm.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
namespace Rooted
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [FiniteDimensional ℝ H]
variable [Fintype V]
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

/-- The same loop residual as v0.18, bundled as a continuous linear map. -/
def rootResidualMap : H →L[ℝ] (OverlapTransport.Edges graph → H) :=
  ContinuousLinearMap.pi fun a =>
    (holonomy T p a).toContinuousLinearMap - ContinuousLinearMap.id ℝ H

omit [Fintype V] in
@[simp] theorem rootResidualMap_apply (z : H) :
    rootResidualMap T p z = rootResidual T p z := rfl

omit [Fintype V] in
theorem rootResidualMap_kernel : (rootResidualMap T p).ker = fixedSpace T p := by
  ext z
  exact rootResidual_zero_iff T p z

/-- Orthogonal projection onto the actual loop-compatible anchor vectors. -/
def anchorProjection : H →L[ℝ] H := KernelProjection.projection (rootResidualMap T p)

/-- The inverse norm on complementary directions, with the original edge max norm. -/
def holonomyGain : ℝ := KernelProjection.gain (rootResidualMap T p)

theorem holonomyGain_nonneg : 0 ≤ holonomyGain T p :=
  KernelProjection.gain_nonneg (rootResidualMap T p)

theorem anchorProjection_fixed (z : H) : anchorProjection T p z ∈ fixedSpace T p := by
  rw [← rootResidualMap_kernel]
  exact KernelProjection.projection_mem (rootResidualMap T p) z

@[simp] theorem anchorProjection_fixes (z : H) (hz : z ∈ fixedSpace T p) :
    anchorProjection T p z = z :=
  KernelProjection.projection_fixes (rootResidualMap T p) z
    ((rootResidual_zero_iff T p z).mpr hz)

@[simp] theorem anchorProjection_idempotent (z : H) :
    anchorProjection T p (anchorProjection T p z) = anchorProjection T p z :=
  anchorProjection_fixes T p _ (anchorProjection_fixed T p z)

theorem anchorProjection_norm (z : H) : ‖anchorProjection T p z‖ ≤ ‖z‖ :=
  KernelProjection.projection_norm (rootResidualMap T p) z

/-- The separate anchor-estimate obligation from v0.18 is discharged here. -/
theorem anchorProjection_error (z : H) :
    ‖z-anchorProjection T p z‖ ≤ holonomyGain T p * ‖rootResidual T p z‖ :=
  KernelProjection.error_bound (rootResidualMap T p) z

theorem anchorProjection_best (z w : H) (hw : w ∈ fixedSpace T p) :
    ‖z-anchorProjection T p z‖ ≤ ‖z-w‖ :=
  KernelProjection.projection_best (rootResidualMap T p) z w
    ((rootResidual_zero_iff T p w).mpr hw)

theorem holonomyGain_optimal (C : ℝ) (hC : 0 ≤ C) :
    (∀ z, ‖z-anchorProjection T p z‖ ≤ C * ‖rootResidual T p z‖) ↔
      holonomyGain T p ≤ C :=
  KernelProjection.gain_characterization (rootResidualMap T p) C hC

/-- The projection is independent of root routes, for a fixed root and inner product. -/
theorem anchorProjection_route_independent (q : OverlapTransport.Routing graph o) :
    anchorProjection T p = anchorProjection T q := by
  apply KernelProjection.projection_eq_of_kernel_eq
  rw [rootResidualMap_kernel, rootResidualMap_kernel,
    fixedSpace_route_independent T p q]

/-- Route reconstruction as a bounded linear map into the existing vertex max norm. -/
def reconstructMap : H →L[ℝ] (V → H) :=
  ContinuousLinearMap.pi fun i => (frame T p i).toContinuousLinearMap

omit [Fintype V] in
@[simp] theorem reconstructMap_apply (z : H) : reconstructMap T p z = reconstruct T p z := rfl

/-- Canonical anchor correction followed by the actual graph reconstruction. -/
def orthogonalRepair : (V → H) →L[ℝ] (V → H) :=
  (reconstructMap T p).comp ((anchorProjection T p).comp (ContinuousLinearMap.proj o))

@[simp] theorem orthogonalRepair_apply (x : V → H) :
    orthogonalRepair T p x = reconstruct T p (anchorProjection T p (x o)) := rfl

@[simp] theorem orthogonalRepair_anchor (x : V → H) :
    orthogonalRepair T p x o = anchorProjection T p (x o) :=
  reconstruct_anchor T p _

theorem orthogonalRepair_parallel (x : V → H) : T.Parallel graph (orthogonalRepair T p x) :=
  (reconstruct_parallel_iff T p _).mpr (anchorProjection_fixed T p (x o))

@[simp] theorem orthogonalRepair_fixes (x : V → H) (hx : T.Parallel graph x) :
    orthogonalRepair T p x = x := by
  rw [orthogonalRepair_apply, anchorProjection_fixes T p _ (parallel_anchor_fixed T p x hx)]
  exact parallel_reconstruction T p x hx

@[simp] theorem orthogonalRepair_idempotent (x : V → H) :
    orthogonalRepair T p (orthogonalRepair T p x) = orthogonalRepair T p x :=
  orthogonalRepair_fixes T p _ (orthogonalRepair_parallel T p x)

theorem orthogonalRepair_norm (x : V → H) : ‖orthogonalRepair T p x‖ ≤ ‖x‖ := by
  rw [orthogonalRepair_apply, reconstruct_norm]
  exact (anchorProjection_norm T p (x o)).trans (norm_le_pi_norm x o)

theorem orthogonalRepair_opNorm : ‖orthogonalRepair T p‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro x
  simpa only [one_mul] using orthogonalRepair_norm T p x

/-- Valid for every candidate, including those with inadmissible original anchors. -/
theorem orthogonalRepair_error (x : V → H) :
    ‖x-orthogonalRepair T p x‖ ≤
      ((p.radius : ℝ) + holonomyGain T p * (2*(p.radius : ℝ)+1)) *
        ‖T.differential graph x‖ :=
  (repair_from_anchor_estimate T p (anchorProjection T p) (holonomyGain T p)
    (holonomyGain_nonneg T p) (anchorProjection_fixed T p) (anchorProjection_error T p) x).2

/-- An exact candidate is uniquely determined by the feasible component of its anchor. -/
theorem orthogonalRepair_unique (x : V → H) :
    ∃! y : V → H, T.Parallel graph y ∧
      anchorProjection T p (y o) = anchorProjection T p (x o) := by
  refine ⟨orthogonalRepair T p x, ⟨orthogonalRepair_parallel T p x, ?_⟩, ?_⟩
  · rw [orthogonalRepair_anchor, anchorProjection_idempotent]
  · intro y hy
    apply parallel_unique T p hy.1 (orthogonalRepair_parallel T p x)
    rw [orthogonalRepair_anchor]
    rw [anchorProjection_fixes T p _ (parallel_anchor_fixed T p y hy.1)] at hy
    exact hy.2

theorem orthogonalRepair_route_independent (q : OverlapTransport.Routing graph o) :
    orthogonalRepair T p = orthogonalRepair T q := by
  ext x i
  change reconstruct T p (anchorProjection T p (x o)) i =
    reconstruct T q (anchorProjection T q (x o)) i
  rw [← anchorProjection_route_independent T p q]
  exact congrFun (reconstruction_route_independent T p q _
    (anchorProjection_fixed T p (x o))) i

/-- An actual old Ambient object, not a renamed numerical candidate. -/
def orthogonalAmbient (x : V → H) : (T.pathViews graph).Ambient :=
  T.toAmbient graph (orthogonalRepair T p x) (orthogonalRepair_parallel T p x)

theorem finite_dimensional_ambient_repair (x : V → H) :
    ∃ s : (T.pathViews graph).Ambient,
      anchorProjection T p (s.val ⟨o⟩) = anchorProjection T p (x o) ∧
      ‖x-T.ambientValues graph s‖ ≤
        ((p.radius : ℝ) + holonomyGain T p * (2*(p.radius : ℝ)+1)) *
          ‖T.differential graph x‖ := by
  refine ⟨orthogonalAmbient T p x, ?_, orthogonalRepair_error T p x⟩
  change anchorProjection T p (orthogonalRepair T p x o) = _
  rw [orthogonalRepair_anchor, anchorProjection_idempotent]

/-- The quantified bound is derived for each fixed finite-dimensional system;
it is not a common constant over all connections. -/
theorem finite_dimensional_stability :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ x : V → H,
      T.Parallel graph (orthogonalRepair T p x) ∧
      ‖x-orthogonalRepair T p x‖ ≤ C * ‖T.differential graph x‖ := by
  refine ⟨(p.radius : ℝ) + holonomyGain T p * (2*(p.radius : ℝ)+1), ?_,
    fun x => ⟨orthogonalRepair_parallel T p x, orthogonalRepair_error T p x⟩⟩
  have hg := holonomyGain_nonneg T p
  positivity

end Rooted
end HolonomyTransport
end KomorebiSpace
end
