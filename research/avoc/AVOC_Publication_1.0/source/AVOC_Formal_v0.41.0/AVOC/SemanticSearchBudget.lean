import AVOC.SemanticSynthesisWork

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

/-- The full bounded-search contract travels with the reusable semantic library. -/
structure Bank (d : Nat) where
  entries : List Entry
  origin : ∀ p ∈ codes entries, p ∈ programs d
  coverage : Covers (programs d) (codes entries)
  unique : Unique entries

structure Layer (d : Nat) where
  bank : Bank d
  work : Work
  reservation : Nat
  charge_bound : work.charge ≤ reservation

def initialLayer : Layer 0 :=
  let r := indexed atoms
  { bank :=
      { entries := r.entries
        origin := by intro p hp; exact compact_codes_origin atoms p (by simpa [r, indexed_refines] using hp)
        coverage := indexed_coverage atoms
        unique := indexed_unique atoms }
    work := r.work
    reservation := reserve atoms.length (nodeBound 0)
    charge_bound := indexed_charge_bound atoms (nodeBound 0)
      (fun p hp => programs_nodes_bound 0 p hp) }

def nextCount {d : Nat} (b : Bank d) : Nat := 2*b.entries.length+3*b.entries.length*b.entries.length

def nextReservation {d : Nat} (b : Bank d) : Nat := reserve (nextCount b) (nodeBound (d+1))

def advanceLayer {d : Nat} (b : Bank d) : Layer (d+1) :=
  let ps := expand (codes b.entries)
  let r := indexed ps
  { bank :=
      { entries := r.entries
        origin := by
          intro p hp
          have hm := compact_codes_origin ps p (by simpa [r, indexed_refines] using hp)
          exact expand_mono b.origin p hm
        coverage := covers_trans (expand_covers b.coverage) (indexed_coverage ps)
        unique := indexed_unique ps }
    work := r.work
    reservation := nextReservation b
    charge_bound := by
      have hnodes : ∀ p ∈ ps, nodes p ≤ nodeBound (d+1) := by
        intro p hp
        exact programs_nodes_bound (d+1) p (expand_mono b.origin p hp)
      have hh := indexed_charge_bound ps (nodeBound (d+1)) hnodes
      have hlen : ps.length = nextCount b := by simp [ps, expand_length, codes, nextCount]
      simpa only [hlen, nextReservation, r] using hh }

structure PaidRun (credit : Nat) where
  depth : Nat
  bank : Bank depth
  work : Work
  remaining : Nat
  stages : List Stage
  conserved : work.charge + remaining = credit

/-- The reservation test is outside the evaluated layer. Failure does not enumerate it. -/
def startPaid (credit : Nat) : Option (PaidRun credit) :=
  if h : reserve atoms.length (nodeBound 0) ≤ credit then
    let r := initialLayer
    some { depth := 0, bank := r.bank, work := r.work
           remaining := credit-r.work.charge
           stages := [⟨0,r.bank.entries.length,r.work⟩]
           conserved := by
             have hb := Nat.le_trans r.charge_bound h
             exact Nat.add_sub_of_le hb }
  else none

def advancePaid {credit : Nat} (r : PaidRun credit) : Option (PaidRun credit) :=
  if h : nextReservation r.bank ≤ r.remaining then
    let layer := advanceLayer r.bank
    some { depth := r.depth+1
           bank := layer.bank
           work := r.work.add layer.work
           remaining := r.remaining-layer.work.charge
           stages := r.stages ++ [⟨r.depth+1,layer.bank.entries.length,layer.work⟩]
           conserved := by
             have hb := Nat.le_trans layer.charge_bound h
             have hr := r.conserved
             rw [work_charge_add]
             omega }
  else none

def continuePaid {credit : Nat} : Nat → PaidRun credit → PaidRun credit
  | 0, r => r
  | n+1, r => match advancePaid r with
    | none => r
    | some next => continuePaid n next

def paidSearch (maxDepth credit : Nat) : Option (PaidRun credit) :=
  match startPaid credit with
  | none => none
  | some r => some (continuePaid maxDepth r)

theorem paid_no_overspend {credit : Nat} (r : PaidRun credit) : r.work.charge ≤ credit := by
  have h := r.conserved
  omega

theorem unfunded_layer_not_run {credit : Nat} (r : PaidRun credit)
    (h : r.remaining < nextReservation r.bank) : advancePaid r = none := by
  simp [advancePaid, show ¬ nextReservation r.bank ≤ r.remaining by omega]

theorem unfunded_seed_no_search (d credit : Nat)
    (h : credit < reserve atoms.length (nodeBound 0)) : paidSearch d credit = none := by
  simp [paidSearch, startPaid, show ¬ reserve atoms.length (nodeBound 0) ≤ credit by omega]

theorem bank_capacity {d : Nat} (b : Bank d) : b.entries.length ≤ 256 :=
  unique_entries_at_most_256 _ b.unique

theorem bank_query_sound {d : Nat} (b : Bank d) (r : Program) :
    Equivalent (select r r (codes b.entries)) r := select_sound r r _ (equivalent_refl r)

theorem bank_query_bounded_optimal {d : Nat} (b : Bank d) (r p : Program)
    (hp : height p ≤ d) (he : Equivalent p r) : nodes (select r r (codes b.entries)) ≤ nodes p := by
  obtain ⟨q,hq,heq,hn⟩ := b.coverage p (bounded_grammar_complete d p hp)
  exact Nat.le_trans (select_minimum r r _ q hq (equivalent_trans heq he)) hn

theorem bank_query_same_frozen {d : Nat} (b : Bank d) (r : Program) :
    nodes (select r r (codes b.entries)) = nodes (select r r (programs d)) := by
  apply Nat.le_antisymm
  · rcases select_member r r (programs d) with hi | hp
    · rw [hi]; exact select_no_larger _ _ _
    · obtain ⟨q,hq,he,hn⟩ := b.coverage _ hp
      exact Nat.le_trans (select_minimum r r _ q hq
        (equivalent_trans he (select_sound _ _ _ (equivalent_refl r)))) hn
  · rcases select_member r r (codes b.entries) with hi | hp
    · rw [hi]; exact select_no_larger _ _ _
    · exact select_minimum r r (programs d) _ (b.origin _ hp) (bank_query_sound b r)

theorem paid_certified_result {credit : Nat} (r : PaidRun credit) (reference : Program) :
    Equivalent (select reference reference (codes r.bank.entries)) reference ∧
    nodes (select reference reference (codes r.bank.entries)) =
      nodes (select reference reference (programs r.depth)) ∧
    r.bank.entries.length ≤ 256 ∧ r.work.charge ≤ credit :=
  ⟨bank_query_sound r.bank reference, bank_query_same_frozen r.bank reference,
    bank_capacity r.bank, paid_no_overspend r⟩

end Komorebi.AVOC.SemanticSynthesis
