import KomorebiPadic.ReachabilityExamples
open KomorebiPadic LinearReachability
noncomputable section
example : reachable correlated = diagonal := correlated_reachable_eq_diagonal
example : Nat.card (State correlated) = 5 := correlated_reachable_card
example : Nat.card (CoordinateIdeal.State (p := 5) (r := 1)
    (CoordinateIdeal.least (p := 5) (r := 1) (by decide : 0 < 5) CoordinateSupport.correlatedSystem)) = 125 :=
  correlated_ideal_card
example : Nat.card (State correlated) < 125 := by rw [correlated_reachable_card]; decide
example : 1 ≤ Nat.log 5 (Nat.card (State correlated)) := by rw [correlated_reachable_card]; decide +kernel
example : Nat.card (State constantOrbit) = 5 := reachability_is_not_observability.1
example : (0 : ZMod 5) ∈ reachable constantOrbit := span_strictly_exceeds_orbit.1
example : run constantOrbit ([] : List (Fin 1)) constantOrbit.initial = 1 := rfl
example : run constantOrbit [0,0,0] constantOrbit.initial = 1 := constantOrbit_run _
example : run correlated [0] correlated.initial = 0 := by
  exact diagonal_transition_zero _ _ diagonal_closed.1
example : iterate correlated 3 = reachable correlated := by
  apply iterate_eq_reachable correlated (by decide : Nat.Prime 5)
  simp [Nat.card_eq_fintype_card]
example : iterate constantOrbit 1 = reachable constantOrbit := by
  apply iterate_eq_reachable constantOrbit (by decide : Nat.Prime 5)
  simp
end
