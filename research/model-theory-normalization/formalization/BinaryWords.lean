module
public import Mathlib.Tactic

@[expose] public section
namespace Komorebi.Binary

abbrev Word := List Bool

def bit (b : Bool) : Nat := if b then 1 else 0

@[simp] theorem bit_false : bit false = 0 := rfl
@[simp] theorem bit_true : bit true = 1 := rfl

def value : Word → Nat
  | [] => 0
  | b :: bs => bit b + 2 * value bs

@[simp] theorem value_nil : value [] = 0 := rfl
@[simp] theorem value_cons (b : Bool) (bs : Word) : value (b::bs) = bit b + 2*value bs := rfl

theorem bit_le_one (b : Bool) : bit b ≤ 1 := by cases b <;> decide

theorem value_lt (a : Word) : value a < 2^a.length := by
  induction a with
  | nil => simp [value]
  | cons a as ih =>
    have ha := bit_le_one a
    simp only [value_cons, List.length_cons, pow_succ]
    omega

def pad (a : Word) (n : Nat) : Word := a ++ List.replicate (n-a.length) false

@[simp] theorem value_append (a b : Word) : value (a++b) = value a + 2^a.length*value b := by
  induction a with
  | nil => simp [value]
  | cons a as ih => simp only [List.cons_append,value_cons,ih,List.length_cons,pow_succ]; ring

@[simp] theorem value_zeros (n : Nat) : value (List.replicate n false) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ,bit,ih]

@[simp] theorem value_pad (a : Word) (n : Nat) : value (pad a n) = value a := by
  simp [pad]

@[simp] theorem length_pad (a : Word) {n : Nat} (h : a.length ≤ n) : (pad a n).length = n := by
  simp only [pad,List.length_append,List.length_replicate]
  omega

/-- One full-adder column: two XORs, two ANDs, one OR. -/
def fullAdd (a b c : Bool) : Bool × Bool :=
  let u := Bool.xor a b
  (Bool.xor u c, (a && b) || (u && c))

theorem fullAdd_correct (a b c : Bool) :
    bit (fullAdd a b c).1 + 2*bit (fullAdd a b c).2 = bit a + bit b + bit c := by
  cases a <;> cases b <;> cases c <;> decide

/-- Ripple carry. Short operands are zero padded; final carry is retained. -/
def addCarry : Word → Word → Bool → Word
  | [], [], c => [c]
  | a::as, [], c =>
    let u := fullAdd a false c
    u.1 :: addCarry as [] u.2
  | [], b::bs, c =>
    let u := fullAdd false b c
    u.1 :: addCarry [] bs u.2
  | a::as, b::bs, c =>
    let u := fullAdd a b c
    u.1 :: addCarry as bs u.2
termination_by a b _ => a.length+b.length

@[simp] theorem addCarry_value (a b : Word) (c : Bool) :
    value (addCarry a b c) = value a + value b + bit c := by
  induction a generalizing b c with
  | nil =>
    induction b generalizing c with
    | nil => simp [addCarry,value]
    | cons b bs ih =>
      have hb := fullAdd_correct false b c
      simp only [addCarry,value_cons,ih,value_nil]
      have hf : bit false = 0 := rfl
      rw [hf] at hb
      nlinarith
  | cons a as ih =>
    cases b with
    | nil =>
      have ha := fullAdd_correct a false c
      simp only [addCarry,value_cons,ih,value_nil]
      have hf : bit false = 0 := rfl
      rw [hf] at ha
      nlinarith
    | cons b bs =>
      have hab := fullAdd_correct a b c
      simp only [addCarry,value_cons,ih]
      nlinarith

@[simp] theorem addCarry_length (a b : Word) (c : Bool) :
    (addCarry a b c).length = max a.length b.length + 1 := by
  induction a generalizing b c with
  | nil =>
    induction b generalizing c with
    | nil => simp [addCarry]
    | cons b bs ih => simp [addCarry,ih]
  | cons a as ih =>
    cases b with
    | nil => simp [addCarry,ih]
    | cons b bs => simp only [addCarry,List.length_cons,ih]; omega

/-- One full-subtractor column; the second component is the outgoing borrow. -/
def fullSub (a b c : Bool) : Bool × Bool :=
  let u := Bool.xor a b
  (Bool.xor u c, ((!a) && b) || ((!u) && c))

theorem fullSub_correct (a b c : Bool) :
    bit (fullSub a b c).1 + bit b + bit c = bit a + 2*bit (fullSub a b c).2 := by
  cases a <;> cases b <;> cases c <;> decide

/-- Fixed-width ripple borrow. Correctness is stated for equal operand lengths. -/
def subBorrow : Word → Word → Bool → Word × Bool
  | [], _, c => ([],c)
  | a::as, bs, c =>
    let u := fullSub a (bs.headD false) c
    let v := subBorrow as bs.tail u.2
    (u.1::v.1,v.2)

@[simp] theorem subBorrow_length (a b : Word) (c : Bool) :
    (subBorrow a b c).1.length = a.length := by
  induction a generalizing b c with
  | nil => rfl
  | cons a as ih => simp [subBorrow,ih]

theorem subBorrow_value (a b : Word) (c : Bool) (h : a.length=b.length) :
    value (subBorrow a b c).1 + value b + bit c =
      value a + 2^a.length * bit (subBorrow a b c).2 := by
  induction a generalizing b c with
  | nil =>
    cases b with
    | nil => simp [subBorrow,value]
    | cons b bs => simp at h
  | cons a as ih =>
    cases b with
    | nil => simp at h
    | cons b bs =>
      have hh : as.length=bs.length := by simpa using h
      have localEq := fullSub_correct a b c
      have tailEq := ih bs (fullSub a b c).2 hh
      simp only [subBorrow,List.headD_cons,List.tail_cons,value_cons,List.length_cons,pow_succ]
      nlinarith

theorem subBorrow_false_iff (a b : Word) (h : a.length=b.length) :
    (subBorrow a b false).2 = false ↔ value b ≤ value a := by
  have he := subBorrow_value a b false h
  have hl := value_lt (subBorrow a b false).1
  rw [subBorrow_length] at hl
  have ha := value_lt a
  have hb := value_lt b
  rw [←h] at hb
  cases hc : (subBorrow a b false).2 <;> simp [hc,bit] at he ⊢ <;> omega

end Komorebi.Binary
