import KomorebiSpace.HolonomyRepair
import KomorebiSpace.ViewSections

set_option autoImplicit false

/-!
# The actual ambient view system for path-dependent transport

A graph walk, rather than only its endpoints, is a morphism. Parallel sections
of this category are exactly the edge-compatible data. This retains nontrivial
loop operators instead of collapsing the graph to a thin comparison category.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

/-- Keeping the graph as a parameter prevents a global category instance on V. -/
structure PathView (graph : SimpleGraph V) where
  vertex : V

instance pathViewCategory (graph : SimpleGraph V) : CategoryTheory.Category (PathView graph) where
  Hom i j := graph.Walk i.vertex j.vertex
  id _ := SimpleGraph.Walk.nil
  comp p q := p.append q
  id_comp := by intros; rfl
  comp_id := by intro i j p; exact SimpleGraph.Walk.append_nil p
  assoc := by intro i j k l p q r; exact (SimpleGraph.Walk.append_assoc p q r).symm

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
      ‖x - T.ambientValues graph s‖ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ := by
  obtain ⟨y,hy,_⟩ := quantitative_prescribed_repair T p U ho x hx
  exact ⟨T.toAmbient graph y hy.1, hy.2.1, hy.2.2⟩

end Finite
end Rooted
end HolonomyTransport
end KomorebiSpace
end
