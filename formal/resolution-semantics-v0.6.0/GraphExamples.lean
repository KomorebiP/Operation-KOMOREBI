import GraphSolver

namespace KRS.Graph.Examples

def diamondAdj (u v : Fin 4) : Bool :=
  ((u == 0 || u == 3) && (v == 1 || v == 2)) ||
    ((v == 0 || v == 3) && (u == 1 || u == 2))

def diamond : SimpleGraph (Fin 4) where
  Adj := fun u v => diamondAdj u v = true
  symm := by decide
  loopless := by decide

instance diamondDecidable : DecidableRel diamond.Adj :=
  fun u v => inferInstanceAs (Decidable (diamondAdj u v = true))

def diamondLabel (v : Fin 4) : Bool := v == 1 || v == 3

def diamondResidual (u v : Fin 4) : Bool := Bool.xor (diamondLabel u) (diamondLabel v)

theorem diamond_residual_integrates : Integrates (G := diamond) diamondResidual diamondLabel := by
  intro v w _
  rfl

theorem diamond_root_false :
    (solve diamond diamondResidual [(0, false)]).map List.ofFn =
      some [false, true, false, true] := by decide

theorem diamond_root_true :
    (solve diamond diamondResidual [(0, true)]).map List.ofFn =
      some [true, false, true, false] := by decide

def triangle : SimpleGraph (Fin 3) where
  Adj := fun u v => u ≠ v
  symm := fun h => Ne.symm h
  loopless := fun _ h => h rfl

instance triangleDecidable : DecidableRel triangle.Adj :=
  fun u v => inferInstanceAs (Decidable (u ≠ v))

def triangleResidual (u v : Fin 3) : Bool :=
  (u == 0 && v == 1) || (u == 1 && v == 0)

theorem triangle_rejected : solve triangle triangleResidual [] = none := by
  have h : (solve triangle triangleResidual []).isNone = true := by decide
  cases hs : solve triangle triangleResidual [] with
  | none => rfl
  | some a => simp [hs] at h

theorem triangle_not_integrable : ¬ ∃ a, Integrates (G := triangle) triangleResidual a := by
  rintro ⟨a, ha⟩
  have hi := solve_complete triangle triangleResidual [] a ha rfl
  simp [triangle_rejected] at hi

def disconnectedAdj (u v : Fin 5) : Bool :=
  (u == 0 && v == 1) || (u == 1 && v == 0) ||
    (u == 2 && v == 3) || (u == 3 && v == 2)

def disconnected : SimpleGraph (Fin 5) where
  Adj := fun u v => disconnectedAdj u v = true
  symm := by decide
  loopless := by decide

instance disconnectedDecidable : DecidableRel disconnected.Adj :=
  fun u v => inferInstanceAs (Decidable (disconnectedAdj u v = true))

def disconnectedResidual (u v : Fin 5) : Bool :=
  (u == 0 && v == 1) || (u == 1 && v == 0)

theorem disconnected_with_isolated_vertex :
    (solve disconnected disconnectedResidual [(0, false), (2, true), (4, true)]).map List.ofFn =
      some [false, true, true, true, true] := by decide

def edgeless (n : Nat) : SimpleGraph (Fin n) where
  Adj := fun _ _ => False
  symm := False.elim
  loopless := fun _ h => h

instance edgelessDecidable (n : Nat) : DecidableRel (edgeless n).Adj :=
  fun _ _ => inferInstanceAs (Decidable False)

theorem empty_graph_has_reconstruction :
    (solve (edgeless 0) (fun _ _ => false) []).map List.ofFn = some [] := by decide

theorem isolated_vertex_can_be_false :
    (solve (edgeless 1) (fun _ _ => false) [(0, false)]).map List.ofFn = some [false] := by decide

theorem isolated_vertex_can_be_true :
    (solve (edgeless 1) (fun _ _ => false) [(0, true)]).map List.ofFn = some [true] := by decide

theorem contradictory_root_pins_rejected :
    solve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)] = none := by
  have h : (solve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)]).isNone = true := by decide
  cases hs : solve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)] with
  | none => rfl
  | some a => simp [hs] at h

theorem no_roots_allows_distinct_reconstructions :
    Integrates (G := edgeless 1) (fun _ _ => false) (fun _ => false) ∧
    Integrates (G := edgeless 1) (fun _ _ => false) (fun _ => true) ∧
    (fun _ : Fin 1 => false) ≠ (fun _ : Fin 1 => true) := by
  refine ⟨by intro _ _ h; exact h.elim, by intro _ _ h; exact h.elim, ?_⟩
  intro h
  have bad := congrFun h 0
  cases bad

def report : List (String × Option (List Bool)) := [
  ("diamond-root-false", (solve diamond diamondResidual [(0, false)]).map List.ofFn),
  ("diamond-root-true", (solve diamond diamondResidual [(0, true)]).map List.ofFn),
  ("inconsistent-triangle", (solve triangle triangleResidual []).map List.ofFn),
  ("disconnected-with-isolated-vertex",
    (solve disconnected disconnectedResidual [(0, false), (2, true), (4, true)]).map List.ofFn),
  ("empty-graph", (solve (edgeless 0) (fun _ _ => false) []).map List.ofFn),
  ("isolated-vertex-true", (solve (edgeless 1) (fun _ _ => false) [(0, true)]).map List.ofFn),
  ("contradictory-root-pins",
    (solve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)]).map List.ofFn)
]

end KRS.Graph.Examples
