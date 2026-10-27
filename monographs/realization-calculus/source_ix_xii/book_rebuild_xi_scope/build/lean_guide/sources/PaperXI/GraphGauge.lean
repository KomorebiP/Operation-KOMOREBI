import PaperXI.GraphTransport
import PaperXI.GraphTree
import PaperXI.GraphLoopRepresentation
import PaperXI.HolonomyResidual

/-! Actual graph gauges and the rooted matrix holonomy criterion, Paper XI 14.2–14.3.
The cycle tests are the based loops determined by a constructed rooted tree. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.GraphGauge

open Quiver
open GraphTransport
attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable {K α : Type*} [Field K] [Quiver α]
variable {V W : α → Type*}
  [∀ u, AddCommGroup (V u)] [∀ u, Module K (V u)]
  [∀ u, AddCommGroup (W u)] [∀ u, Module K (W u)]

variable (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
  (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
  {r : α}

/-- The actual based loop associated to an original oriented edge and root paths. -/
def cycle (P : ∀ v, Walk r v) {u v : α} (e : u ⟶ v) : Walk r r :=
  ((P u).cons (Sum.inl e)).comp (P v).reverse

/-- Vertex gauges transported from a specified root isomorphism. -/
def rootGauge (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v) (v : α) : V v ≃ₗ[K] W v :=
  HolonomyResidual.transported U (path A (P v)) (path B (P v))

/-- Intertwining equations on every original edge. -/
def EdgeCompatible (F : ∀ v, V v ≃ₗ[K] W v) : Prop :=
  ∀ {u v : α} (e : u ⟶ v) (x : V u), F v (A e x) = B e (F u x)

/-- Intertwining equations on all actual based paths. -/
def LoopCompatible (U : V r ≃ₗ[K] W r) : Prop :=
  ∀ (p : Walk r r) (x : V r), U (path A p x) = path B p (U x)

/-- One fundamental-cycle intertwining test. -/
def CycleCompatible (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v)
    (e : GraphTree.Edge α) : Prop :=
  ∀ x : V r, U (path A (cycle (α := α) P e.2.2) x) = path B (cycle (α := α) P e.2.2) (U x)

@[simp] theorem rootGauge_root (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v)
    (hP : P r = .nil) : rootGauge A B U P r = U := by
  ext x
  simp [rootGauge, hP, HolonomyResidual.transported]

/-- The fundamental-cycle defect is exactly the edge obstruction for transported gauges. -/
theorem rootGauge_edge_iff (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v)
    {u v : α} (e : u ⟶ v) :
    (∀ x, rootGauge A B U P v (A e x) = B e (rootGauge A B U P u x)) ↔
      CycleCompatible A B U P ⟨u, v, e⟩ := by
  constructor
  · intro h x
    have hp := congrArg (path B (P v)).symm (h (path A (P u) x))
    simpa [rootGauge, cycle, CycleCompatible, HolonomyResidual.transported, GraphTransport.comp, GraphTransport.reverse, GraphTransport.cons, GraphTransport.edge] using hp
  · intro h x
    have hp := congrArg (path B (P v)) (h ((path A (P u)).symm x))
    simpa [rootGauge, cycle, CycleCompatible, HolonomyResidual.transported, GraphTransport.comp, GraphTransport.reverse, GraphTransport.cons, GraphTransport.edge] using hp

/-- Edge equations propagate along actual paths to every based loop. -/
theorem edgeCompatible_loops (F : ∀ v, V v ≃ₗ[K] W v)
    (hF : EdgeCompatible A B F) : LoopCompatible A B (F r) := by
  intro p x
  exact gauge_path A B (fun v => (F v).toLinearMap) hF p x

/-- All based-loop equations construct a global gauge for any root path family. -/
theorem rootGauge_compatible_of_loops (U : V r ≃ₗ[K] W r)
    (P : ∀ v, Walk r v) (h : LoopCompatible A B U) :
    EdgeCompatible A B (rootGauge A B U P) := by
  intro u v e
  exact (rootGauge_edge_iff A B U P e).mpr (h (cycle P e))

/-- A compatible gauge is uniquely determined by its value at the root. -/
theorem gauge_unique (F : ∀ v, V v ≃ₗ[K] W v) (hF : EdgeCompatible A B F)
    (P : ∀ v, Walk r v) : F = rootGauge A B (F r) P := by
  funext v
  ext x
  have h := gauge_path A B (fun v => (F v).toLinearMap) hF (P v)
    ((path A (P v)).symm x)
  simpa [rootGauge, HolonomyResidual.transported] using h

/-- Based existence is equivalent to intertwining every actual loop. -/
theorem based_iff_loops (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v)
    (hP : P r = .nil) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      LoopCompatible A B U := by
  constructor
  · rintro ⟨F, hroot, hF⟩
    rw [← hroot]
    exact edgeCompatible_loops A B F hF
  · intro h
    exact ⟨rootGauge A B U P, rootGauge_root A B U P hP,
      rootGauge_compatible_of_loops A B U P h⟩

/-- Transported gauges satisfy each selected parent traversal automatically. -/
theorem rootGauge_parent (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r)
    (a : {a : α // a ≠ r}) (x : V (T.parent a)) :
    rootGauge A B U (GraphTree.rootPath T) a.val (edge A (T.parentEdge a) x) =
      edge B (T.parentEdge a) (rootGauge A B U (GraphTree.rootPath T) (T.parent a) x) := by
  simp only [rootGauge, HolonomyResidual.transported_apply]
  rw [← GraphTree.rootPath_parent T a]
  simp [GraphTransport.path]

/-- The chosen root gauges intertwine every original edge in the selected tree. -/
theorem rootGauge_tree (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    ∀ e ∈ GraphTree.treeEdges T,
      ∀ x : V e.1, rootGauge A B U (GraphTree.rootPath T) e.2.1 (A e.2.2 x) =
        B e.2.2 (rootGauge A B U (GraphTree.rootPath T) e.1 x) := by
  apply GraphTree.treeEdges_induction T
  intro a
  have h := rootGauge_parent A B U T a
  unfold GraphTree.selected GraphTree.underlying
  cases he : T.parentEdge a with
  | inl e =>
    simpa [GraphTree.selected, GraphTree.underlying, he] using h
  | inr e =>
    intro x
    have hx := congrArg (B e) (h (A e x))
    simpa [GraphTree.selected, GraphTree.underlying, he] using hx.symm

/-- Chord tests are sufficient: all selected-tree edge equations hold automatically. -/
theorem rootGauge_compatible_iff_chords (U : V r ≃ₗ[K] W r)
    (T : GraphTree.Rooted α r) :
    EdgeCompatible A B (rootGauge A B U (GraphTree.rootPath T)) ↔
      ∀ e : GraphTree.Chord T, CycleCompatible A B U (GraphTree.rootPath T) e.val := by
  classical
  constructor
  · intro h e
    exact (rootGauge_edge_iff A B U (GraphTree.rootPath T) e.val.2.2).mp (h e.val.2.2)
  · intro h u v e
    by_cases he : (⟨u, v, e⟩ : GraphTree.Edge α) ∈ GraphTree.treeEdges T
    · exact rootGauge_tree A B U T ⟨u, v, e⟩ he
    · exact (rootGauge_edge_iff A B U (GraphTree.rootPath T) e).mpr (h ⟨⟨u,v,e⟩, he⟩)

/-- Source 14.2: a fixed root gauge extends exactly when its fundamental-cycle tests pass. -/
theorem based_iff_chords (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord T, CycleCompatible A B U (GraphTree.rootPath T) e.val := by
  constructor
  · rintro ⟨F, hroot, hF⟩ e
    have h := edgeCompatible_loops A B (r := r) F hF
    rw [hroot] at h
    exact h (cycle (GraphTree.rootPath T) e.val.2.2)
  · intro h
    exact ⟨rootGauge A B U (GraphTree.rootPath T),
      rootGauge_root A B U _ (GraphTree.rootPath_root T),
      (rootGauge_compatible_iff_chords A B U T).mpr h⟩

/-- The source endpoint obtains its tree from actual connectedness. -/
theorem connected_based_iff_chords (U : V r ≃ₗ[K] W r)
    (hc : GraphTree.Connected (α := α)) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord (GraphTree.ofConnected r hc),
        CycleCompatible A B U (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val :=
  based_iff_chords A B U (GraphTree.ofConnected r hc)

/-- Fundamental-cycle tests imply all based-loop tests, without an abelianization shortcut. -/
theorem chords_iff_loops (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∀ e : GraphTree.Chord T, CycleCompatible A B U (GraphTree.rootPath T) e.val) ↔
      LoopCompatible A B U :=
  (based_iff_chords A B U T).symm.trans
    (based_iff_loops A B U _ (GraphTree.rootPath_root T))

/-- The criterion is independent of the rooted spanning tree chosen. -/
theorem tree_independence (U : V r ≃ₗ[K] W r)
    (T S : GraphTree.Rooted α r) :
    (∀ e : GraphTree.Chord T, CycleCompatible A B U (GraphTree.rootPath T) e.val) ↔
      ∀ e : GraphTree.Chord S, CycleCompatible A B U (GraphTree.rootPath S) e.val :=
  (chords_iff_loops A B U T).trans (chords_iff_loops A B U S).symm

/-- Source 14.3: graph gauge equivalence is conjugacy of the actual loop representations. -/
theorem unbased_iff_conjugates (r : α) (hc : GraphTree.Connected (α := α)) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, EdgeCompatible A B F) ↔
      ∃ U : V r ≃ₗ[K] W r, GraphLoop.Conjugates A B U := by
  let T := GraphTree.ofConnected r hc
  constructor
  · rintro ⟨F, hF⟩
    exact ⟨F r, (GraphLoop.conjugates_iff_paths A B (F r)).mpr
      (edgeCompatible_loops A B F hF)⟩
  · rintro ⟨U, hU⟩
    have h := (GraphLoop.conjugates_iff_paths A B U).mp hU
    exact ⟨rootGauge A B U (GraphTree.rootPath T),
      rootGauge_compatible_of_loops A B U (GraphTree.rootPath T) h⟩

end PaperXI.GraphGauge
