module
public import BinarySigned

@[expose] public section
namespace Komorebi.Binary

/-- Canonical unsigned conversion. This is a boundary conversion, not a free
step in a full-machine implementation model. -/
def ofNat (n : Nat) : Word :=
  if h : n=0 then [] else decide (n%2=1) :: ofNat (n/2)
termination_by n
decreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by decide)

@[simp] theorem ofNat_value (n : Nat) : value (ofNat n)=n := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n=0
    · subst n; simp [ofNat]
    · have hlt : n/2<n := Nat.div_lt_self (Nat.pos_of_ne_zero hn) (by decide)
      have hr := Nat.mod_lt n (by decide : 0<2)
      have hb : bit (decide (n%2=1)) = n%2 := by
        by_cases he : n%2=1
        · simp [he,bit]
        · have hz : n%2=0 := by omega
          simp [hz,bit]
      rw [ofNat]
      simp only [hn,↓reduceDIte,value_cons,ih _ hlt,hb]
      omega

theorem ofNat_length_le (B n : Nat) (h : n<2^B) : (ofNat n).length≤B := by
  induction B generalizing n with
  | zero =>
    have hn : n=0 := by simpa using h
    subst n; simp [ofNat]
  | succ B ih =>
    by_cases hn : n=0
    · subst n; simp [ofNat]
    · rw [ofNat]
      simp only [hn,↓reduceDIte,List.length_cons]
      have hdiv : n/2<2^B := by rw [pow_succ] at h; omega
      exact Nat.succ_le_succ (ih _ hdiv)

def ofInt (a : Int) : SignedWord := ⟨decide (a<0),ofNat a.natAbs⟩

@[simp] theorem ofInt_value (a : Int) : intValue (ofInt a)=a := by
  by_cases ha : a<0
  · simp [ofInt,intValue,ha,abs_of_neg ha]
  · have hnonneg : 0≤a := by omega
    simp [ofInt,intValue,ha,abs_of_nonneg hnonneg]

/-- A scalar multiplication adapter to the native semantic ring, computed by bits. -/
def mulInt (a b : Int) : Int := intValue (signedMul (ofInt a) (ofInt b))

@[simp] theorem mulInt_eq (a b : Int) : mulInt a b=a*b := by simp [mulInt]

def addInt (a b : Int) : Int := intValue (signedAdd (ofInt a) (ofInt b))

@[simp] theorem addInt_eq (a b : Int) : addInt a b=a+b := by simp [addInt]

def subInt (a b : Int) : Int := intValue (signedSub (ofInt a) (ofInt b))

@[simp] theorem subInt_eq (a b : Int) : subInt a b=a-b := by simp [subInt]

/-- The positive-divisor interface used by the lattice backend. -/
def divModInt (a : Int) (d : Nat) : Option (Int × Nat) :=
  (signedDiv (ofInt a) (ofNat d)).map (fun qr => (intValue qr.1,value qr.2))

theorem divModInt_eq (a : Int) (d : Nat) (hd : 0<d) :
    divModInt a d = some (a/(d:Int),(a%(d:Int)).toNat) := by
  have hs := signedDivRaw_value (ofInt a) (ofNat d) (by simpa using hd)
  have hz : isZero (ofNat d) ≠ true := by simp; omega
  have hr := hs.2
  simp only [ofNat_value,ofInt_value] at hs hr
  have hn : value (signedDivRaw (ofInt a) (ofNat d)).2=(a%(d:Int)).toNat := by
    exact_mod_cast congrArg Int.toNat hr
  simp [divModInt,signedDiv,hz,hs.1,hn]

@[simp] theorem divModInt_zero (a : Int) : divModInt a 0=none := by simp [divModInt,signedDiv]

end Komorebi.Binary
