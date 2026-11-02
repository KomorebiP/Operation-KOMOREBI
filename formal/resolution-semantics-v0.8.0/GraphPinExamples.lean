import GraphPinning
import GraphCountExamples

namespace KRS.Graph.PinExamples

open KRS.Graph.Examples KRS.Graph.CountExamples

theorem diamond_one_pin_count :
    (pinnedSolutions diamond diamondResidual [(0, false)]).length = 1 := by
  apply pinned_solutions_count diamond diamondIndex diamondResidual [(0, false)]
    ⟨diamondLabel, diamond_residual_integrates, by rfl⟩

theorem disconnected_one_pin_count :
    (pinnedSolutions disconnected disconnectedResidual [(0, false)]).length = 4 := by
  apply pinned_solutions_count disconnected disconnectedIndex disconnectedResidual [(0, false)]
    ⟨fun v => v == 1, by decide, by rfl⟩

theorem disconnected_same_component_pins_count :
    (pinnedSolutions disconnected disconnectedResidual [(0, false), (1, true)]).length = 4 := by
  apply pinned_solutions_count disconnected disconnectedIndex disconnectedResidual
    [(0, false), (1, true)] ⟨fun v => v == 1, by decide, by rfl⟩

theorem disconnected_two_components_pinned_count :
    (pinnedSolutions disconnected disconnectedResidual [(0, false), (2, false)]).length = 2 := by
  apply pinned_solutions_count disconnected disconnectedIndex disconnectedResidual
    [(0, false), (2, false)] ⟨fun v => v == 1, by decide, by rfl⟩

theorem disconnected_all_components_pinned_count :
    (pinnedSolutions disconnected disconnectedResidual [(0, false), (2, false), (4, false)]).length = 1 := by
  apply pinned_solutions_count disconnected disconnectedIndex disconnectedResidual
    [(0, false), (2, false), (4, false)] ⟨fun v => v == 1, by decide, by rfl⟩

theorem duplicate_pin_count :
    (pinnedSolutions diamond diamondResidual [(0, false), (0, false)]).length = 1 := by decide

theorem compatible_connected_pins_count :
    (pinnedSolutions diamond diamondResidual [(0, false), (1, true)]).length = 1 := by decide

theorem conflicting_connected_pins_count :
    (pinnedSolutions diamond diamondResidual [(0, false), (1, false)]).length = 0 := by decide

theorem contradictory_vertex_pins_count :
    (pinnedSolutions diamond diamondResidual [(0, false), (0, true)]).length = 0 := by decide

theorem empty_pinned_count :
    (pinnedSolutions (edgeless 0) (fun _ _ => false) []).length = 1 := by decide

theorem isolated_pinned_count :
    (pinnedSolutions (edgeless 1) (fun _ _ => false) [(0, true)]).length = 1 := by decide

theorem nonintegrable_pinned_count :
    (pinnedSolutions triangle triangleResidual [(0, false)]).length = 0 := by decide

def report : List (String × Nat) := [
  ("diamond-no-pins", (pinnedSolutions diamond diamondResidual []).length),
  ("diamond-one-pin", (pinnedSolutions diamond diamondResidual [(0, false)]).length),
  ("diamond-duplicate-pin", (pinnedSolutions diamond diamondResidual [(0, false), (0, false)]).length),
  ("diamond-compatible-pins", (pinnedSolutions diamond diamondResidual [(0, false), (1, true)]).length),
  ("diamond-conflicting-pins", (pinnedSolutions diamond diamondResidual [(0, false), (1, false)]).length),
  ("diamond-contradictory-vertex-pins", (pinnedSolutions diamond diamondResidual [(0, false), (0, true)]).length),
  ("disconnected-no-pins", (pinnedSolutions disconnected disconnectedResidual []).length),
  ("disconnected-one-pin", (pinnedSolutions disconnected disconnectedResidual [(0, false)]).length),
  ("disconnected-same-component-pins", (pinnedSolutions disconnected disconnectedResidual [(0, false), (1, true)]).length),
  ("disconnected-two-components-pinned", (pinnedSolutions disconnected disconnectedResidual [(0, false), (2, false)]).length),
  ("disconnected-all-components-pinned", (pinnedSolutions disconnected disconnectedResidual [(0, false), (2, false), (4, false)]).length),
  ("empty-graph-no-pins", (pinnedSolutions (edgeless 0) (fun _ _ => false) []).length),
  ("isolated-vertex-pinned", (pinnedSolutions (edgeless 1) (fun _ _ => false) [(0, true)]).length),
  ("nonintegrable-triangle-pinned", (pinnedSolutions triangle triangleResidual [(0, false)]).length)
]

end KRS.Graph.PinExamples
