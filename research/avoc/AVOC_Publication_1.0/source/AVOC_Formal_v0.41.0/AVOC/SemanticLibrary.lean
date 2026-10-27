import AVOC.BooleanCostClosure

namespace Komorebi.AVOC.SemanticLibrary

open Synthesis BoolClosure

/-- Fixed count of primitive and unary/binary cost inequalities for Bool3. -/
def closureObligations : Nat := 5 + 256 + 3 * 256 * 256

theorem closure_obligation_count : closureObligations = 196869 := by decide

/-- A declared full-validation tariff, not a CPU/time bound. Parsing is separate. -/
def validationCharge (rows : Array Row) : Nat :=
  closureObligations + rows.size + 8 * (rows.toList.map (fun r => nodes r.code)).sum

structure ImportResult where
  checked : Option CheckedBank
  attempted : Bool
  charged : Nat
  remaining : Nat

def paidImport (rows : Array Row) (credit : Nat) : ImportResult :=
  if validationCharge rows ≤ credit then
    if h : checkBank rows = true then
      ⟨some ⟨rows,h⟩,true,validationCharge rows,credit-validationCharge rows⟩
    else ⟨none,true,validationCharge rows,credit-validationCharge rows⟩
  else ⟨none,false,0,credit⟩

theorem import_conservation (rows : Array Row) (credit : Nat) :
    (paidImport rows credit).charged + (paidImport rows credit).remaining = credit := by
  unfold paidImport
  split
  next h => split <;> simp_all <;> omega
  · simp

theorem import_budget (rows : Array Row) (credit : Nat) :
    (paidImport rows credit).charged ≤ credit := by
  have h := import_conservation rows credit
  omega

theorem unfunded_import (rows : Array Row) (credit : Nat)
    (h : credit < validationCharge rows) :
    (paidImport rows credit).checked = none ∧
    (paidImport rows credit).attempted = false ∧ (paidImport rows credit).charged = 0 := by
  have hn : ¬ validationCharge rows ≤ credit := by omega
  simp [paidImport,hn]

theorem funded_invalid_still_charged (rows : Array Row) (credit : Nat)
    (hcredit : validationCharge rows ≤ credit) (hbad : checkBank rows = false) :
    (paidImport rows credit).checked = none ∧
    (paidImport rows credit).attempted = true ∧
    (paidImport rows credit).charged = validationCharge rows := by
  simp [paidImport,hcredit,hbad]

theorem accepted_rows_exact (rows : Array Row) (credit : Nat) (b : CheckedBank)
    (h : (paidImport rows credit).checked = some b) : b.rows = rows := by
  unfold paidImport at h
  split at h
  · split at h
    · cases h; rfl
    · contradiction
  · contradiction

theorem accepted_import_valid (rows : Array Row) (credit : Nat) (b : CheckedBank)
    (h : (paidImport rows credit).checked = some b) :
    checkBank rows = true ∧ (paidImport rows credit).charged = validationCharge rows := by
  have he := accepted_rows_exact rows credit b h
  have hc : checkBank rows = true := by simpa only [he] using b.valid
  refine ⟨hc,?_⟩
  unfold paidImport at h ⊢
  split at h
  next hcredit => simp [hcredit,hc]
  · contradiction

theorem accepted_import_global (rows : Array Row) (credit : Nat) (b : CheckedBank)
    (_h : (paidImport rows credit).checked = some b) (p : Program) :
    Equivalent (query b p) p ∧
    ∀ q, Equivalent q p → nodes (query b p) ≤ nodes q :=
  ⟨query_equivalent b p,query_globally_minimum b p⟩

/-- Query tariff covers eight eager semantic traversals and one indexed lookup. -/
def queryCharge (p : Program) : Nat := 8 * nodes p + 1

structure QueryResult where
  result : Option Program
  charged : Nat
  remaining : Nat
  deriving Repr, DecidableEq

def paidQuery (b : CheckedBank) (p : Program) (credit : Nat) : QueryResult :=
  if queryCharge p ≤ credit then ⟨some (query b p),queryCharge p,credit-queryCharge p⟩
  else ⟨none,0,credit⟩

theorem query_conservation (b : CheckedBank) (p : Program) (credit : Nat) :
    (paidQuery b p credit).charged + (paidQuery b p credit).remaining = credit := by
  unfold paidQuery
  split <;> simp_all <;> omega

theorem paid_query_certified (b : CheckedBank) (p q : Program) (credit : Nat)
    (h : (paidQuery b p credit).result = some q) :
    Equivalent q p ∧ ∀ r, Equivalent r p → nodes q ≤ nodes r := by
  unfold paidQuery at h
  split at h
  · cases h
    exact ⟨query_equivalent b p,query_globally_minimum b p⟩
  · contradiction

theorem import_query_accounting (rows : Array Row) (credit : Nat) (b : CheckedBank)
    (_h : (paidImport rows credit).checked = some b) (p : Program) :
    (paidImport rows credit).charged +
      (paidQuery b p (paidImport rows credit).remaining).charged +
      (paidQuery b p (paidImport rows credit).remaining).remaining = credit := by
  have hi := import_conservation rows credit
  have hq := query_conservation b p (paidImport rows credit).remaining
  omega

/-- Certified upper bound on positive node-saving value for any equivalent replacement. -/
theorem maximum_future_saving (b : CheckedBank) (p q : Program) (calls : Nat)
    (heq : Equivalent q p) :
    calls * (nodes p - nodes q) ≤ calls * (nodes p - nodes (query b p)) := by
  have hm := query_globally_minimum b p q heq
  have hd : nodes p - nodes q ≤ nodes p - nodes (query b p) := by omega
  exact Nat.mul_le_mul_left calls hd

theorem stop_if_cost_covers_all_saving (b : CheckedBank) (p q : Program)
    (calls futureCost : Nat) (heq : Equivalent q p)
    (hc : calls * (nodes p - nodes (query b p)) ≤ futureCost) :
    calls * (nodes p - nodes q) ≤ futureCost :=
  Nat.le_trans (maximum_future_saving b p q calls heq) hc

theorem globally_minimum_no_positive_saving (b : CheckedBank) (p q : Program)
    (calls : Nat) (heq : Equivalent q (query b p)) :
    calls * (nodes (query b p) - nodes q) = 0 := by
  have hq : Equivalent q p := equivalent_trans heq (query_equivalent b p)
  have hm := query_globally_minimum b p q hq
  rw [Nat.sub_eq_zero_of_le hm,Nat.mul_zero]

structure ManyResult where
  queries : List QueryResult
  charged : Nat
  remaining : Nat
  deriving Repr, DecidableEq

def queryMany (b : CheckedBank) : List Program → Nat → ManyResult
  | [], credit => ⟨[],0,credit⟩
  | p :: ps, credit =>
    let first := paidQuery b p credit
    let rest := queryMany b ps first.remaining
    ⟨first :: rest.queries,first.charged + rest.charged,rest.remaining⟩

theorem many_conservation (b : CheckedBank) (ps : List Program) (credit : Nat) :
    (queryMany b ps credit).charged + (queryMany b ps credit).remaining = credit := by
  induction ps generalizing credit with
  | nil => simp [queryMany]
  | cons p ps ih =>
    have hf := query_conservation b p credit
    have hr := ih (paidQuery b p credit).remaining
    simp only [queryMany]
    omega

def QueriesSound : List Program → List QueryResult → Prop
  | [], [] => True
  | p :: ps, r :: rs =>
    (∀ q, r.result = some q → Equivalent q p ∧
      ∀ c, Equivalent c p → nodes q ≤ nodes c) ∧ QueriesSound ps rs
  | _, _ => False

theorem many_sound (b : CheckedBank) (ps : List Program) (credit : Nat) :
    QueriesSound ps (queryMany b ps credit).queries := by
  induction ps generalizing credit with
  | nil => trivial
  | cons p ps ih =>
    exact ⟨fun q h => paid_query_certified b p q credit h, ih _⟩

theorem many_charges_exact (b : CheckedBank) (ps : List Program) (credit : Nat) :
    (queryMany b ps credit).charged =
      ((queryMany b ps credit).queries.map QueryResult.charged).sum := by
  induction ps generalizing credit with
  | nil => simp [queryMany]
  | cons p ps ih => simp only [queryMany, List.map_cons, List.sum_cons, ih]

theorem import_many_accounting (rows : Array Row) (credit : Nat) (b : CheckedBank)
    (_h : (paidImport rows credit).checked = some b) (ps : List Program) :
    (paidImport rows credit).charged +
      (queryMany b ps (paidImport rows credit).remaining).charged +
      (queryMany b ps (paidImport rows credit).remaining).remaining = credit := by
  have hi := import_conservation rows credit
  have hq := many_conservation b ps (paidImport rows credit).remaining
  omega

end Komorebi.AVOC.SemanticLibrary
