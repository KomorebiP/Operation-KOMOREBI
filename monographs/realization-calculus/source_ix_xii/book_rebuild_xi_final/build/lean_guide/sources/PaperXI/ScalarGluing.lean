import PaperXI.GraphGauge
import PaperXI.ProjectiveHolonomy

/-! Scalar gluing on actual graph cycles, with the zero-dimensional branch retained. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section

namespace PaperXI.ScalarGluing

open PaperXI.GraphTransport PaperXI.GraphGauge PaperXI.ScalarHolonomy
open PaperXI.ProjectiveHolonomy

attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable {K α : Type*} [Field K] [Quiver α]
variable {V W : α → Type*}
  [∀ u, AddCommGroup (V u)] [∀ u, Module K (V u)]
  [∀ u, AddCommGroup (W u)] [∀ u, Module K (W u)]

variable (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
  (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v)) {r : α}

/-- A cycle test compares the actual operators after identifying the root spaces. -/
theorem cycle_operator_iff (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v)
    (e : GraphTree.Edge α) :
    CycleCompatible A B U P e ↔
      ((U.symm.trans (path (α := α) A (cycle (α := α) P e.2.2))).trans U) = path (α := α) B (cycle (α := α) P e.2.2) := by
  constructor
  · intro h
    ext y
    simpa using h (U.symm y)
  · intro h x
    simpa using LinearEquiv.congr_fun h (U x)

/-- For scalar loop operators, the root identification does not affect any cycle test. -/
theorem cycle_independent (hA : IsScalar (GraphLoop.holonomy A r))
    (U Q : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v) (e : GraphTree.Edge α) :
    CycleCompatible A B U P e ↔ CycleCompatible A B Q P e := by
  rw [cycle_operator_iff, cycle_operator_iff]
  have h := (isScalar_iff_paths A r).mp hA (cycle P e.2.2)
  rw [scalar_conjugate_independent U Q _ h]

/-- At all ranks, gluing with one root identification is tested by actual scalar
operators using any other root identification. -/
theorem based_iff_scalar_operators (hA : IsScalar (GraphLoop.holonomy A r))
    (U Q : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord T,
        ((Q.symm.trans (path (α := α) A (cycle (α := α) (GraphTree.rootPath T) e.val.2.2))).trans Q) =
          path (α := α) B (cycle (α := α) (GraphTree.rootPath T) e.val.2.2) := by
  rw [based_iff_chords A B U T]
  apply forall_congr'
  intro e
  exact (cycle_independent A B hA U Q _ e.val).trans (cycle_operator_iff A B Q _ e.val)

/-- This version of scalar gluing is independent of root gauges even at dimension zero. -/
theorem based_root_independent (hA : IsScalar (GraphLoop.holonomy A r))
    (U Q : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      ∃ F : ∀ v, V v ≃ₗ[K] W v, F r = Q ∧ EdgeCompatible A B F := by
  rw [based_iff_chords A B U T, based_iff_chords A B Q T]
  exact forall_congr' fun e => cycle_independent A B hA U Q _ e.val

/-- When scalar values are identifiable, one cycle equation is precisely equality of values. -/
theorem cycle_units_iff [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (U : V r ≃ₗ[K] W r) (P : ∀ v, Walk r v) (e : GraphTree.Edge α) :
    CycleCompatible A B U P e ↔
      loopCharacter A r hA (GraphLoop.loopClass (cycle P e.2.2)) =
        loopCharacter B r hB (GraphLoop.loopClass (cycle P e.2.2)) := by
  have h := intertwines_iff U
    (loopCharacter A r hA (GraphLoop.loopClass (cycle P e.2.2)))
    (loopCharacter B r hB (GraphLoop.loopClass (cycle P e.2.2)))
  simpa only [CycleCompatible, loopCharacter_spec, GraphLoop.holonomy_loopClass] using h

/-- Source 14.4's unit-valued formulation, with its necessary nonzero-root hypothesis. -/
theorem based_iff_scalar_units [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord T,
        loopCharacter A r hA (GraphLoop.loopClass (cycle (GraphTree.rootPath T) e.val.2.2)) =
          loopCharacter B r hB (GraphLoop.loopClass (cycle (GraphTree.rootPath T) e.val.2.2)) := by
  rw [based_iff_chords A B U T]
  exact forall_congr' fun e => cycle_units_iff A B hA hB U _ e.val

/-- Allowing the root map to vary introduces no conjugacy condition for scalar holonomy. -/
theorem unbased_iff_scalar_units [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord T,
        loopCharacter A r hA (GraphLoop.loopClass (cycle (GraphTree.rootPath T) e.val.2.2)) =
          loopCharacter B r hB (GraphLoop.loopClass (cycle (GraphTree.rootPath T) e.val.2.2)) := by
  constructor
  · rintro ⟨F, hF⟩
    exact (based_iff_scalar_units A B hA hB (F r) T).mp ⟨F, rfl, hF⟩
  · intro h
    obtain ⟨F, _, hF⟩ := (based_iff_scalar_units A B hA hB U T).mpr h
    exact ⟨F, hF⟩

/-- Equality of the extracted characters is equivalent to all actual loop equations. -/
theorem loops_iff_characters [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (U : V r ≃ₗ[K] W r) :
    LoopCompatible A B U ↔ loopCharacter A r hA = loopCharacter B r hB := by
  rw [loopCharacter, loopCharacter, ← character_intertwines_iff _ _ hA hB U]
  constructor
  · intro h g
    obtain ⟨p, rfl⟩ := GraphLoop.loopClass_surjective r g
    simpa only [GraphLoop.holonomy_loopClass] using h p
  · intro h p
    simpa only [GraphLoop.holonomy_loopClass] using h (GraphLoop.loopClass p)

/-- The first-homology ratio is the exact scalar gluing obstruction. -/
theorem based_iff_ratioH1_trivial [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F) ↔
      transportRatioH1 A B r hA hB = 1 := by
  rw [based_iff_loops A B U (GraphTree.rootPath T) (GraphTree.rootPath_root T),
    loops_iff_characters A B hA hB U]
  exact (ratioH1_eq_one_iff r _ _).symm

/-- A zero root space has automatic loop equations, so connected transport glues without tests. -/
theorem zero_root_gluing [Subsingleton (V r)]
    (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    ∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F := by
  apply (based_iff_loops A B U (GraphTree.rootPath T) (GraphTree.rootPath_root T)).mpr
  intro p x
  exact zero_space_intertwines U (path A p) (path B p) x

/-- The literal zero-dimensional case of the manuscript has no gluing obstruction. -/
theorem zero_finrank_gluing [FiniteDimensional K (V r)]
    (hzero : Module.finrank K (V r) = 0)
    (U : V r ≃ₗ[K] W r) (T : GraphTree.Rooted α r) :
    ∃ F : ∀ v, V v ≃ₗ[K] W v, F r = U ∧ EdgeCompatible A B F := by
  let : Subsingleton (V r) := (Module.finrank_zero_iff).mp hzero
  exact zero_root_gluing A B U T

/-- The source-facing scalar criterion constructs the root identification from equal
dimensions and the rooted spanning tree from connectedness. -/
theorem connected_scalar_criterion [FiniteDimensional K (V r)] [FiniteDimensional K (W r)]
    [Nontrivial (V r)] [Nontrivial (W r)]
    (hdim : Module.finrank K (V r) = Module.finrank K (W r))
    (hc : GraphTree.Connected (α := α))
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r)) :
    (∃ F : ∀ v, V v ≃ₗ[K] W v, EdgeCompatible A B F) ↔
      ∀ e : GraphTree.Chord (GraphTree.ofConnected r hc),
        loopCharacter A r hA (GraphLoop.loopClass
          (cycle (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val.2.2)) =
        loopCharacter B r hB (GraphLoop.loopClass
          (cycle (GraphTree.rootPath (GraphTree.ofConnected r hc)) e.val.2.2)) := by
  obtain ⟨U⟩ := FiniteDimensional.nonempty_linearEquiv_of_finrank_eq hdim
  exact unbased_iff_scalar_units A B hA hB U (GraphTree.ofConnected r hc)

/-- The equal zero-dimensional source case constructs a global gauge without scalar choices. -/
theorem connected_zero_dimensional [FiniteDimensional K (V r)] [FiniteDimensional K (W r)]
    (hV : Module.finrank K (V r) = 0) (hW : Module.finrank K (W r) = 0)
    (hc : GraphTree.Connected (α := α)) :
    ∃ F : ∀ v, V v ≃ₗ[K] W v, EdgeCompatible A B F := by
  obtain ⟨U⟩ := FiniteDimensional.nonempty_linearEquiv_of_finrank_eq (hV.trans hW.symm)
  obtain ⟨F, _, hF⟩ := zero_finrank_gluing A B hV U (GraphTree.ofConnected r hc)
  exact ⟨F, hF⟩

end PaperXI.ScalarGluing
