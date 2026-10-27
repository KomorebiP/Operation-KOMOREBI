module
public import Euler.TerminalCoordinates
public import Mathlib.Data.Nat.Factorial.BigOperators
public import Mathlib.Algebra.BigOperators.Intervals
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Canonical depth that separates an integer root from every other skeleton root. -/
def skeletonDepth (j i : ℕ) : ℕ := Nat.log 2 (max i (j-1-i))+1

def skeletonSlope (j i : ℕ) : ℕ :=
  padicValNat 2 i.factorial+padicValNat 2 (j-1-i).factorial

def skeletonContent (j i : ℕ) : ℕ := skeletonDepth j i+skeletonSlope j i

lemma skeletonDepth_pos (j i : ℕ) : 0<skeletonDepth j i := by
  unfold skeletonDepth
  omega

/-- Exact odd part of a positive integer. -/
def skeletonOddPart (n : ℕ) : ℕ := n.divMaxPow 2

lemma skeletonOddPart_factor (n : ℕ) :
    skeletonOddPart n*2^(padicValNat 2 n)=n :=
  Nat.divMaxPow_mul_pow_padicValNat _ _

lemma skeletonOddPart_red (n : ℕ) (hn : 0<n) :
    red (skeletonOddPart n:D)=1 := by
  have h : ¬2∣skeletonOddPart n := Nat.not_dvd_divMaxPow (by decide) (by omega)
  have hm : skeletonOddPart n%2=1 := by
    have : skeletonOddPart n%2≠0 := by simpa only [Nat.dvd_iff_mod_eq_zero] using h
    omega
  rw [map_natCast]
  rw [← ZMod.natCast_mod (skeletonOddPart n) 2,hm]
  norm_num

lemma skeletonVal_lt_of_lt_pow (n k : ℕ) (hn : 0<n) (hk : n<2^k) :
    padicValNat 2 n<k := by
  by_contra h
  have hd : 2^k∣n := (padicValNat_dvd_iff_le (by omega : n≠0)).mpr (by omega)
  exact (Nat.le_of_dvd hn hd).not_gt hk

lemma skeletonVal_factorial_sum (n : ℕ) :
    (∑ h ∈ Finset.range n,padicValNat 2 (h+1))=padicValNat 2 n.factorial := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ,ih,Nat.factorial_succ,
      padicValNat.mul (by omega) (Nat.factorial_ne_zero _)]
    omega

lemma skeletonDepth_bounds (j i : ℕ) :
    i<2^(skeletonDepth j i) ∧ j-1-i<2^(skeletonDepth j i) := by
  have h : max i (j-1-i)<2^(Nat.log 2 (max i (j-1-i))+1) :=
    Nat.lt_pow_succ_log_self (by decide) _
  exact ⟨lt_of_le_of_lt (le_max_left _ _) h,lt_of_le_of_lt (le_max_right _ _) h⟩

end Komorebi.Euler
