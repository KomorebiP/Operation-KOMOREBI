import PaperXI.GraphTree
import PaperXI.GraphTransport

/-! Actual tree paths intertwine every reversible system of edge transports.
Tree membership refers to the chosen original edge identity. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.GraphTreePaths

open Quiver
open GraphTree
variable {K α : Type*} [Field K] [Quiver α] {r : α}
variable {V : α → Type*} [∀ a, AddCommGroup (V a)] [∀ a, Module K (V a)]
attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable (T : Rooted α r)
variable (A : ∀ {a b : α}, (a ⟶ b) → (V a ≃ₗ[K] V b))

theorem parent_transport (a : {a : α // a ≠ r}) :
    (GraphTransport.path A (rootPath T (T.parent a))).trans
        (GraphTransport.edge A (T.parentEdge a)) =
      GraphTransport.path A (rootPath T a.val) := by
  rw [← GraphTransport.cons, rootPath_parent]

/-- Transport is coherent along each selected original tree edge. -/
theorem tree_transport (e : Edge α) (he : e ∈ treeEdges T) :
    (GraphTransport.path A (rootPath T e.1)).trans (A e.2.2) =
      GraphTransport.path A (rootPath T e.2.1) := by
  apply treeEdges_induction T (fun e =>
    (GraphTransport.path A (rootPath T e.1)).trans (A e.2.2) =
      GraphTransport.path A (rootPath T e.2.1)) ?_ e he
  intro a
  have hp := parent_transport T A a
  cases h : T.parentEdge a with
  | inl f =>
    have hs : selected T a = ⟨T.parent a, a.val, f⟩ := by
      unfold selected
      rw [h]
      rfl
    rw [hs]
    simpa only [h, GraphTransport.edge_inl] using hp
  | inr f =>
    have hs : selected T a = ⟨a.val, T.parent a, f⟩ := by
      unfold selected
      rw [h]
      rfl
    rw [hs]
    rw [h, GraphTransport.edge_inr] at hp
    rw [← hp]
    ext x
    simp

/-- The same coherence holds in either formal orientation of a tree edge. -/
theorem traversal_transport {a b : α} (e : Traversal a b)
    (he : underlying e ∈ treeEdges T) :
    (GraphTransport.path A (rootPath T a)).trans (GraphTransport.edge A e) =
      GraphTransport.path A (rootPath T b) := by
  have hp := tree_transport T A (underlying e) he
  cases e with
  | inl f => exact hp
  | inr f =>
    change (GraphTransport.path A (rootPath T b)).trans (A f) =
      GraphTransport.path A (rootPath T a) at hp
    rw [hp.symm]
    ext x
    simp

/-- Every supported path has the endpoint transport forced by the rooted tree. -/
theorem supported_transport {a b : Quiver.Symmetrify α} (p : Quiver.Path a b)
    (hp : Supported T p) :
    (GraphTransport.path A (rootPath T a)).trans (GraphTransport.path A p) =
      GraphTransport.path A (rootPath T b) := by
  induction p with
  | nil => ext x; rfl
  | cons p e ih =>
    rcases hp with ⟨hp, he⟩
    rw [GraphTransport.cons, ← LinearEquiv.trans_assoc, ih hp]
    exact traversal_transport T A e he

/-- Every based loop supported on the tree has identity transport. -/
theorem tree_loop_identity (p : GraphTree.Path r r) (hp : Supported T p) :
    GraphTransport.path A p = LinearEquiv.refl K (V r) := by
  have h := supported_transport T A p hp
  simpa only [rootPath_root, GraphTransport.nil, LinearEquiv.refl_trans] using h

end PaperXI.GraphTreePaths
