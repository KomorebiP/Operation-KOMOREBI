import MachineTheory

/-! Independently restated source-facing contract for Core 5.1. -/
open Komorebi.MachineTheory
open HardInquiry Finset
variable {X E O C R : Type} [DecidableEq X] [Fintype E]
  [Fintype O] [DecidableEq O] [Fintype C] [Fintype R]

example (M : Model X E O C R) (h : ℕ) (V : Finset X) (p : Profile R) :
    p ∈ M.solve h V ↔
      (∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p) ∧
      ∀ t : Tree E O C h, M.Valid h V t → M.profile h V t ≤ p → p ≤ M.profile h V t :=
  M.exact_frontier h V p

example (M : Model X E O C R) (h : ℕ) (V : Finset X) (online : R → ℕ) (storage : ℕ) :
    (∃ t : Tree E O C h, M.Valid h V t ∧
      (∀ r, (M.profile h V t).1 r ≤ online r) ∧ (M.profile h V t).2 ≤ storage) ↔
      ∃ p ∈ M.solve h V, (∀ r, p.1 r ≤ online r) ∧ p.2 ≤ storage :=
  M.joint_budget_iff h V (online,storage)

example (M : Model X E O C R) (h : ℕ) (V : Finset X) (p : Profile R)
    (hp : p ∈ M.compute h V) :
    ∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p := by
  rw [M.compute_eq_solve] at hp
  exact M.solve_witness h V p hp

example (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h) :
    (M.profile h V t).2 = Model.records h t := M.profile_records h V t

example (M : Model X E O C R) (charge : C → X → R → ℕ)
    (hc : ∀ c V r, M.terminalCost c V r = V.sup (fun x => charge c x r))
    (h : ℕ) (V : Finset X) (t : Tree E O C h) (ht : M.Valid h V t) (j : R) :
    ∃ x ∈ V, ∃ r, M.execute charge h t x = some r ∧ r.cost j = (M.profile h V t).1 j :=
  M.worst_coordinate_attained charge hc h V t ht j

example {I : Type} {B Y : I → Type} (M : Model X E O C R)
    (A : RecipientExecution.Audience X C I B Y) (V : Finset X) (c : C) :
    (AudienceBridge.attach M A).Terminal V c ↔ V.Nonempty ∧ ∀ x ∈ V, A.Accepts x c :=
  AudienceBridge.terminal_common M A V c

example (n : ℕ) : HardExamples.four.solve (3+n) univ =
    {HardExamples.scalar 4 5,HardExamples.scalar 3 7} := HardExamples.four_frontier_all n

example (h : ℕ) : ¬ ∃ t : Tree (Option (Fin 4)) (Fin 4) (Fin 4) h,
    HardExamples.four.Valid h univ t ∧
    HardExamples.four.profile h univ t ≤ HardExamples.scalar 3 5 := HardExamples.four_no_mixed_budget h
