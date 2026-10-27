import PaperIRelease.GraphReachability
import Mathlib.Order.Antisymmetrization
import Mathlib.Order.WellFoundedSet

/-! Finite condensation is the actual quotient by mutual graph reachability.
Every vertex is proved reachable from a source component by finite minimality. -/

noncomputable section
set_option autoImplicit false

namespace Komorebi.PaperIRelease.FiniteDigraph

universe w
variable {I : Type w}

abbrev Reach (edge : I → I → Prop) := Relation.ReflTransGen edge

@[instance_reducible] def reachPreorder (edge : I → I → Prop) : Preorder I where
  le := Reach edge
  le_refl _ := .refl
  le_trans _ _ _ := Relation.ReflTransGen.trans

/-- Strongly connected components are classes of mutual reachability. -/
def SCC (edge : I → I → Prop) := Antisymmetrization I (Reach edge)

instance sccPartialOrder (edge : I → I → Prop) : PartialOrder (SCC edge) :=
  @instPartialOrderAntisymmetrization I (reachPreorder edge)

def component (edge : I → I → Prop) : I → SCC edge :=
  toAntisymmetrization (Reach edge)

theorem component_surjective (edge : I → I → Prop) : Function.Surjective (component edge) := by
  intro C
  exact ⟨ofAntisymmetrization (Reach edge) C, toAntisymmetrization_ofAntisymmetrization (Reach edge) C⟩

@[simp] theorem component_le_iff (edge : I → I → Prop) (a b : I) :
    component edge a ≤ component edge b ↔ Reach edge a b := Iff.rfl

@[simp] theorem component_eq_iff (edge : I → I → Prop) (a b : I) :
    component edge a = component edge b ↔ Reach edge a b ∧ Reach edge b a :=
  toAntisymmetrization_eq (Reach edge) a b

instance sccFintype [Fintype I] (edge : I → I → Prop) : Fintype (SCC edge) := by
  classical
  exact Fintype.ofSurjective (component edge) (component_surjective edge)

instance sccDecidableEq (edge : I → I → Prop) : DecidableEq (SCC edge) := Classical.decEq _

/-- A source component has no strictly preceding component in condensation. -/
def Source (edge : I → I → Prop) (C : SCC edge) : Prop := ∀ D, D ≤ C → D = C

abbrev Sources (edge : I → I → Prop) := {C : SCC edge // Source edge C}

instance sourcesFintype [Fintype I] (edge : I → I → Prop) : Fintype (Sources edge) :=
  Fintype.ofFinite _

/-- An actual edge of the condensation graph joins distinct SCCs and is
witnessed by an original graph edge between their vertices. -/
def CondensationEdge (edge : I → I → Prop) (C D : SCC edge) : Prop :=
  C ≠ D ∧ ∃ a b, component edge a = C ∧ component edge b = D ∧ edge a b

/-- Order-minimal components are exactly the sources of the actual
condensation graph, rather than an independently supplied source set. -/
theorem source_iff_no_incoming_edge (edge : I → I → Prop) (C : SCC edge) :
    Source edge C ↔ ∀ D, ¬ CondensationEdge edge D C := by
  constructor
  · intro hC D hDC
    obtain ⟨hne, a, b, ha, hb, hab⟩ := hDC
    apply hne
    apply hC
    rw [← ha, ← hb]
    exact (component_le_iff edge a b).mpr (.single hab)
  · intro hnone D hDC
    obtain ⟨a, rfl⟩ := component_surjective edge D
    obtain ⟨b, hb⟩ := component_surjective edge C
    have hab : Reach edge a b := (component_le_iff edge a b).mp (hb ▸ hDC)
    have hback : ∀ {x y : I}, Reach edge x y → component edge y = C →
        component edge x = C := by
      intro x y hxy
      induction hxy using Relation.ReflTransGen.head_induction_on with
      | refl => exact id
      | @head x z hxz hzy ih =>
        intro hy
        have hz := ih hy
        by_contra hx
        exact hnone (component edge x) ⟨hx, x, z, rfl, hz, hxz⟩
    exact hback hab hb

/-- Every component in a finite directed graph lies above a source.
No topological ordering or reachability certificate is supplied as a premise. -/
theorem exists_source_le [Fintype I] (edge : I → I → Prop) (C : SCC edge) :
    ∃ D : Sources edge, D.val ≤ C := by
  obtain ⟨D, hDC, hD⟩ := (Set.finite_univ : (Set.univ : Set (SCC edge)).Finite).isPWO.exists_le_minimal
    (a := C) (Set.mem_univ C)
  refine ⟨⟨D, ?_⟩, hDC⟩
  intro E hED
  exact le_antisymm hED (hD.2 (Set.mem_univ E) hED)

/-- Every vertex is reached from an actual vertex in an actual source SCC. -/
theorem exists_source_reaching [Fintype I] (edge : I → I → Prop) (b : I) :
    ∃ C : Sources edge, ∃ a : I, component edge a = C.val ∧ Reach edge a b := by
  obtain ⟨C, hC⟩ := exists_source_le edge (component edge b)
  obtain ⟨a, ha⟩ := component_surjective edge C.val
  refine ⟨C, a, ha, ?_⟩
  exact (component_le_iff edge a b).mp (ha ▸ hC)

/-- A path entering a source SCC must have started in that same SCC. -/
theorem no_reach_into_source (edge : I → I → Prop) (C : Sources edge)
    {a b : I} (hb : component edge b = C.val) (hab : Reach edge a b) :
    component edge a = C.val := by
  apply C.property
  rw [← hb]
  exact (component_le_iff edge a b).mpr hab

theorem source_vertex_iff (edge : I → I → Prop) (a : I) :
    Source edge (component edge a) ↔ ∀ b, Reach edge b a → Reach edge a b := by
  constructor
  · intro h b hba
    exact ((component_eq_iff edge b a).mp (h _ hba)).2
  · intro h C hC
    obtain ⟨b, rfl⟩ := component_surjective edge C
    exact (component_eq_iff edge b a).mpr ⟨hC, h b hC⟩

/-- Paths between vertices of one SCC stay in that SCC at every intermediate vertex. -/
theorem intermediate_same_component (edge : I → I → Prop) {a b c : I}
    (hac : component edge a = component edge c)
    (hab : Reach edge a b) (hbc : Reach edge b c) :
    component edge b = component edge a := by
  have hca := ((component_eq_iff edge a c).mp hac).2
  exact (component_eq_iff edge b a).mpr ⟨hbc.trans hca, hab⟩

end Komorebi.PaperIRelease.FiniteDigraph
