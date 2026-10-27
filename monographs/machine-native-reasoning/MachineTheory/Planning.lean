import MachineTheory.Feedback
import Mathlib.Data.Finset.Max

/-!
Reviewed Core 0.2, Theorem 5.4: finite-horizon inquiry on observable information states.
Menus are finite and depend on the retained state; terminal menus are nonempty.
A successor is requested only with a proof that its report has positive probability.
An observation tree chooses actions using reports, never the hidden physical state.
-/
namespace Komorebi.MachineTheory
namespace Planning
open scoped BigOperators
noncomputable section

/-- Finite minimum, with nonemptiness retained as a premise rather than a default value. -/
def finiteMin {I : Type*} (s : Finset I) (hs : s.Nonempty) (f : I → ℝ) : ℝ := by
  classical
  exact (s.image f).min' (hs.image f)

theorem finiteMin_le {I : Type*} (s : Finset I) (hs : s.Nonempty) (f : I → ℝ)
    (i : I) (hi : i ∈ s) : finiteMin s hs f ≤ f i := by
  classical
  exact Finset.min'_le _ _ (Finset.mem_image.mpr ⟨i, hi, rfl⟩)

theorem finiteMin_attained {I : Type*} (s : Finset I) (hs : s.Nonempty) (f : I → ℝ) :
    ∃ i ∈ s, f i = finiteMin s hs f := by
  classical
  exact Finset.mem_image.mp (Finset.min'_mem _ (hs.image f))

theorem le_finiteMin {I : Type*} (s : Finset I) (hs : s.Nonempty) (f : I → ℝ)
    (v : ℝ) (hv : ∀ i ∈ s, v ≤ f i) : v ≤ finiteMin s hs f := by
  obtain ⟨i, hi, he⟩ := finiteMin_attained s hs f
  rw [← he]
  exact hv i hi

theorem finiteMin_congr {I : Type*} (s t : Finset I) (hs : s.Nonempty) (ht : t.Nonempty)
    (f g : I → ℝ) (hst : s = t) (hfg : ∀ i ∈ s, f i = g i) :
    finiteMin s hs f = finiteMin t ht g := by
  subst t
  apply le_antisymm
  · apply le_finiteMin
    intro i hi
    rw [← hfg i hi]
    exact finiteMin_le s hs f i hi
  · apply le_finiteMin
    intro i hi
    rw [hfg i hi]
    exact finiteMin_le s ht g i hi

/-- S is the information available to planning, not an unobserved physical state. -/
structure Model (S A O D : Type*) [Fintype O] where
  actions : S → Finset A
  decisions : S → Finset D
  decisions_nonempty : ∀ s, (decisions s).Nonempty
  cost : S → A → ℝ
  cost_nonnegative : ∀ s a, 0 ≤ cost s a
  loss : S → D → ℝ
  prob : S → A → O → ℝ
  nonnegative : ∀ s a o, 0 ≤ prob s a o
  normalized : ∀ s a, ∑ o, prob s a o = 1
  next : (s : S) → (a : A) → (o : O) → 0 < prob s a o → S

/-- Syntax of finite report-dependent plans. No hidden-state argument is available to a node. -/
inductive Tree (A O D : Type*) where
  | stop : D → Tree A O D
  | experiment : A → (O → Tree A O D) → Tree A O D

/-- A syntactic height bound also covers dormant, impossible-report branches. -/
def Tree.Bounded {A O D : Type*} : Nat → Tree A O D → Prop
  | _, .stop _ => True
  | 0, .experiment _ _ => False
  | h + 1, .experiment _ k => ∀ o, Tree.Bounded h (k o)

variable {S A O D : Type*} [Fintype O]

/-- Expected charge plus terminal loss. A zero-mass report contributes zero and has no successor. -/
def evaluate (M : Model S A O D) : Tree A O D → S → ℝ
  | .stop d, s => M.loss s d
  | .experiment a k, s => M.cost s a + ∑ o,
      if ho : 0 < M.prob s a o then
        M.prob s a o * evaluate M (k o) (M.next s a o ho) else 0

/-- Admissibility is imposed at every reachable information state, including terminal choices. -/
def Feasible (M : Model S A O D) : Nat → S → Tree A O D → Prop
  | _, s, .stop d => d ∈ M.decisions s
  | 0, _, .experiment _ _ => False
  | h + 1, s, .experiment a k => a ∈ M.actions s ∧
      ∀ o (ho : 0 < M.prob s a o), Feasible M h (M.next s a o ho) (k o)

/-- The same first-choice type names both stopping and experiments. -/
def menu (M : Model S A O D) (s : S) : Finset (D ⊕ A) := by
  classical
  exact (M.decisions s).image Sum.inl ∪ (M.actions s).image Sum.inr

theorem menu_nonempty (M : Model S A O D) (s : S) : (menu M s).Nonempty := by
  classical
  obtain ⟨d, hd⟩ := M.decisions_nonempty s
  exact ⟨Sum.inl d, by simp [menu, hd]⟩

@[simp] theorem stop_mem_menu (M : Model S A O D) (s : S) (d : D) :
    Sum.inl d ∈ menu M s ↔ d ∈ M.decisions s := by
  classical
  simp [menu]

@[simp] theorem experiment_mem_menu (M : Model S A O D) (s : S) (a : A) :
    Sum.inr a ∈ menu M s ↔ a ∈ M.actions s := by
  classical
  simp [menu]

/-- One backup of a supplied continuation function. -/
def backup (M : Model S A O D) (V : S → ℝ) (s : S) (a : A) : ℝ :=
  M.cost s a + ∑ o, if ho : 0 < M.prob s a o then
    M.prob s a o * V (M.next s a o ho) else 0

/-- Finite Bellman recursion: no experiment is available at horizon zero. -/
def value (M : Model S A O D) : Nat → S → ℝ
  | 0, s => finiteMin (M.decisions s) (M.decisions_nonempty s) (M.loss s)
  | h + 1, s => finiteMin (menu M s) (menu_nonempty M s)
      (fun c => match c with
        | Sum.inl d => M.loss s d
        | Sum.inr a => backup M (value M h) s a)

/-- Stop and experiment values at a positive horizon, with the same continuation value. -/
def firstValue (M : Model S A O D) (h : Nat) (s : S) : D ⊕ A → ℝ
  | Sum.inl d => M.loss s d
  | Sum.inr a => backup M (value M h) s a

theorem value_le_stop (M : Model S A O D) (h : Nat) (s : S) (d : D)
    (hd : d ∈ M.decisions s) : value M h s ≤ M.loss s d := by
  cases h with
  | zero => exact finiteMin_le _ _ _ d hd
  | succ h => exact finiteMin_le _ _ _ (Sum.inl d) ((stop_mem_menu M s d).mpr hd)

theorem value_le_experiment (M : Model S A O D) (h : Nat) (s : S) (a : A)
    (ha : a ∈ M.actions s) : value M (h + 1) s ≤ backup M (value M h) s a :=
  finiteMin_le _ _ _ (Sum.inr a) ((experiment_mem_menu M s a).mpr ha)

/-- Bellman's number is a lower bound on the cost of every admissible report-dependent tree. -/
theorem value_le_tree (M : Model S A O D) (h : Nat) (s : S) (P : Tree A O D)
    (hP : Feasible M h s P) : value M h s ≤ evaluate M P s := by
  induction h generalizing s P with
  | zero =>
      cases P with
      | stop d => exact value_le_stop M 0 s d hP
      | experiment a k => exact False.elim hP
  | succ h ih =>
      cases P with
      | stop d => exact value_le_stop M (h + 1) s d hP
      | experiment a k =>
          apply le_trans (value_le_experiment M h s a hP.1)
          simp only [backup, evaluate]
          apply add_le_add le_rfl
          apply Finset.sum_le_sum
          intro o _
          split_ifs with ho
          · exact mul_le_mul_of_nonneg_left (ih (M.next s a o ho) (k o) (hP.2 o ho))
              (M.nonnegative s a o)
          · exact le_rfl

/-- A minimizing tree exists; the proof builds each child from the same actual first choice. -/
theorem minimizing_tree_exists (M : Model S A O D) (h : Nat) (s : S) :
    ∃ P : Tree A O D, P.Bounded h ∧ Feasible M h s P ∧ evaluate M P s = value M h s := by
  classical
  induction h generalizing s with
  | zero =>
      obtain ⟨d, hd, he⟩ := finiteMin_attained (M.decisions s) (M.decisions_nonempty s) (M.loss s)
      exact ⟨.stop d, trivial, hd, he⟩
  | succ h ih =>
      obtain ⟨c, hc, he⟩ := finiteMin_attained (menu M s) (menu_nonempty M s) (firstValue M h s)
      cases c with
      | inl d =>
          exact ⟨.stop d, trivial, (stop_mem_menu M s d).mp hc, he⟩
      | inr a =>
          let child : O → Tree A O D := fun o =>
            if ho : 0 < M.prob s a o then (ih (M.next s a o ho)).choose
            else .stop (M.decisions_nonempty s).choose
          refine ⟨.experiment a child, ?_, ?_, ?_⟩
          · intro o
            dsimp [child]
            split_ifs with ho
            · exact (ih (M.next s a o ho)).choose_spec.1
            · simp only [Tree.Bounded]
          · refine ⟨(experiment_mem_menu M s a).mp hc, ?_⟩
            intro o ho
            dsimp [child]
            rw [dite_eq_left ho]
            exact (ih (M.next s a o ho)).choose_spec.2.1
          · change M.cost s a + _ = value M (h+1) s
            calc
              M.cost s a + _ = backup M (value M h) s a := by
                unfold backup
                congr 1
                apply Finset.sum_congr rfl
                intro o _
                split_ifs with ho
                · congr 1
                  dsimp [child]
                  rw [dite_eq_left ho]
                  exact (ih (M.next s a o ho)).choose_spec.2.2
                · rfl
              _ = value M (h+1) s := he

/-- The Bellman value is characterized by actual finite trees, not defined as an unproved infimum. -/
theorem optimal_value_characterization (M : Model S A O D) (h : Nat) (s : S) :
    (∃ P, P.Bounded h ∧ Feasible M h s P ∧ evaluate M P s = value M h s) ∧
      (∀ P, Feasible M h s P → value M h s ≤ evaluate M P s) :=
  ⟨minimizing_tree_exists M h s, fun P hp => value_le_tree M h s P hp⟩

/-- Immediate terminal optimality is meaningful at every horizon, including zero. -/
def OptimalStop (M : Model S A O D) (h : Nat) (s : S) (d : D) : Prop :=
  d ∈ M.decisions s ∧ M.loss s d = value M h s

/-- An optimal first choice, including a specified terminal decision. -/
def OptimalFirst (M : Model S A O D) (h : Nat) (s : S) (c : D ⊕ A) : Prop :=
  c ∈ menu M s ∧ firstValue M h s c = value M (h + 1) s

theorem optimal_first_exists (M : Model S A O D) (h : Nat) (s : S) :
    ∃ c, OptimalFirst M h s c :=
  finiteMin_attained (menu M s) (menu_nonempty M s) (firstValue M h s)

/-- A finite randomized mixture of valid trees cannot beat their common Bellman lower bound. -/
theorem randomized_tree_lower_bound (M : Model S A O D) (h : Nat) (s : S)
    {I : Type*} [Fintype I] (w : I → ℝ) (hw : ∀ i, 0 ≤ w i) (hsum : ∑ i, w i = 1)
    (P : I → Tree A O D) (hP : ∀ i, Feasible M h s (P i)) :
    value M h s ≤ ∑ i, w i * evaluate M (P i) s := by
  calc
    value M h s = (∑ i, w i) * value M h s := by rw [hsum, one_mul]
    _ = ∑ i, w i * value M h s := by rw [Finset.sum_mul]
    _ ≤ ∑ i, w i * evaluate M (P i) s :=
      Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (value_le_tree M h s (P i) (hP i)) (hw i))

/-- Returning a minimizing tree is noncomputable choice over a finite mathematical search.
It is not a claim of an efficient extracted solver. -/
def optimalTree (M : Model S A O D) (h : Nat) (s : S) : Tree A O D :=
  (minimizing_tree_exists M h s).choose

theorem optimalTree_spec (M : Model S A O D) (h : Nat) (s : S) :
    (optimalTree M h s).Bounded h ∧ Feasible M h s (optimalTree M h s) ∧
      evaluate M (optimalTree M h s) s = value M h s :=
  (minimizing_tree_exists M h s).choose_spec

end
end Planning
end Komorebi.MachineTheory
