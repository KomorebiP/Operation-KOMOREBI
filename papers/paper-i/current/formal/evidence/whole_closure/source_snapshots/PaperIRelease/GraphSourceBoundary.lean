import PaperIRelease.GraphSourceProjection

set_option autoImplicit false

namespace Komorebi.PaperIRelease.FiniteDigraph

universe u
variable {I : Type u}

/-- With no edges each vertex is a source SCC. -/
theorem empty_graph_source_boundary (a : I) :
    Source (fun _ _ : I => False) (component (fun _ _ : I => False) a) := by
  apply (source_vertex_iff _ _).mpr
  intro b hba
  rcases hba.cases_head with h | ⟨c, hbc, _⟩
  · subst b; exact .refl
  · exact hbc.elim

def oneArrow (a b : Bool) : Prop := a = false ∧ b = true

theorem oneArrow_no_reverse : ¬ Reach oneArrow true false := by
  intro h
  rcases h.cases_tail with h | ⟨c, _, hc⟩
  · cases h
  · cases hc.2

/-- In the two-vertex one-arrow graph the tail is a source. -/
theorem oneArrow_source_boundary : Source oneArrow (component oneArrow false) := by
  apply (source_vertex_iff _ _).mpr
  intro b hb
  cases b
  · exact .refl
  · exact (oneArrow_no_reverse hb).elim

/-- The arrow head is not a source, and cannot be confused with its tail SCC. -/
theorem oneArrow_not_source_boundary : ¬ Source oneArrow (component oneArrow true) := by
  intro h
  exact oneArrow_no_reverse ((source_vertex_iff _ _).mp h false (.single ⟨rfl, rfl⟩))

theorem oneArrow_components_distinct : component oneArrow false ≠ component oneArrow true := by
  intro h
  exact oneArrow_no_reverse ((component_eq_iff _ _ _).mp h).2

/-- The two-vertex directed cycle contracts to one strongly connected component. -/
theorem twoCycle_single_component_boundary (a b : Bool) :
    component (fun x y : Bool => x ≠ y) a = component (fun x y : Bool => x ≠ y) b := by
  apply (component_eq_iff _ _ _).mpr
  by_cases h : a = b
  · subst b; exact ⟨.refl, .refl⟩
  · exact ⟨.single h, .single (fun hba => h hba.symm)⟩

end Komorebi.PaperIRelease.FiniteDigraph
