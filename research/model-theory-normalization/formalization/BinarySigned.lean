module
public import BinaryMulDiv

@[expose] public section
namespace Komorebi.Binary

/-- Every zero representation, including padded zero, is recognized. -/
def isZero : Word → Bool
  | [] => true
  | b::bs => (!b) && isZero bs

@[simp] theorem isZero_iff (a : Word) : isZero a = true ↔ value a=0 := by
  induction a with
  | nil => simp [isZero]
  | cons a as ih => cases a <;> simp [isZero,ih]

/-- Subtract padded words. The natural subtraction theorem requires b≤a. -/
def subNat (a b : Word) : Word :=
  let width := max a.length b.length
  (subBorrow (pad a width) (pad b width) false).1

theorem subNat_value (a b : Word) (h : value b≤value a) :
    value (subNat a b) + value b = value a := by
  let width := max a.length b.length
  have ha : (pad a width).length=width := length_pad _ (le_max_left _ _)
  have hb : (pad b width).length=width := length_pad _ (le_max_right _ _)
  have he := subBorrow_value (pad a width) (pad b width) false (ha.trans hb.symm)
  have hn : (subBorrow (pad a width) (pad b width) false).2=false :=
    (subBorrow_false_iff _ _ (ha.trans hb.symm)).mpr (by simpa using h)
  simpa only [subNat,hn,bit_false,Nat.mul_zero,Nat.add_zero,value_pad] using he

structure SignedWord where
  negative : Bool
  magnitude : Word
  deriving DecidableEq, Repr

def intValue (a : SignedWord) : Int :=
  if a.negative then -(value a.magnitude : Int) else (value a.magnitude : Int)

/-- Exact signed difference via borrow, without native integer subtraction. -/
def difference (a b : Word) : SignedWord :=
  let width := max a.length b.length
  let p := pad a width
  let q := pad b width
  let s := subBorrow p q false
  if s.2 then ⟨true,(subBorrow q p false).1⟩ else ⟨false,s.1⟩

theorem difference_value (a b : Word) :
    intValue (difference a b) = (value a : Int) - (value b : Int) := by
  let width := max a.length b.length
  let p := pad a width
  let q := pad b width
  have hp : p.length=width := length_pad _ (le_max_left _ _)
  have hq : q.length=width := length_pad _ (le_max_right _ _)
  have he := subBorrow_value p q false (hp.trans hq.symm)
  have hc := subBorrow_false_iff p q (hp.trans hq.symm)
  change intValue (if (subBorrow p q false).2 then
    ⟨true,(subBorrow q p false).1⟩ else ⟨false,(subBorrow p q false).1⟩) = _
  cases hb : (subBorrow p q false).2 with
  | false =>
    simp [hb] at he
    simp [intValue]
    have he' : value (subBorrow p q false).1 + value b = value a := by simpa [p,q] using he
    omega
  | true =>
    have hle : value p ≤ value q := by simp [hb] at hc; omega
    have hz : (subBorrow q p false).2 = false :=
      (subBorrow_false_iff q p (hq.trans hp.symm)).mpr hle
    have hr := subBorrow_value q p false (hq.trans hp.symm)
    simp [hz] at hr
    simp [intValue]
    have hr' : value (subBorrow q p false).1 + value a = value b := by simpa [p,q] using hr
    omega

def signedAdd (a b : SignedWord) : SignedWord :=
  match a.negative,b.negative with
  | false,false => ⟨false,addCarry a.magnitude b.magnitude false⟩
  | true,true => ⟨true,addCarry a.magnitude b.magnitude false⟩
  | false,true => difference a.magnitude b.magnitude
  | true,false => difference b.magnitude a.magnitude

@[simp] theorem signedAdd_value (a b : SignedWord) :
    intValue (signedAdd a b) = intValue a + intValue b := by
  rcases a with ⟨an,am⟩; rcases b with ⟨bn,bm⟩
  cases an <;> cases bn <;> simp only [signedAdd,difference_value] <;> simp [intValue] <;> ring

def signedNeg (a : SignedWord) : SignedWord := ⟨!a.negative,a.magnitude⟩

@[simp] theorem signedNeg_value (a : SignedWord) : intValue (signedNeg a) = -intValue a := by
  rcases a with ⟨an,am⟩; cases an <;> simp [signedNeg,intValue]

def signedSub (a b : SignedWord) := signedAdd a (signedNeg b)

@[simp] theorem signedSub_value (a b : SignedWord) :
    intValue (signedSub a b) = intValue a - intValue b := by simp [signedSub,sub_eq_add_neg]

def signedMul (a b : SignedWord) : SignedWord :=
  ⟨Bool.xor a.negative b.negative,mulWord a.magnitude b.magnitude⟩

@[simp] theorem signedMul_value (a b : SignedWord) :
    intValue (signedMul a b) = intValue a * intValue b := by
  rcases a with ⟨an,am⟩; rcases b with ⟨bn,bm⟩
  cases an <;> cases bn <;> simp [signedMul,intValue]

/-- Euclidean quotient and nonnegative remainder for a positive divisor.
Negative inexact division rounds the quotient downward, not toward zero. -/
def signedDivRaw (a : SignedWord) (divisor : Word) : SignedWord × Word :=
  let qr := divRaw a.magnitude divisor
  if a.negative then
    if isZero qr.2 then (⟨true,qr.1⟩,qr.2)
    else (⟨true,addCarry qr.1 [] true⟩,subNat divisor qr.2)
  else (⟨false,qr.1⟩,qr.2)

theorem signedDivRaw_spec (a : SignedWord) (divisor : Word) (hd : 0<value divisor) :
    intValue a = intValue (signedDivRaw a divisor).1 * (value divisor : Int) +
      (value (signedDivRaw a divisor).2 : Int) ∧
    value (signedDivRaw a divisor).2 < value divisor := by
  have hraw := divRaw_correct a.magnitude divisor hd
  have he : (value a.magnitude : Int) =
      (value (divRaw a.magnitude divisor).1 : Int) * (value divisor : Int) +
      (value (divRaw a.magnitude divisor).2 : Int) := by exact_mod_cast hraw.1.symm
  rcases a with ⟨neg,mag⟩
  cases neg with
  | false => simpa [signedDivRaw,intValue] using And.intro he hraw.2
  | true =>
    by_cases hz : isZero (divRaw mag divisor).2 = true
    · have hr0 := (isZero_iff _).mp hz
      simp only [signedDivRaw,hz,↓reduceIte,intValue,hr0]
      constructor
      · push_cast at he ⊢; nlinarith
      · exact hd
    · have hdiff := subNat_value divisor (divRaw mag divisor).2 (Nat.le_of_lt hraw.2)
      have hnonzero : value (divRaw mag divisor).2 ≠ 0 := by simpa using hz
      have hdiff' : (value (subNat divisor (divRaw mag divisor).2) : Int) +
          (value (divRaw mag divisor).2 : Int) = (value divisor : Int) := by exact_mod_cast hdiff
      simp [signedDivRaw,hz,intValue]
      constructor
      · nlinarith
      · omega

/-- Uniqueness identifies the binary result with Lean's actual Euclidean arithmetic. -/
theorem signedDivRaw_value (a : SignedWord) (divisor : Word) (hd : 0<value divisor) :
    intValue (signedDivRaw a divisor).1 = intValue a / (value divisor : Int) ∧
    (value (signedDivRaw a divisor).2 : Int) = intValue a % (value divisor : Int) := by
  have hs := signedDivRaw_spec a divisor hd
  have hd' : (0:Int)<(value divisor:Int) := by exact_mod_cast hd
  have hr : (value (signedDivRaw a divisor).2 : Int)<(value divisor:Int) := by exact_mod_cast hs.2
  have hq : intValue a / (value divisor:Int) = intValue (signedDivRaw a divisor).1 :=
    (Int.ediv_eq_iff_of_pos hd').mpr (by constructor <;> nlinarith [Int.natCast_nonneg (value (signedDivRaw a divisor).2)])
  have hi := Int.emod_add_ediv_mul (intValue a) (value divisor : Int)
  rw [hq] at hi
  exact ⟨hq.symm,by linarith [hs.1]⟩

/-- Invalid zero divisors are rejected, including noncanonical padded zeros. -/
def signedDiv (a : SignedWord) (divisor : Word) : Option (SignedWord × Word) :=
  if isZero divisor then none else some (signedDivRaw a divisor)

@[simp] theorem signedDiv_none_iff (a : SignedWord) (divisor : Word) :
    signedDiv a divisor = none ↔ value divisor=0 := by simp [signedDiv]

end Komorebi.Binary
