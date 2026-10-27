import PaperXI.GraphGauge
import Mathlib.RepresentationTheory.Basic

/-! Gluing within actual representation intertwiners. Edge covariance ensures
that tree transport of a root bridge remains a local bridge at every vertex. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.RepresentationGraph
open Quiver GraphTransport GraphGauge
attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable {K α G : Type*} [Field K] [Quiver α] [Monoid G]
variable {V W : α → Type*}
  [∀ v, AddCommGroup (V v)] [∀ v, Module K (V v)]
  [∀ v, AddCommGroup (W v)] [∀ v, Module K (W v)]

/-- Every edge transport intertwines the declared local representations. -/
def EdgeEquivariant
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (ρ : ∀ v, Representation K G (V v)) : Prop :=
  ∀ {u v : α} (e : u ⟶ v) (g : G) (x : V u), A e (ρ u g x) = ρ v g (A e x)

/-- A family of maps lies in the actual local representation bridge spaces. -/
def Intertwines (ρ : ∀ v, Representation K G (V v))
    (τ : ∀ v, Representation K G (W v)) (F : ∀ v, V v ≃ₗ[K] W v) : Prop :=
  ∀ v g x, F v (ρ v g x) = τ v g (F v x)

variable (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (ρ : ∀ v, Representation K G (V v)) (τ : ∀ v, Representation K G (W v))

/-- Actual covariance along the entire path follows from its original edge equations. -/
theorem path_equivariant (hA : EdgeEquivariant A ρ)
    {u v : α} (p : Walk u v) (g : G) (x : V u) :
    path A p (ρ u g x) = ρ v g (path A p x) := by
  exact (gauge_path A A (fun v => ρ v g) (fun e x => (hA e g x).symm) p x).symm

variable {r : α}

/-- Root-path transport preserves a genuine representation bridge. -/
theorem rootGauge_intertwines (hA : EdgeEquivariant A ρ) (hB : EdgeEquivariant B τ)
    (U : V r ≃ₗ[K] W r) (hU : ∀ g x, U (ρ r g x) = τ r g (U x))
    (P : ∀ v, Walk r v) : Intertwines ρ τ (rootGauge A B U P) := by
  intro v g x
  have hInv := path_equivariant A ρ hA (P v).reverse g x
  simp only [GraphTransport.reverse] at hInv
  change path B (P v) (U ((path A (P v)).symm (ρ v g x))) =
    τ v g (path B (P v) (U ((path A (P v)).symm x)))
  rw [hInv, hU]
  exact path_equivariant B τ hB (P v) g _

/-- The matrix chord criterion stays exact within local intertwiner spaces when
edge transports themselves satisfy actual representation covariance. -/
theorem based_iff_chords (hA : EdgeEquivariant A ρ) (hB : EdgeEquivariant B τ)
    (U : V r ≃ₗ[K] W r) (hU : ∀ g x, U (ρ r g x) = τ r g (U x))
    (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v,
      F r = U ∧ EdgeCompatible A B F ∧ Intertwines ρ τ F) ↔
      ∀ e : GraphTree.Chord T, CycleCompatible A B U (GraphTree.rootPath T) e.val := by
  constructor
  · rintro ⟨F, hroot, hF, _⟩
    exact (GraphGauge.based_iff_chords A B U T).mp ⟨F, hroot, hF⟩
  · intro h
    exact ⟨rootGauge A B U (GraphTree.rootPath T),
      rootGauge_root A B U _ (GraphTree.rootPath_root T),
      (rootGauge_compatible_iff_chords A B U T).mpr h,
      rootGauge_intertwines A B ρ τ hA hB U hU _⟩

/-- The corrected graph source endpoint constructs the actual tree from connectedness. -/
theorem connected_iff_chords (hA : EdgeEquivariant A ρ) (hB : EdgeEquivariant B τ)
    (U : V r ≃ₗ[K] W r) (hU : ∀ g x, U (ρ r g x) = τ r g (U x))
    (hc : GraphTree.Connected (α := α)) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v,
      F r = U ∧ EdgeCompatible A B F ∧ Intertwines ρ τ F) ↔
      ∀ e : GraphTree.Chord (GraphTree.ofConnected r hc),
        CycleCompatible A B U (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val :=
  based_iff_chords A B ρ τ hA hB U hU (GraphTree.ofConnected r hc)

/-- The same constrained gluing criterion is equivalent to all actual based-loop tests. -/
theorem based_iff_loops (hA : EdgeEquivariant A ρ) (hB : EdgeEquivariant B τ)
    (U : V r ≃ₗ[K] W r) (hU : ∀ g x, U (ρ r g x) = τ r g (U x))
    (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v,
      F r = U ∧ EdgeCompatible A B F ∧ Intertwines ρ τ F) ↔
      LoopCompatible A B U :=
  (based_iff_chords A B ρ τ hA hB U hU T).trans (GraphGauge.chords_iff_loops A B U T)

/-- The root bridge condition and actual holonomy conjugacy classify unbased
compatible representation bridges. -/
theorem unbased_iff_conjugates (hA : EdgeEquivariant A ρ) (hB : EdgeEquivariant B τ)
    (r : α) (hc : GraphTree.Connected (α := α)) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, EdgeCompatible A B F ∧ Intertwines ρ τ F) ↔
      ∃ U : V r ≃ₗ[K] W r,
        (∀ g x, U (ρ r g x) = τ r g (U x)) ∧ GraphLoop.Conjugates A B U := by
  constructor
  · rintro ⟨F, hF, hI⟩
    exact ⟨F r, hI r, (GraphLoop.conjugates_iff_paths A B (F r)).mpr
      (GraphGauge.edgeCompatible_loops A B F hF)⟩
  · rintro ⟨U, hU, hC⟩
    let P := GraphTree.rootPath (GraphTree.ofConnected r hc)
    exact ⟨rootGauge A B U P,
      rootGauge_compatible_of_loops A B U P ((GraphLoop.conjugates_iff_paths A B U).mp hC),
      rootGauge_intertwines A B ρ τ hA hB U hU P⟩

end PaperXI.RepresentationGraph
