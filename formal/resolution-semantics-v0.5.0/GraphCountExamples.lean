import GraphCounting
import GraphExamples

namespace KRS.Graph.CountExamples

open KRS.Graph.Examples

theorem diamond_reachable_from_zero (v : Fin 4) : Reachable diamond 0 v := by
  have hv : v = 0 ∨ v = 1 ∨ v = 2 ∨ v = 3 := by omega
  rcases hv with rfl | rfl | rfl | rfl
  · exact ⟨.nil 0⟩
  · exact ⟨.cons (by decide) (.nil 1)⟩
  · exact ⟨.cons (by decide) (.nil 2)⟩
  · exact ⟨.cons (w := 1) (by decide) (.cons (by decide) (.nil 3))⟩

def diamondIndex : ComponentIndex diamond 1 :=
  connectedComponentIndex diamond 0 diamond_reachable_from_zero

theorem diamond_has_two_reconstructions : (allSolutions diamond diamondResidual).length = 2 := by
  exact all_solutions_count diamond diamondIndex diamondResidual ⟨diamondLabel, diamond_residual_integrates⟩

def disconnectedLabel (v : Fin 5) : Fin 3 :=
  if v.val < 2 then 0 else if v.val < 4 then 1 else 2

def disconnectedVertex (i : Fin 3) : Fin 5 := if i = 0 then 0 else if i = 1 then 2 else 4

def disconnectedIndex : ComponentIndex disconnected 3 where
  label := disconnectedLabel
  vertex := disconnectedVertex
  edge_same := by decide
  label_vertex := by decide
  vertex_reachable := by
    intro v
    have hv : v = 0 ∨ v = 1 ∨ v = 2 ∨ v = 3 ∨ v = 4 := by omega
    rcases hv with rfl | rfl | rfl | rfl | rfl
    · exact ⟨.nil 0⟩
    · exact ⟨.cons (by decide) (.nil 1)⟩
    · exact ⟨.nil 2⟩
    · exact ⟨.cons (by decide) (.nil 3)⟩
    · exact ⟨.nil 4⟩

theorem disconnected_has_eight_reconstructions :
    (allSolutions disconnected disconnectedResidual).length = 8 := by
  apply all_solutions_count disconnected disconnectedIndex disconnectedResidual
  exact ⟨fun v => v == 1, by decide⟩

def edgelessIndex (n : Nat) : ComponentIndex (edgeless n) n where
  label := id
  vertex := id
  edge_same := fun _ _ h => h.elim
  vertex_reachable := fun v => ⟨.nil v⟩
  label_vertex := fun _ => rfl

theorem edgeless_count (n : Nat) (r : Fin n → Fin n → Bool) :
    (allSolutions (edgeless n) r).length = 2 ^ n := by
  apply all_solutions_count (edgeless n) (edgelessIndex n) r
  exact ⟨fun _ => false, by intro _ _ h; exact h.elim⟩

theorem empty_graph_has_one_reconstruction :
    (allSolutions (edgeless 0) (fun _ _ => false)).length = 1 := edgeless_count 0 _

theorem isolated_vertex_has_two_reconstructions :
    (allSolutions (edgeless 1) (fun _ _ => false)).length = 2 := edgeless_count 1 _

theorem triangle_reachable_from_zero (v : Fin 3) : Reachable triangle 0 v := by
  by_cases h : v = 0
  · subst v
    exact ⟨.nil 0⟩
  · exact ⟨.cons (Ne.symm h) (.nil v)⟩

def triangleIndex : ComponentIndex triangle 1 :=
  connectedComponentIndex triangle 0 triangle_reachable_from_zero

theorem triangle_has_no_reconstructions : (allSolutions triangle triangleResidual).length = 0 := by
  rw [(all_solutions_empty_iff triangle triangleResidual).mpr triangle_not_integrable]
  rfl

def report : List (String × Nat) := [
  ("diamond-connected", (allSolutions diamond diamondResidual).length),
  ("inconsistent-triangle", (allSolutions triangle triangleResidual).length),
  ("two-edges-and-isolated-vertex", (allSolutions disconnected disconnectedResidual).length),
  ("empty-graph", (allSolutions (edgeless 0) (fun _ _ => false)).length),
  ("isolated-vertex", (allSolutions (edgeless 1) (fun _ _ => false)).length),
  ("four-isolated-vertices", (allSolutions (edgeless 4) (fun _ _ => false)).length)
]

end KRS.Graph.CountExamples
