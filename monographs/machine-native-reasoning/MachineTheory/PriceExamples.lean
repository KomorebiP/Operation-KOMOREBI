import MachineTheory.WorkloadPricing
import MachineTheory.PrefixExamples

/-! # Price-sensitive value of the actual ordered compiler

False names a report-table read and true names a capacity test. The two event
counters below are projections of Block 10's actual search results. No setup,
allocation, semantic check, peak-memory, or host-time cost is inferred from them.
-/
namespace Komorebi.MachineTheory.PriceExamples
open ResourcePrices Finset
open scoped BigOperators
noncomputable section

def fullCounts (event : Bool) : ℕ :=
  if event then PrefixExamples.fullEight.checks else PrefixExamples.fullEight.reads

def streamCounts (event : Bool) : ℕ :=
  if event then PrefixExamples.streamEight.checks else PrefixExamples.streamEight.reads

def perUse (event : Bool) : ℝ := (fullCounts event : ℝ) - streamCounts event

def prices (readPrice testPrice : ℝ) : Bool → ℝ := fun b => if b then testPrice else readPrice

/-- Literal projections of the inherited full/streaming search counter theorem. -/
theorem counter_binding :
    fullCounts false=184 ∧ fullCounts true=45 ∧ streamCounts false=153 ∧ streamCounts true=198 := by
  have h := PrefixExamples.eight_measured_reads
  exact ⟨congrArg (fun x => x.1) h,congrArg (fun x => x.2.1) h,
    congrArg (fun x => x.2.2.1) h,congrArg (fun x => x.2.2.2) h⟩

theorem actual_delta : perUse = prices 31 (-153) := by
  funext b
  rcases counter_binding with ⟨h0,h1,h2,h3⟩
  cases b <;> norm_num [perUse,prices,h0,h1,h2,h3]

/-- The comparison is derived from the actual signed difference, not inserted as data. -/
theorem priced_scan (r t : ℝ) : saving perUse (prices r t) = 31*r-153*t := by
  rw [actual_delta]
  simp [saving,prices]
  ring

theorem same_valid_controller :
    PrefixExamples.streamEight.answer=PrefixExamples.fullEight.answer ∧
    ∀ t, PrefixExamples.streamEight.answer=some t → BinaryExamples.eight.Valid 3 univ t :=
  ⟨PrefixExamples.eight_same_literal_answer,PrefixExamples.eight_returned_valid⟩

theorem source_price_reversal : saving perUse (prices 5 1)=2 ∧ saving perUse (prices 1 1)= -122 := by
  constructor <;> rw [priced_scan] <;> norm_num

theorem not_universally_beneficial :
    ¬ ∀ w : Bool → ℝ, (∀ i,0 ≤ w i) → 0 ≤ saving perUse w := by
  rw [all_nonnegative_prices_iff,actual_delta]
  intro h
  have ht := h true
  norm_num [prices] at ht

/-- Natural subtraction destroys the negative coordinate before pricing. -/
theorem natural_subtraction_loses_cost :
    fullCounts true-streamCounts true=0 ∧ (fullCounts true : ℝ)-streamCounts true= -153 := by
  rcases counter_binding with ⟨_,h1,_,h3⟩
  rw [h1,h3]
  norm_num

def expensivePrices : Finset (Bool → ℝ) := by
  classical
  exact {prices 5 1,prices 8 1}

theorem expensive_nonempty : expensivePrices.Nonempty := by
  classical
  simp [expensivePrices]

theorem listed_minimum : Planning.finiteMin expensivePrices expensive_nonempty (saving perUse)=2 := by
  classical
  apply le_antisymm
  · have h := Planning.finiteMin_le expensivePrices expensive_nonempty (saving perUse)
      (prices 5 1) (by simp [expensivePrices])
    rw [priced_scan] at h
    norm_num at h
    exact h
  · apply Planning.le_finiteMin
    intro w hw
    simp only [expensivePrices,mem_insert,mem_singleton] at hw
    rcases hw with rfl | rfl <;> rw [priced_scan] <;> norm_num

/-- Every convex-mixture price in this declared family saves at least two units. -/
theorem expensive_hull_minimum :
    IsLeast ((saving perUse) '' convexHull ℝ (expensivePrices : Set (Bool → ℝ))) 2 := by
  obtain ⟨_,_,_,h⟩ := finite_price_minimum perUse expensivePrices expensive_nonempty
  rwa [listed_minimum] at h

/-- Positivity on one price family says nothing about a price outside it. -/
theorem equal_price_outside_family :
    prices 1 1 ∉ convexHull ℝ (expensivePrices : Set (Bool → ℝ)) := by
  intro h
  have hh := expensive_hull_minimum.2 ⟨prices 1 1,h,rfl⟩
  rw [priced_scan] at hh
  norm_num at hh

/-- A hypothetical extra preparation account: 200 capacity-test units and no reads. -/
def extraPreparation : Bool → ℝ := prices 0 200

def paid (N : ℕ) : Bool → ℝ := repeated extraPreparation perUse N

theorem preparation_price (r t : ℝ) : saving extraPreparation (prices r t)=200*t := by
  simp [saving,extraPreparation,prices]
  ring

/-- Natural event totals of the same repeated compiler comparison, with paid setup. -/
def actualWorkload (N : ℕ) : Ledger Unit Bool where
  setup := fun i => if i then 200 else 0
  uses := fun _ => N
  old := fun _ => fullCounts
  revised := fun _ => streamCounts

theorem actual_workload_delta (N : ℕ) : (actualWorkload N).delta=paid N := by
  funext i
  simp [Ledger.delta,net,actualWorkload,paid,repeated,extraPreparation,prices,perUse]

theorem actual_workload_totals (N : ℕ) :
    (actualWorkload N).oldTotal false=N*184 ∧
    (actualWorkload N).newTotal false=N*153 ∧
    (actualWorkload N).oldTotal true=N*45 ∧
    (actualWorkload N).newTotal true=200+N*198 := by
  rcases counter_binding with ⟨h0,h1,h2,h3⟩
  simp [Ledger.oldTotal,Ledger.newTotal,actualWorkload,h0,h1,h2,h3]

/-- Price variation between uses cannot be collapsed into one unpriced cancellation. -/
theorem time_varying_prices_boundary :
    (1 : ℝ)+(-1)=0 ∧ (1 : ℝ)*1+2*(-1) < 0 := by norm_num

theorem paid_value (N : ℕ) (r t : ℝ) :
    saving (paid N) (prices r t) = (N : ℝ)*(31*r-153*t)-200*t := by
  exact (saving_repeated extraPreparation perUse (prices r t) N).trans
    (by rw [priced_scan,preparation_price])

theorem paid_at_five (N : ℕ) : saving (paid N) (prices 5 1)=2*(N : ℝ)-200 := by
  rw [paid_value]
  ring

theorem paid_strict_threshold (N : ℕ) : 0 < saving (paid N) (prices 5 1) ↔ 100 < N := by
  rw [paid_at_five]
  constructor
  · intro h
    have h' : (100 : ℝ) < N := by linarith
    exact_mod_cast h'
  · intro h
    have h' : (100 : ℝ) < N := by exact_mod_cast h
    linarith

/-- The full declared convex family, not only its endpoints, has this attained minimum. -/
theorem paid_hull_minimum (N : ℕ) :
    IsLeast ((saving (paid N)) '' convexHull ℝ (expensivePrices : Set (Bool → ℝ)))
      (2*(N : ℝ)-200) := by
  classical
  constructor
  · refine ⟨prices 5 1,subset_convexHull ℝ (expensivePrices : Set (Bool → ℝ)) ?_,paid_at_five N⟩
    simp [expensivePrices]
  · rintro x ⟨w,hw,rfl⟩
    apply (hull_lower_bound_iff (paid N) (expensivePrices : Set (Bool → ℝ)) _).mpr ?_ w hw
    intro z hz
    simp only [Finset.mem_coe,expensivePrices,mem_insert,mem_singleton] at hz
    rcases hz with rfl | rfl
    · rw [paid_at_five]
    · rw [paid_value]
      have hn : (0 : ℝ) ≤ N := Nat.cast_nonneg N
      nlinarith

/-- The uniform strict threshold follows because the lower price is actually attained. -/
theorem robust_reuse_threshold (N : ℕ) :
    (∀ w ∈ convexHull ℝ (expensivePrices : Set (Bool → ℝ)),0 < saving (paid N) w) ↔ 100 < N := by
  classical
  constructor
  · intro h
    apply (paid_strict_threshold N).mp
    exact h (prices 5 1) (subset_convexHull ℝ _ (by simp [expensivePrices]))
  · intro h w hw
    have hp : 0 < 2*(N : ℝ)-200 := by
      rw [← paid_at_five]
      exact (paid_strict_threshold N).mpr h
    exact lt_of_lt_of_le hp ((paid_hull_minimum N).2 ⟨w,hw,rfl⟩)

theorem setup_and_boundary_values :
    saving (paid 1) (prices 5 1)= -198 ∧ saving (paid 100) (prices 5 1)=0 ∧
    saving (paid 101) (prices 5 1)=2 := by
  constructor
  · rw [paid_at_five]; norm_num
  · constructor <;> rw [paid_at_five] <;> norm_num

/-- At equal prices every repeat loses work, and preparation makes the result worse. -/
theorem equal_price_never_pays (N : ℕ) : saving (paid N) (prices 1 1) < 0 := by
  rw [paid_value]
  have hn : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  nlinarith

/-- Changing the workload changes the sign even with the price fixed. -/
theorem workload_change_boundary :
    saving (net (fun _ : Unit => 0) (fun _ : Bool => 1)
      (fun (j : Bool) (_ : Unit) => if j then (-2 : ℝ) else 1)) (fun _ => 1)= -1 := by
  norm_num [saving,net]

/-- A negative conversion price can reverse a componentwise positive event difference. -/
theorem negative_price_boundary : saving (fun _ : Unit => (1 : ℝ)) (fun _ => -1) < 0 := by
  norm_num [saving]

/-- An unnormalized or signed combination is not a convex-price certificate. -/
theorem extrapolation_boundary :
    (1 : ℝ) ≤ 1 ∧ (1 : ℝ) ≤ 2 ∧ 2*(1 : ℝ)+(-1)*2 < 1 := by
  norm_num

/-- Re-expressing one event as ten subunits without adjusting its price changes the value. -/
theorem unmatched_units_boundary :
    saving (fun _ : Unit => (10 : ℝ)) (fun _ => 1) ≠
      saving (fun _ : Unit => (1 : ℝ)) (fun _ => 1) := by
  norm_num [saving]

/-- The source book's supplied weighted-search ledger, not a new execution of that study. -/
def sourceWeighted : Fin 3 → ℝ := fun i => if i.val=0 then 1552 else if i.val=1 then 1552 else -1868

theorem source_ledger_arithmetic :
    saving sourceWeighted (fun _ => 1)=1236 ∧
    saving sourceWeighted (fun i => if i.val=1 then 0 else 1)= -316 := by
  constructor <;> norm_num [saving,sourceWeighted,Fin.sum_univ_succ]

end
end Komorebi.MachineTheory.PriceExamples
