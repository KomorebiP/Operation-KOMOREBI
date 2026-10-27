import PaperXI.RepresentationGraph
import Mathlib.RepresentationTheory.Intertwining

/-! Actual linear spaces of compatible sections, their representation, and the
map obtained from root holonomy tests. The final section equivalence is built;
a compatible family of comparison maps is not part of the input. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.GluedPacketSections
open Quiver GraphTransport GraphGauge
attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable {K α G : Type*} [Field K] [Quiver α] [Monoid G]
variable {V W : α → Type*}
variable [∀ v, AddCommGroup (V v)] [∀ v, Module K (V v)]
variable [∀ v, AddCommGroup (W v)] [∀ v, Module K (W v)]
variable (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
variable (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))

/-- Sections satisfy every original oriented-edge equation, not just tree edges. -/
def sections : Submodule K (∀ v, V v) where
  carrier s := ∀ {u v : α} (e : u ⟶ v), A e (s u) = s v
  zero_mem' := by intro u v e; simp
  add_mem' := by intro a b ha hb u v e; simpa using (map_add (A e) (a u) (b u)).trans (congrArg₂ (· + ·) (ha e) (hb e))
  smul_mem' := by intro c a ha u v e; simpa using (map_smul (A e) c (a u)).trans (congrArg (c • ·) (ha e))

theorem section_edge (s : sections A) {u v : α} (e : Traversal u v) :
    edge A e (s.val u) = s.val v := by
  cases e using Sum.rec with
  | inl e => exact s.property e
  | inr e =>
    change (A e).symm (s.val u) = s.val v
    apply (A e).injective
    simpa using (s.property e).symm

theorem section_path (s : sections A) {u v : α} (p : Walk u v) :
    path A p (s.val u) = s.val v := by
  induction p with
  | nil => rfl
  | cons p e ih =>
    change edge A e (path A p (s.val u)) = _
    rw [ih, section_edge A s e]

/-- Evaluation at a root is injective when actual paths reach every vertex. -/
theorem root_evaluation_injective {r : α} (P : ∀ v, Walk r v) :
    Function.Injective (fun s : sections A => s.val r) := by
  intro s t h
  change s.val r = t.val r at h
  apply Subtype.ext
  funext v
  exact (section_path A s (P v)).symm.trans
    ((congrArg (path A (P v)) h).trans (section_path A t (P v)))

/-- The actual fixed space of the based-loop representation. -/
def loopFixed (r : α) : Submodule K (V r) where
  carrier x := ∀ p : Walk r r, path A p x = x
  zero_mem' := by intro p; simp
  add_mem' := by intro x y hx hy p; simp [hx p, hy p]
  smul_mem' := by intro c x hx p; simp [hx p]

/-- A loop-fixed root vector is transported to an edge-compatible global section. -/
def extendRoot {r : α} (P : ∀ v, Walk r v) (x : loopFixed A r) : sections A :=
  ⟨fun v => path A (P v) x.val, by
    intro u v e
    have h := congrArg (path A (P v)) (x.property (cycle P e))
    simpa [cycle, GraphTransport.comp, GraphTransport.cons, GraphTransport.reverse,
      GraphTransport.edge] using h⟩

/-- Global sections are exactly root vectors fixed by all actual loop transports. -/
def evaluationEquiv {r : α} (P : ∀ v, Walk r v) (hr : P r = .nil) :
    sections A ≃ₗ[K] loopFixed A r where
  toFun s := ⟨s.val r, fun p => section_path A s p⟩
  invFun x := extendRoot A P x
  left_inv s := by
    apply Subtype.ext
    funext v
    exact section_path A s (P v)
  right_inv x := by
    apply Subtype.ext
    change path A (P r) x.val = x.val
    simp [hr]
  map_add' s t := rfl
  map_smul' c s := rfl

variable (ρ : ∀ v, Representation K G (V v))
variable (τ : ∀ v, Representation K G (W v))

/-- Coordinatewise action preserves the section space by the actual edge covariance. -/
def sectionRepresentation (hA : RepresentationGraph.EdgeEquivariant A ρ) :
    Representation K G (sections A) where
  toFun g := {
    toFun s := ⟨fun v => ρ v g (s.val v), by
      intro u v e
      rw [hA e g, s.property e]⟩
    map_add' s t := by ext v; exact map_add (ρ v g) (s.val v) (t.val v)
    map_smul' c s := by ext v; exact map_smul (ρ v g) c (s.val v) }
  map_one' := by ext s v; exact DFunLike.congr_fun (map_one (ρ v)) (s.val v)
  map_mul' g h := by ext s v; exact DFunLike.congr_fun (map_mul (ρ v) g h) (s.val v)

@[simp] theorem sectionRepresentation_apply
    (hA : RepresentationGraph.EdgeEquivariant A ρ) (g : G) (s : sections A) (v : α) :
    (sectionRepresentation A ρ hA g s).val v = ρ v g (s.val v) := rfl

/-- An edge-compatible gauge induces a genuine invertible map of section spaces. -/
def ofGauge (F : ∀ v, V v ≃ₗ[K] W v) (hF : EdgeCompatible A B F) :
    sections A ≃ₗ[K] sections B where
  toFun s := ⟨fun v => F v (s.val v), by
    intro u v e
    rw [← hF e, s.property e]⟩
  invFun t := ⟨fun v => (F v).symm (t.val v), by
    intro u v e
    apply (F v).injective
    rw [hF e, LinearEquiv.apply_symm_apply, t.property e,
      LinearEquiv.apply_symm_apply]⟩
  left_inv s := by ext v; exact (F v).symm_apply_apply _
  right_inv t := by ext v; exact (F v).apply_symm_apply _
  map_add' s t := by ext v; exact map_add (F v) _ _
  map_smul' c s := by ext v; exact map_smul (F v) c _

/-- No numerical proxy: this is a Mathlib representation equivalence of the
actual spaces of parallel sections. -/
def equivOfGauge (hA : RepresentationGraph.EdgeEquivariant A ρ)
    (hB : RepresentationGraph.EdgeEquivariant B τ)
    (F : ∀ v, V v ≃ₗ[K] W v) (hF : EdgeCompatible A B F)
    (hI : RepresentationGraph.Intertwines ρ τ F) :
    Representation.Equiv (sectionRepresentation A ρ hA) (sectionRepresentation B τ hB) := by
  refine Representation.Equiv.mk (ofGauge A B F hF) ?_
  intro g
  ext s v
  exact hI v g (s.val v)

/-- Constructed root-path gauge. The tree is derived from connectedness. -/
def gluedGauge {r : α} (hc : GraphTree.Connected (α := α)) (U : V r ≃ₗ[K] W r) :=
  rootGauge A B U (GraphTree.rootPath (GraphTree.ofConnected r hc))

/-- A root equivalence and fundamental-cycle tests produce a global equivalence. -/
def fromChords {r : α} (hc : GraphTree.Connected (α := α))
    (hA : RepresentationGraph.EdgeEquivariant A ρ)
    (hB : RepresentationGraph.EdgeEquivariant B τ)
    (U : Representation.Equiv (ρ r) (τ r))
    (hch : ∀ e : GraphTree.Chord (GraphTree.ofConnected r hc),
      CycleCompatible A B U.toLinearEquiv (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val) :
    Representation.Equiv (sectionRepresentation A ρ hA) (sectionRepresentation B τ hB) := by
  let P := GraphTree.rootPath (GraphTree.ofConnected r hc)
  apply equivOfGauge A B ρ τ hA hB (rootGauge A B U.toLinearEquiv P)
  · exact (rootGauge_compatible_iff_chords A B U.toLinearEquiv _).mpr hch
  · exact RepresentationGraph.rootGauge_intertwines A B ρ τ hA hB U.toLinearEquiv
      (fun g x => DFunLike.congr_fun (U.toIntertwiningMap.isIntertwining' g) x) P

/-- Pointwise description of the constructed map: B(path) U A(path)^(-1). -/
theorem fromChords_apply {r : α} (hc : GraphTree.Connected (α := α))
    (hA : RepresentationGraph.EdgeEquivariant A ρ)
    (hB : RepresentationGraph.EdgeEquivariant B τ)
    (U : Representation.Equiv (ρ r) (τ r))
    (hch : ∀ e : GraphTree.Chord (GraphTree.ofConnected r hc),
      CycleCompatible A B U.toLinearEquiv (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val)
    (s : sections A) (v : α) :
    (fromChords A B ρ τ hc hA hB U hch s).val v =
      gluedGauge A B hc U.toLinearEquiv v (s.val v) := rfl

/-- The compatible family is unique once the root map is fixed. -/
theorem gauge_unique_at_root {r : α} (hc : GraphTree.Connected (α := α))
    (U : V r ≃ₗ[K] W r) (F : ∀ v, V v ≃ₗ[K] W v)
    (hF : EdgeCompatible A B F) (hr : F r = U) :
    F = gluedGauge A B hc U := by
  rw [GraphGauge.gauge_unique A B F hF (GraphTree.rootPath (GraphTree.ofConnected r hc)), hr]
  rfl

end PaperXI.GluedPacketSections
