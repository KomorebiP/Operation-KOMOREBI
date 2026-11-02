import GraphAutomaticTraversal
import GraphTraversalExamples

namespace KRS.Graph.AutomaticExamples

open KRS.Graph.Examples

def lineGraph (n : Nat) : SimpleGraph (Fin n) where
  Adj := fun u v => u.val + 1 = v.val ∨ v.val + 1 = u.val
  symm := fun h => h.symm
  loopless := by intro v h; omega

instance lineGraphDecidable (n : Nat) : DecidableRel (lineGraph n).Adj :=
  fun u v => inferInstanceAs (Decidable (u.val + 1 = v.val ∨ v.val + 1 = u.val))

def alternatingLabel {n : Nat} (v : Fin n) : Bool := v.val % 2 == 1

def lineResidual {n : Nat} (u v : Fin n) : Bool :=
  Bool.xor (alternatingLabel u) (alternatingLabel v)

theorem automatic_diamond_exists :
    (automaticSolve diamond diamondResidual [(0, false)]).isSome = true :=
  automatic_solve_complete diamond diamondResidual [(0, false)] diamondLabel
    diamond_residual_integrates rfl

theorem automatic_nonroot_pin_exists :
    (automaticSolve diamond diamondResidual [(3, false)]).isSome = true := by
  apply automatic_solve_complete diamond diamondResidual [(3, false)]
    (fun v => !diamondLabel v)
  · decide
  · rfl

theorem automatic_triangle_rejected : automaticSolve triangle triangleResidual [] = none := by
  apply (automatic_solve_none_iff_no_solution triangle triangleResidual []).mpr
  rintro ⟨a, ha, _⟩
  exact triangle_not_integrable ⟨a, ha⟩

theorem automatic_contradictory_pins_rejected :
    automaticSolve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)] = none := by
  apply (automatic_solve_none_iff_no_solution _ _ _).mpr
  rintro ⟨a, _, hp⟩
  have h0 := pins_match_at_vertex a _ hp 0 false (by simp)
  have h1 := pins_match_at_vertex a _ hp 0 true (by simp)
  rw [h0] at h1
  cases h1

theorem automatic_line_exists (n : Nat) :
    (automaticSolve (lineGraph n) lineResidual []).isSome = true := by
  apply automatic_solve_complete (lineGraph n) lineResidual [] alternatingLabel
  · intro _ _ _; rfl
  · rfl

theorem automatic_empty_component_count : (buildTraversal (edgeless 0)).1 = 0 := by decide

theorem automatic_empty_solution :
    (automaticSolve (edgeless 0) (fun _ _ => false) []).map List.ofFn = some [] := by decide

def resultText {n : Nat} (result : Option (Fin n → Bool)) : String :=
  match result.map List.ofFn with
  | none => "none"
  | some bits => "some [" ++ String.intercalate ", " (bits.map toString) ++ "]"

def report : List (String × String) := [
  ("automatic-diamond-unpinned", resultText (automaticSolve diamond diamondResidual [])),
  ("automatic-diamond-root-true", resultText (automaticSolve diamond diamondResidual [(0, true)])),
  ("automatic-diamond-nonroot-pin", resultText (automaticSolve diamond diamondResidual [(3, false)])),
  ("automatic-diamond-conflicting-pins", resultText (automaticSolve diamond diamondResidual [(0, false), (1, false)])),
  ("automatic-diamond-duplicate-pin", resultText (automaticSolve diamond diamondResidual [(0, false), (0, false)])),
  ("automatic-inconsistent-triangle", resultText (automaticSolve triangle triangleResidual [])),
  ("automatic-consistent-triangle", resultText (automaticSolve triangle (fun _ _ => false) [])),
  ("automatic-asymmetric-field", resultText (automaticSolve (lineGraph 2) (fun u v => u == 0 && v == 1) [])),
  ("automatic-disconnected-partial-pin", resultText (automaticSolve disconnected disconnectedResidual [(1, false)])),
  ("automatic-disconnected-covered", resultText (automaticSolve disconnected disconnectedResidual [(0, false), (2, true), (4, true)])),
  ("automatic-disconnected-unpinned", resultText (automaticSolve disconnected disconnectedResidual [])),
  ("automatic-empty-graph", resultText (automaticSolve (edgeless 0) (fun _ _ => false) [])),
  ("automatic-isolated-pin", resultText (automaticSolve (edgeless 1) (fun _ _ => false) [(0, true)])),
  ("automatic-contradictory-pins", resultText (automaticSolve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)])),
  ("automatic-line-eight", resultText (automaticSolve (lineGraph 8) lineResidual [])),
  ("automatic-line-eight-terminal-pin", resultText (automaticSolve (lineGraph 8) lineResidual [(7, false)])),
  ("automatic-line-thirty-two", resultText (automaticSolve (lineGraph 32) lineResidual [])),
  ("automatic-components-diamond", toString (buildTraversal diamond).1),
  ("automatic-components-disconnected", toString (buildTraversal disconnected).1),
  ("automatic-components-empty", toString (buildTraversal (edgeless 0)).1),
  ("automatic-components-four-isolated", toString (buildTraversal (edgeless 4)).1)
]

end KRS.Graph.AutomaticExamples
