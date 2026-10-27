module
public import BinaryWords

@[expose] public section
namespace Komorebi.Binary

/-- Shift-and-add multiplication on actual bit lists. No native multiplication
is used to compute the value. Leading zero padding is permitted. -/
def mulWord : Word → Word → Word
  | [], _ => []
  | b::bs, a =>
    let shifted := false :: mulWord bs a
    if b then addCarry a shifted false else shifted

@[simp] theorem mulWord_value (a b : Word) : value (mulWord a b) = value a * value b := by
  induction a with
  | nil => simp [mulWord]
  | cons a as ih =>
    cases a <;> simp [mulWord,bit,ih] <;> ring

theorem mulWord_length (a b : Word) : (mulWord a b).length ≤ 2*a.length+b.length := by
  induction a with
  | nil => simp [mulWord]
  | cons a as ih =>
    cases a <;> simp only [mulWord,Bool.false_eq_true,↓reduceIte,
      addCarry_length,List.length_cons] <;> omega

/-- A full-adder column is charged ten gate/cell units, and final-carry output one.
This models explicit Boolean/cell work, not Lean runtime, allocation or index arithmetic. -/
def addCost (a b : Word) : Nat := 10 * max a.length b.length + 1

/-- Cost is accumulated on the same data-dependent recursive path as multiplication. -/
def mulCost : Word → Word → Nat
  | [], _ => 1
  | b::bs, a =>
    mulCost bs a + 2 + if b then addCost a (false :: mulWord bs a) else 0

theorem mulCost_bound (a b : Word) :
    mulCost a b ≤ 1 + a.length * (10*(2*a.length+b.length)+3) := by
  induction a with
  | nil => simp [mulCost]
  | cons a as ih =>
    have hl := mulWord_length as b
    have hh : max b.length ((mulWord as b).length+1) ≤ 2*as.length+b.length+1 := by omega
    cases a <;> simp [mulCost,addCost] <;> nlinarith

/-- One restoring long-division column. Subtraction and comparison are both supplied
by the verified borrow circuit. All data are bit lists; no native division is called. -/
def divStep (divisor : Word) (b : Bool) (qr : Word × Word) : Word × Word :=
  let u := b :: qr.2
  let width := max u.length divisor.length
  let x := pad u width
  let y := pad divisor width
  let s := subBorrow x y false
  if s.2 then (false::qr.1,x) else (true::qr.1,s.1)

def divRaw : Word → Word → Word × Word
  | [], _ => ([],[])
  | b::bs, divisor => divStep divisor b (divRaw bs divisor)

theorem divStep_correct (divisor : Word) (b : Bool) (q r : Word)
    (hr : value r < value divisor) :
    (value (divStep divisor b (q,r)).1 * value divisor +
      value (divStep divisor b (q,r)).2 =
      2*(value q*value divisor+value r)+bit b) ∧
    value (divStep divisor b (q,r)).2 < value divisor := by
  let width := max (b::r).length divisor.length
  let x := pad (b::r) width
  let y := pad divisor width
  have hxl : x.length=width := length_pad _ (le_max_left _ _)
  have hyl : y.length=width := length_pad _ (le_max_right _ _)
  have hvx : value x=bit b+2*value r := by simp [x]
  have hvy : value y=value divisor := by simp [y]
  have hv := subBorrow_value x y false (hxl.trans hyl.symm)
  have hb := subBorrow_false_iff x y (hxl.trans hyl.symm)
  have bitBound := bit_le_one b
  change (value (if (subBorrow x y false).2 then (false::q,x) else (true::q,(subBorrow x y false).1)).1 * _ +
    value (if (subBorrow x y false).2 then (false::q,x) else (true::q,(subBorrow x y false).1)).2 = _) ∧
    value (if (subBorrow x y false).2 then (false::q,x) else (true::q,(subBorrow x y false).1)).2 < _
  cases hbor : (subBorrow x y false).2 with
  | false =>
    simp
    simp [hbor] at hv hb
    rw [hvy,hvx] at hv hb
    constructor <;> nlinarith
  | true =>
    simp
    simp [hbor] at hv hb
    rw [hvy,hvx] at hb
    constructor <;> nlinarith

theorem divRaw_correct (a divisor : Word) (hd : 0 < value divisor) :
    value (divRaw a divisor).1 * value divisor + value (divRaw a divisor).2 = value a ∧
    value (divRaw a divisor).2 < value divisor := by
  induction a with
  | nil => simp [divRaw,hd]
  | cons b bs ih =>
    have hs := divStep_correct divisor b (divRaw bs divisor).1 (divRaw bs divisor).2 ih.2
    simpa only [divRaw,Prod.eta,ih.1,value_cons,Nat.add_comm] using hs

@[simp] theorem divRaw_quotient_length (a divisor : Word) :
    (divRaw a divisor).1.length = a.length := by
  induction a with
  | nil => rfl
  | cons a as ih =>
    simp only [divRaw,divStep]
    split <;> simp [ih]

theorem divStep_remainder_length (divisor : Word) (b : Bool) (qr : Word × Word) :
    (divStep divisor b qr).2.length = max (b::qr.2).length divisor.length := by
  dsimp only [divStep]
  split <;> simp only [subBorrow_length] <;> exact length_pad _ (le_max_left _ _)

theorem divRaw_remainder_length (a divisor : Word) :
    (divRaw a divisor).2.length ≤ a.length + divisor.length := by
  induction a with
  | nil => simp [divRaw]
  | cons a as ih =>
    rw [divRaw, divStep_remainder_length]
    simp only [List.length_cons]
    omega

/-- Each stage explicitly pads two words and executes a seven-gate full subtractor.
Fourteen units per active column plus four stage units is the declared gate/cell model. -/
def divCost : Word → Word → Nat
  | [], _ => 1
  | _b::bs, divisor =>
    let rem := (divRaw bs divisor).2
    divCost bs divisor + 14 * max (rem.length+1) divisor.length + 4

theorem divCost_bound (a divisor : Word) :
    divCost a divisor ≤ 1 + a.length * (14*(a.length+divisor.length)+4) := by
  induction a with
  | nil => simp [divCost]
  | cons a as ih =>
    have hl := divRaw_remainder_length as divisor
    simp only [divCost,List.length_cons]
    have hh : max ((divRaw as divisor).2.length+1) divisor.length ≤
        as.length+1+divisor.length := by omega
    nlinarith

end Komorebi.Binary
