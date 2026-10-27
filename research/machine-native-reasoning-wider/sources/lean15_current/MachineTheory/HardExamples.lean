import MachineTheory.HardSemantics
import Mathlib.Data.Fintype.Powerset
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! # Exact hard-budget examples and scope controls -/
namespace Komorebi.MachineTheory.HardExamples
open HardInquiry Finset

/-- Scalar cost displayed in a one-coordinate resource vector. -/
def scalar (w m : ℕ) : Profile Unit := (fun _ => w, m)

/-- Four immutable cases. `none` is direct reveal; `some i` is equality testing. -/
def four : Model (Fin 4) (Option (Fin 4)) (Fin 4) (Fin 4) Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun e x => match e with | none => x | some i => if x=i then 1 else 0
  accept := fun x c => decide (x=c)
  stepCost := fun e _ => if e.isNone then 4 else 1
  terminalCost := fun _ _ _ => 0


set_option maxRecDepth 16384 in
set_option maxHeartbeats 2000000 in
theorem four_frontier_three : four.compute 3 univ = {scalar 4 5, scalar 3 7} := by
  decide

/-- A finite invariant table, not a fit inferred from a few horizons. -/
def fourTable (V : Finset (Fin 4)) : Finset (Profile Unit) :=
  match V.card with
  | 0 => ∅
  | 1 => {scalar 0 1}
  | 2 => {scalar 1 3}
  | 3 => {scalar 2 5, scalar 4 4}
  | _ => {scalar 3 7, scalar 4 5}

set_option maxRecDepth 16384 in
set_option maxHeartbeats 2000000 in
theorem fourTable_closed : ∀ V : Finset (Fin 4),
    Model.prune (four.backup fourTable V) = fourTable V := by
  decide

theorem fourTable_full : fourTable univ = {scalar 4 5, scalar 3 7} := by decide

/-- The certificate is a fixed-point argument for every horizon, not extrapolated tests. -/
theorem four_frontier_all (n : ℕ) : four.solve (3+n) univ = {scalar 4 5, scalar 3 7} := by
  rw [← fourTable_full]
  apply four.closed_family_exact fourTable fourTable_closed (3+n) univ
  intro p hp
  have hb : p ∈ four.solve 3 univ := by
    rw [← four.compute_eq_solve, four_frontier_three]
    simpa only [fourTable_full] using hp
  obtain ⟨t,ht,he⟩ := four.solve_witness 3 univ p hb
  obtain ⟨u,hu,hue⟩ := four.pad_horizon 3 n univ t ht
  exact ⟨u,hu,hue.trans he⟩

/-- No controller at ANY finite depth can combine the separate resource minima. -/
theorem four_no_mixed_budget (h : ℕ) :
    ¬ ∃ t : Tree (Option (Fin 4)) (Fin 4) (Fin 4) h,
      four.Valid h univ t ∧ four.profile h univ t ≤ scalar 3 5 := by
  rintro ⟨t,ht,hb⟩
  obtain ⟨p,hp,hpt⟩ := four.closed_family_dominates fourTable fourTable_closed h univ t ht
  have hpb := hpt.trans hb
  rw [fourTable_full, mem_insert, mem_singleton] at hp
  rcases hp with rfl | rfl
  · have h := hpb.1 (); norm_num [scalar] at h
  · have h := hpb.2; norm_num [scalar] at h

/-- Both nondominated profiles are actually achieved, not just lower bounds. -/
theorem four_two_witnesses :
    (∃ t : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 3,
      four.Valid 3 univ t ∧ four.profile 3 univ t = scalar 4 5) ∧
    (∃ t : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 3,
      four.Valid 3 univ t ∧ four.profile 3 univ t = scalar 3 7) := by
  constructor
  · apply four.solve_witness 3 univ
    rw [← four.compute_eq_solve, four_frontier_three]
    exact mem_insert_self _ _
  · apply four.solve_witness 3 univ
    rw [← four.compute_eq_solve, four_frontier_three]
    exact mem_insert_of_mem (mem_singleton_self _)

/-- One direct reveal, one branch for each of four reports. -/
def direct : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 1 := .inr (none,fun o => some o)

def equalLast : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 1 :=
  .inr (some 2, fun o => if o=1 then some (2 : Fin 4) else if o=0 then some (3 : Fin 4) else none)
def equalMiddle : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 2 :=
  .inr (some 1, fun o => if o=1 then some (.inl 1) else if o=0 then some equalLast else none)
def equality : Tree (Option (Fin 4)) (Fin 4) (Fin 4) 3 :=
  .inr (some 0, fun o => if o=1 then some (.inl 0) else if o=0 then some equalMiddle else none)

theorem direct_valid : four.Valid 1 univ direct := by decide
theorem direct_profile : four.profile 1 univ direct = scalar 4 5 := by decide
theorem equality_valid : four.Valid 3 univ equality := by decide
theorem equality_profile : four.profile 3 univ equality = scalar 3 7 := by decide

/-- The four full execution traces, not a count of only one selected branch. -/
theorem equality_report_counts : ∀ x : Fin 4,
    (four.execute (fun _ _ _ => 0) 3 equality x).map (fun r => r.history.length) =
      some (if x=0 then 1 else if x=1 then 2 else 3) := by decide

theorem equality_terminal_outputs : ∀ x : Fin 4,
    (four.execute (fun _ _ _ => 0) 3 equality x).map (fun r => r.artifact) = some x := by decide

theorem equality_records : Model.records 3 equality = 7 := by decide
theorem direct_records : Model.records 1 direct = 5 := by decide

end Komorebi.MachineTheory.HardExamples
