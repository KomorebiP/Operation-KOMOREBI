import GraphTraversalSolver
import GraphPinExamples

namespace KRS.Graph.TraversalExamples

open KRS.Graph.Examples KRS.Graph.CountExamples

def diamondPath (v : Fin 4) : Walk diamond 0 v := by
  by_cases h0 : v = 0
  · subst v; exact .nil 0
  by_cases h1 : v = 1
  · subst v; exact .cons (by decide) (.nil 1)
  by_cases h2 : v = 2
  · subst v; exact .cons (by decide) (.nil 2)
  have h3 : v = 3 := by omega
  subst v
  exact .cons (w := 1) (by decide) (.cons (by decide) (.nil 3))

def diamondTraversal : RootedTraversal diamond 1 where
  index := diamondIndex
  walk := diamondPath

def diamondAlternatePath (v : Fin 4) : Walk diamond 0 v := by
  by_cases h3 : v = 3
  · subst v
    exact .cons (w := 2) (by decide) (.cons (by decide) (.nil 3))
  exact diamondPath v

def diamondAlternateTraversal : RootedTraversal diamond 1 where
  index := diamondIndex
  walk := diamondAlternatePath

def diamondOtherRootPath (v : Fin 4) : Walk diamond 3 v := by
  by_cases h0 : v = 0
  · subst v
    exact .cons (w := 1) (by decide) (.cons (by decide) (.nil 0))
  by_cases h1 : v = 1
  · subst v; exact .cons (by decide) (.nil 1)
  by_cases h2 : v = 2
  · subst v; exact .cons (by decide) (.nil 2)
  have h3 : v = 3 := by omega
  subst v
  exact .nil 3

def diamondOtherRootTraversal : RootedTraversal diamond 1 where
  index := connectedComponentIndex diamond 3 (fun v => ⟨diamondOtherRootPath v⟩)
  walk := diamondOtherRootPath

def trianglePath (v : Fin 3) : Walk triangle 0 v := by
  by_cases h : v = 0
  · subst v; exact .nil 0
  exact .cons (Ne.symm h) (.nil v)

def triangleTraversal : RootedTraversal triangle 1 where
  index := triangleIndex
  walk := trianglePath

def disconnectedPath (v : Fin 5) : Walk disconnected
    (disconnectedIndex.vertex (disconnectedIndex.label v)) v := by
  by_cases h0 : v = 0
  · subst v; exact .nil 0
  by_cases h1 : v = 1
  · subst v; exact .cons (by decide) (.nil 1)
  by_cases h2 : v = 2
  · subst v; exact .nil 2
  by_cases h3 : v = 3
  · subst v; exact .cons (by decide) (.nil 3)
  have h4 : v = 4 := by omega
  subst v
  exact .nil 4

def disconnectedTraversal : RootedTraversal disconnected 3 where
  index := disconnectedIndex
  walk := disconnectedPath

def edgelessTraversal (n : Nat) : RootedTraversal (edgeless n) n where
  index := edgelessIndex n
  walk := fun v => .nil v

theorem diamond_root_false :
    (traversalSolve diamondTraversal diamondResidual [(0, false)]).map List.ofFn =
      some [false, true, false, true] := by decide

theorem diamond_root_true :
    (traversalSolve diamondTraversal diamondResidual [(0, true)]).map List.ofFn =
      some [true, false, true, false] := by decide

theorem diamond_nonroot_pin :
    (traversalSolve diamondTraversal diamondResidual [(3, false)]).map List.ofFn =
      some [true, false, true, false] := by decide

theorem diamond_duplicate_pin :
    (traversalSolve diamondTraversal diamondResidual [(0, false), (0, false)]).map List.ofFn =
      some [false, true, false, true] := by decide

theorem diamond_conflicting_pins :
    (traversalSolve diamondTraversal diamondResidual [(0, false), (1, false)]).isNone = true := by decide

theorem diamond_alternate_path :
    (traversalSolve diamondAlternateTraversal diamondResidual [(0, false)]).map List.ofFn =
      some [false, true, false, true] := by decide

theorem diamond_other_root :
    (traversalSolve diamondOtherRootTraversal diamondResidual []).map List.ofFn =
      some [true, false, true, false] := by decide

theorem nonintegrable_triangle_rejected :
    (traversalSolve triangleTraversal triangleResidual []).isNone = true := by decide

theorem consistent_triangle_accepted :
    (traversalSolve triangleTraversal (fun _ _ => false) []).map List.ofFn =
      some [false, false, false] := by decide

theorem disconnected_partial_pin :
    (traversalSolve disconnectedTraversal disconnectedResidual [(1, false)]).map List.ofFn =
      some [true, false, false, false, false] := by decide

theorem disconnected_covered :
    (traversalSolve disconnectedTraversal disconnectedResidual [(0, false), (2, true), (4, true)]).map List.ofFn =
      some [false, true, true, true, true] := by decide

theorem empty_graph_accepted :
    (traversalSolve (edgelessTraversal 0) (fun _ _ => false) []).map List.ofFn = some [] := by decide

theorem isolated_pin_accepted :
    (traversalSolve (edgelessTraversal 1) (fun _ _ => false) [(0, true)]).map List.ofFn =
      some [true] := by decide

theorem contradictory_pins_rejected :
    (traversalSolve (edgelessTraversal 1) (fun _ _ => false) [(0, false), (0, true)]).isNone = true := by decide

def report : List (String × Option (List Bool)) := [
  ("traversal-diamond-root-false", (traversalSolve diamondTraversal diamondResidual [(0, false)]).map List.ofFn),
  ("traversal-diamond-root-true", (traversalSolve diamondTraversal diamondResidual [(0, true)]).map List.ofFn),
  ("traversal-diamond-nonroot-pin", (traversalSolve diamondTraversal diamondResidual [(3, false)]).map List.ofFn),
  ("traversal-diamond-duplicate-pin", (traversalSolve diamondTraversal diamondResidual [(0, false), (0, false)]).map List.ofFn),
  ("traversal-diamond-conflicting-pins", (traversalSolve diamondTraversal diamondResidual [(0, false), (1, false)]).map List.ofFn),
  ("traversal-diamond-alternate-path", (traversalSolve diamondAlternateTraversal diamondResidual [(0, false)]).map List.ofFn),
  ("traversal-diamond-other-root", (traversalSolve diamondOtherRootTraversal diamondResidual []).map List.ofFn),
  ("traversal-nonintegrable-triangle", (traversalSolve triangleTraversal triangleResidual []).map List.ofFn),
  ("traversal-consistent-triangle", (traversalSolve triangleTraversal (fun _ _ => false) []).map List.ofFn),
  ("traversal-disconnected-partial-pin", (traversalSolve disconnectedTraversal disconnectedResidual [(1, false)]).map List.ofFn),
  ("traversal-disconnected-covered", (traversalSolve disconnectedTraversal disconnectedResidual [(0, false), (2, true), (4, true)]).map List.ofFn),
  ("traversal-empty-graph", (traversalSolve (edgelessTraversal 0) (fun _ _ => false) []).map List.ofFn),
  ("traversal-isolated-pin", (traversalSolve (edgelessTraversal 1) (fun _ _ => false) [(0, true)]).map List.ofFn),
  ("traversal-contradictory-pins", (traversalSolve (edgelessTraversal 1) (fun _ _ => false) [(0, false), (0, true)]).map List.ofFn)
]

end KRS.Graph.TraversalExamples
