import AVOC.BooleanProgram

namespace Komorebi.AVOC.Synthesis

/-- Retain the first smallest certified candidate; ties do not churn the incumbent. -/
def prefer (reference incumbent candidate : Program) : Program :=
  if check candidate reference && decide (nodes candidate < nodes incumbent) then
    candidate
  else incumbent

def select (reference : Program) : Program → List Program → Program
  | incumbent, [] => incumbent
  | incumbent, candidate :: tail => select reference (prefer reference incumbent candidate) tail

theorem prefer_sound (r i c : Program) (h : Equivalent i r) :
    Equivalent (prefer r i c) r := by
  unfold prefer
  split
  next hc =>
    have hh : check c r = true ∧ nodes c < nodes i := by simpa using hc
    exact check_sound c r hh.1
  · exact h

theorem prefer_no_larger (r i c : Program) : nodes (prefer r i c) ≤ nodes i := by
  unfold prefer
  split
  next h =>
    have hh : check c r = true ∧ nodes c < nodes i := by simpa using h
    exact Nat.le_of_lt hh.2
  · exact Nat.le_refl _

theorem prefer_le_candidate (r i c : Program) (h : Equivalent c r) :
    nodes (prefer r i c) ≤ nodes c := by
  by_cases hn : nodes c < nodes i
  · simp [prefer, check_complete c r h, hn]
  · simp [prefer, check_complete c r h, hn]
    omega

theorem prefer_member (r i c : Program) : prefer r i c = i ∨ prefer r i c = c := by
  unfold prefer
  split <;> simp

theorem select_sound (r i : Program) (xs : List Program) (h : Equivalent i r) :
    Equivalent (select r i xs) r := by
  induction xs generalizing i with
  | nil => exact h
  | cons c xs ih => exact ih _ (prefer_sound r i c h)

theorem select_no_larger (r i : Program) (xs : List Program) :
    nodes (select r i xs) ≤ nodes i := by
  induction xs generalizing i with
  | nil => exact Nat.le_refl _
  | cons c xs ih => exact Nat.le_trans (ih _) (prefer_no_larger r i c)

theorem select_minimum (r i : Program) (xs : List Program)
    (c : Program) (hc : c ∈ xs) (hv : Equivalent c r) :
    nodes (select r i xs) ≤ nodes c := by
  induction xs generalizing i with
  | nil => simp at hc
  | cons x xs ih =>
    rcases List.mem_cons.mp hc with he | ht
    · subst c
      exact Nat.le_trans (select_no_larger r (prefer r i x) xs) (prefer_le_candidate r i x hv)
    · exact ih _ ht

theorem select_member (r i : Program) (xs : List Program) :
    select r i xs = i ∨ select r i xs ∈ xs := by
  induction xs generalizing i with
  | nil => exact Or.inl rfl
  | cons c xs ih =>
    rcases ih (prefer r i c) with he | hm
    · rcases prefer_member r i c with hp | hp
      · exact Or.inl (he.trans hp)
      · exact Or.inr (List.mem_cons.mpr (Or.inl (he.trans hp)))
    · exact Or.inr (List.mem_cons.mpr (Or.inr hm))

/-- Uniform conservative charge for eight comparisons and eager AST evaluations.
No claim about CPU, allocation, multiplication, serialization or wall time. -/
def testCharge (reference : Program) (depth : Nat) : Nat :=
  8 * (nodes reference + nodeBound depth + 1)

theorem testCharge_positive (r : Program) (d : Nat) : 0 < testCharge r d := by
  unfold testCharge; omega

theorem testCharge_covers (r c : Program) (d : Nat) (hc : c ∈ programs d) :
    8 * (nodes r + nodes c + 1) ≤ testCharge r d := by
  have h := programs_nodes_bound d c hc
  unfold testCharge
  omega

/-- The full finite grammar layer is generated only after its charge fits.
The tested prefix is then bounded independently by credit and a user trial cap. -/
def examined (reference : Program) (depth limit budget : Nat) : List Program :=
  if generationCharge depth ≤ budget then
    (programs depth).take (min limit ((budget - generationCharge depth) / testCharge reference depth))
  else []

def generationSpent (depth budget : Nat) : Nat :=
  if generationCharge depth ≤ budget then generationCharge depth else 0

def searchSpent (reference : Program) (depth limit budget : Nat) : Nat :=
  generationSpent depth budget + (examined reference depth limit budget).length * testCharge reference depth

def synthesize (reference : Program) (depth limit budget : Nat) : Program :=
  select reference reference (examined reference depth limit budget)

theorem examined_mem_generated (r : Program) (d l b : Nat) (p : Program)
    (h : p ∈ examined r d l b) : p ∈ programs d := by
  unfold examined at h
  split at h
  · exact List.mem_of_mem_take h
  · simp at h

theorem examined_count (r : Program) (d l b : Nat) :
    (examined r d l b).length ≤ l ∧ (examined r d l b).length ≤ poolSize d := by
  unfold examined
  split
  · rw [List.length_take, programs_length]
    omega
  · simp

theorem search_budget (r : Program) (d l b : Nat) : searchSpent r d l b ≤ b := by
  by_cases h : generationCharge d ≤ b
  · have hlen : (examined r d l b).length ≤ (b - generationCharge d) / testCharge r d := by
      simp only [examined, h, ↓reduceIte, List.length_take]
      omega
    have hm := Nat.mul_le_mul_right (testCharge r d) hlen
    have hd := Nat.div_mul_le_self (b - generationCharge d) (testCharge r d)
    simp only [searchSpent, generationSpent, h, ↓reduceIte]
    omega
  · simp [searchSpent, generationSpent, examined, h]

theorem insufficient_generation_no_search (r : Program) (d l b : Nat)
    (h : b < generationCharge d) :
    synthesize r d l b = r ∧ searchSpent r d l b = 0 := by
  have hn : ¬ generationCharge d ≤ b := by omega
  simp [synthesize, searchSpent, generationSpent, examined, hn, select]

theorem synthesis_sound (r : Program) (d l b : Nat) :
    Equivalent (synthesize r d l b) r :=
  select_sound r r _ (equivalent_refl r)

theorem synthesis_work_nondegrading (r : Program) (d l b : Nat) :
    nodes (synthesize r d l b) ≤ nodes r := select_no_larger r r _

theorem synthesis_minimum_on_examined (r : Program) (d l b : Nat)
    (p : Program) (hp : p ∈ examined r d l b) (hv : Equivalent p r) :
    nodes (synthesize r d l b) ≤ nodes p := select_minimum r r _ p hp hv

theorem changed_candidate_was_generated (r : Program) (d l b : Nat)
    (h : synthesize r d l b ≠ r) : synthesize r d l b ∈ programs d := by
  rcases select_member r r (examined r d l b) with he | hm
  · exact False.elim (h he)
  · exact examined_mem_generated r d l b _ hm

theorem certified_synthesis (r : Program) (d l b : Nat) :
    (∀ s, run (synthesize r d l b) s = run r s) ∧
    (∀ s, (runCount (synthesize r d l b) s).2 ≤ (runCount r s).2) ∧
    searchSpent r d l b ≤ b := by
  refine ⟨synthesis_sound r d l b, ?_, search_budget r d l b⟩
  intro s
  rw [runCount_visits, runCount_visits]
  exact synthesis_work_nondegrading r d l b

theorem examined_full (r : Program) (d l b : Nat)
    (hl : poolSize d ≤ l)
    (hb : generationCharge d + poolSize d * testCharge r d ≤ b) :
    examined r d l b = programs d := by
  have hg : generationCharge d ≤ b := by omega
  have hm : poolSize d * testCharge r d ≤ b - generationCharge d := by omega
  have hd := (Nat.le_div_iff_mul_le (testCharge_positive r d)).2 hm
  unfold examined
  simp only [hg, ↓reduceIte]
  apply List.take_of_length_le
  rw [programs_length]
  omega

theorem synthesis_optimal_bounded_grammar (r : Program) (d l b : Nat)
    (hl : poolSize d ≤ l)
    (hb : generationCharge d + poolSize d * testCharge r d ≤ b)
    (p : Program) (hp : height p ≤ d) (hv : Equivalent p r) :
    nodes (synthesize r d l b) ≤ nodes p := by
  apply synthesis_minimum_on_examined r d l b p _ hv
  rw [examined_full r d l b hl hb]
  exact bounded_grammar_complete d p hp

structure SearchResult where
  candidate : Program
  tested : Nat
  generation : Nat
  evaluation : Nat
  deriving Repr, DecidableEq

/-- Single executed search: the materialized prefix is shared, not regenerated for
reporting its length or fee. -/
def search (r : Program) (d l b : Nat) : SearchResult :=
  let xs := examined r d l b
  ⟨select r r xs, xs.length, generationSpent d b, xs.length * testCharge r d⟩

theorem search_candidate (r : Program) (d l b : Nat) :
    (search r d l b).candidate = synthesize r d l b := rfl

theorem search_safe (r : Program) (d l b : Nat) :
    Equivalent (search r d l b).candidate r ∧
    (search r d l b).generation + (search r d l b).evaluation ≤ b :=
  ⟨synthesis_sound r d l b, search_budget r d l b⟩

theorem search_tested_bounded (r : Program) (d l b : Nat) :
    (search r d l b).tested ≤ l := (examined_count r d l b).1

end Komorebi.AVOC.Synthesis
