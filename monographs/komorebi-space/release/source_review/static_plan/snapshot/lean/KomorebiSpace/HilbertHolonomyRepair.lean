import KomorebiSpace.AmplifiedViews
import KomorebiSpace.HilbertKernelProjection

set_option autoImplicit false

/-!
# Infinite-dimensional amplified holonomy reconstruction

The fiber is a real Hilbert space, not necessarily finite dimensional.
Orthogonal anchor repair exists without a range hypothesis. A global
residual-to-repair estimate holds precisely when the actual holonomy
operator has closed range. The old finite-dimensional repair is retained.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
namespace Rooted
namespace Hilbert
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H] [Fintype V]
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

/-- Orthogonality is on the anchor fiber, not the vertex maximum norm. -/
def anchorProjection : H →L[ℝ] H := HilbertKernelProjection.projection (rootResidualMap T p)

variable (hr : IsClosed (Set.range (rootResidualMap T p)))

def holonomyGain : ℝ := HilbertKernelProjection.gain (rootResidualMap T p) hr

theorem holonomyGain_nonneg : 0 ≤ holonomyGain T p hr :=
  HilbertKernelProjection.gain_nonneg (rootResidualMap T p) hr

theorem anchorProjection_fixed (z : H) : anchorProjection T p z ∈ fixedSpace T p := by
  rw [← rootResidualMap_kernel]
  exact HilbertKernelProjection.projection_mem (rootResidualMap T p) z

@[simp] theorem anchorProjection_fixes (z : H) (hz : z ∈ fixedSpace T p) :
    anchorProjection T p z = z := by
  apply HilbertKernelProjection.projection_fixes
  change z ∈ (rootResidualMap T p).ker
  rw [rootResidualMap_kernel]
  exact hz

@[simp] theorem anchorProjection_idempotent (z : H) :
    anchorProjection T p (anchorProjection T p z) = anchorProjection T p z :=
  anchorProjection_fixes T p _ (anchorProjection_fixed T p z)

theorem anchorProjection_norm (z : H) : ‖anchorProjection T p z‖ ≤ ‖z‖ :=
  HilbertKernelProjection.projection_norm (rootResidualMap T p) z

theorem anchorProjection_error (z : H) :
    ‖z-anchorProjection T p z‖ ≤ holonomyGain T p hr * ‖rootResidualMap T p z‖ :=
  HilbertKernelProjection.error_bound (rootResidualMap T p) hr z

/-- Every factor is constructed from the connection, routes and specified norms. -/
def stabilityGain : ℝ := routeGain T p +
  ‖reconstructMap T p‖ * holonomyGain T p hr * ‖normalizer T p‖ *
    (‖T.differential graph‖ * routeGain T p + 1)

theorem stabilityGain_nonneg : 0 ≤ stabilityGain T p hr := by
  unfold stabilityGain
  have ha := routeGain_nonneg T p
  have hk := holonomyGain_nonneg T p hr
  positivity

def orthogonalRepair : (V → H) →L[ℝ] (V → H) :=
  (reconstructMap T p).comp ((anchorProjection T p).comp (ContinuousLinearMap.proj o))

@[simp] theorem orthogonalRepair_apply (x : V → H) :
    orthogonalRepair T p x = reconstruct T p (anchorProjection T p (x o)) := rfl

@[simp] theorem orthogonalRepair_anchor (x : V → H) :
    orthogonalRepair T p x o = anchorProjection T p (x o) := reconstruct_anchor T p _

theorem orthogonalRepair_parallel (x : V → H) : T.Parallel graph (orthogonalRepair T p x) :=
  (reconstruct_parallel_iff T p _).mpr (anchorProjection_fixed T p (x o))

@[simp] theorem orthogonalRepair_fixes (x : V → H) (hx : T.Parallel graph x) :
    orthogonalRepair T p x = x := by
  rw [orthogonalRepair_apply, anchorProjection_fixes T p _ (parallel_anchor_fixed T p x hx)]
  exact parallel_reconstruction T p x hx

@[simp] theorem orthogonalRepair_idempotent (x : V → H) :
    orthogonalRepair T p (orthogonalRepair T p x) = orthogonalRepair T p x :=
  orthogonalRepair_fixes T p _ (orthogonalRepair_parallel T p x)

/-- Unlike the isometric case, this projector is not asserted nonexpansive. -/
theorem orthogonalRepair_norm (x : V → H) :
    ‖orthogonalRepair T p x‖ ≤ ‖reconstructMap T p‖ * ‖x‖ :=
  (reconstruct_bound T p _).trans (mul_le_mul_of_nonneg_left
    ((anchorProjection_norm T p _).trans (norm_le_pi_norm x o)) (norm_nonneg (reconstructMap T p)))

theorem orthogonalRepair_error (x : V → H) :
    ‖x-orthogonalRepair T p x‖ ≤ stabilityGain T p hr * ‖T.differential graph x‖ := by
  have ha := anchorProjection_error T p hr (x o)
  have hh := rootResidual_anchor_bound T p x
  have hm := mul_le_mul_of_nonneg_left hh (holonomyGain_nonneg T p hr)
  have hq := ha.trans hm
  calc
    _ ≤ routeGain T p * ‖T.differential graph x‖ +
        ‖reconstructMap T p‖ * ‖x o-anchorProjection T p (x o)‖ :=
      changed_anchor_error T p x _
    _ ≤ routeGain T p * ‖T.differential graph x‖ +
        ‖reconstructMap T p‖ * (holonomyGain T p hr *
        (‖normalizer T p‖ * (‖T.differential graph‖ * routeGain T p + 1) *
         ‖T.differential graph x‖)) :=
      add_le_add le_rfl (mul_le_mul_of_nonneg_left hq (norm_nonneg (reconstructMap T p)))
    _ = _ := by unfold stabilityGain; ring

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

theorem anchorProjection_route_independent (q : OverlapTransport.Routing graph o) :
    anchorProjection T p = anchorProjection T q := by
  apply HilbertKernelProjection.projection_eq_of_kernel_eq
  rw [rootResidualMap_kernel, rootResidualMap_kernel, fixedSpace_route_independent T p q]

theorem orthogonalRepair_route_independent (q : OverlapTransport.Routing graph o) :
    orthogonalRepair T p = orthogonalRepair T q := by
  ext x i
  change reconstruct T p (anchorProjection T p (x o)) i =
    reconstruct T q (anchorProjection T q (x o)) i
  rw [← anchorProjection_route_independent T p q]
  exact congrFun (reconstruction_route_independent T p q _
    (anchorProjection_fixed T p (x o))) i


/-- Inverse normalization on the actual directed-edge residual space. -/
def denormalizer : (OverlapTransport.Edges graph → H) →L[ℝ]
    (OverlapTransport.Edges graph → H) :=
  ContinuousLinearMap.pi fun a =>
    (frame T p a.val.1).toContinuousLinearMap.comp
      (ContinuousLinearMap.proj a : (OverlapTransport.Edges graph → H) →L[ℝ] H)

omit [CompleteSpace H] [Fintype V] in
@[simp] theorem denormalizer_normalizer (r : OverlapTransport.Edges graph → H) :
    denormalizer T p (normalizer T p r) = r := by
  funext a
  exact (frame T p a.val.1).apply_symm_apply (r a)

omit [CompleteSpace H] in
/-- Reconstructed edge defects and root defects differ only by bounded normalization. -/
theorem differential_reconstruct (z : H) :
    T.differential graph (reconstruct T p z) =
      denormalizer T p (rootResidualMap T p z) := by
  rw [← normalized_reconstruction T p z, denormalizer_normalizer]

/-- A global estimate would in particular control the root's orthogonal displacement. -/
theorem closed_range_of_global_bound (C : ℝ) (hC : 0 ≤ C)
    (hb : ∀ x : V → H, ‖x-orthogonalRepair T p x‖ ≤
      C * ‖T.differential graph x‖) :
    IsClosed (Set.range (rootResidualMap T p)) := by
  apply HilbertKernelProjection.closed_range_of_bound (rootResidualMap T p)
    (C * ‖denormalizer T p‖) (mul_nonneg hC (norm_nonneg (denormalizer T p)))
  intro z
  have he : ‖z-anchorProjection T p z‖ ≤
      ‖reconstruct T p z-orthogonalRepair T p (reconstruct T p z)‖ := by
    simpa only [Pi.sub_apply, reconstruct_anchor, orthogonalRepair_anchor]
      using norm_le_pi_norm
        (reconstruct T p z-orthogonalRepair T p (reconstruct T p z)) o
  calc
    _ ≤ ‖reconstruct T p z-orthogonalRepair T p (reconstruct T p z)‖ := he
    _ ≤ C * ‖T.differential graph (reconstruct T p z)‖ := hb _
    _ = C * ‖denormalizer T p (rootResidualMap T p z)‖ := by
      rw [differential_reconstruct]
    _ ≤ C * (‖denormalizer T p‖ * ‖rootResidualMap T p z‖) :=
      mul_le_mul_of_nonneg_left ((denormalizer T p).le_opNorm _) hC
    _ = _ := by ring

/-- Closed holonomy range is necessary and sufficient for a finite global repair gain. -/
theorem closed_range_iff_global_bound :
    IsClosed (Set.range (rootResidualMap T p)) ↔
      ∃ C : ℝ, 0 ≤ C ∧ ∀ x : V → H,
        ‖x-orthogonalRepair T p x‖ ≤ C * ‖T.differential graph x‖ := by
  constructor
  · intro h
    exact ⟨stabilityGain T p h, stabilityGain_nonneg T p h,
      orthogonalRepair_error T p h⟩
  · rintro ⟨C,hC,hb⟩
    exact closed_range_of_global_bound T p C hC hb

/-- The criterion is not restricted to this chosen projector: any exact answer
with a uniform residual estimate would force the same closed range. -/
theorem closed_range_iff_near_parallel :
    IsClosed (Set.range (rootResidualMap T p)) ↔
      ∃ C : ℝ, 0 ≤ C ∧ ∀ x : V → H, ∃ y : V → H,
        T.Parallel graph y ∧ ‖x-y‖ ≤ C * ‖T.differential graph x‖ := by
  constructor
  · intro h
    exact ⟨stabilityGain T p h, stabilityGain_nonneg T p h, fun x =>
      ⟨orthogonalRepair T p x, orthogonalRepair_parallel T p x,
        orthogonalRepair_error T p h x⟩⟩
  · rintro ⟨C,hC,hb⟩
    apply HilbertKernelProjection.closed_range_of_bound (rootResidualMap T p)
      (C * ‖denormalizer T p‖) (mul_nonneg hC (norm_nonneg (denormalizer T p)))
    intro z
    obtain ⟨y,hy,he⟩ := hb (reconstruct T p z)
    have hzero : rootResidualMap T p (y o) = 0 := by
      change y o ∈ (rootResidualMap T p).ker
      rw [rootResidualMap_kernel]
      exact parallel_anchor_fixed T p y hy
    calc
      _ ≤ ‖z-y o‖ := HilbertKernelProjection.projection_best (rootResidualMap T p) z (y o) hzero
      _ ≤ ‖reconstruct T p z-y‖ := by
        simpa only [Pi.sub_apply,reconstruct_anchor] using
          norm_le_pi_norm (reconstruct T p z-y) o
      _ ≤ C * ‖T.differential graph (reconstruct T p z)‖ := he
      _ = C * ‖denormalizer T p (rootResidualMap T p z)‖ := by
        rw [differential_reconstruct]
      _ ≤ C * (‖denormalizer T p‖ * ‖rootResidualMap T p z‖) :=
        mul_le_mul_of_nonneg_left ((denormalizer T p).le_opNorm _) hC
      _ = _ := by ring

/-- Closed-range stability, unlike a selected numerical upper bound, is route-independent. -/
theorem closed_range_route_independent (q : OverlapTransport.Routing graph o) :
    IsClosed (Set.range (rootResidualMap T p)) ↔
      IsClosed (Set.range (rootResidualMap T q)) := by
  rw [closed_range_iff_global_bound T p, closed_range_iff_global_bound T q,
    orthogonalRepair_route_independent T p q]

/-- The reconstructed exact object lives in the previous ambient-section type. -/
def orthogonalAmbient (x : V → H) : (T.pathViews graph).Ambient :=
  T.toAmbient graph (orthogonalRepair T p x) (orthogonalRepair_parallel T p x)

theorem closed_range_ambient_repair (x : V → H) :
    ∃ s : (T.pathViews graph).Ambient,
      anchorProjection T p (s.val ⟨o⟩) = anchorProjection T p (x o) ∧
      ‖x-T.ambientValues graph s‖ ≤ stabilityGain T p hr * ‖T.differential graph x‖ := by
  refine ⟨orthogonalAmbient T p x, ?_, orthogonalRepair_error T p hr x⟩
  change anchorProjection T p (orthogonalRepair T p x o) = _
  rw [orthogonalRepair_anchor, anchorProjection_idempotent]

/-- Finite-dimensional v0.20 repair is definitionally the same projector. -/
theorem finite_dimensional_agreement [FiniteDimensional ℝ H] :
    orthogonalRepair T p = KomorebiSpace.AmplifiedTransport.Rooted.orthogonalRepair T p := rfl

end Hilbert
end Rooted
end AmplifiedTransport
end KomorebiSpace
end
