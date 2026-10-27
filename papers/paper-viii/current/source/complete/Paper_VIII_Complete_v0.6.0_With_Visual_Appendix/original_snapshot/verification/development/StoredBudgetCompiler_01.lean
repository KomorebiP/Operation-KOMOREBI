module
public import QuantizedTreeCompiler
import all QuantizedTreeCompiler
import all ExactTreeCompiler
import all BudgetConvolution
public import DiscretePrecision
import all DiscretePrecision
public import Init.Data.Vector.OfFn

/-!
Author: Komorebi P.
Paper VIII 9.9 and executable refinements of 9.8 and 8.7.
Tables are real array-backed Vectors: every child table is computed once and
convolutions read cached entries. This is not the exponentially recomputing
functional recurrence used to state the specification.
Work counts use unit-cost table cells and min-plus candidate trials, excluding
arbitrary-precision bit complexity and hardware timing.
-/
public section
set_option autoImplicit false
set_option maxRecDepth 2048
namespace KomorebiPaperVIII
open scoped BigOperators
namespace BudgetDP
variable {R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

abbrev StoredTable (R : Type*) (B : ℕ) := Vector (Option R) (B + 1)

def tabulate (B : ℕ) (F : ℕ → Option R) : StoredTable R B :=
  Vector.ofFn (fun b => F b.val)

def lookup {B : ℕ} (T : StoredTable R B) (b : ℕ) : Option R :=
  if h : b ≤ B then T.get ⟨b, Nat.lt_succ_of_le h⟩ else none

omit [Field R] [LinearOrder R] [IsStrictOrderedRing R] in
theorem lookup_tabulate (B : ℕ) (F : ℕ → Option R) (b : ℕ) (hb : b ≤ B) :
    lookup (tabulate B F) b = F b := by
  simp [lookup, tabulate, hb, Vector.get]

omit [Field R] [IsStrictOrderedRing R] in
theorem bestOver_congr {ι : Type*} (xs : List ι) (F G : ι → Option R)
    (h : ∀ i ∈ xs, F i = G i) : bestOver F xs = bestOver G xs := by
  induction xs with
  | nil => rfl
  | cons i xs ih =>
    simp only [bestOver]
    rw [h i (by simp), ih (fun j hj => h j (by simp [hj]))]

/-- Only entries at most the requested output weight can affect a convolution. -/
theorem convolution_congr_local (F G F' G' : ℕ → Option R) (b : ℕ)
    (hF : ∀ k ≤ b, F k = F' k) (hG : ∀ k ≤ b, G k = G' k) :
    convolution F G b = convolution F' G' b := by
  apply bestOver_congr
  intro k hk
  have hkb : k ≤ b := Nat.lt_succ_iff.mp (List.mem_range.mp hk)
  rw [hF k hkb, hG (b - k) (Nat.sub_le _ _)]

theorem combine_congr_local {n : ℕ} (F G : Fin n → ℕ → Option R) (b : ℕ)
    (h : ∀ i k, k ≤ b → F i k = G i k) : combine F b = combine G b := by
  induction n generalizing b with
  | zero => rfl
  | succ n ih =>
    apply convolution_congr_local
    · exact h 0
    · intro k hk
      exact ih (fun i => F i.succ) (fun i => G i.succ) k
        (fun i l hl => h i.succ l (hl.trans hk))

/-- Every entry is computed once from two already stored tables. -/
def mergeStored {B : ℕ} (F G : StoredTable R B) : StoredTable R B :=
  tabulate B (convolution (lookup F) (lookup G))

/-- A linear number of table merges combines arbitrary finite branching. -/
def combineStored {B : ℕ} : {n : ℕ} → (Fin n → StoredTable R B) → StoredTable R B
  | 0, _ => tabulate B (singletonTable 0 0)
  | n + 1, F =>
    let tail := combineStored (fun i : Fin n => F i.succ)
    mergeStored (F 0) tail

theorem combineStored_correct {B n : ℕ} (F : Fin n → StoredTable R B)
    (b : ℕ) (hb : b ≤ B) :
    lookup (combineStored F) b = combine (fun i => lookup (F i)) b := by
  induction n generalizing b with
  | zero => exact lookup_tabulate B _ b hb
  | succ n ih =>
    change lookup (mergeStored (F 0) (combineStored (fun i : Fin n => F i.succ))) b = _
    rw [mergeStored, lookup_tabulate _ _ _ hb]
    apply convolution_congr_local _ _ _ _ b (fun _ _ => rfl)
    intro k hk
    exact ih (fun i => F i.succ) k (hk.trans hb)
end BudgetDP

namespace CandidateTree
variable {α R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Bottom-up tabulation. Child arrays are eagerly cached before merging. -/
def storedTree (B : ℕ) (κ : α → R) (w : α → ℕ) (σ : α → R) :
    CandidateTree α → BudgetDP.StoredTable R B
  | .leaf a => BudgetDP.tabulate B (BudgetDP.singletonTable (w a) (κ a))
  | .node a n ts =>
    let cached := Vector.ofFn (fun i => storedTree B κ w σ (ts i))
    let merged := BudgetDP.combineStored (fun i : Fin (n + 1) => cached.get i)
    BudgetDP.tabulate B (fun b => BudgetDP.choose (BudgetDP.singletonTable (w a) (κ a) b)
      (BudgetDP.add (some (σ a)) (BudgetDP.lookup merged b)))

/-- The implemented cached array agrees entrywise with the proved exact recurrence. -/
theorem storedTree_correct (B : ℕ) (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (b : ℕ) (hb : b ≤ B) :
    BudgetDP.lookup (storedTree B κ w σ t) b = budgetTable κ w σ t b := by
  induction t generalizing b with
  | leaf a => exact BudgetDP.lookup_tabulate B _ b hb
  | node a n ts ih =>
    simp only [storedTree, budgetTable, BudgetDP.lookup_tabulate _ _ _ hb]
    congr 2
    rw [BudgetDP.combineStored_correct _ b hb]
    apply BudgetDP.combine_congr_local
    intro i k hk
    simpa only [Vector.get, Vector.getElem_ofFn] using ih i k (hk.trans hb)

/-- The executable tabulated compiler scans its stored root table. -/
def storedBudget (B : ℕ) (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) : Option R :=
  let rootTable := storedTree B κ w σ t
  BudgetDP.withinBudget (BudgetDP.lookup rootTable) B

theorem storedBudget_correct (B : ℕ) (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) : storedBudget B κ w σ t = compileBudget κ w σ t B := by
  apply BudgetDP.bestOver_congr
  intro b hb
  exact storedTree_correct B κ w σ t b (Nat.lt_succ_iff.mp (List.mem_range.mp hb))

/-- Optimality and attainment apply to the actual array-backed implementation. -/
theorem storedBudget_minimum (B : ℕ) (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) :
    BudgetDP.IsMinimum (storedBudget B κ w σ t)
      (fun z => ∃ c : Cut t, cutWeight w c ≤ B ∧ cutValue κ σ c = z) := by
  rw [storedBudget_correct]
  exact quantized_budget_compiler κ w σ t B
end CandidateTree

namespace BudgetDP
variable {R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Discrete precision tabulation caches the preceding edge table once. -/
def storedDiscrete (B : ℕ) : List (List (ℕ × R)) → StoredTable R B
  | [] => tabulate B (singletonTable 0 0)
  | opts :: edges =>
    let prior := storedDiscrete B edges
    tabulate B (fun b => bestOver (fun o => if o.1 ≤ b then
      add (lookup prior (b - o.1)) (some o.2) else none) opts)

theorem storedDiscrete_correct (B : ℕ) (edges : List (List (ℕ × R)))
    (b : ℕ) (hb : b ≤ B) : lookup (storedDiscrete B edges) b = discreteTable edges b := by
  induction edges with
  | nil => exact lookup_tabulate B _ b hb
  | cons opts edges ih =>
    simp only [storedDiscrete, discreteTable, lookup_tabulate _ _ _ hb]
    apply bestOver_congr
    intro o _
    by_cases ho : o.1 ≤ b
    · simp only [ho, ↓reduceIte]
      rw [ih (b - o.1) ((Nat.sub_le _ _).trans hb)]
    · simp only [ho, ↓reduceIte]

/-- Cached implementation of the discrete precision optimizer. -/
def storedDiscreteBudget (B : ℕ) (edges : List (List (ℕ × R))) : Option R :=
  let finalTable := storedDiscrete B edges
  withinBudget (lookup finalTable) B

theorem storedDiscreteBudget_correct (B : ℕ) (edges : List (List (ℕ × R))) :
    storedDiscreteBudget B edges = discreteBudget edges B := by
  apply bestOver_congr
  intro b hb
  exact storedDiscrete_correct B edges b (Nat.lt_succ_iff.mp (List.mem_range.mp hb))
end BudgetDP

namespace CandidateTree
variable {α : Type*}

/-- Number of nodes in the independently supplied candidate tree. -/
def nodeCount : CandidateTree α → ℕ
  | .leaf _ => 1
  | .node _ _ ts => 1 + ∑ i, nodeCount (ts i)

/-- Number of child-table merges actually used by the tabulator. -/
def mergeCount : CandidateTree α → ℕ
  | .leaf _ => 0
  | .node _ n ts => n + 1 + ∑ i, mergeCount (ts i)

/-- A nonempty finite tree has one fewer child edges than nodes. -/
theorem mergeCount_add_one (t : CandidateTree α) : mergeCount t + 1 = nodeCount t := by
  induction t with
  | leaf => rfl
  | node a n ts ih =>
    simp only [mergeCount, nodeCount]
    have h : (∑ i, mergeCount (ts i)) + (n + 1) = ∑ i, nodeCount (ts i) := by
      simpa only [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ,
        Fintype.card_fin, smul_eq_mul, mul_one] using
          (Finset.sum_congr rfl (fun i (_ : i ∈ Finset.univ) => ih i))
    omega

/-- Concrete indices of the candidate trials in one complete convolution table. -/
def MergeTrial (B : ℕ) := (b : Fin (B + 1)) × Fin (b.val + 1)

instance mergeTrialFintype (B : ℕ) : Fintype (MergeTrial B) :=
  inferInstanceAs (Fintype ((b : Fin (B + 1)) × Fin (b.val + 1)))

theorem merge_trial_count (B : ℕ) :
    Fintype.card (MergeTrial B) = ∑ b ∈ Finset.range (B + 1), (b + 1) := by
  simp [MergeTrial, Fintype.card_sigma, ← Fin.sum_univ_eq_sum_range]

theorem merge_trial_bound (B : ℕ) : Fintype.card (MergeTrial B) ≤ (B + 1) ^ 2 := by
  rw [merge_trial_count]
  calc
    _ ≤ ∑ _b ∈ Finset.range (B + 1), (B + 1) :=
      Finset.sum_le_sum (fun b hb => by have := Finset.mem_range.mp hb; omega)
    _ = _ := by simp [pow_two]

/-- Unit-cost model: table-cell construction plus each tested min-plus candidate.
The empty combination table costs B+1 cells at every internal node as well. -/
def tabulationWork (B : ℕ) : CandidateTree α → ℕ
  | .leaf _ => B + 1
  | .node _ n ts =>
    2 * (B + 1) + (n + 1) * (B + 1 + Fintype.card (MergeTrial B)) +
      ∑ i, tabulationWork B (ts i)

/-- Corollary 9.9: an explicit O(nodes * (B+1)^2) bound in the declared model. -/
theorem tabulation_work_bound (B : ℕ) (t : CandidateTree α) :
    tabulationWork B t ≤
      2 * (B + 1) * nodeCount t +
        ((B + 1) + (B + 1)^2) * mergeCount t := by
  induction t with
  | leaf => simp [tabulationWork, nodeCount, mergeCount]; omega
  | node a n ts ih =>
    simp only [tabulationWork, nodeCount, mergeCount]
    have hs := Finset.sum_le_sum (fun i (_ : i ∈ Finset.univ) => ih i)
    have hm := Nat.mul_le_mul_left (n + 1) (merge_trial_bound B)
    simp only [Finset.sum_add_distrib, ← Finset.mul_sum] at hs
    nlinarith

/-- The bound is polynomial in numeric budget, not in its binary input length. -/
theorem tabulation_pseudopolynomial (B : ℕ) (t : CandidateTree α) :
    tabulationWork B t ≤ nodeCount t * (3 * (B + 1) + (B + 1)^2) := by
  have h := tabulation_work_bound B t
  have hm := mergeCount_add_one t
  nlinarith
end CandidateTree
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.BudgetDP.lookup_tabulate
#print axioms KomorebiPaperVIII.BudgetDP.bestOver_congr
#print axioms KomorebiPaperVIII.BudgetDP.convolution_congr_local
#print axioms KomorebiPaperVIII.BudgetDP.combine_congr_local
#print axioms KomorebiPaperVIII.BudgetDP.combineStored_correct
#print axioms KomorebiPaperVIII.CandidateTree.storedTree_correct
#print axioms KomorebiPaperVIII.CandidateTree.storedBudget_correct
#print axioms KomorebiPaperVIII.CandidateTree.storedBudget_minimum
#print axioms KomorebiPaperVIII.BudgetDP.storedDiscrete_correct
#print axioms KomorebiPaperVIII.BudgetDP.storedDiscreteBudget_correct
#print axioms KomorebiPaperVIII.CandidateTree.mergeCount_add_one
#print axioms KomorebiPaperVIII.CandidateTree.merge_trial_count
#print axioms KomorebiPaperVIII.CandidateTree.merge_trial_bound
#print axioms KomorebiPaperVIII.CandidateTree.tabulation_work_bound
#print axioms KomorebiPaperVIII.CandidateTree.tabulation_pseudopolynomial
#print axioms KomorebiPaperVIII.CandidateTree.storedTree
#print axioms KomorebiPaperVIII.BudgetDP.storedDiscrete
