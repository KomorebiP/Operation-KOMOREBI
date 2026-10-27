module
public import Euler.ResidualCarry
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Binary digits split at the least significant bit, including zero. -/
lemma binaryDigitSum_div_mod (n : ℕ) :
    binaryDigitSum n = n % 2 + binaryDigitSum (n / 2) := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp
  · simp only [binaryDigitSum, Nat.digits_def' (by decide : 1 < 2) hn,
      List.sum_cons]

lemma binaryDigitSum_bit (a b : ℕ) (ha : a < 2) :
    binaryDigitSum (a + 2*b) = a + binaryDigitSum b := by
  rw [binaryDigitSum_div_mod]
  congr 1
  · omega
  · congr 1; omega

lemma binaryDigitSum_odd (n : ℕ) (hn : n % 2 = 1) :
    binaryDigitSum n = binaryDigitSum (n-1)+1 := by
  have h0 := binaryDigitSum_div_mod n
  have h1 := binaryDigitSum_div_mod (n-1)
  have he : (n-1)%2=0 := by omega
  have hd : (n-1)/2=n/2 := by omega
  rw [he,hd,zero_add] at h1
  omega

lemma binaryDigitSum_mul_pow (b L : ℕ) :
    binaryDigitSum (b*2^L) = binaryDigitSum b := by
  induction L with
  | zero => simp
  | succ L ih =>
    rw [pow_succ, show b*(2^L*2)=2*(b*2^L) by ring,
      binaryDigitSum_two_mul, ih]

/-- No binary carry crosses a block boundary. -/
lemma binaryDigitSum_append (b n L : ℕ) (hn : n < 2^L) :
    binaryDigitSum (b*2^L+n)=binaryDigitSum b+binaryDigitSum n := by
  induction L generalizing n with
  | zero =>
    have : n=0 := by simpa using hn
    subst n
    simp
  | succ L ih =>
    have hd : n/2 < 2^L := by
      rw [pow_succ] at hn
      omega
    have he : b*2^(L+1)+n=n%2+2*(b*2^L+n/2) := by
      rw [pow_succ]
      have hm := Nat.mod_add_div n 2
      nlinarith
    rw [he,binaryDigitSum_bit _ _ (Nat.mod_lt _ (by decide)),ih _ hd]
    have hn' := binaryDigitSum_div_mod n
    omega

/-- Complementation inside a fixed binary block. -/
lemma binaryDigitSum_complement (L n : ℕ) (hn : n < 2^L) :
    binaryDigitSum (2^L-1-n)+binaryDigitSum n=L := by
  induction L generalizing n with
  | zero =>
    have : n=0 := by simpa using hn
    subst n
    simp
  | succ L ih =>
    have hp : 0<2^L := by positivity
    have hd : n/2 < 2^L := by
      rw [pow_succ] at hn
      omega
    have hc := ih (n/2) hd
    have hq : (2^(L+1)-1-n)/2=2^L-1-n/2 := by
      rw [pow_succ] at *
      omega
    have hm : (2^(L+1)-1-n)%2+n%2=1 := by
      rw [pow_succ] at *
      omega
    rw [binaryDigitSum_div_mod (2^(L+1)-1-n),hq,
      binaryDigitSum_div_mod n]
    omega

/-- Digit-sum formula for an odd multiple of a power of two minus a short address. -/
lemma binaryDigitSum_wall (b L j : ℕ) (hb : b%2=1) (hj : 0<j) (hjp : j<2^L) :
    binaryDigitSum (b*2^L-j)+binaryDigitSum (j-1)+1=
      binaryDigitSum b+L := by
  have hbpos : 0<b := by omega
  have hp : 0<2^L := by positivity
  have he : b*2^L-j=(b-1)*2^L+(2^L-1-(j-1)) := by
    have hmul : b*2^L=(b-1)*2^L+2^L := by
      rw [← Nat.succ_mul]
      congr 1
      omega
    omega
  rw [he,binaryDigitSum_append (b-1) _ L (by omega)]
  have hc := binaryDigitSum_complement L (j-1) (by omega)
  have ho := binaryDigitSum_odd b hb
  omega

end Komorebi.Euler
