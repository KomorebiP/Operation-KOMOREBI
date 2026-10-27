import MachineTheory.PrefixAdmission
import MachineTheory.BinaryExamples
import MachineTheory.SynthesisExamples

/-! # Concrete compiler instances, sharp boundaries and separately metered work -/
namespace Komorebi.MachineTheory.PrefixExamples
open OrderedCompiler BinaryDiagnosis HardInquiry Finset

/-- A fifth zero closes a capacity-four child; its unread suffix is not inspected. -/
theorem first_excess_stops :
    PrefixScan.stream id 4 0 0 [false,false,false,false,false,true,true,true] = ⟨none,5,6⟩ ∧
    PrefixScan.full id 4 0 0 [false,false,false,false,false,true,true,true] = ⟨none,8,1⟩ := by decide

theorem capacity_equality_survives :
    (PrefixScan.stream id 4 0 0 [false,false,false,false,true,true,true,true]).branches =
      some ([false,false,false,false],[true,true,true,true]) ∧
    (PrefixScan.stream id 4 0 0 [false,false,false,false,true,true,true,true]).reads=8 := by decide

/-- Total headroom, not just the two partial counts, is needed for the completion iff. -/
theorem missing_total_capacity : max (0:ℕ) 0≤4 ∧ ¬ PrefixScan.Completable 9 4 0 0 := by
  constructor
  · decide
  · rintro ⟨u,v,hs,hu,hv⟩; omega

/-- The result acquired in Block09 separately denotes the universally sound predicate. -/
theorem acquired_rule_meaning (a b C : ℕ) :
    SynthesisExamples.evaluate .maxGtC (a,b,C)=true ↔ C<max a b := by
  simp only [SynthesisExamples.evaluate,decide_eq_true_eq]

theorem acquired_rule_completion (m C a b : ℕ) (hr : a+b≤m) (hc : m≤2*C) :
    SynthesisExamples.evaluate .maxGtC (a,b,C)=false ↔ PrefixScan.Completable m C a b := by
  rw [PrefixScan.completion_iff m C a b hr hc]
  simp [SynthesisExamples.evaluate]

/-- A training-perfect alternative would reject a legal larger-capacity prefix. -/
theorem learned_fit_can_erase_completion :
    Synthesis.Correct SynthesisExamples.task .capped ∧
    SynthesisExamples.evaluate .capped (0,5,8)=true ∧
    PrefixScan.Completable 8 8 0 5 := by
  refine ⟨SynthesisExamples.finite_fit_not_universal.1,by decide,?_⟩
  exact (PrefixScan.completion_iff 8 8 0 5 (by decide) (by decide)).mpr (by decide)

/-- The artifact acquired earlier receives a separate certificate against actual controller semantics. -/
theorem acquired_rule_excludes_actual_root {X E C : Type} [DecidableEq X]
    (M : Model X E Bool C Unit) (s : Scope M) (h : ℕ) (V P : Finset X) (hPV : P⊆V) (e : E)
    (hr : SynthesisExamples.evaluate .maxGtC
      ((P.filter (fun x => M.observe e x=false)).card,
       (P.filter (fun x => M.observe e x=true)).card,2^h)=true) :
    ¬ ∃ k : Bool → Option (Tree E Bool C h),M.Valid (h+1) V (.inr (e,k)) := by
  have ht := (acquired_rule_meaning _ _ _).mp hr
  rcases lt_max_iff.mp ht with h0 | h1
  · exact prefix_exclusion M s h V P hPV e false h0
  · exact prefix_exclusion M s h V P hPV e true h1

abbrev World := BinaryExamples.World
abbrev Query := BinaryExamples.Query

def rows : List World :=
  [(false,false,false),(false,false,true),(false,true,false),(false,true,true),
   (true,false,false),(true,false,true),(true,true,false),(true,true,true)]

def queries : List Query := rows.map Sum.inr ++ [Sum.inl 0,Sum.inl 1,Sum.inl 2]

theorem rows_exact : rows.toFinset=univ ∧ rows.Nodup := by decide

theorem complete_repairs : ∀ c : World,c∈rows := by decide

theorem complete_queries : ∀ e : Query,e∈queries := by
  intro e
  rcases e with i | x
  · exact List.mem_append_right _ (by fin_cases i <;> simp)
  · exact List.mem_append_left _ (List.mem_map.mpr ⟨x,complete_repairs x,rfl⟩)

def fullEight := search fullScanner BinaryExamples.eight queries rows 3 rows
def streamEight := search streamScanner BinaryExamples.eight queries rows 3 rows

theorem eight_measured_reads :
    (fullEight.reads,fullEight.checks,streamEight.reads,streamEight.checks) = (184,45,153,198) := by decide

theorem eight_returned_profile :
    fullEight.answer.map (fun t => ((BinaryExamples.eight.profile 3 univ t).1 (),
      (BinaryExamples.eight.profile 3 univ t).2))=some (4,15) := by decide

/-- Equal event prices do not turn the decrease in reads into a total saving. -/
theorem predicate_work_can_cost_more :
    fullEight.reads+fullEight.checks < streamEight.reads+streamEight.checks := by decide

theorem weighted_event_saving (w : ℕ) :
    w*streamEight.reads+streamEight.checks < w*fullEight.reads+fullEight.checks ↔ 153<31*w := by
  have hh := eight_measured_reads
  have h0 : fullEight.reads=184 := by decide
  have h1 : fullEight.checks=45 := by decide
  have h2 : streamEight.reads=153 := by decide
  have h3 : streamEight.checks=198 := by decide
  rw [h0,h1,h2,h3]
  omega

theorem eight_same_literal_answer : streamEight.answer=fullEight.answer :=
  same_returned_tree BinaryExamples.eight queries rows 3 rows

/-- Not just a matching outcome: the emitted tree is checked under the original semantics. -/
theorem eight_returned_valid : ∀ t, streamEight.answer=some t → BinaryExamples.eight.Valid 3 univ t := by
  intro t ht
  have h := (streaming_sound_complete BinaryExamples.eight BinaryExamples.eight_scope
    queries rows complete_queries complete_repairs 3 rows rows_exact.2).1 t ht
  simpa only [rows_exact.1] using h

theorem eight_has_answer : ∃ t, streamEight.answer=some t := by
  have h := full_search_complete BinaryExamples.eight BinaryExamples.eight_scope queries rows
    complete_queries complete_repairs 3 rows rows_exact.2 BinaryExamples.balanced
    (by simpa only [rows_exact.1] using BinaryExamples.balanced_valid)
  obtain ⟨t,ht⟩ := h
  refine ⟨t,?_⟩
  change (search streamScanner _ _ _ _ _).answer=some t
  rw [same_returned_tree]
  exact ht

/-- In an equality-only model the lower-depth capacity test need not be attainable. -/
theorem three_short_horizon_fails :
    (search streamScanner BinaryExamples.three [0,1,2] [0,1,2] 1 [0,1,2]).answer=none := by decide

/-- Capacity survival is not evidence of an informative remaining query. -/
theorem silent_capacity_is_not_solution :
    (streamScanner (BinaryExamples.silent.observe ()) 2 [false,true]).branches ≠ none ∧
    (search streamScanner BinaryExamples.silent [()] [false,true] 2 [false,true]).answer=none := by decide

/-- Duplicated rows falsely enlarge counts, so nodup is an explicit completeness premise. -/
def boolModel : Model Bool Unit Bool Bool Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => x
  accept := fun x c => decide (x=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

def boolTree : Tree Unit Bool Bool 2 := .inr ((),fun b => some (.inl b))

theorem duplicate_rows_boundary :
    boolModel.Valid 2 ([false,false,false,true].toFinset) boolTree ∧
    (streamScanner (boolModel.observe ()) 2 [false,false,false,true]).branches=none := by decide

/-- A reset changes what must be repaired; cardinality pruning then loses a valid tree. -/
theorem reset_boundary :
    BinaryExamples.reset.Valid 1 univ BinaryExamples.resetTree ∧
    (search streamScanner BinaryExamples.reset queries rows 1 rows).answer=none ∧
    checkScope BinaryExamples.reset=false := by
  exact ⟨BinaryExamples.reset_valid_and_small.1,by decide,BinaryExamples.reset_guard_rejects⟩

/-- One repair per first-bit class violates the singleton leaf premise. -/
def classRepair : Model World Unit Bool Bool Unit where
  permitted := fun _ _ => true
  next := fun _ x => x
  observe := fun _ x => x.1
  accept := fun x c => decide (x.1=c)
  stepCost := fun _ _ => 1
  terminalCost := fun _ _ _ => 1

def classTree : Tree Unit Bool Bool 1 := .inr ((),fun b => some b)

theorem non_singleton_boundary : classRepair.Valid 1 univ classTree ∧
    (search streamScanner classRepair [()] [false,true] 1 rows).answer=none ∧
    checkScope classRepair=false := by decide

/-- Changing the fixed query order is outside literal-tree preservation. -/
def rootLabel (t : Option (Tree (Fin 3) Bool (Fin 3) 2)) : Option (Fin 3) :=
  t.bind (fun t => match t with | .inl _ => none | .inr (e,_) => some e)

theorem query_order_changes_tree :
    (search streamScanner BinaryExamples.three [0,1,2] [0,1,2] 2 [0,1,2]).answer ≠
    (search streamScanner BinaryExamples.three [1,0,2] [0,1,2] 2 [0,1,2]).answer := by
  intro he
  have h0 : rootLabel (search streamScanner BinaryExamples.three [0,1,2] [0,1,2] 2 [0,1,2]).answer = some 0 := by decide
  have h1 : rootLabel (search streamScanner BinaryExamples.three [1,0,2] [0,1,2] 2 [0,1,2]).answer = some 1 := by decide
  have hh := congrArg rootLabel he
  rw [h0,h1] at hh
  have hbad : (0 : Fin 3)=1 := Option.some.inj hh
  exact (by decide : (0:Fin 3)≠1) hbad

/-- An incomplete menu cannot certify impossibility in the full model. -/
theorem missing_query_boundary :
    (search streamScanner boolModel [] [false,true] 1 [false,true]).answer=none ∧
    ∃ t : Tree Unit Bool Bool 1, boolModel.Valid 1 univ t := by
  refine ⟨by decide,⟨(show Tree Unit Bool Bool 1 from .inr ((),fun b => some b)),by decide⟩⟩

/-- The theorem never permits a terminal whose installed permission was removed. -/
def forbidden : Model Bool Unit Bool Bool Unit :=
  {boolModel with permitted := fun _ _ => false}

theorem permission_boundary :
    (search streamScanner forbidden [()] [false,true] 1 [false,true]).answer=none ∧
    (search streamScanner boolModel [()] [false,true] 1 [false,true]).answer ≠ none := by decide


/-- Checked completion is available for the actual source-shaped finite example. -/
theorem eight_guarded_completion :
    ∃ r, checkedSearch BinaryExamples.eight queries rows 3 rows=some r ∧
      r.answer=fullEight.answer := by
  classical
  have hg : guard BinaryExamples.eight queries rows rows=true :=
    (guard_iff _ _ _ _).mpr ⟨BinaryExamples.eight_scope,rows_exact.2,complete_queries,complete_repairs⟩
  refine ⟨streamEight,?_,eight_same_literal_answer⟩
  simp only [checkedSearch,hg,ite_true]
  rfl

/-- Rejection of the optimization's scope is not a proof of an unsolvable task. -/
theorem scope_rejection_not_infeasible :
    checkedSearch BinaryExamples.reset queries rows 1 rows=none ∧
    BinaryExamples.reset.Valid 1 univ BinaryExamples.resetTree := by
  classical
  constructor
  · simp only [checkedSearch,OrderedCompiler.guard,BinaryExamples.reset_guard_rejects,Bool.false_and,
      Bool.false_eq_true,ite_false]
  · exact BinaryExamples.reset_valid_and_small.1

end Komorebi.MachineTheory.PrefixExamples

