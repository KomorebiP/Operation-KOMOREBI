import MachineTheory.BinaryCertificate
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! # Source examples of checked closure and its required assumptions -/
namespace Komorebi.MachineTheory.BinaryExamples
open HardInquiry BinaryDiagnosis Finset

abbrev World := Bool × Bool × Bool
abbrev Query := Fin 3 ⊕ World

def eight : Model World Query Bool World Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun e x => match e with
    | .inl i => if i=0 then x.1 else if i=1 then x.2.1 else x.2.2
    | .inr y => decide (x=y)
  accept := fun x y => decide (x=y)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

theorem eight_scope : Scope eight := by
  constructor
  · intro e x; rfl
  · intro c x y hx hy
    have hx' : x = c := of_decide_eq_true hx
    have hy' : y = c := of_decide_eq_true hy
    exact hx'.trans hy'.symm
  · intro e; rfl
  · intro c V _; rfl

/-- The source supplies both coordinate queries and singleton queries to this same model. -/
def balanced : Tree Query Bool World 3 :=
  .inr (.inl 0, fun a => some (.inr (.inl 1, fun b =>
    some (.inr (.inl 2, fun c => some (a,b,c))))))

theorem balanced_checked : checkCandidate eight 3 univ balanced = true := by decide

theorem balanced_valid : eight.Valid 3 univ balanced :=
  ((checkCandidate_iff eight 3 univ balanced).mp balanced_checked).1

theorem balanced_profile : eight.profile 3 univ balanced = (fun _ => 4,15) := by decide

theorem balanced_structure : leaves 3 balanced = 8 ∧ depth 3 balanced = 3 ∧
    unary 3 balanced = 0 ∧ Model.records 3 balanced = 15 := by decide

/-- Every horizon at least three has this frontier, by the general theorem, not enumeration. -/
theorem eight_frontier_all (n : ℕ) : eight.solve (3+n) univ = {(fun _ => 4,15)} := by
  have h := closed_frontier_all_larger_horizons eight eight_scope 3 univ balanced balanced_checked n
  have he : lowerProfile (univ : Finset World).card = (fun _ => 4,15) := by decide
  simpa only [he] using h

theorem eight_no_two_queries : ¬ ∃ t : Tree Query Bool World 2, eight.Valid 2 univ t :=
  impossible_below_information_depth eight eight_scope 2 univ (by decide)

def stop (h : ℕ) (c : World) : Tree Query Bool World h :=
  match h with | 0 => c | _+1 => .inl c

def equalityStep (h : ℕ) (c : World) (tail : Tree Query Bool World h) :
    Tree Query Bool World (h+1) :=
  .inr (.inr c, fun o => some (if o then stop h c else tail))

def equality : Tree Query Bool World 7 :=
  equalityStep 6 (false,false,false)
    (equalityStep 5 (false,false,true)
    (equalityStep 4 (false,true,false)
    (equalityStep 3 (false,true,true)
    (equalityStep 2 (true,false,false)
    (equalityStep 1 (true,false,true)
    (equalityStep 0 (true,true,false) (true,true,true)))))))

theorem equality_valid : eight.Valid 7 univ equality := by decide

theorem equality_profile : eight.profile 7 univ equality = (fun _ => 8,15) := by decide

/-- Smallest storage alone does not close the work/storage frontier. -/
theorem equality_rejected : checkCandidate eight 7 univ equality = false := by decide

/-- The checker rejecting one candidate supplies no infeasibility conclusion. -/
theorem rejected_but_feasible : checkCandidate eight 7 univ equality = false ∧
    ∃ t : Tree Query Bool World 7, eight.Valid 7 univ t :=
  ⟨equality_rejected,⟨equality,equality_valid⟩⟩

/-- A matching tree shape with a wrong terminal action is not a certificate. -/
def wrongLeaves : Tree Query Bool World 3 :=
  .inr (.inl 0, fun _ => some (.inr (.inl 1, fun _ =>
    some (.inr (.inl 2, fun _ => some (false,false,false))))))

theorem wrong_shape_matches_cost : eight.profile 3 univ wrongLeaves = (fun _ => 4,15) := by decide

theorem wrong_leaves_rejected : checkCandidate eight 3 univ wrongLeaves = false ∧
    ¬ eight.Valid 3 univ wrongLeaves := by decide

/-- A three-case binary model makes a redundant query fit inside an optimal depth. -/
def three : Model (Fin 3) (Fin 3) Bool (Fin 3) Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun e x => decide (e=x)
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

theorem three_scope : Scope three := by
  constructor
  · intro e x; rfl
  · intro c x y hx hy
    exact (of_decide_eq_true hx).trans (of_decide_eq_true hy).symm
  · intro e; rfl
  · intro c V _; rfl

def cleanThree : Tree (Fin 3) Bool (Fin 3) 2 :=
  .inr (0,fun o => if o then some (.inl 0)
    else some (.inr (1,fun p => some (if p then (1 : Fin 3) else (2 : Fin 3)))))

def unaryThree : Tree (Fin 3) Bool (Fin 3) 2 :=
  .inr (0,fun o => if o then some (.inr (0,fun p => if p then some (0 : Fin 3) else none))
    else some (.inr (1,fun p => some (if p then (1 : Fin 3) else (2 : Fin 3)))))

theorem cleanThree_checked : checkCandidate three 2 univ cleanThree = true := by decide

theorem unaryThree_valid : three.Valid 2 univ unaryThree := by decide

theorem unaryThree_profile : three.profile 2 univ unaryThree = (fun _ => 3,6) := by decide

theorem unaryThree_extra_record : unary 2 unaryThree = 1 ∧ Model.records 2 unaryThree = 6 := by decide

/-- Optimal work alone does not certify minimum literal storage. -/
theorem unaryThree_rejected : checkCandidate three 2 univ unaryThree = false := by decide

theorem three_frontier_all (n : ℕ) : three.solve (2+n) univ = {(fun _ => 3,5)} := by
  have h := closed_frontier_all_larger_horizons three three_scope 2 univ cleanThree cleanThree_checked n
  have he : lowerProfile (univ : Finset (Fin 3)).card = (fun _ => 3,5) := by decide
  simpa only [he] using h

/-- State reset leaves singleton repair semantics intact, but removes original-state identification. -/
def reset : Model World Query Bool World Unit :=
  { eight with next := fun _ _ => (false,false,false), observe := fun _ _ => false }

def resetTree : Tree Query Bool World 1 :=
  .inr (.inl 0,fun o => if o then none else some (false,false,false))

theorem reset_valid_and_small : reset.Valid 1 univ resetTree ∧
    reset.profile 1 univ resetTree = (fun _ => 2,2) := by decide

theorem reset_not_scope : ¬ Scope reset := by
  intro s
  have he := s.immutable (.inl 0) (true,true,true)
  have : (false,false,false) ≠ (true,true,true) := by decide
  exact this he

/-- Changing only the success predicate admits a universal one-step repair. -/
def universalRepair : Model World Query Bool World Unit :=
  { eight with accept := fun _ _ => true }

theorem universal_repair_small : universalRepair.Valid 0 univ (false,false,false) ∧
    universalRepair.profile 0 univ (false,false,false) = (fun _ => 1,1) := by
  constructor
  · change universalRepair.Terminal univ (false,false,false)
    decide
  · rfl

theorem universal_not_scope : ¬ Scope universalRepair := by
  intro s
  have he := s.singleton (false,false,false) (false,false,false) (true,true,true) rfl rfl
  exact (by decide : (false,false,false) ≠ (true,true,true)) he

/-- The missing terminal unit changes the online statement, not the number of leaves. -/
def freeTerminal : Model World Query Bool World Unit :=
  { eight with terminalCost := fun _ _ _ => 0 }

theorem free_terminal_work : freeTerminal.Valid 3 univ balanced ∧
    freeTerminal.profile 3 univ balanced = (fun _ => 3,15) := by decide

/-- A nonbinary direct reveal violates binary counting if the alphabet is ignored. -/
def directFour : Model (Fin 4) Unit (Fin 4) (Fin 4) Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => x
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

def directFourTree : Tree Unit (Fin 4) (Fin 4) 1 := .inr ((),fun o => some o)

theorem direct_four_small : directFour.Valid 1 univ directFourTree ∧
    directFour.profile 1 univ directFourTree = (fun _ => 2,5) := by decide

/-- Immutability and binary reports alone do not supply informative queries. -/
def silent : Model Bool Unit Bool Bool Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ _ => false
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

theorem silent_scope : Scope silent := by
  constructor
  · intro e x; rfl
  · intro c x y hx hy
    exact (of_decide_eq_true hx).trans (of_decide_eq_true hy).symm
  · intro e; rfl
  · intro c V _; rfl

theorem silent_update : silent.update univ () false = univ := by decide

/-- No finite horizon succeeds, despite fitting the numerical lower bounds at larger horizons. -/
theorem silent_impossible (h : ℕ) : ¬ ∃ t : Tree Unit Bool Bool h, silent.Valid h univ t := by
  induction h with
  | zero =>
    rintro ⟨t,ht⟩
    have hc := terminal_card_one silent silent_scope univ t ht
    have hn : (univ : Finset Bool).card = 2 := by decide
    omega
  | succ h ih =>
    rintro ⟨t,ht⟩
    cases t with
    | inl c =>
      have hc := terminal_card_one silent silent_scope univ c ht
      have hn : (univ : Finset Bool).card = 2 := by decide
      omega
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      cases e
      obtain ⟨u,_,hu⟩ := (silent.valid_child ht false).mp (by rw [silent_update]; exact univ_nonempty)
      rw [silent_update] at hu
      exact ih ⟨u,hu⟩

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
/-- The full finite guard is computed on the eight-case source model. -/
theorem eight_admission_checked : admissionCheck eight 3 univ balanced = true := by decide

theorem reset_guard_rejects : checkScope reset = false := by decide

theorem universal_guard_rejects : checkScope universalRepair = false := by decide

theorem free_terminal_guard_rejects : checkScope freeTerminal = false := by decide

/-- The n=1 boundary includes the final unit-cost repair and one stored record. -/
theorem singleton_checked : checkCandidate eight 0 {(false,false,false)} (false,false,false) = true := by decide

theorem empty_support_impossible (h : ℕ) :
    ¬ ∃ t : Tree Query Bool World h, eight.Valid h ∅ t := by
  rintro ⟨t,ht⟩
  exact (eight.valid_nonempty ht).ne_empty rfl

end Komorebi.MachineTheory.BinaryExamples
