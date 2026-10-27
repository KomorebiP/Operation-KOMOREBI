import MachineTheory.BinaryDiagnosis

/-! # Execution meaning of the binary lower bounds -/
namespace Komorebi.MachineTheory.BinaryDiagnosis
open HardInquiry Finset
variable {X E C : Type} [DecidableEq X]

/-- An actual successful run attains the worst-case online coordinate.
The terminal is charged one unit on every reachable state. Empty supports are not runs. -/
theorem worst_execution_attained (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    ∃ x ∈ V, ∃ r, M.execute (fun _ _ _ => 1) h t x = some r ∧
      r.cost () = (M.profile h V t).1 () := by
  induction h generalizing V with
  | zero =>
    obtain ⟨x,hx⟩ := ht.1
    exact ⟨x,hx,⟨x,t,fun _ => 1,[]⟩,rfl,(s.terminal_cost t V ht.1).symm⟩
  | succ h ih =>
    cases t with
    | inl c =>
      obtain ⟨x,hx⟩ := ht.1
      exact ⟨x,hx,⟨x,c,fun _ => 1,[]⟩,rfl,(s.terminal_cost c V ht.1).symm⟩
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      let f : Bool → ℕ := fun o => (Model.optional ((k o).map (M.profile h (M.update V e o)))).1 ()
      have hpos : 0 < univ.sup f := by
        obtain ⟨x,hx⟩ := ht.1.1
        obtain ⟨u,hu,hv⟩ := (M.valid_child ht (M.observe e x)).mp ⟨_,M.actual_next_mem hx e⟩
        have hcost : 1 ≤ f (M.observe e x) := by
          simp only [f,hu,Option.map_some,Model.optional,Option.getD_some]
          rw [work_eq_depth_succ M s h _ u hv]
          omega
        exact lt_of_lt_of_le (Nat.lt_of_lt_of_le Nat.zero_lt_one hcost)
          (Finset.le_sup (f := f) (mem_univ (M.observe e x)))
      obtain ⟨o,_,hmax⟩ := (univ : Finset Bool).exists_mem_eq_sup univ_nonempty f
      cases he : k o with
      | none =>
        have hz : f o = 0 := by simp [f,he,Model.optional]
        omega
      | some child =>
        have hv : M.Valid h (M.update V e o) child := by simpa only [he] using ht.2 o
        obtain ⟨y,hy,r,hr,hcost⟩ := ih _ child hv
        obtain ⟨x,hx,hobs,hnext⟩ := (M.mem_update V e o y).mp hy
        have hp := ht.1.2 x hx
        refine ⟨x,hx,M.prepend e o r,?_,?_⟩
        · simp only [Model.execute,hp,ite_true,hobs,he,Option.bind_some,hnext,hr,Option.map_some]
        · change M.stepCost e () + r.cost () = M.stepCost e () + univ.sup f
          rw [hmax,hcost]
          simp only [f,he,Option.map_some,Model.optional,Option.getD_some]

/-- The information bound is a lower bound on an actual possible execution, not just a ledger. -/
theorem actual_run_lower_bound (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    ∃ x ∈ V, ∃ r, M.execute (fun _ _ _ => 1) h t x = some r ∧
      1 + Nat.clog 2 V.card ≤ r.cost () := by
  obtain ⟨x,hx,r,hr,hcost⟩ := worst_execution_attained M s h V t ht
  exact ⟨x,hx,r,hr,hcost ▸ (binary_lower_bounds M s h V t ht).2.1⟩

end Komorebi.MachineTheory.BinaryDiagnosis
