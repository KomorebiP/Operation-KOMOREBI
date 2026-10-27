import KomorebiSpace.AmplifiedHolonomy
import KomorebiSpace.KernelProjectionBounds
import KomorebiSpace.Correction

set_option autoImplicit false

/-!
# Exact reconstruction with nonisometric amplification

Both forward normalization and inverse route restoration enter the gain.
The fiber's finite-dimensional inner product supplies the anchor projection;
the vertex and edge products retain their maximum norms.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
namespace Rooted
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H] [Fintype V]
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

/-- Bring each edge's residual back to the root coordinate frame. -/
def normalizer : (OverlapTransport.Edges graph → H) →L[ℝ]
    (OverlapTransport.Edges graph → H) :=
  ContinuousLinearMap.pi fun a =>
    ((frame T p a.val.1).symm.toContinuousLinearMap).comp (ContinuousLinearMap.proj a : (OverlapTransport.Edges graph → H) →L[ℝ] H)

omit [Fintype V] in
@[simp] theorem normalizer_apply (r : OverlapTransport.Edges graph → H)
    (a : OverlapTransport.Edges graph) :
    normalizer T p r a = (frame T p a.val.1).symm (r a) := rfl

def rootResidualMap : H →L[ℝ] (OverlapTransport.Edges graph → H) :=
  ContinuousLinearMap.pi fun a =>
    (holonomy T p a).toContinuousLinearMap - ContinuousLinearMap.id ℝ H

omit [Fintype V] in
@[simp] theorem rootResidualMap_apply (z : H) (a : OverlapTransport.Edges graph) :
    rootResidualMap T p z a = holonomy T p a z-z := rfl

omit [Fintype V] in
theorem rootResidualMap_kernel : (rootResidualMap T p).ker = fixedSpace T p := by
  ext z
  change rootResidualMap T p z = 0 ↔ _
  constructor
  · intro h a
    exact sub_eq_zero.mp (congrFun h a)
  · intro h
    funext a
    exact sub_eq_zero.mpr (h a)

/-- The root operator is tied to the actual graph differential. -/
theorem normalized_reconstruction (z : H) :
    normalizer T p (T.differential graph (reconstruct T p z)) = rootResidualMap T p z := by
  funext a
  exact normalized_reconstruction_defect T p z a

theorem rootResidual_anchor_bound (x : V → H) :
    ‖rootResidualMap T p (x o)‖ ≤
      ‖normalizer T p‖ * (‖T.differential graph‖ * routeGain T p + 1) *
        ‖T.differential graph x‖ := by
  have herror : ‖reconstruct T p (x o)-x‖ ≤
      routeGain T p * ‖T.differential graph x‖ := by
    rw [norm_sub_rev]
    exact anchored_approximation_bound T p x
  have hd : ‖T.differential graph (reconstruct T p (x o))‖ ≤
      (‖T.differential graph‖ * routeGain T p + 1) * ‖T.differential graph x‖ := by
    calc
      _ ≤ ‖T.differential graph (reconstruct T p (x o))-T.differential graph x‖ +
          ‖T.differential graph x‖ := norm_le_norm_sub_add _ _
      _ = ‖T.differential graph (reconstruct T p (x o)-x)‖ +
          ‖T.differential graph x‖ := by rw [map_sub]
      _ ≤ ‖T.differential graph‖ * ‖reconstruct T p (x o)-x‖ +
          ‖T.differential graph x‖ := add_le_add ((T.differential graph).le_opNorm _) le_rfl
      _ ≤ ‖T.differential graph‖ * (routeGain T p * ‖T.differential graph x‖) +
          ‖T.differential graph x‖ :=
        add_le_add (mul_le_mul_of_nonneg_left herror (norm_nonneg _)) le_rfl
      _ = _ := by ring
  rw [← normalized_reconstruction]
  exact ((normalizer T p).le_opNorm _).trans
    ((mul_le_mul_of_nonneg_left hd (norm_nonneg _)).trans_eq (by ring))

/-- The original prescribed-observation correction problem, now with amplified bonds. -/
def problem (U : Set V) : CorrectionProblem (V → H)
    (OverlapTransport.Edges graph → H) (U → H) where
  residual := (T.differential graph).toLinearMap.toAddMonoidHom
  semantics :=
    { toFun := fun x i => x i.val
      map_zero' := rfl
      map_add' := by intros; rfl }

theorem obstruction_criterion (U : Set V) (ho : o ∈ U) (x : V → H) :
    (problem T (graph := graph) U).obstruction x = 0 ↔
      x o ∈ fixedSpace T p ∧ ∀ i : U, reconstruct T p (x o) i.val = x i.val := by
  rw [(problem T (graph := graph) U).flatten_iff]
  constructor
  · rintro ⟨y, hy, hp⟩
    have hpar : T.Parallel graph y := (T.parallel_iff_differential_zero y).mpr hy
    have ha : y o = x o := congrFun hp ⟨o,ho⟩
    constructor
    · rw [← ha]; exact parallel_anchor_fixed T p y hpar
    · intro i
      rw [← ha, parallel_reconstruction T p y hpar]
      exact congrFun hp i
  · rintro ⟨hf,hp⟩
    exact ⟨reconstruct T p (x o), (T.parallel_iff_differential_zero _).mp
      ((reconstruct_parallel_iff T p _).mpr hf), funext hp⟩

theorem quantitative_prescribed_repair (U : Set V) (ho : o ∈ U) (x : V → H)
    (hx : (problem T (graph := graph) U).obstruction x = 0) :
    ∃! y : V → H, T.Parallel graph y ∧ (∀ i : U, y i.val = x i.val) ∧
      ‖x-y‖ ≤ routeGain T p * ‖T.differential graph x‖ := by
  obtain ⟨hf,hp⟩ := (obstruction_criterion T p U ho x).mp hx
  refine ⟨reconstruct T p (x o), ⟨(reconstruct_parallel_iff T p _).mpr hf,
    hp, anchored_approximation_bound T p x⟩, ?_⟩
  intro y hy
  exact parallel_unique T p hy.1 ((reconstruct_parallel_iff T p _).mpr hf)
    ((hy.2.1 ⟨o,ho⟩).trans (reconstruct_anchor T p _).symm)

end Rooted
end AmplifiedTransport
end KomorebiSpace
end

noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
namespace Rooted
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [FiniteDimensional ℝ H] [Fintype V]
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

/-- Orthogonality is on the anchor fiber, not the vertex maximum norm. -/
def anchorProjection : H →L[ℝ] H := KernelProjection.projection (rootResidualMap T p)

def holonomyGain : ℝ := KernelProjection.gain (rootResidualMap T p)

theorem holonomyGain_nonneg : 0 ≤ holonomyGain T p :=
  KernelProjection.gain_nonneg (rootResidualMap T p)

theorem anchorProjection_fixed (z : H) : anchorProjection T p z ∈ fixedSpace T p := by
  rw [← rootResidualMap_kernel]
  exact KernelProjection.projection_mem (rootResidualMap T p) z

@[simp] theorem anchorProjection_fixes (z : H) (hz : z ∈ fixedSpace T p) :
    anchorProjection T p z = z := by
  apply KernelProjection.projection_fixes
  change z ∈ (rootResidualMap T p).ker
  rw [rootResidualMap_kernel]
  exact hz

@[simp] theorem anchorProjection_idempotent (z : H) :
    anchorProjection T p (anchorProjection T p z) = anchorProjection T p z :=
  anchorProjection_fixes T p _ (anchorProjection_fixed T p z)

theorem anchorProjection_norm (z : H) : ‖anchorProjection T p z‖ ≤ ‖z‖ :=
  KernelProjection.projection_norm (rootResidualMap T p) z

theorem anchorProjection_error (z : H) :
    ‖z-anchorProjection T p z‖ ≤ holonomyGain T p * ‖rootResidualMap T p z‖ :=
  KernelProjection.error_bound (rootResidualMap T p) z

/-- Every factor is constructed from the connection, routes and specified norms. -/
def stabilityGain : ℝ := routeGain T p +
  ‖reconstructMap T p‖ * holonomyGain T p * ‖normalizer T p‖ *
    (‖T.differential graph‖ * routeGain T p + 1)

theorem stabilityGain_nonneg : 0 ≤ stabilityGain T p := by
  unfold stabilityGain
  have ha := routeGain_nonneg T p
  have hk := holonomyGain_nonneg T p
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
    ‖x-orthogonalRepair T p x‖ ≤ stabilityGain T p * ‖T.differential graph x‖ := by
  have ha := anchorProjection_error T p (x o)
  have hh := rootResidual_anchor_bound T p x
  have hm := mul_le_mul_of_nonneg_left hh (holonomyGain_nonneg T p)
  have hq := ha.trans hm
  calc
    _ ≤ routeGain T p * ‖T.differential graph x‖ +
        ‖reconstructMap T p‖ * ‖x o-anchorProjection T p (x o)‖ :=
      changed_anchor_error T p x _
    _ ≤ routeGain T p * ‖T.differential graph x‖ +
        ‖reconstructMap T p‖ * (holonomyGain T p *
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
  apply KernelProjection.projection_eq_of_kernel_eq
  rw [rootResidualMap_kernel, rootResidualMap_kernel, fixedSpace_route_independent T p q]

theorem orthogonalRepair_route_independent (q : OverlapTransport.Routing graph o) :
    orthogonalRepair T p = orthogonalRepair T q := by
  ext x i
  change reconstruct T p (anchorProjection T p (x o)) i =
    reconstruct T q (anchorProjection T q (x o)) i
  rw [← anchorProjection_route_independent T p q]
  exact congrFun (reconstruction_route_independent T p q _
    (anchorProjection_fixed T p (x o))) i

end Rooted
end AmplifiedTransport
end KomorebiSpace
end
