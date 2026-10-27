import KomorebiSpace.AmplifiedTransport

set_option autoImplicit false

/-!
# Exact holonomy coordinates for bounded nonisometric transports

The fixed-vector classification uses invertibility, not preservation of norms.
The resulting equivalence is continuous linear, and is not claimed isometric.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
namespace Rooted
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

def frame (i : V) : H ≃L[ℝ] H := (T.walkTransport (p.path i)).symm

def reconstruct (z : H) (i : V) : H := frame T p i z

@[simp] theorem frame_anchor (z : H) : frame T p o z = z := by
  simp only [frame, p.at_anchor, Connection.walkTransport]
  rfl

@[simp] theorem reconstruct_anchor (z : H) : reconstruct T p z o = z := frame_anchor T p z

def holonomy (a : OverlapTransport.Edges graph) : H ≃L[ℝ] H :=
  ((frame T p a.val.2).trans (T.transport a.val.1 a.val.2)).trans
    (frame T p a.val.1).symm

@[simp] theorem holonomy_apply (a : OverlapTransport.Edges graph) (z : H) :
    holonomy T p a z = (frame T p a.val.1).symm
      (T.transport a.val.1 a.val.2 (frame T p a.val.2 z)) := rfl

def fixedSpace : Submodule ℝ H where
  carrier := {z | ∀ a, holonomy T p a z = z}
  zero_mem' := by intro a; exact map_zero _
  add_mem' := by intro x y hx hy a; rw [map_add, hx a, hy a]
  smul_mem' := by intro c x hx a; rw [map_smul, hx a]

@[simp] theorem mem_fixedSpace (z : H) :
    z ∈ fixedSpace T p ↔ ∀ a, holonomy T p a z = z := Iff.rfl

theorem normalized_reconstruction_defect (z : H) (a : OverlapTransport.Edges graph) :
    (frame T p a.val.1).symm (T.defect (reconstruct T p z) a.val.1 a.val.2) =
      holonomy T p a z - z := by
  simp only [Connection.defect, reconstruct, map_sub, holonomy_apply,
    ContinuousLinearEquiv.symm_apply_apply]

theorem reconstruct_parallel_iff (z : H) :
    T.Parallel graph (reconstruct T p z) ↔ z ∈ fixedSpace T p := by
  constructor
  · intro hx a
    have he := congrArg (frame T p a.val.1).symm (hx _ _ a.property)
    simpa only [holonomy_apply, reconstruct, ContinuousLinearEquiv.symm_apply_apply] using he
  · intro hz i j hij
    have he := hz (⟨(i,j),hij⟩ : OverlapTransport.Edges graph)
    apply (frame T p i).symm.injective
    simpa only [holonomy_apply, reconstruct, ContinuousLinearEquiv.symm_apply_apply] using he

theorem parallel_reconstruction (x : V → H) (hx : T.Parallel graph x) :
    reconstruct T p (x o) = x := by
  funext i
  have he := T.parallel_walk x hx (p.path i)
  change (T.walkTransport (p.path i)).symm (x o) = x i
  rw [← he, ContinuousLinearEquiv.symm_apply_apply]

theorem parallel_anchor_fixed (x : V → H) (hx : T.Parallel graph x) :
    x o ∈ fixedSpace T p := by
  apply (reconstruct_parallel_iff T p (x o)).mp
  rw [parallel_reconstruction T p x hx]
  exact hx

include p in
theorem parallel_unique {x y : V → H} (hx : T.Parallel graph x)
    (hy : T.Parallel graph y) (he : x o = y o) : x = y := by
  rw [← parallel_reconstruction T p x hx, ← parallel_reconstruction T p y hy, he]

theorem anchor_extendable_iff (z : H) :
    (∃ x : V → H, T.Parallel graph x ∧ x o = z) ↔ z ∈ fixedSpace T p := by
  constructor
  · rintro ⟨x,hx,hz⟩
    rw [← hz]
    exact parallel_anchor_fixed T p x hx
  · intro hz
    exact ⟨reconstruct T p z, (reconstruct_parallel_iff T p z).mpr hz,
      reconstruct_anchor T p z⟩

theorem anchor_unique_extension_iff (z : H) :
    (∃! x : V → H, T.Parallel graph x ∧ x o = z) ↔ z ∈ fixedSpace T p := by
  constructor
  · intro h; exact (anchor_extendable_iff T p z).mp h.exists
  · intro hz
    refine ⟨reconstruct T p z, ⟨(reconstruct_parallel_iff T p z).mpr hz,
      reconstruct_anchor T p z⟩, ?_⟩
    intro y hy
    exact parallel_unique T p hy.1 ((reconstruct_parallel_iff T p z).mpr hz)
      (hy.2.trans (reconstruct_anchor T p z).symm)

theorem fixedSpace_route_independent (q : OverlapTransport.Routing graph o) :
    fixedSpace T p = fixedSpace T q := by
  ext z
  rw [← anchor_extendable_iff T p z, ← anchor_extendable_iff T q z]

theorem reconstruction_route_independent (q : OverlapTransport.Routing graph o)
    (z : H) (hz : z ∈ fixedSpace T p) :
    reconstruct T p z = reconstruct T q z := by
  have hq : z ∈ fixedSpace T q := by rw [← fixedSpace_route_independent T p q]; exact hz
  exact parallel_unique T p ((reconstruct_parallel_iff T p z).mpr hz)
    ((reconstruct_parallel_iff T q z).mpr hq)
    ((reconstruct_anchor T p z).trans (reconstruct_anchor T q z).symm)

/-- The finite edge-based operator is transport around a genuine closed walk. -/
def edgeLoop (a : OverlapTransport.Edges graph) : graph.Walk o o :=
  (p.path a.val.1).append (.cons a.property (p.path a.val.2).reverse)

theorem holonomy_is_loop (a : OverlapTransport.Edges graph) (z : H) :
    holonomy T p a z = T.walkTransport (edgeLoop p a) z := by
  simp only [edgeLoop, Connection.walkTransport_append, Connection.walkTransport_cons,
    Connection.walkTransport_reverse_eq_symm, holonomy_apply, frame,
    ContinuousLinearEquiv.symm_symm]

/-- Finitely many rooted edge loops detect every closed-walk constraint. -/
theorem fixed_iff_all_loops (z : H) :
    z ∈ fixedSpace T p ↔ ∀ q : graph.Walk o o, T.walkTransport q z = z := by
  constructor
  · intro hz q
    have he := T.parallel_walk (reconstruct T p z)
      ((reconstruct_parallel_iff T p z).mpr hz) q
    simpa only [reconstruct_anchor] using he
  · intro hz a
    rw [holonomy_is_loop]
    exact hz (edgeLoop p a)

section Finite
variable [Fintype V]

def parallelSpace : Submodule ℝ (V → H) := (T.differential graph).ker

def parameterLinearEquiv : fixedSpace T p ≃ₗ[ℝ] parallelSpace T (graph := graph) where
  toFun z := ⟨reconstruct T p z.val,
    (T.parallel_iff_differential_zero _).mp ((reconstruct_parallel_iff T p z.val).mpr z.property)⟩
  invFun x := ⟨x.val o, parallel_anchor_fixed T p x.val
    ((T.parallel_iff_differential_zero _).mpr x.property)⟩
  left_inv := by intro z; apply Subtype.ext; exact reconstruct_anchor T p z.val
  right_inv := by
    intro x
    apply Subtype.ext
    exact parallel_reconstruction T p x.val
      ((T.parallel_iff_differential_zero _).mpr x.property)
  map_add' := by intro z w; apply Subtype.ext; funext i; exact map_add (frame T p i) z.val w.val
  map_smul' := by intro c z; apply Subtype.ext; funext i; exact map_smul (frame T p i) c z.val

/-- Bounded reconstruction with the original vertex maximum norm. -/
def reconstructMap : H →L[ℝ] (V → H) :=
  ContinuousLinearMap.pi fun i => (frame T p i).toContinuousLinearMap

omit [Fintype V] in
@[simp] theorem reconstructMap_apply (z : H) : reconstructMap T p z = reconstruct T p z := rfl

theorem reconstruct_bound (z : H) :
    ‖reconstruct T p z‖ ≤ ‖reconstructMap T p‖ * ‖z‖ :=
  (reconstructMap T p).le_opNorm z

theorem anchor_lower_bound (z : H) : ‖z‖ ≤ ‖reconstruct T p z‖ := by
  have he := norm_le_pi_norm (reconstruct T p z) o
  simpa only [reconstruct_anchor] using he

/-- The former isometry is replaced by a bounded linear equivalence. -/
def parameterEquiv : fixedSpace T p ≃L[ℝ] parallelSpace T (graph := graph) :=
  (parameterLinearEquiv T p).toContinuousLinearEquivOfBounds
    ‖reconstructMap T p‖ 1
    (fun z => reconstruct_bound T p z.val)
    (by intro x; change ‖x.val o‖ ≤ 1 * ‖x.val‖; rw [one_mul]; exact norm_le_pi_norm x.val o)

@[simp] theorem parameterEquiv_coordinate (z : fixedSpace T p) (i : V) :
    (parameterEquiv T p z).val i = frame T p i z.val := rfl

/-- Reverse routes directly control errors in each destination's norm. -/
def routeGain : ℝ := ‖fun i : V => T.walkGain (p.path i).reverse‖

theorem routeGain_nonneg : 0 ≤ routeGain T p := norm_nonneg _

theorem routeGain_le (i : V) : T.walkGain (p.path i).reverse ≤ routeGain T p := by
  have h := norm_le_pi_norm (fun i : V => T.walkGain (p.path i).reverse) i
  simpa only [routeGain, Real.norm_eq_abs, abs_of_nonneg (T.walkGain_nonneg _)] using h

theorem anchored_approximation_bound (x : V → H) :
    ‖x-reconstruct T p (x o)‖ ≤ routeGain T p * ‖T.differential graph x‖ := by
  apply (pi_norm_le_iff_of_nonneg
    (mul_nonneg (routeGain_nonneg T p) (norm_nonneg _))).mpr
  intro i
  have he := T.walk_error x (p.path i).reverse
  rw [Connection.walkTransport_reverse_eq_symm, norm_sub_rev] at he
  exact he.trans (mul_le_mul_of_nonneg_right (routeGain_le T p i) (norm_nonneg _))

theorem changed_anchor_error (x : V → H) (z : H) :
    ‖x-reconstruct T p z‖ ≤ routeGain T p * ‖T.differential graph x‖ +
      ‖reconstructMap T p‖ * ‖x o-z‖ := by
  calc
    _ ≤ ‖x-reconstruct T p (x o)‖ + ‖reconstruct T p (x o)-reconstruct T p z‖ :=
      norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ _ := add_le_add (anchored_approximation_bound T p x) (by
      have he := (reconstructMap T p).le_opNorm (x o-z)
      simpa only [map_sub, reconstructMap_apply] using he)

end Finite
end Rooted
end AmplifiedTransport
end KomorebiSpace
end
