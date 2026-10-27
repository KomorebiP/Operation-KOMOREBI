import AVOC.SemanticCostCertificate

namespace Komorebi.AVOC.BoolClosure

open Synthesis CostCertificate

/-- Complete truth signature. Field order is the inherited lexicographic input order. -/
structure Sig where
  a : Bool
  b : Bool
  c : Bool
  d : Bool
  e : Bool
  f : Bool
  g : Bool
  h : Bool
  deriving Repr, DecidableEq

def Sig.ofFun (f : Input → Bool) : Sig :=
  ⟨f ⟨false,false,false⟩, f ⟨false,false,true⟩,
   f ⟨false,true,false⟩, f ⟨false,true,true⟩,
   f ⟨true,false,false⟩, f ⟨true,false,true⟩,
   f ⟨true,true,false⟩, f ⟨true,true,true⟩⟩

def Sig.get (s : Sig) (i : Input) : Bool :=
  if i.first then
    if i.second then (if i.third then s.h else s.g)
    else (if i.third then s.f else s.e)
  else
    if i.second then (if i.third then s.d else s.c)
    else (if i.third then s.b else s.a)

def Sig.neg (s : Sig) : Sig := ⟨!s.a,!s.b,!s.c,!s.d,!s.e,!s.f,!s.g,!s.h⟩
def Sig.bin (op : Bool → Bool → Bool) (s t : Sig) : Sig :=
  ⟨op s.a t.a,op s.b t.b,op s.c t.c,op s.d t.d,
   op s.e t.e,op s.f t.f,op s.g t.g,op s.h t.h⟩

theorem get_ofFun (f : Input → Bool) (i : Input) : (Sig.ofFun f).get i = f i := by
  rcases i with ⟨a,b,c⟩
  cases a <;> cases b <;> cases c <;> rfl

theorem get_neg (s : Sig) (i : Input) : s.neg.get i = !(s.get i) := by
  rcases i with ⟨a,b,c⟩
  cases a <;> cases b <;> cases c <;> rfl

theorem get_bin (op : Bool → Bool → Bool) (s t : Sig) (i : Input) :
    (Sig.bin op s t).get i = op (s.get i) (t.get i) := by
  rcases i with ⟨a,b,c⟩
  cases a <;> cases b <;> cases c <;> rfl

theorem sig_ext {s t : Sig} (h : ∀ i, s.get i = t.get i) : s = t := by
  cases s with
  | mk a b c d e f g hh =>
    cases t with
    | mk aa bb cc dd ee ff gg hhh =>
      have h0 := h ⟨false,false,false⟩
      have h1 := h ⟨false,false,true⟩
      have h2 := h ⟨false,true,false⟩
      have h3 := h ⟨false,true,true⟩
      have h4 := h ⟨true,false,false⟩
      have h5 := h ⟨true,false,true⟩
      have h6 := h ⟨true,true,false⟩
      have h7 := h ⟨true,true,true⟩
      simp only [Sig.get] at h0 h1 h2 h3 h4 h5 h6 h7
      cases h0; cases h1; cases h2; cases h3; cases h4; cases h5; cases h6; cases h7
      rfl

def algebra : Algebra Sig where
  literal b := Sig.ofFun (fun _ => b)
  atom v := Sig.ofFun (fun s => s.get v)
  neg := Sig.neg
  conj := Sig.bin (fun x y => x && y)
  disj := Sig.bin (fun x y => x || y)
  excl := Sig.bin xor

def sem (p : Program) : Sig := interpret algebra p

theorem sem_get (p : Program) (i : Input) : (sem p).get i = run p i := by
  induction p with
  | literal b => simpa only [sem, interpret, algebra, run] using get_ofFun (fun _ => b) i
  | «variable» v => simpa only [sem, interpret, algebra, run] using get_ofFun (fun s : Input => s.get v) i
  | neg p ih =>
    change (sem p).neg.get i = !(run p i)
    rw [get_neg, ih]
  | conjunction p q ihp ihq =>
    change (Sig.bin (fun x y => x && y) (sem p) (sem q)).get i = (run p i && run q i)
    rw [get_bin, ihp, ihq]
  | disjunction p q ihp ihq =>
    change (Sig.bin (fun x y => x || y) (sem p) (sem q)).get i = (run p i || run q i)
    rw [get_bin, ihp, ihq]
  | exclusive p q ihp ihq =>
    change (Sig.bin xor (sem p) (sem q)).get i = xor (run p i) (run q i)
    rw [get_bin, ihp, ihq]

theorem sem_eq_iff (p q : Program) : sem p = sem q ↔ Equivalent p q := by
  constructor
  · intro h i
    rw [← sem_get p i, h, sem_get]
  · intro h
    apply sig_ext
    intro i
    rw [sem_get, sem_get]
    exact h i

def bools : List Bool := [false,true]

def signatures : List Sig :=
  bools.flatMap fun a => bools.flatMap fun b => bools.flatMap fun c =>
  bools.flatMap fun d => bools.flatMap fun e => bools.flatMap fun f =>
  bools.flatMap fun g => bools.map fun h => ⟨a,b,c,d,e,f,g,h⟩

theorem mem_bools (b : Bool) : b ∈ bools := by cases b <;> decide

theorem signatures_complete (s : Sig) : s ∈ signatures := by
  rcases s with ⟨a,b,c,d,e,f,g,h⟩
  unfold signatures
  apply List.mem_flatMap.mpr; refine ⟨a,mem_bools a,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨b,mem_bools b,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨c,mem_bools c,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨d,mem_bools d,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨e,mem_bools e,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨f,mem_bools f,?_⟩
  apply List.mem_flatMap.mpr; refine ⟨g,mem_bools g,?_⟩
  exact List.mem_map.mpr ⟨h,mem_bools h,rfl⟩

set_option maxRecDepth 4096 in
theorem signatures_length : signatures.length = 256 := by decide

/-- Positional index: bit zero corresponds to false,false,false. -/
def Sig.index (s : Sig) : Nat :=
  s.a.toNat + 2*s.b.toNat + 4*s.c.toNat + 8*s.d.toNat +
  16*s.e.toNat + 32*s.f.toNat + 64*s.g.toNat + 128*s.h.toNat

theorem bool_cost_bit_bound (b : Bool) : b.toNat ≤ 1 := by cases b <;> decide

theorem signature_index_bound (s : Sig) : s.index < 256 := by
  have ha := bool_cost_bit_bound s.a
  have hb := bool_cost_bit_bound s.b
  have hc := bool_cost_bit_bound s.c
  have hd := bool_cost_bit_bound s.d
  have he := bool_cost_bit_bound s.e
  have hf := bool_cost_bit_bound s.f
  have hg := bool_cost_bit_bound s.g
  have hh := bool_cost_bit_bound s.h
  unfold Sig.index
  omega

structure Row where
  claimed : Sig
  size : Nat
  code : Program
  deriving Repr, DecidableEq

def defaultRow : Row := ⟨sem (.literal false),1,.literal false⟩
def rowAt (rows : Array Row) (s : Sig) : Row := (rows[s.index]?).getD defaultRow
def cost (rows : Array Row) (s : Sig) : Nat := (rowAt rows s).size
def witness (rows : Array Row) (s : Sig) : Program := (rowAt rows s).code

/-- Realizability includes exact stored signature and node-count correspondence. -/
def witnessesCheck (rows : Array Row) : Bool := signatures.all fun s =>
  decide ((rowAt rows s).claimed = s ∧ sem (witness rows s) = s ∧
    nodes (witness rows s) = cost rows s)

def lowerCheck (rows : Array Row) : Bool :=
  (atoms.all fun p => decide (cost rows (sem p) ≤ nodes p)) &&
  (signatures.all fun s => decide (cost rows s.neg ≤ cost rows s + 1)) &&
  (signatures.all fun s => signatures.all fun t =>
    decide (cost rows (Sig.bin (fun x y => x && y) s t) ≤ cost rows s + cost rows t + 1) &&
    decide (cost rows (Sig.bin (fun x y => x || y) s t) ≤ cost rows s + cost rows t + 1) &&
    decide (cost rows (Sig.bin xor s t) ≤ cost rows s + cost rows t + 1))

def checkBank (rows : Array Row) : Bool :=
  decide (rows.size = 256) && witnessesCheck rows && lowerCheck rows

theorem witness_check_sound (rows : Array Row) (h : witnessesCheck rows = true) :
    Realizes algebra (cost rows) (witness rows) := by
  intro s
  have hs := List.all_eq_true.mp h s (signatures_complete s)
  have hp := of_decide_eq_true hs
  exact ⟨hp.2.1,hp.2.2⟩

theorem lower_check_sound (rows : Array Row) (h : lowerCheck rows = true) :
    LowerValid algebra (cost rows) := by
  have parts :
      (atoms.all fun p => decide (cost rows (sem p) ≤ nodes p)) = true ∧
      (signatures.all fun s => decide (cost rows s.neg ≤ cost rows s + 1)) = true ∧
      (signatures.all fun s => signatures.all fun t =>
        decide (cost rows (Sig.bin (fun x y => x && y) s t) ≤ cost rows s + cost rows t + 1) &&
        decide (cost rows (Sig.bin (fun x y => x || y) s t) ≤ cost rows s + cost rows t + 1) &&
        decide (cost rows (Sig.bin xor s t) ≤ cost rows s + cost rows t + 1)) = true := by
    simpa only [lowerCheck, Bool.and_eq_true, and_assoc] using h
  have hatom : ∀ p ∈ atoms, cost rows (sem p) ≤ nodes p := by
    intro p hp
    exact of_decide_eq_true (List.all_eq_true.mp parts.1 p hp)
  have hneg : ∀ s, cost rows s.neg ≤ cost rows s + 1 := by
    intro s
    exact of_decide_eq_true (List.all_eq_true.mp parts.2.1 s (signatures_complete s))
  have hbin : ∀ s t,
      cost rows (Sig.bin (fun x y => x && y) s t) ≤ cost rows s + cost rows t + 1 ∧
      cost rows (Sig.bin (fun x y => x || y) s t) ≤ cost rows s + cost rows t + 1 ∧
      cost rows (Sig.bin xor s t) ≤ cost rows s + cost rows t + 1 := by
    intro s t
    have hs := List.all_eq_true.mp parts.2.2 s (signatures_complete s)
    have ht := List.all_eq_true.mp hs t (signatures_complete t)
    simpa only [Bool.and_eq_true, decide_eq_true_eq, and_assoc] using ht
  refine ⟨?_,?_,hneg,fun s t => (hbin s t).1,
    fun s t => (hbin s t).2.1,fun s t => (hbin s t).2.2⟩
  · intro b
    exact hatom (.literal b) (by cases b <;> simp [atoms])
  · intro v
    exact hatom (.variable v) (by cases v <;> simp [atoms])

theorem check_bank_parts (rows : Array Row) (h : checkBank rows = true) :
    rows.size = 256 ∧ Realizes algebra (cost rows) (witness rows) ∧
      LowerValid algebra (cost rows) := by
  have hh : rows.size = 256 ∧ witnessesCheck rows = true ∧ lowerCheck rows = true := by
    simpa only [checkBank, Bool.and_eq_true, decide_eq_true_eq, and_assoc] using h
  exact ⟨hh.1,witness_check_sound rows hh.2.1,lower_check_sound rows hh.2.2⟩

/-- Only the checked importer creates this proof-carrying record from external rows. -/
structure CheckedBank where
  rows : Array Row
  valid : checkBank rows = true

def importBank (rows : Array Row) : Except String CheckedBank :=
  if h : checkBank rows = true then .ok ⟨rows,h⟩ else .error "invalid cost-closure certificate"

def query (b : CheckedBank) (p : Program) : Program := witness b.rows (sem p)

theorem query_equivalent (b : CheckedBank) (p : Program) : Equivalent (query b p) p := by
  apply (sem_eq_iff _ _).mp
  exact ((check_bank_parts b.rows b.valid).2.1 (sem p)).1

theorem query_globally_minimum (b : CheckedBank) (p q : Program) (h : Equivalent q p) :
    nodes (query b p) ≤ nodes q := by
  have parts := check_bank_parts b.rows b.valid
  exact witness_global_minimum algebra (cost b.rows) (witness b.rows) parts.2.2 parts.2.1
    (sem p) q ((sem_eq_iff q p).mpr h)

theorem query_no_larger (b : CheckedBank) (p : Program) : nodes (query b p) ≤ nodes p :=
  query_globally_minimum b p p (equivalent_refl p)

theorem query_cost_fixed (b c : CheckedBank) (p : Program) :
    nodes (query b p) = nodes (query c p) := by
  apply Nat.le_antisymm
  · exact query_globally_minimum b p (query c p) (query_equivalent c p)
  · exact query_globally_minimum c p (query b p) (query_equivalent b p)

theorem query_idempotent_cost (b : CheckedBank) (p : Program) :
    nodes (query b (query b p)) = nodes (query b p) := by
  apply Nat.le_antisymm
  · exact query_no_larger b (query b p)
  · exact query_globally_minimum b p (query b (query b p))
      (equivalent_trans (query_equivalent b (query b p)) (query_equivalent b p))

theorem larger_equivalent_cannot_be_witness (b : CheckedBank) (p q : Program)
    (h : Equivalent q p) (hl : nodes q < nodes (query b p)) : False := by
  have hn := query_globally_minimum b p q h
  omega

end Komorebi.AVOC.BoolClosure
