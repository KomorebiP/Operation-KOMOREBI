import KomorebiSpace.HolonomyTransport

set_option autoImplicit false

/-!
# Exact realizations are fixed anchor vectors

Root routes construct frames; they are not assumed to trivialize the connection.
Every edge then defines a loop operator at the anchor. The common fixed space
classifies exactly the parallel sections, with norm and anchor preserved.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
namespace Rooted
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

def frame (i : V) : H ≃ₗᵢ[ℝ] H := (T.walkTransport (p.path i)).symm

def reconstruct (z : H) (i : V) : H := frame T p i z

@[simp] theorem frame_anchor (z : H) : frame T p o z = z := by
  simp only [frame, p.at_anchor, Connection.walkTransport]
  rfl

@[simp] theorem reconstruct_anchor (z : H) : reconstruct T p z o = z := frame_anchor T p z

def holonomy (a : OverlapTransport.Edges graph) : H ≃ₗᵢ[ℝ] H :=
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
    LinearIsometryEquiv.symm_apply_apply]

theorem reconstruct_parallel_iff (z : H) :
    T.Parallel graph (reconstruct T p z) ↔ z ∈ fixedSpace T p := by
  constructor
  · intro hx a
    have he := congrArg (frame T p a.val.1).symm (hx _ _ a.property)
    simpa only [holonomy_apply, reconstruct, LinearIsometryEquiv.symm_apply_apply] using he
  · intro hz i j hij
    have he := hz (⟨(i,j),hij⟩ : OverlapTransport.Edges graph)
    apply (frame T p i).symm.injective
    simpa only [holonomy_apply, reconstruct, LinearIsometryEquiv.symm_apply_apply] using he

theorem parallel_reconstruction (x : V → H) (hx : T.Parallel graph x) :
    reconstruct T p (x o) = x := by
  funext i
  have he := T.parallel_walk x hx (p.path i)
  change (T.walkTransport (p.path i)).symm (x o) = x i
  rw [← he, LinearIsometryEquiv.symm_apply_apply]

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
    LinearIsometryEquiv.symm_symm]

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

theorem reconstruct_norm (z : H) : ‖reconstruct T p z‖ = ‖z‖ := by
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg (norm_nonneg z)).mpr
    intro i
    exact le_of_eq ((frame T p i).norm_map z)
  · have he := norm_le_pi_norm (reconstruct T p z) o
    simpa only [reconstruct_anchor] using he

/-- An actual linear isometric equivalence, not only a dimension count. -/
def parameterEquiv : fixedSpace T p ≃ₗᵢ[ℝ] parallelSpace T (graph := graph) where
  toLinearEquiv := parameterLinearEquiv T p
  norm_map' := by intro z; exact reconstruct_norm T p z.val

@[simp] theorem parameterEquiv_coordinate (z : fixedSpace T p) (i : V) :
    (parameterEquiv T p z).val i = frame T p i z.val := rfl

/-- Routed reconstruction is close to a candidate, even when its anchor is inadmissible. -/
theorem anchored_approximation_bound (x : V → H) :
    ‖x - reconstruct T p (x o)‖ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ := by
  apply (pi_norm_le_iff_of_nonneg
    (mul_nonneg (Nat.cast_nonneg _) (norm_nonneg _))).mpr
  intro i
  have he : ‖x i - reconstruct T p (x o) i‖ =
      ‖T.walkTransport (p.path i) (x i) - x o‖ := by
    rw [← (T.walkTransport (p.path i)).norm_map, map_sub]
    simp only [reconstruct, frame, LinearIsometryEquiv.apply_symm_apply]
  rw [show (x - reconstruct T p (x o)) i = x i - reconstruct T p (x o) i from rfl, he]
  exact (T.walk_error x (p.path i)).trans
    (mul_le_mul_of_nonneg_right (by exact_mod_cast p.length_le_radius i) (norm_nonneg _))

/-- Feasible anchors admit the same graph-derived error bound as in the flat model. -/
theorem anchored_quantitative_repair (x : V → H) (hx : x o ∈ fixedSpace T p) :
    ∃! y : V → H, T.Parallel graph y ∧ y o = x o ∧
      ‖x-y‖ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ := by
  refine ⟨reconstruct T p (x o), ⟨(reconstruct_parallel_iff T p _).mpr hx,
    reconstruct_anchor T p _, anchored_approximation_bound T p x⟩, ?_⟩
  intro y hy
  exact parallel_unique T p hy.1 ((reconstruct_parallel_iff T p _).mpr hx)
    (hy.2.1.trans (reconstruct_anchor T p _).symm)

end Finite
end Rooted
end HolonomyTransport
end KomorebiSpace
end
