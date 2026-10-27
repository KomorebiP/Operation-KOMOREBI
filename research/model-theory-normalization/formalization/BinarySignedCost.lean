module
public import BinaryPricing

@[expose] public section
namespace Komorebi.Binary

/-- Full scan: not/and gates and one read/write per input bit; terminal one. -/
def zeroEval : Word → Bool × Nat
  | [] => (true,1)
  | b::bs =>
    let t := zeroEval bs
    ((!b)&&t.1,t.2+4)

@[simp] theorem zeroEval_value (a : Word) : (zeroEval a).1=isZero a := by
  induction a with
  | nil => rfl
  | cons a as ih => simp [zeroEval,isZero,ih]

@[simp] theorem zeroEval_cost (a : Word) : (zeroEval a).2=4*a.length+1 := by
  induction a with
  | nil => rfl
  | cons a as ih => simp [zeroEval,ih]; omega

def differenceEval (a b : Word) : BitEval SignedWord :=
  let width:=max a.length b.length
  let p:=pad a width
  let q:=pad b width
  let s:=subEval p q false
  if s.1.2 then
    let t:=subEval q p false
    (⟨true,t.1.1⟩,2*width+s.2+1+t.2)
  else (⟨false,s.1.1⟩,2*width+s.2+1)

@[simp] theorem differenceEval_value (a b : Word) :
    (differenceEval a b).1=difference a b := by
  simp only [differenceEval,difference,subEval_value]
  split <;> rfl

theorem differenceEval_cost_bound (a b : Word) :
    (differenceEval a b).2≤26*max a.length b.length+3 := by
  have hp : (pad a (max a.length b.length)).length=max a.length b.length := length_pad _ (le_max_left _ _)
  have hq : (pad b (max a.length b.length)).length=max a.length b.length := length_pad _ (le_max_right _ _)
  simp only [differenceEval,subEval_cost,hp,hq]
  split <;> omega

def signedAddEval (a b : SignedWord) : BitEval SignedWord :=
  match a.negative,b.negative with
  | false,false => let z:=addEval a.magnitude b.magnitude false; (⟨false,z.1⟩,z.2+2)
  | true,true => let z:=addEval a.magnitude b.magnitude false; (⟨true,z.1⟩,z.2+2)
  | false,true => let z:=differenceEval a.magnitude b.magnitude; (z.1,z.2+2)
  | true,false => let z:=differenceEval b.magnitude a.magnitude; (z.1,z.2+2)

@[simp] theorem signedAddEval_value (a b : SignedWord) :
    (signedAddEval a b).1=signedAdd a b := by
  rcases a with ⟨an,am⟩;rcases b with ⟨bn,bm⟩
  cases an <;> cases bn <;> simp [signedAddEval,signedAdd]

def signedMulEval (a b : SignedWord) : BitEval SignedWord :=
  let z:=mulEval a.magnitude b.magnitude
  (⟨Bool.xor a.negative b.negative,z.1⟩,z.2+1)

@[simp] theorem signedMulEval_value (a b : SignedWord) :
    (signedMulEval a b).1=signedMul a b := by simp [signedMulEval,signedMul]

/-- Positive-divisor signed correction. Zero rejection is supplied by signedDivEval. -/
def signedDivCoreEval (a : SignedWord) (b : Word) : BitEval (SignedWord × Word) :=
  let z:=divEval a.magnitude b
  if a.negative then
    let zero:=zeroEval z.1.2
    if zero.1 then ((⟨true,z.1.1⟩,z.1.2),z.2+1+zero.2)
    else
      let inc:=addEval z.1.1 [] true
      let width:=max b.length z.1.2.length
      let sub:=subEval (pad b width) (pad z.1.2 width) false
      ((⟨true,inc.1⟩,sub.1.1),z.2+1+zero.2+inc.2+2*width+sub.2)
  else ((⟨false,z.1.1⟩,z.1.2),z.2+1)

@[simp] theorem signedDivCoreEval_value (a : SignedWord) (b : Word) :
    (signedDivCoreEval a b).1=signedDivRaw a b := by
  simp only [signedDivCoreEval,signedDivRaw,divEval_value,zeroEval_value,addEval_value,subEval_value,subNat]
  split
  · split <;> rfl
  · rfl

def signedDivEval (a : SignedWord) (b : Word) : BitEval (Option (SignedWord × Word)) :=
  let z:=zeroEval b
  if z.1 then (none,z.2)
  else let t:=signedDivCoreEval a b; (some t.1,z.2+t.2)

@[simp] theorem signedDivEval_value (a : SignedWord) (b : Word) :
    (signedDivEval a b).1=signedDiv a b := by
  simp only [signedDivEval,signedDiv,zeroEval_value,signedDivCoreEval_value]
  split <;> rfl

def signedBudget (B : Nat) := 64*(B+1)^2

theorem signedAddEval_budget (a b : SignedWord) (B : Nat)
    (ha : a.magnitude.length≤B) (hb : b.magnitude.length≤B) :
    (signedAddEval a b).2≤signedBudget B := by
  have hc:=differenceEval_cost_bound a.magnitude b.magnitude
  have hc':=differenceEval_cost_bound b.magnitude a.magnitude
  have hm : max a.magnitude.length b.magnitude.length≤B := max_le ha hb
  have hm' : max b.magnitude.length a.magnitude.length≤B := max_le hb ha
  rcases a with ⟨an,am⟩;rcases b with ⟨bn,bm⟩
  cases an <;> cases bn <;> simp only [signedAddEval,addEval_cost,signedBudget] <;> nlinarith

theorem signedMulEval_budget (a b : SignedWord) (B : Nat)
    (ha : a.magnitude.length≤B) (hb : b.magnitude.length≤B) :
    (signedMulEval a b).2≤signedBudget B := by
  have hc:=mulEval_budget a.magnitude b.magnitude B ha hb
  dsimp [signedMulEval,signedBudget,primitiveBudget] at *
  nlinarith

theorem signedDivCoreEval_budget (a : SignedWord) (b : Word) (B : Nat)
    (ha : a.magnitude.length≤B) (hb : b.length≤B) :
    (signedDivCoreEval a b).2≤32*(B+1)^2+46*B+4 := by
  have hd:=divEval_budget a.magnitude b B ha hb
  have hrl : (divEval a.magnitude b).1.2.length≤2*B := by
    rw [divEval_value]
    exact le_trans (divRaw_remainder_length _ _) (by omega)
  have hql : (divEval a.magnitude b).1.1.length≤B := by simp; exact ha
  have hp : (pad b (max b.length (divEval a.magnitude b).1.2.length)).length=
      max b.length (divEval a.magnitude b).1.2.length := length_pad _ (le_max_left _ _)
  have hm : max b.length (divEval a.magnitude b).1.2.length≤2*B := by omega
  dsimp only [signedDivCoreEval]
  split
  · split <;> simp only [zeroEval_cost,addEval_cost,subEval_cost,hp,List.length_nil,Nat.max_zero] <;>
      dsimp [primitiveBudget] at hd <;> nlinarith
  · dsimp [primitiveBudget] at hd; nlinarith

theorem signedDivEval_budget (a : SignedWord) (b : Word) (B : Nat)
    (ha : a.magnitude.length≤B) (hb : b.length≤B) :
    (signedDivEval a b).2≤signedBudget B := by
  have hc:=signedDivCoreEval_budget a b B ha hb
  dsimp only [signedDivEval]
  split <;> simp only [zeroEval_cost] <;> dsimp [signedBudget] <;> nlinarith

end Komorebi.Binary
