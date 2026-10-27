import KomorebiSpace.AmplifiedRepair
import KomorebiSpace.HolonomyViews
import KomorebiSpace.ViewSections

set_option autoImplicit false

/-!
# Nonisometric reconstruction in the existing ambient-section language

The graph-walk view category is reused from v0.18. Only its actual transport
functor changes. The quantitative statement returns the old Ambient type.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

abbrev PathView (graph : SimpleGraph V) := HolonomyTransport.PathView graph

namespace Connection
variable (T : Connection V H) (graph : SimpleGraph V)

def pathViews : ViewSystem (PathView graph) where
  Obj := fun _ => H
  pull := fun f => T.walkTransport f
  pull_id := by intros; rfl
  pull_comp := by intro i j k f g z; exact T.walkTransport_append f g z

def ambientValues (x : (T.pathViews graph).Ambient) : V → H := fun i => x.val ⟨i⟩

def toAmbient (x : V → H) (hx : T.Parallel graph x) : (T.pathViews graph).Ambient :=
  ⟨fun i => x i.vertex, fun _i _j f => T.parallel_walk x hx f⟩

@[simp] theorem toAmbient_coordinate (x : V → H) (hx : T.Parallel graph x) (i : V) :
    (T.toAmbient graph x hx).val ⟨i⟩ = x i := rfl

theorem ambient_parallel (x : (T.pathViews graph).Ambient) :
    T.Parallel graph (fun i => x.val ⟨i⟩) := by
  intro i j hij
  exact x.property ⟨i⟩ ⟨j⟩ (.cons hij .nil)

/-- This is the old Ambient type with the new, actual walk restriction maps. -/
def ambientParallelEquiv :
    (T.pathViews graph).Ambient ≃ {x : V → H // T.Parallel graph x} where
  toFun x := ⟨fun i => x.val ⟨i⟩, T.ambient_parallel graph x⟩
  invFun x := T.toAmbient graph x.val x.property
  left_inv := by intro x; apply ViewSystem.Ambient.ext; intro i; rfl
  right_inv := by intro x; rfl

end Connection

namespace Rooted
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

def ambientParameters : fixedSpace T p ≃ (T.pathViews graph).Ambient where
  toFun z := T.toAmbient graph (reconstruct T p z.val)
    ((reconstruct_parallel_iff T p z.val).mpr z.property)
  invFun x := ⟨x.val ⟨o⟩, parallel_anchor_fixed T p (fun i => x.val ⟨i⟩)
    (T.ambient_parallel graph x)⟩
  left_inv := by intro z; apply Subtype.ext; exact reconstruct_anchor T p z.val
  right_inv := by
    intro x
    apply ViewSystem.Ambient.ext
    intro i
    exact congrFun (parallel_reconstruction T p (fun j => x.val ⟨j⟩)
      (T.ambient_parallel graph x)) i.vertex

@[simp] theorem ambientParameters_coordinate (z : fixedSpace T p) (i : V) :
    (ambientParameters T p z).val ⟨i⟩ = frame T p i z.val := rfl

section Finite
variable [Fintype V]

theorem quantitative_ambient_realization (U : Set V) (ho : o ∈ U) (x : V → H)
    (hx : (problem T (graph := graph) U).obstruction x = 0) :
    ∃ s : (T.pathViews graph).Ambient,
      (∀ i : U, s.val ⟨i.val⟩ = x i.val) ∧
      ‖x - T.ambientValues graph s‖ ≤ routeGain T p * ‖T.differential graph x‖ := by
  obtain ⟨y,hy,_⟩ := quantitative_prescribed_repair T p U ho x hx
  exact ⟨T.toAmbient graph y hy.1, hy.2.1, hy.2.2⟩

end Finite
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

def orthogonalAmbient (x : V → H) : (T.pathViews graph).Ambient :=
  T.toAmbient graph (orthogonalRepair T p x) (orthogonalRepair_parallel T p x)

theorem finite_dimensional_ambient_repair (x : V → H) :
    ∃ s : (T.pathViews graph).Ambient,
      anchorProjection T p (s.val ⟨o⟩) = anchorProjection T p (x o) ∧
      ‖x-T.ambientValues graph s‖ ≤ stabilityGain T p * ‖T.differential graph x‖ := by
  refine ⟨orthogonalAmbient T p x, ?_, orthogonalRepair_error T p x⟩
  change anchorProjection T p (orthogonalRepair T p x o) = _
  rw [orthogonalRepair_anchor, anchorProjection_idempotent]

end Rooted
end AmplifiedTransport
end KomorebiSpace
end
