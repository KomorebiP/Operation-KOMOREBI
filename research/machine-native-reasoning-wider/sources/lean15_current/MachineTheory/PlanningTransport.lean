import MachineTheory.Planning

/-!
Core 5.4, exact transport of planning through a joint-instrument quotient.
The proof first establishes a general information-state simulation, then constructs
that simulation from actual fine/coarse probability beliefs and the checked instrument.
-/
namespace Komorebi.MachineTheory
namespace Planning
open scoped BigOperators
noncomputable section

variable {S T A O D : Type*} [Fintype O]

/-- Every operational input to planning must factor through the retained state. -/
structure ExactMap (M : Model S A O D) (N : Model T A O D) (f : S → T) : Prop where
  actions : ∀ s, M.actions s = N.actions (f s)
  decisions : ∀ s, M.decisions s = N.decisions (f s)
  cost : ∀ s a, M.cost s a = N.cost (f s) a
  loss : ∀ s d, M.loss s d = N.loss (f s) d
  prob : ∀ s a o, M.prob s a o = N.prob (f s) a o
  next : ∀ s a o (ho : 0 < M.prob s a o),
    f (M.next s a o ho) = N.next (f s) a o (by rw [← prob s a o]; exact ho)

variable {M : Model S A O D} {N : Model T A O D} {f : S → T}

/-- Report-dependent continuation payoffs are preserved on exactly the positive branches. -/
theorem ExactMap.sum_eq (H : ExactMap M N f) (V : O → S → ℝ) (W : O → T → ℝ)
    (hVW : ∀ o s, V o s = W o (f s)) (s : S) (a : A) :
    (∑ o, if ho : 0 < M.prob s a o then M.prob s a o * V o (M.next s a o ho) else 0) =
    ∑ o, if ho : 0 < N.prob (f s) a o then
      N.prob (f s) a o * W o (N.next (f s) a o ho) else 0 := by
  classical
  apply Finset.sum_congr rfl
  intro o _
  by_cases ho : 0 < M.prob s a o
  · have ho' : 0 < N.prob (f s) a o := by rw [← H.prob s a o]; exact ho
    rw [dite_eq_left ho, dite_eq_left ho', hVW, H.next]
    exact congrArg₂ (· * ·) (H.prob s a o) rfl
  · have ho' : ¬ 0 < N.prob (f s) a o := by rw [← H.prob s a o]; exact ho
    rw [dite_eq_right ho, dite_eq_right ho']

theorem ExactMap.backup_eq (H : ExactMap M N f) (V : S → ℝ) (W : T → ℝ)
    (hVW : ∀ s, V s = W (f s)) (s : S) (a : A) :
    backup M V s a = backup N W (f s) a := by
  unfold backup
  rw [H.cost]
  congr 1
  exact H.sum_eq (fun _ => V) (fun _ => W) (fun _ => hVW) s a

theorem ExactMap.menu_eq (H : ExactMap M N f) (s : S) : menu M s = menu N (f s) := by
  classical
  simp only [menu, H.actions, H.decisions]

/-- Equality of Bellman values at every horizon, proved from the local operational map. -/
theorem ExactMap.value_eq (H : ExactMap M N f) (h : Nat) (s : S) :
    value M h s = value N h (f s) := by
  induction h generalizing s with
  | zero =>
      apply finiteMin_congr _ _ _ _ _ _ (H.decisions s)
      intro d _
      exact H.loss s d
  | succ h ih =>
      apply finiteMin_congr _ _ _ _ _ _ (H.menu_eq s)
      intro c _
      cases c with
      | inl d => exact H.loss s d
      | inr a => exact H.backup_eq (value M h) (value N h) ih s a

/-- This compares each first experiment with itself, including all of its continuation branches. -/
theorem ExactMap.firstValue_eq (H : ExactMap M N f) (h : Nat) (s : S) (c : D ⊕ A) :
    firstValue M h s c = firstValue N h (f s) c := by
  cases c with
  | inl d => exact H.loss s d
  | inr a => exact H.backup_eq _ _ (H.value_eq h) s a

/-- The complete minimizing first-choice set is preserved, not only one minimum number. -/
theorem ExactMap.optimalFirst_iff (H : ExactMap M N f) (h : Nat) (s : S) (c : D ⊕ A) :
    OptimalFirst M h s c ↔ OptimalFirst N h (f s) c := by
  simp only [OptimalFirst, H.menu_eq, H.firstValue_eq, H.value_eq]

/-- In particular, the allowed optimal stopping decisions agree at horizon zero. -/
theorem ExactMap.optimalStop_iff (H : ExactMap M N f) (h : Nat) (s : S) (d : D) :
    OptimalStop M h s d ↔ OptimalStop N h (f s) d := by
  simp only [OptimalStop, H.decisions, H.loss, H.value_eq]

/-- A fixed tree has the same expected loss on the fine and coarse realization. -/
theorem ExactMap.evaluate_eq (H : ExactMap M N f) (P : Tree A O D) (s : S) :
    evaluate M P s = evaluate N P (f s) := by
  induction P generalizing s with
  | stop d => exact H.loss s d
  | experiment a k ih =>
      simp only [evaluate, H.cost]
      congr 1
      exact H.sum_eq (fun o => evaluate M (k o)) (fun o => evaluate N (k o)) ih s a

/-- Fine legality and coarse legality agree at every positive-probability continuation. -/
theorem ExactMap.feasible_iff (H : ExactMap M N f) (h : Nat) (s : S) (P : Tree A O D) :
    Feasible M h s P ↔ Feasible N h (f s) P := by
  induction h generalizing s P with
  | zero =>
      cases P with
      | stop d => simp only [Feasible, H.decisions]
      | experiment a k => rfl
  | succ h ih =>
      cases P with
      | stop d => simp only [Feasible, H.decisions]
      | experiment a k =>
          simp only [Feasible, H.actions]
          apply and_congr_right
          intro _
          constructor
          · intro hk o ho'
            have ho : 0 < M.prob s a o := by rw [H.prob]; exact ho'
            have hh := (ih (M.next s a o ho) (k o)).mp (hk o ho)
            rw [H.next] at hh
            exact hh
          · intro hk o ho
            have ho' : 0 < N.prob (f s) a o := by rw [← H.prob]; exact ho
            apply (ih (M.next s a o ho) (k o)).mpr
            rw [H.next]
            exact hk o ho'

/-- One coarse tree, constructed from q alone, works for every fine belief mapping to q. -/
theorem ExactMap.common_minimizing_tree (H : ExactMap M N f) (h : Nat) (q : T) :
    ∃ P : Tree A O D, P.Bounded h ∧ Feasible N h q P ∧ evaluate N P q = value N h q ∧
      ∀ s, f s = q → Feasible M h s P ∧ evaluate M P s = value M h s := by
  obtain ⟨P, hb, hp, he⟩ := minimizing_tree_exists N h q
  refine ⟨P, hb, hp, he, ?_⟩
  intro s hs
  constructor
  · exact (H.feasible_iff h s P).mpr (hs.symm ▸ hp)
  · rw [H.evaluate_eq, H.value_eq, hs, he]

end
end Planning

namespace BeliefPlanning
open Instrument Planning
open scoped BigOperators
noncomputable section

/-- A belief carries its positivity and normalization proof. -/
abbrev Belief (X : Type*) [Fintype X] := {p : X → ℝ // IsDist p}

variable {X Z A O D : Type*} [Fintype X] [Fintype Z] [Fintype O] [DecidableEq Z]

def aggregate (π : X → Z) (p : Belief X) : Belief Z := ⟨push π p.val, push_dist π p.val p.property⟩

/-- Catalogues and charges are functions of the observable coarse belief. Terminal loss is statewise. -/
structure Contract (Z A D : Type*) [Fintype Z] where
  actions : Belief Z → Finset A
  decisions : Belief Z → Finset D
  decisions_nonempty : ∀ q, (decisions q).Nonempty
  charge : Belief Z → A → ℝ
  charge_nonnegative : ∀ q a, 0 ≤ charge q a
  terminalLoss : D → Z → ℝ

/-- Fine-model planning has access only to catalogues and charges inherited from C p. -/
def fineModel (K : Law X A O) (π : X → Z) (C : Contract Z A D) :
    Model (Belief X) A O D where
  actions p := C.actions (aggregate π p)
  decisions p := C.decisions (aggregate π p)
  decisions_nonempty p := C.decisions_nonempty (aggregate π p)
  cost p a := C.charge (aggregate π p) a
  cost_nonnegative p a := C.charge_nonnegative (aggregate π p) a
  loss p d := ∑ x, p.val x * C.terminalLoss d (π x)
  prob p a o := mass (applyKernel (K.kernel a o) p.val)
  nonnegative p a o := Finset.sum_nonneg (fun x _ =>
    apply_nonnegative _ (K.nonnegative a o) p.val p.property.1 x)
  normalized p a := (report_mass_total K a p.val).trans p.property.2
  next p a o ho := ⟨normalize (applyKernel (K.kernel a o) p.val),
    normalize_dist _ (apply_nonnegative _ (K.nonnegative a o) p.val p.property.1) ho⟩

/-- The coarse planner uses the actual normalized coarse instrument. -/
def coarseModel (L : Law Z A O) (C : Contract Z A D) : Model (Belief Z) A O D where
  actions := C.actions
  decisions := C.decisions
  decisions_nonempty := C.decisions_nonempty
  cost := C.charge
  cost_nonnegative := C.charge_nonnegative
  loss q d := ∑ z, q.val z * C.terminalLoss d z
  prob q a o := mass (applyKernel (L.kernel a o) q.val)
  nonnegative q a o := Finset.sum_nonneg (fun z _ =>
    apply_nonnegative _ (L.nonnegative a o) q.val q.property.1 z)
  normalized q a := (report_mass_total L a q.val).trans q.property.2
  next q a o ho := ⟨normalize (applyKernel (L.kernel a o) q.val),
    normalize_dist _ (apply_nonnegative _ (L.nonnegative a o) q.val q.property.1) ho⟩

/-- Aggregation preserves every terminal risk whose loss factors through the retained state. -/
theorem terminal_risk_eq (π : X → Z) (p : X → ℝ) (l : Z → ℝ) :
    (∑ x, p x * l (π x)) = ∑ z, push π p z * l z := by
  classical
  simp only [push, Finset.sum_mul, ite_mul, zero_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro x _
  simp

/-- The operational planning map is derived from, not substituted for, the joint-law theorem. -/
theorem instrumentMap (K : Law X A O) (L : Law Z A O) (π : X → Z)
    (H : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o)) (C : Contract Z A D) :
    ExactMap (fineModel K π C) (coarseModel L C) (aggregate π) where
  actions _ := rfl
  decisions _ := rfl
  cost _ _ := rfl
  loss p d := terminal_risk_eq π p.val (C.terminalLoss d)
  prob p a o := report_mass_eq π (H a o) p.val
  next p a o _ := by
    apply Subtype.ext
    change push π (normalize (applyKernel (K.kernel a o) p.val)) =
      normalize (applyKernel (L.kernel a o) (push π p.val))
    rw [push_normalize, H a o p.val]

/-- Core 5.4: equal finite-horizon values, all first-choice values, and all optimal first-choice sets. -/
theorem compressed_belief_planning (K : Law X A O) (L : Law Z A O) (π : X → Z)
    (H : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o)) (C : Contract Z A D)
    (h : Nat) (p : Belief X) :
    value (fineModel K π C) h p = value (coarseModel L C) h (aggregate π p) ∧
    (∀ c, firstValue (fineModel K π C) h p c =
      firstValue (coarseModel L C) h (aggregate π p) c) ∧
    (∀ c, OptimalFirst (fineModel K π C) h p c ↔
      OptimalFirst (coarseModel L C) h (aggregate π p) c) :=
  ⟨(instrumentMap K L π H C).value_eq h p,
    (instrumentMap K L π H C).firstValue_eq h p,
    (instrumentMap K L π H C).optimalFirst_iff h p⟩

/-- A finite optimal policy tree can be chosen from the coarse belief, uniformly over its entire fibre. -/
theorem common_optimal_inquiry (K : Law X A O) (L : Law Z A O) (π : X → Z)
    (H : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o)) (C : Contract Z A D)
    (h : Nat) (q : Belief Z) :
    ∃ P : Tree A O D, P.Bounded h ∧ Feasible (coarseModel L C) h q P ∧
      evaluate (coarseModel L C) P q = value (coarseModel L C) h q ∧
      ∀ p : Belief X, aggregate π p = q → Feasible (fineModel K π C) h p P ∧
        evaluate (fineModel K π C) P p = value (fineModel K π C) h p :=
  (instrumentMap K L π H C).common_minimizing_tree h q

/-- Even the coarse instrument is an output of the checked fibre criterion, not an assumed oracle. -/
theorem constructed_quotient_planning (K : Law X A O) (π : X → Z)
    (hπ : Function.Surjective π) (hc : FiberCriterion π K.kernel)
    (C : Contract Z A D) (h : Nat) (p : Belief X) :
    value (fineModel K π C) h p = value (coarseModel (coarseLaw π hπ K) C) h (aggregate π p) :=
  (instrumentMap K (coarseLaw π hπ K) π (coarseLaw_intertwines π hπ K hc) C).value_eq h p

end
end BeliefPlanning
end Komorebi.MachineTheory
