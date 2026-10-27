module
public import BinaryEncoding

@[expose] public section
namespace Komorebi.Binary

abbrev BitEval (α : Type) := α × Nat

/-- Declared gate/cell evaluator: ten units per full-adder column, one carry output. -/
def addEval : Word → Word → Bool → BitEval Word
  | [],[],c => ([c],1)
  | a::as,[],c =>
    let f := fullAdd a false c
    let z := addEval as [] f.2
    (f.1::z.1,z.2+10)
  | [],b::bs,c =>
    let f := fullAdd false b c
    let z := addEval [] bs f.2
    (f.1::z.1,z.2+10)
  | a::as,b::bs,c =>
    let f := fullAdd a b c
    let z := addEval as bs f.2
    (f.1::z.1,z.2+10)
termination_by a b _ => a.length+b.length

@[simp] theorem addEval_value (a b : Word) (c : Bool) : (addEval a b c).1=addCarry a b c := by
  induction a generalizing b c with
  | nil =>
    induction b generalizing c with
    | nil => simp [addEval,addCarry]
    | cons b bs ih => simp only [addEval,addCarry,ih]
  | cons a as ih => cases b <;> simp only [addEval,addCarry,ih]

@[simp] theorem addEval_cost (a b : Word) (c : Bool) :
    (addEval a b c).2=10*max a.length b.length+1 := by
  induction a generalizing b c with
  | nil =>
    induction b generalizing c with
    | nil => simp [addEval]
    | cons b bs ih => simp [addEval,ih]; omega
  | cons a as ih =>
    cases b <;> simp only [addEval,List.length_cons,List.length_nil,ih] <;> omega

/-- Twelve units per full-subtractor column: seven gates and five cell accesses;
one terminal borrow output. No constant-cost arithmetic on whole data words. -/
def subEval : Word → Word → Bool → BitEval (Word × Bool)
  | [],_,c => (([],c),1)
  | a::as,b,c =>
    let f := fullSub a (b.headD false) c
    let z := subEval as b.tail f.2
    ((f.1::z.1.1,z.1.2),z.2+12)

@[simp] theorem subEval_value (a b : Word) (c : Bool) :
    (subEval a b c).1=subBorrow a b c := by
  induction a generalizing b c with
  | nil => rfl
  | cons a as ih => simp only [subEval,subBorrow,ih]

@[simp] theorem subEval_cost (a b : Word) (c : Bool) :
    (subEval a b c).2=12*a.length+1 := by
  induction a generalizing b c with
  | nil => rfl
  | cons a as ih => simp only [subEval,ih,List.length_cons]; omega

/-- Actual metered shift-and-add evaluation, sharing the recursive result. -/
def mulEval : Word → Word → BitEval Word
  | [],_ => ([],1)
  | a::as,b =>
    let z := mulEval as b
    if a then
      let t := addEval b (false::z.1) false
      (t.1,z.2+2+t.2)
    else (false::z.1,z.2+2)

@[simp] theorem mulEval_value (a b : Word) : (mulEval a b).1=mulWord a b := by
  induction a with
  | nil => rfl
  | cons a as ih => simp only [mulEval,mulWord,addEval_value,ih]; split <;> rfl

@[simp] theorem mulEval_cost (a b : Word) : (mulEval a b).2=mulCost a b := by
  induction a with
  | nil => rfl
  | cons a as ih =>
    cases a <;> simp [mulEval,mulCost,addEval_cost,addCost,ih]

/-- Actual metered restoring division. Both paddings copy width cells; each stage
adds three control/output-cell units to the subtractor cost. -/
def divEval : Word → Word → BitEval (Word × Word)
  | [],_ => (([],[]),1)
  | a::as,b =>
    let z := divEval as b
    let u := a::z.1.2
    let width := max u.length b.length
    let x := pad u width
    let y := pad b width
    let s := subEval x y false
    let cost := z.2+2*width+s.2+3
    if s.1.2 then ((false::z.1.1,x),cost) else ((true::z.1.1,s.1.1),cost)

@[simp] theorem divEval_value (a b : Word) : (divEval a b).1=divRaw a b := by
  induction a with
  | nil => rfl
  | cons a as ih =>
    simp only [divEval,divRaw,divStep,subEval_value,ih]
    split <;> rfl

@[simp] theorem divEval_cost (a b : Word) : (divEval a b).2=divCost a b := by
  induction a with
  | nil => rfl
  | cons a as ih =>
    have hh : (pad (a::(divRaw as b).2)
      (max (a::(divRaw as b).2).length b.length)).length =
      max (a::(divRaw as b).2).length b.length := length_pad _ (le_max_left _ _)
    simp only [List.length_cons] at hh
    simp only [divEval,divCost,subEval_cost,subEval_value,divEval_value,ih]
    split <;> simp only [List.length_cons] <;> rw [hh] <;> omega

/-- Native quotient/remainder appears only in this correctness statement. -/
theorem divEval_semantics (a b : Word) (hb : 0<value b) :
    value (divEval a b).1.1=value a/value b ∧
    value (divEval a b).1.2=value a%value b := by
  rw [divEval_value]
  have hs := divRaw_correct a b hb
  have hu := (Nat.div_mod_unique hb).mpr (And.intro (by nlinarith [hs.1]) hs.2)
  exact ⟨hu.1.symm,hu.2.symm⟩

/-- Modular multiplication explicitly pays for the wider product and its reduction. -/
def residueMulEval (a b modulus : Word) : BitEval Word :=
  let p := mulEval a b
  let r := divEval p.1 modulus
  (r.1.2,p.2+r.2)

theorem residueMulEval_value (a b m : Word) (hm : 0<value m) :
    value (residueMulEval a b m).1=(value a*value b)%value m := by
  have hd := (divEval_semantics (mulEval a b).1 m hm).2
  simpa only [residueMulEval,mulEval_value,mulWord_value] using hd

def primitiveBudget (B : Nat) := 32*(B+1)^2

theorem mulEval_budget (a b : Word) (B : Nat) (ha : a.length≤B) (hb : b.length≤B) :
    (mulEval a b).2≤primitiveBudget B := by
  rw [mulEval_cost]
  have h := mulCost_bound a b
  have h' : 1+a.length*(10*(2*a.length+b.length)+3) ≤ 1+B*(30*B+3) := by
    calc
      _ ≤ 1+B*(10*(2*B+B)+3) := by gcongr
      _ = _ := by ring
  dsimp [primitiveBudget]
  nlinarith

theorem divEval_budget (a b : Word) (B : Nat) (ha : a.length≤B) (hb : b.length≤B) :
    (divEval a b).2≤primitiveBudget B := by
  rw [divEval_cost]
  have h := divCost_bound a b
  have h' : 1+a.length*(14*(a.length+b.length)+4) ≤ 1+B*(28*B+4) := by
    calc
      _ ≤ 1+B*(14*(B+B)+4) := by gcongr
      _ = _ := by ring
  dsimp [primitiveBudget]
  nlinarith

def residueBudget (B : Nat) := 256*(B+1)^2

theorem residueMulEval_budget (a b m : Word) (B : Nat)
    (ha : a.length≤B) (hb : b.length≤B) (hm : m.length≤B) :
    (residueMulEval a b m).2≤residueBudget B := by
  have hmval := mulWord_length a b
  have hml : (mulEval a b).1.length≤3*B := by rw [mulEval_value]; omega
  have hc := mulCost_bound a b
  have hd := divCost_bound (mulEval a b).1 m
  have hc' : 1+a.length*(10*(2*a.length+b.length)+3) ≤ 1+B*(30*B+3) := by
    calc
      _ ≤ 1+B*(10*(2*B+B)+3) := by gcongr
      _ = _ := by ring
  have hd' : 1+(mulEval a b).1.length*(14*((mulEval a b).1.length+m.length)+4)
      ≤ 1+3*B*(56*B+4) := by
    calc
      _ ≤ 1+(3*B)*(14*(3*B+B)+4) := by gcongr
      _ = _ := by ring
  simp only [residueMulEval,mulEval_cost,divEval_cost]
  dsimp [residueBudget]
  nlinarith

end Komorebi.Binary
