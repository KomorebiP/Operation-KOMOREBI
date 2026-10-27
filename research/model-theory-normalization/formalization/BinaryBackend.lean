module
public import BinarySignedCost

@[expose] public section
namespace Komorebi.Binary

/-- Subtraction uses the proved signed adder after one sign-bit negation. -/
def signedSubEval (a b : SignedWord) : BitEval SignedWord :=
  let z := signedAddEval a (signedNeg b)
  (z.1,z.2+1)

@[simp] theorem signedSubEval_value (a b : SignedWord) :
    (signedSubEval a b).1=signedSub a b := by
  simp [signedSubEval,signedSub]

theorem signedSubEval_budget (a b : SignedWord) (B : Nat)
    (ha : a.magnitude.length≤B) (hb : b.magnitude.length≤B) :
    (signedSubEval a b).2≤residueBudget B := by
  have hc := signedAddEval_budget a (signedNeg b) B ha hb
  dsimp [signedSubEval,signedBudget,residueBudget] at *
  nlinarith

/-- Reduction is charged after addition, including its carry bit. -/
def residueAddEval (a b modulus : Word) : BitEval Word :=
  let s := addEval a b false
  let r := divEval s.1 modulus
  (r.1.2,s.2+r.2)

theorem residueAddEval_value (a b m : Word) (hm : 0<value m) :
    value (residueAddEval a b m).1=(value a+value b)%value m := by
  have hd := (divEval_semantics (addEval a b false).1 m hm).2
  simpa [residueAddEval,bit] using hd

theorem residueAddEval_budget (a b m : Word) (B : Nat)
    (ha : a.length≤B) (hb : b.length≤B) (hm : m.length≤B) :
    (residueAddEval a b m).2≤residueBudget B := by
  have hs : (addEval a b false).1.length≤B+1 := by
    simp only [addEval_value,addCarry_length]
    omega
  have hd := divEval_budget (addEval a b false).1 m (B+1) hs (by omega)
  have hab : max a.length b.length≤B := max_le ha hb
  simp only [residueAddEval,addEval_cost]
  dsimp [primitiveBudget,residueBudget] at *
  nlinarith

/-- The metered implementations have the intended signed arithmetic semantics. -/
theorem signed_arithmetic_semantics (a b : SignedWord) :
    intValue (signedAddEval a b).1=intValue a+intValue b ∧
    intValue (signedSubEval a b).1=intValue a-intValue b ∧
    intValue (signedMulEval a b).1=intValue a*intValue b := by
  simp

/-- Meaning of metered signed division, with an actual positive-divisor premise. -/
theorem signedDivEval_semantics (a : SignedWord) (b : Word) (hb : 0<value b) :
    (signedDivEval a b).1.map (fun qr => (intValue qr.1,value qr.2))=
      some (intValue a / (value b : Int), (intValue a % (value b : Int)).toNat) := by
  rw [signedDivEval_value]
  have hz : isZero b=false := by
    cases h : isZero b
    · rfl
    · have hzero := (isZero_iff b).mp h
      omega
  simp only [signedDiv,hz,Bool.false_eq_true,ite_false,Option.map_some]
  have hs := signedDivRaw_value a b hb
  have hr := hs.2
  have hr' : value (signedDivRaw a b).2=(intValue a % (value b : Int)).toNat := by
    rw [← hr]
    simp
  rw [hs.1,hr']

end Komorebi.Binary
